#!/usr/bin/env python3
"""Inventory pages, native cells, image cells, labels and source styles."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from drawio_common import load_pages, cells, style_map, image_value, plain_text, wrap_model, write_xml

def inspect(path: Path) -> dict:
    pages = []
    for name, model in load_pages(path):
        cc = cells(model)
        vertices = [c for c in cc if c.get('vertex') == '1']
        edges = [c for c in cc if c.get('edge') == '1']
        images = [c for c in vertices if image_value(c.get('style', '')) is not None]
        colors, fonts, shapes, parents = Counter(), Counter(), Counter(), Counter()
        records = []
        for c in cc:
            st = style_map(c.get('style', ''))
            parents[c.get('parent', '(none)')] += 1
            shapes[st.get('shape', 'default')] += 1
            if 'fontSize' in st:
                fonts[st['fontSize']] += 1
            for key in ('fillColor', 'strokeColor', 'fontColor'):
                if key in st:
                    colors[f'{key}:{st[key]}'] += 1
            g = c.find('mxGeometry')
            record = {k: c.get(k) for k in ('id', 'parent', 'source', 'target', 'vertex', 'edge') if c.get(k) is not None}
            record['label'] = plain_text(c.get('value', ''))
            record['geometry'] = dict(g.attrib) if g is not None else None
            record['style'] = {k: v for k, v in st.items() if k != 'image'}
            image = image_value(c.get('style', ''))
            if image is not None:
                record['image'] = {'embedded': image.startswith('data:'), 'data_uri_length': len(image), 'content_omitted': True}
            records.append(record)
        pages.append({'name': name, 'cells': len(cc), 'vertices': len(vertices),
                      'edges': len(edges), 'images': len(images),
                      'non_image_vertices': len(vertices)-len(images),
                      'parent_counts': dict(parents), 'explicit_colors': dict(colors),
                      'explicit_font_sizes': dict(fonts), 'shapes': dict(shapes),
                      'records': records})
    return {'source_name': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'page_count': len(pages), 'pages': pages,
            'limitations': 'Counts do not prove visual quality, scientific correctness or native editability inside image cells.'}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--extract-page', type=int, help='1-based page number; requires --page-out')
    ap.add_argument('--page-out', type=Path)
    args = ap.parse_args()
    try:
        if args.extract_page is not None:
            if args.page_out is None:
                raise ValueError('--extract-page requires --page-out')
            pages = load_pages(args.source)
            if not 1 <= args.extract_page <= len(pages):
                raise ValueError('Requested page does not exist')
            name, model = pages[args.extract_page - 1]
            write_xml(wrap_model(name, model), args.page_out)
        report = inspect(args.source)
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text+'\n', encoding='utf-8')
            print(f'{report["page_count"]} page(s); inventory: {args.out}')
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f'inspect_drawio: {exc}', file=sys.stderr)
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
