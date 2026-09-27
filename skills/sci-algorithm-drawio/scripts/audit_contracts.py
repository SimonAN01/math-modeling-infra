#!/usr/bin/env python3
"""Compare topology, scene and actual XML. Does not validate source-paper truth."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from contracts import load_json, scene_contract_errors, named, anchors_for_edge, finite
from drawio_common import load_pages, cells, style_map, plain_text

def audit(path: Path, scene: dict, topology: dict) -> dict:
    errors = scene_contract_errors(scene, topology)
    reports = []
    pp = load_pages(path)
    sp = scene.get('pages', [])
    if len(pp) != len(sp):
        errors.append('Output page count differs from scene')
    for (name, model), page in zip(pp, sp):
        prefix = str(page.get('id', '?'))
        cc = cells(model)
        actual = {c.get('id'):c for c in cc if c.get('edge')=='1'}
        vertices = {c.get('id'):c for c in cc if c.get('vertex')=='1'}
        expected = named(page.get('edges', []), 'scene.edges')
        nodes = named(page.get('nodes', []), 'scene.nodes')
        if name != page.get('name'):
            errors.append(f'{prefix}: output page name differs')
        if set(vertices) != set(nodes):
            errors.append(f'{prefix}: output vertex set differs from scene')
        for nid in vertices.keys() & nodes.keys():
            c,n=vertices[nid],nodes[nid]
            if c.get('parent')!=n.get('parent','1'):
                errors.append(f'{prefix}/{nid}: XML parent differs from scene')
            if plain_text(c.get('value',''))!=n.get('label','').strip():
                errors.append(f'{prefix}/{nid}: XML node label differs from scene')
            g=c.find('mxGeometry')
            if g is None:
                errors.append(f'{prefix}/{nid}: missing geometry');continue
            for key,field in (('x','x'),('y','y'),('width','w'),('height','h')):
                if abs(finite(g.get(key,0),key)-finite(n.get(field,0),field))>1e-7:
                    errors.append(f'{prefix}/{nid}: XML {key} differs from scene; rerun layout audit on actual geometry')
        for eid in actual.keys() - expected.keys():
            errors.append(f'{prefix}: extra XML relation {eid}')
        for eid in expected.keys() - actual.keys():
            errors.append(f'{prefix}: missing XML relation {eid}')
        fixed = 0
        for eid in actual.keys() & expected.keys():
            c, e = actual[eid], expected[eid]
            for key in ('source','target'):
                if c.get(key)!=e.get(key):
                    errors.append(f'{prefix}/{eid}: XML {key} differs from relation')
            if plain_text(c.get('value',''))!=e.get('label','').strip():
                errors.append(f'{prefix}/{eid}: XML label differs')
            st = style_map(c.get('style',''))
            try:
                anchors = anchors_for_edge(e,nodes)
                okay = True
                for key,value in anchors.items():
                    if key not in st or abs(finite(st.get(key),key)-float(value))>1e-8:
                        errors.append(f'{prefix}/{eid}: missing/changed fixed-point {key}')
                        okay=False
                fixed+=okay
            except (ValueError,TypeError,KeyError,AttributeError) as exc:
                errors.append(f'{prefix}/{eid}: {exc}')
            if st.get('startArrow','none')!='none':
                errors.append(f'{prefix}/{eid}: unexpected start/reverse arrow')
            expected_end=str(e.get('style',{}).get('endArrow','none' if e.get('kind')=='annotation' else 'block'))
            if st.get('endArrow','classic')!=expected_end:
                errors.append(f'{prefix}/{eid}: XML end-arrow differs')
            g=c.find('mxGeometry')
            if g is None:
                errors.append(f'{prefix}/{eid}: missing edge geometry')
                continue
            points=[[float(p.get('x',0)),float(p.get('y',0))] for p in g.findall("Array[@as='points']/mxPoint")]
            if points != e.get('points',[]):
                errors.append(f'{prefix}/{eid}: XML waypoints differ from scene')
        reports.append({'name':name,'expected_relations':len(expected),'xml_relations':len(actual),
                        'fixed_at_both_declared_ports':fixed})
    return {'contract_pass':not errors,'errors':errors,'pages':reports,
            'scientific_truth':'NOT validated; evidence must be checked against original materials',
            'actual_routing':'NOT rendered by this script','interactive_attachment':'NOT tested'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('--scene',type=Path,required=True)
    ap.add_argument('--topology',type=Path,required=True);ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    try:
        result=audit(a.source,load_json(a.scene),load_json(a.topology))
    except Exception as exc:
        result={'contract_pass':False,'errors':[str(exc)]}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(text,encoding='utf-8')
    print(text,end='');return 0 if result['contract_pass'] else 2
if __name__=='__main__':raise SystemExit(main())
