#!/usr/bin/env python3
"""Serialize an explicit scene to native Draw.io XML; no layout or image generation."""
from __future__ import annotations
import argparse
import html
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET
from drawio_common import MAX_BYTES, write_xml
from validate_drawio import validate
from contracts import anchors_for_edge, load_json, scene_contract_errors
from reference_gate import audit_reference_records

# Small, explicit native subset. Unsupported types fail rather than becoming boxes.
BASE = {'html':'1','whiteSpace':'wrap','fontColor':'#252525','fontSize':'22',
        'strokeColor':'#252525','fillColor':'#FFFFFF','strokeWidth':'1',
        'shadow':'0','align':'center','verticalAlign':'middle','spacing':'6'}
KINDS = {
    'rect': ('', {'rounded':'0'}),
    'roundrect': ('', {'rounded':'1','arcSize':'10'}),
    'ellipse': ('ellipse;', {'perimeter':'ellipsePerimeter'}),
    'diamond': ('rhombus;', {'perimeter':'rhombusPerimeter'}),
    'text': ('text;', {'strokeColor':'none','fillColor':'none','spacing':'0'}),
    'group': ('group;', {'strokeColor':'none','fillColor':'none','pointerEvents':'0','container':'1','recursiveResize':'0'}),
    'container': ('', {'rounded':'0','container':'1','recursiveResize':'0','pointerEvents':'0','verticalAlign':'top','spacingTop':'8'}),
    'dashed_group': ('', {'rounded':'0','container':'1','recursiveResize':'0','pointerEvents':'0','dashed':'1','dashPattern':'5 4','verticalAlign':'top','spacingTop':'8'}),
    'image': ('', {'shape':'image','imageAspect':'1','strokeColor':'none','fillColor':'none'})
}

def number(x, name, *, positive=False):
    if isinstance(x, bool): raise ValueError(f'{name}: boolean is not a coordinate')
    try: n=float(x)
    except (ValueError,TypeError) as e: raise ValueError(f'{name}: expected a number') from e
    if not math.isfinite(n) or (positive and n<=0): raise ValueError(f'{name}: invalid value {x!r}')
    return format(n,'.10g')

def label(item):
    # JSON labels are plain text, not arbitrary HTML. XML serialization adds escaping.
    value=item.get('label','')
    if not isinstance(value,str): raise ValueError('label must be a string')
    return html.escape(value,quote=False).replace('\n','<br>')

def style_string(prefix, defaults, overrides):
    if not isinstance(overrides,dict): raise ValueError('style must be an object of key/value pairs')
    data={**defaults,**overrides}
    for k,v in data.items():
        if not isinstance(k,str) or any(c in k for c in ';=\r\n'):
            raise ValueError(f'Invalid style key {k!r}')
        if not isinstance(v,(str,int,float)) or isinstance(v,bool): raise ValueError(f'Invalid style value for {k}')
        if any(c in str(v) for c in ';\r\n'): raise ValueError(f'Invalid style delimiter in {k}')
    if str(data.get('html'))!='1': raise ValueError('The scene builder requires html=1 for safe plain labels')
    return prefix+''.join(f'{k}={v};' for k,v in data.items())

def ordered_nodes(nodes):
    if not isinstance(nodes,list) or not nodes: raise ValueError('Each page must contain actual nodes; empty template rejected')
    known={};order=[];state={}
    for n in nodes:
        if not isinstance(n,dict): raise ValueError('Node must be an object')
        ident=n.get('id')
        if not isinstance(ident,str) or not ident or ident in ('0','1') or ident in known:
            raise ValueError(f'Invalid or duplicate node ID {ident!r}')
        known[ident]=n
    def visit(ident):
        if state.get(ident)==1: raise ValueError(f'Parent cycle at {ident}')
        if state.get(ident)==2:return
        state[ident]=1;n=known[ident];parent=n.get('parent','1')
        if parent!='1':
            if parent not in known:raise ValueError(f'{ident}: missing parent {parent!r}')
            if known[parent].get('kind') not in ('group','container','dashed_group'):
                raise ValueError(f'{ident}: parent {parent} is not a declared container')
            visit(parent)
        order.append(n);state[ident]=2
    for ident in known:visit(ident)
    return order,known

def edge_parent(source,target,nodes):
    # Coordinate frame shared by both terminals. Do not parent an edge to a terminal.
    def ancestors(ident):
        out=[];p=nodes[ident].get('parent','1')
        while True:
            out.append(p)
            if p=='1':return out
            p=nodes[p].get('parent','1')
    target_anc=set(ancestors(target))
    return next(p for p in ancestors(source) if p in target_anc)

def build(scene):
    pages=scene.get('pages')
    if not isinstance(pages,list) or not pages:raise ValueError('scene.pages must be nonempty')
    mx=ET.Element('mxfile',{'host':'app.diagrams.net'});page_ids=set()
    for index,p in enumerate(pages,1):
        pid=p.get('id',f'p{index}')
        if not isinstance(pid,str) or not pid or pid in page_ids:raise ValueError('Duplicate or invalid page ID')
        page_ids.add(pid)
        width=number(p.get('width',1000),'page.width',positive=True);height=number(p.get('height',640),'page.height',positive=True)
        font=p.get('font_family','Noto Serif CJK SC')
        if not isinstance(font,str) or not font:raise ValueError('font_family must be a nonempty string')
        diagram=ET.SubElement(mx,'diagram',{'id':pid,'name':str(p.get('name',f'图{index}'))})
        model=ET.SubElement(diagram,'mxGraphModel',{'dx':'0','dy':'0','grid':'0','gridSize':'10','guides':'1','tooltips':'1',
            'connect':'1','arrows':'1','fold':'0','page':'1','pageScale':'1','pageWidth':width,'pageHeight':height,
            'math':'0','shadow':'0','background':'#FFFFFF'})
        root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',{'id':'0'});ET.SubElement(root,'mxCell',{'id':'1','parent':'0'})
        ordered,lookup=ordered_nodes(p.get('nodes'));ids={'0','1',*lookup}
        for n in ordered:
            kind=n.get('kind','rect')
            if kind not in KINDS:raise ValueError(f'{n["id"]}: unsupported kind {kind!r}; add a verified native implementation')
            prefix,extra=KINDS[kind];st={**BASE,'fontFamily':font,'fontSize':number(p.get('base_font_size',22),'base_font_size',positive=True),**extra}
            if kind=='image':
                image=n.get('image','')
                if not isinstance(image,str) or not image.startswith('data:image/'):
                    raise ValueError('image requires a verified embedded data:image URI; no network URLs')
                image=image.replace(';base64,',',',1)
                st['image']=image
                if n.get('label'):raise ValueError('Use a separate native text node for image annotations')
            attrs={'id':n['id'],'value':label(n),'vertex':'1','parent':n.get('parent','1'),
                'style':style_string(prefix,st,n.get('style',{}))}
            if kind in ('group','container','dashed_group'):attrs['connectable']='0'
            cell=ET.SubElement(root,'mxCell',attrs)
            geom={'x':number(n.get('x',0),n['id']+'.x'),'y':number(n.get('y',0),n['id']+'.y'),
                'width':number(n.get('w'),n['id']+'.w',positive=True),'height':number(n.get('h'),n['id']+'.h',positive=True),'as':'geometry'}
            ET.SubElement(cell,'mxGeometry',geom)
        edges=p.get('edges',[])
        if not isinstance(edges,list):raise ValueError('edges must be a list')
        for e in edges:
            ident=e.get('id');source=e.get('source');target=e.get('target')
            if not isinstance(ident,str) or not ident or ident in ids:raise ValueError(f'Duplicate/invalid edge ID {ident!r}')
            ids.add(ident)
            if source not in lookup or target not in lookup:raise ValueError(f'{ident}: missing terminal; topology edges require source and target IDs')
            for terminal in (source,target):
                if lookup[terminal].get('kind') in ('group','container','dashed_group'):
                    raise ValueError(f'{ident}: bind to a real module/port rather than a nonconnectable container')
            parent=edge_parent(source,target,lookup)
            if 'parent' in e and e['parent']!=parent:raise ValueError(f'{ident}: parent must be common ancestor {parent!r}')
            style={'html':'1','edgeStyle':'orthogonalEdgeStyle','rounded':'0','strokeColor':'#252525','strokeWidth':'1.3',
                'startArrow':'none','endArrow':'none' if e.get('kind')=='annotation' else 'block','endFill':'1',
                'fontFamily':font,'fontSize':number(p.get('edge_font_size',21),'edge_font_size',positive=True),
                'fontColor':'#252525','labelBackgroundColor':'#FFFFFF','jettySize':'8'}
            if 'source_port' in e or 'target_port' in e:
                anchors=anchors_for_edge(e,lookup)
                for key,value in anchors.items():
                    if key in e.get('style',{}) and float(e['style'][key])!=float(value):
                        raise ValueError(f'{ident}: cannot override named fixed port {key}')
                style.update(anchors)
            cell=ET.SubElement(root,'mxCell',{'id':ident,'value':label(e),'edge':'1','parent':parent,'source':source,'target':target,
                'style':style_string('',style,e.get('style',{}))})
            geom=ET.SubElement(cell,'mxGeometry',{'relative':'1','as':'geometry'})
            if 'label_position' in e:
                pos=e['label_position']
                if not isinstance(pos,dict):raise ValueError('label_position must be an object')
                px=number(pos.get('x',0),'label_position.x')
                if not -1<=float(px)<=1:raise ValueError('edge label x must be within [-1,1]')
                geom.set('x',px);geom.set('y',number(pos.get('y',0),'label_position.y'))
                if 'dx' in pos or 'dy' in pos:
                    ET.SubElement(geom,'mxPoint',{'x':number(pos.get('dx',0),'label.dx'),
                        'y':number(pos.get('dy',0),'label.dy'),'as':'offset'})
            if 'points' in e:
                arr=ET.SubElement(geom,'Array',{'as':'points'})
                for point in e['points']:
                    if not isinstance(point,list) or len(point)!=2:raise ValueError('points must be [[x,y],...] in edge parent coordinates')
                    ET.SubElement(arr,'mxPoint',{'x':number(point[0],'point.x'),'y':number(point[1],'point.y')})
    return mx

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('scene',type=Path);ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--force',action='store_true',help='Explicitly overwrite an existing output')
    ap.add_argument('--topology',type=Path,help='Required for final output: independently checked relation whitelist')
    ap.add_argument('--references',type=Path,help='Required for final output: actual search, visual inspection and adaptation records')
    ap.add_argument('--draft',action='store_true',help='Explicit unverified draft only; missing prerequisite records are not approval')
    args=ap.parse_args();tmp=None
    try:
        if args.scene.stat().st_size>MAX_BYTES:raise ValueError('Scene too large')
        inputs=[args.scene,args.topology,args.references]
        if any(p is not None and args.out.resolve()==p.resolve() for p in inputs):
            raise ValueError('Output must not overwrite scene, topology, or reference inputs')
        if args.out.exists() and not args.force:raise ValueError('Output exists; use a new name or --force after review')
        scene=load_json(args.scene)
        topology=load_json(args.topology) if args.topology else None
        if topology is not None:
            errors=scene_contract_errors(scene,topology)
            if errors:raise ValueError('Relation contract failed: '+ '; '.join(errors))
        elif not args.draft:
            raise ValueError('Final build requires --topology. Use --draft only for an explicitly unverified draft.')
        else:
            print('DRAFT ONLY: scientific relations and fixed-port contract NOT verified.',file=sys.stderr)
        if args.references:
            if topology is None:raise ValueError('--references requires --topology')
            reference_report=audit_reference_records(load_json(args.references),topology,base_dir=args.references.parent)
            if not reference_report['reference_record_pass']:
                raise ValueError('Reference prerequisite failed: '+'; '.join(reference_report['errors']))
        elif not args.draft:
            raise ValueError('Final build requires --references. Search, inspect the original figures and record adaptation before drawing.')
        if args.draft:
            print('DRAFT ONLY: not a final figure; missing reviews must not be implied complete.',file=sys.stderr)
        root=build(scene)
        if args.draft:root.set('reviewStatus','unverified-draft')
        args.out.parent.mkdir(parents=True,exist_ok=True)
        fd,name=tempfile.mkstemp(prefix='.drawio-build-',suffix='.drawio',dir=args.out.parent);os.close(fd);tmp=Path(name)
        write_xml(root,tmp);report=validate(tmp)
        if not report['structural_pass']:raise ValueError('; '.join(report['errors']))
        os.replace(tmp,args.out);tmp=None
        print(f'Wrote {args.out}; {len(report["pages"])} page(s). Structure checked; relation contract '+('checked against supplied table' if args.topology else 'NOT checked (DRAFT)')+'. Reference-record gate '+('checked' if args.references else 'NOT checked (DRAFT)')+'. Actual source inspection, scientific, rendered and interactive review remain separate.')
        for warning in report['warnings']:print('WARNING: '+warning,file=sys.stderr)
        return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(f'build_drawio: {exc}',file=sys.stderr);return 2
    finally:
        if tmp and tmp.exists():tmp.unlink()
if __name__=='__main__':raise SystemExit(main())
