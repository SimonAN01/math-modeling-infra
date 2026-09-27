#!/usr/bin/env python3
"""Structural checks only. Visual and scientific review remain required."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import sys
from drawio_common import load_pages, cells, style_map, image_value, plain_text

def validate(path: Path) -> dict:
    errors, warnings, summaries = [], [], []
    for pi, (name, model) in enumerate(load_pages(path), 1):
        cc = cells(model)
        counts = Counter(c.get('id') for c in cc)
        lookup = {c.get('id'): c for c in cc if c.get('id')}
        prefix = f'page {pi} ({name})'
        for ident, count in counts.items():
            if not ident or count != 1:
                errors.append(f'{prefix}: missing or duplicate id {ident!r}')
        if '0' not in lookup or '1' not in lookup or lookup.get('1', {}).get('parent') != '0':
            errors.append(f'{prefix}: expected root 0 and default layer 1 parent=0')
        if '0' in lookup and lookup['0'].get('parent'):
            errors.append(f'{prefix}: root 0 must not have a parent')
        if model.get('math', '0') != '0':
            errors.append(f'{prefix}: math mode is enabled; this skill requires no in-figure equations')
        nv = ne = ni = ng = 0
        for c in cc:
            ident = c.get('id', '?'); where = f'{prefix}/{ident}'
            parent = c.get('parent')
            if ident != '0' and parent not in lookup:
                errors.append(f'{where}: missing parent {parent!r}')
            visited = {ident}; ancestor = parent
            while ancestor is not None and ancestor in lookup:
                if ancestor in visited:
                    errors.append(f'{where}: parent cycle')
                    break
                visited.add(ancestor)
                ancestor = lookup[ancestor].get('parent')
            vertex, edge = c.get('vertex') == '1', c.get('edge') == '1'
            nv += vertex; ne += edge
            if vertex and edge:
                errors.append(f'{where}: both vertex and edge flags are set')
            st = style_map(c.get('style', ''))
            ng += (c.get('style', '').startswith('group;') or st.get('container') == '1')
            g = c.find('mxGeometry')
            if vertex or edge:
                if g is None:
                    errors.append(f'{where}: missing mxGeometry'); continue
                for attr in ('x', 'y', 'width', 'height'):
                    if g.get(attr) is not None:
                        try:
                            value = float(g.get(attr))
                            if not math.isfinite(value): raise ValueError()
                        except ValueError:
                            errors.append(f'{where}: invalid geometry {attr}')
                if vertex:
                    for attr in ('width', 'height'):
                        try:
                            if float(g.get(attr, '0')) <= 0:
                                # Common auto-sized edge-label cells are allowed, but flagged.
                                if parent in lookup and lookup[parent].get('edge') == '1':
                                    warnings.append(f'{where}: auto-sized edge label; inspect rendered text')
                                else:
                                    errors.append(f'{where}: vertex {attr} must be positive')
                        except ValueError:
                            pass
                    try:
                        if float(g.get('x', '0')) < 0 or float(g.get('y', '0')) < 0:
                            warnings.append(f'{where}: negative coordinates; inspect clipping/intentional placement')
                    except ValueError:
                        pass
                if edge:
                    if g.get('relative') != '1':
                        warnings.append(f'{where}: edge geometry normally uses relative=1')
                    for terminal in ('source', 'target'):
                        ref = c.get(terminal)
                        if ref:
                            if ref not in lookup:
                                errors.append(f'{where}: missing {terminal} id {ref}')
                            elif lookup[ref].get('vertex') != '1':
                                warnings.append(f'{where}: {terminal} is not a vertex; inspect intent')
                        elif g.find(f"mxPoint[@as='{terminal}Point']") is None:
                            errors.append(f'{where}: no {terminal} reference or explicit point')
                        else:
                            warnings.append(f'{where}: floating {terminal} point; classify as annotation or bind to a port')
            image = image_value(c.get('style', ''))
            if image is not None:
                ni += 1
                if not image.startswith('data:'):
                    warnings.append(f'{where}: external/local image reference may be nonportable')
            text = plain_text(c.get('value', ''))
            if re.search(r'\\(?:frac|sum|begin|alpha|beta)|\$[^$]+\$|[≤≥]|[=∑∏∫]', text):
                warnings.append(f'{where}: possible equation label; human review required: {text[:90]}')
            for key in ('movable', 'editable'):
                if st.get(key) == '0' and (text or (vertex and not image)):
                    warnings.append(f'{where}: {key}=0; confirm this does not block required editing')
        if ni and nv-ni <= 3:
            warnings.append(f'{prefix}: mostly image objects; possible image-only pseudo-editability')
        summaries.append({'name':name,'cells':len(cc),'vertices':nv,'edges':ne,'images':ni,'group_or_container_vertices':ng})
    return {'file': path.name, 'structural_pass': not errors, 'errors': errors, 'warnings': warnings,
            'pages': summaries, 'visual_review': 'not performed by this script',
            'scientific_review': 'not performed by this script',
            'interactive_edit_test': 'not performed by this script'}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path); ap.add_argument('--report', type=Path)
    args=ap.parse_args()
    try:
        report=validate(args.source)
    except Exception as exc:
        report={'structural_pass':False,'errors':[str(exc)],'warnings':[]}
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(text+'\n',encoding='utf-8')
    print(text)
    return 0 if report['structural_pass'] else 2
if __name__=='__main__':
    raise SystemExit(main())
