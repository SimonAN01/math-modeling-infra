#!/usr/bin/env python3
"""Heuristic scene audit: print-size estimates, spacing, boxes and planned routes.
No drawing renderer, OCR, scientific verification or blanket visual pass is provided.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import unicodedata
from contracts import load_json, named, finite, CONTAINERS, anchors_for_edge


def rect_intersection(a, b):
    x=max(a[0],b[0]);y=max(a[1],b[1]);r=min(a[0]+a[2],b[0]+b[2]);d=min(a[1]+a[3],b[1]+b[3])
    return max(0,r-x)*max(0,d-y)

def envelope(rects):
    if not rects:return None
    x=min(r[0] for r in rects);y=min(r[1] for r in rects)
    return (x,y,max(r[0]+r[2] for r in rects)-x,max(r[1]+r[3] for r in rects)-y)

def union_area(rects):
    if not rects:return 0.0
    xs=sorted({x for r in rects for x in (r[0],r[0]+r[2])});area=0.
    for x1,x2 in zip(xs,xs[1:]):
        spans=sorted((r[1],r[1]+r[3]) for r in rects if r[0]<x2 and r[0]+r[2]>x1)
        low=high=None;length=0.
        for a,b in spans:
            if low is None:low,high=a,b
            elif a<=high:high=max(high,b)
            else:length+=high-low;low,high=a,b
        if low is not None:length+=high-low
        area+=(x2-x1)*length
    return area

def abs_rectangles(nodes):
    result={};visiting=set()
    def locate(ident):
        if ident in result:return result[ident]
        if ident in visiting:raise ValueError('Parent cycle in scene')
        visiting.add(ident);n=nodes[ident];parent=n.get('parent','1')
        dx=dy=0.
        if parent!='1':
            if parent not in nodes:raise ValueError(f'Missing parent {parent}')
            pr=locate(parent);dx,dy=pr[:2]
        x=finite(n.get('x',0),'x')+dx;y=finite(n.get('y',0),'y')+dy
        w=finite(n.get('w'),'w');h=finite(n.get('h'),'h')
        if w<=0 or h<=0:raise ValueError(f'{ident}: nonpositive box size')
        result[ident]=(x,y,w,h);visiting.remove(ident);return result[ident]
    for ident in nodes:locate(ident)
    return result

def ancestors(ident,nodes):
    out=[];p=nodes[ident].get('parent','1')
    while True:
        out.append(p)
        if p=='1':return out
        p=nodes[p].get('parent','1')

def char_width(ch):
    if ch.isspace():return .33
    return 1.0 if unicodedata.east_asian_width(ch) in ('W','F','A') else .55

def estimated_lines(label,width,font_size):
    capacity=max(.1,width/font_size);total=0
    for line in label.split('\n'):
        length=0;count=1
        for ch in line:
            cw=char_width(ch)
            if length and length+cw>capacity:count+=1;length=cw
            else:length+=cw
        total+=count
    return total

def segment_hits_rect(a,b,r):
    # Axis-aligned planned paths only, and only strict interior intersections.
    x,y,w,h=r;eps=.5
    if abs(a[1]-b[1])<1e-7:
        return y+eps<a[1]<y+h-eps and max(min(a[0],b[0]),x+eps)<min(max(a[0],b[0]),x+w-eps)
    if abs(a[0]-b[0])<1e-7:
        return x+eps<a[0]<x+w-eps and max(min(a[1],b[1]),y+eps)<min(max(a[1],b[1]),y+h-eps)
    return False

def audit(scene):
    pages=scene.get('pages')
    if not isinstance(pages,list) or not pages:raise ValueError('scene.pages is empty or invalid')
    errors=[];warnings=[];summaries=[]
    for page in pages:
        name=page.get('name',page.get('id','?'))
        def issue(code,obj,message,hard=False):
            (errors if hard else warnings).append({'page':name,'code':code,'object':obj,'detail':message})
        nodes=named(page.get('nodes'), 'scene.nodes')
        if not nodes:raise ValueError('Scene must contain actual nodes')
        boxes=abs_rectangles(nodes);F=finite(page.get('base_font_size',22),'base_font_size')
        if F<=0:raise ValueError('base_font_size must be positive')
        paper=page.get('paper',{});paper_mm=finite(paper.get('width_mm',160),'paper.width_mm')
        if paper_mm<=0:raise ValueError('paper.width_mm must be positive')
        min_pt=finite(paper.get('min_text_pt',8),'paper.min_text_pt')
        main_min=finite(paper.get('main_min_pt',9.5),'paper.main_min_pt')
        note_min=finite(paper.get('note_min_pt',8.5),'paper.note_min_pt')
        visible=[r for k,r in boxes.items() if nodes[k].get('kind')!='group']
        if not visible:raise ValueError('No visible content')
        extent=envelope(visible);route_points=[]
        for e in page.get('edges',[]):
            if e.get('source') not in nodes or e.get('target') not in nodes:
                issue('missing_terminal',e.get('id'), 'Run contract/structural audit first',True);continue
            sa=ancestors(e['source'],nodes);ta=set(ancestors(e['target'],nodes));parent=next(a for a in sa if a in ta)
            px,py=(0.,0.) if parent=='1' else boxes[parent][:2]
            for pt in e.get('points',[]):
                if not isinstance(pt,list) or len(pt)!=2:raise ValueError('Invalid edge point')
                route_points.append((finite(pt[0],'point.x')+px,finite(pt[1],'point.y')+py,0.,0.))
        extent=envelope(visible+route_points)
        estimate_width=extent[2]+20 # renderer wrapper uses border=10 per side
        export_width=finite(paper.get('export_width_units',estimate_width),'paper.export_width_units')
        if export_width<=0:raise ValueError('export_width_units must be positive')
        if export_width+1e-7<extent[2]:
            issue('export_extent_understated','page','Declared export width is smaller than planned visible content',True)
            export_width=estimate_width
        scale_pt=paper_mm*72/25.4/export_width
        text_stats=[];leaf_ids=[k for k,n in nodes.items() if n.get('kind') not in CONTAINERS]
        for ident,n in nodes.items():
            st=n.get('style',{});label=n.get('label','')
            if not isinstance(label,str):raise ValueError('Node labels must be text')
            font=finite(st.get('fontSize',F),'fontSize')
            if font<=0:raise ValueError('fontSize must be positive')
            if label.strip():
                pt=font*scale_pt;role=n.get('text_role','main')
                text_stats.append({'id':ident,'role':role,'font_size_units':font,'estimated_pt':round(pt,2)})
                if pt<min_pt:
                    issue('text_below_minimum',ident,f'{pt:.2f} pt estimated, below {min_pt:g} pt',True)
                elif pt<(note_min if role=='note' else main_min):
                    issue('text_below_target',ident,f'{pt:.2f} pt estimated at {paper_mm:g} mm width')
                if n.get('kind') not in CONTAINERS and n.get('kind')!='image':
                    base=finite(st.get('spacing',0 if n.get('kind')=='text' else 6),'spacing')
                    left=base+finite(st.get('spacingLeft',0),'spacingLeft')
                    right=base+finite(st.get('spacingRight',0),'spacingRight')
                    top=base+finite(st.get('spacingTop',0),'spacingTop')
                    bottom=base+finite(st.get('spacingBottom',0),'spacingBottom')
                    width=boxes[ident][2]-left-right;height=boxes[ident][3]-top-bottom
                    lines=estimated_lines(label,width,font)
                    needed=lines*font*1.2
                    if width<font or needed>height+font*.3:
                        issue('text_fit_risk',ident,f'Estimated {lines} lines need about {needed:.1f} units; interior height {height:.1f}. Check actual font/render.')
                    if n.get('kind') in ('rect','roundrect') and height>max(needed*2.2,needed+1.6*F):
                        issue('oversized_text_box',ident,'Text-only module is much taller than estimated content; tighten unless other meaningful internal objects justify it')
        # Edge label point size matters as much as node labels.
        for e in page.get('edges',[]):
            if str(e.get('label','')).strip():
                f=finite(e.get('style',{}).get('fontSize',page.get('edge_font_size',21)),'edge.fontSize')
                pt=f*scale_pt;text_stats.append({'id':e.get('id'),'role':'edge-label','font_size_units':f,'estimated_pt':round(pt,2)})
                if pt<min_pt:issue('text_below_minimum',e.get('id'),f'Edge label estimated at {pt:.2f} pt',True)
                elif pt<note_min:issue('text_below_target',e.get('id'),f'Edge label estimated at {pt:.2f} pt')
        # Same-level unrelated leaves should not overlap.
        if len(leaf_ids)>2000:issue('audit_limit','page','Over 2000 leaf objects: detailed pairwise overlap audit skipped')
        else:
            for i,a in enumerate(leaf_ids):
                for b in leaf_ids[i+1:]:
                    if nodes[a].get('parent','1')!=nodes[b].get('parent','1'):continue
                    if b in nodes[a].get('allow_overlap_with',[]) or a in nodes[b].get('allow_overlap_with',[]):continue
                    if rect_intersection(boxes[a],boxes[b])>1:
                        issue('peer_overlap',f'{a},{b}','Sibling leaf bounding boxes overlap; intentional layering must be explicitly reviewed')
        for ident,n in nodes.items():
            parent=n.get('parent','1')
            if parent!='1':
                x,y,w,h=boxes[ident];px,py,pw,ph=boxes[parent]
                if x<px-.5 or y<py-.5 or x+w>px+pw+.5 or y+h>py+ph+.5:
                    issue('outside_parent',ident,f'Child extends outside parent {parent}; inspect intentional interface or clipping')
        # Outer containers do not count as filled content.
        for ident,n in nodes.items():
            if n.get('kind') not in CONTAINERS:continue
            children=[boxes[k] for k,nn in nodes.items() if nn.get('parent','1')==ident]
            if not children:
                issue('empty_container',ident,'Container has no native child objects; do not use large empty wrappers');continue
            env=envelope(children);r=boxes[ident]
            pads={'left':env[0]-r[0],'right':r[0]+r[2]-env[0]-env[2],
                  'top':env[1]-r[1],'bottom':r[1]+r[3]-env[1]-env[3]}
            for side,value in pads.items():
                limit=2.5*F if side=='top' and n.get('label') else 1.4*F
                if value>limit:
                    issue('loose_container',ident,f'{side} content-to-frame gap {value:.1f} units ({value/F:.2f}F); justify title/routing or shrink')
        for adj in page.get('layout',{}).get('adjacencies',[]):
            a,b=adj.get('a'),adj.get('b');axis=adj.get('axis')
            if a not in boxes or b not in boxes or axis not in ('x','y'):
                issue('invalid_adjacency',f'{a},{b}','Explicit adjacency must name existing boxes and x/y',True);continue
            idx=0 if axis=='x' else 1;dim=2 if idx==0 else 3
            ra,rb=sorted([boxes[a],boxes[b]],key=lambda r:r[idx])
            gap=rb[idx]-(ra[idx]+ra[dim]);limit=finite(adj.get('max_gap_em',1.4),'max_gap_em')*F
            if gap>limit:
                reason=adj.get('reason','No reason supplied')
                issue('excessive_gap',f'{a},{b}',f'{gap:.1f} units ({gap/F:.2f}F), above {limit/F:.2f}F. Recorded reason: {reason}')
        planned_routes=unknown_routes=0
        for e in page.get('edges',[]):
            ident=e.get('id');s=e.get('source');t=e.get('target')
            if s not in boxes or t not in boxes:continue
            try:anchor=anchors_for_edge(e,nodes)
            except ValueError:
                unknown_routes+=1;issue('route_unknown',ident,'Missing named ports; no planned path assertion');continue
            x1,y1,w1,h1=boxes[s];x2,y2,w2,h2=boxes[t]
            u=(x1+float(anchor['exitX'])*w1,y1+float(anchor['exitY'])*h1)
            v=(x2+float(anchor['entryX'])*w2,y2+float(anchor['entryY'])*h2)
            nonrect=False
            for k,prefix in ((s,'exit'),(t,'entry')):
                if nodes[k].get('kind') in ('ellipse','diamond'):
                    xy=(float(anchor[prefix+'X']),float(anchor[prefix+'Y']))
                    if xy not in ((0,.5),(1,.5),(.5,0),(.5,1)):nonrect=True
            ta=set(ancestors(t,nodes));parent=next(a for a in ancestors(s,nodes) if a in ta)
            px,py=(0.,0.) if parent=='1' else boxes[parent][:2]
            points=[u]+[(float(p[0])+px,float(p[1])+py) for p in e.get('points',[])]+[v]
            segments=[(a,b) for a,b in zip(points,points[1:]) if a!=b]
            if nonrect or str(e.get('style',{}).get('curved','0'))=='1' or any(abs(a[0]-b[0])>1e-7 and abs(a[1]-b[1])>1e-7 for a,b in segments):
                unknown_routes+=1;issue('route_unknown',ident,'Automatic/nonrectangular/curved route needs actual renderer; no obstacle-free claim');continue
            planned_routes+=1
            for leaf in leaf_ids:
                if leaf in (s,t):continue
                if any(segment_hits_rect(a,b,boxes[leaf]) for a,b in segments):
                    issue('planned_route_through_node',ident,f'Planned segment crosses unrelated object {leaf}; reorder nodes or reroute')
            turns=max(0,len(segments)-1)
            budget=4 if e.get('kind')=='feedback' else 2
            if turns>budget:issue('many_route_turns',ident,f'{turns} planned turns; inspect layout before adding more waypoints')
        lr=[boxes[k] for k in leaf_ids];le=envelope(lr)
        proxy=None
        if le and le[2]*le[3]>0 and len(lr)<=2000:proxy=union_area(lr)/(le[2]*le[3])
        summaries.append({'name':name,'paper_width_mm':paper_mm,'planned_extent_units':list(extent),
            'export_width_used_units':export_width,'width_source':'declared actual export width' if 'export_width_units' in paper else 'planned geometry plus 20-unit border; actual export still required',
            'text_sizes':text_stats,'leaf_bbox_union_to_envelope_proxy':round(proxy,3) if proxy is not None else None,
            'density_note':'Diagnostic proxy only, excludes containers; not a universal density score or pass criterion',
            'planned_orthogonal_routes_checked':planned_routes,'routes_requiring_actual_render':unknown_routes,
            'recorded_layout_exceptions':page.get('layout',{}).get('exceptions',[])})
    return {'layout_hard_pass':not errors,'errors':errors,'warnings':warnings,'pages':summaries,
            'visual_acceptance':'NOT determined: actual final-size rendering and viewing required',
            'limits':['Text fit uses estimated character widths, not a font engine','Only declared adjacencies are gap-audited',
                      'Planned polylines are not the editor final routes','Does not detect every possible empty region or line crossing',
                      'Does not verify scientific relations']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('scene',type=Path);ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    try:result=audit(load_json(a.scene))
    except Exception as exc:result={'layout_hard_pass':False,'errors':[str(exc)],'warnings':[]}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(text,encoding='utf-8')
    print(text,end='');return 0 if result['layout_hard_pass'] else 2
if __name__=='__main__':raise SystemExit(main())
