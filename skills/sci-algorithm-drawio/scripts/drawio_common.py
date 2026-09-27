"""Local Draw.io XML helpers. Standard library only; no network or execution."""
from __future__ import annotations
import base64
import copy
import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

MAX_BYTES = 80 * 1024 * 1024

def safe_xml(data: bytes | str) -> ET.Element:
    raw = data.encode('utf-8') if isinstance(data, str) else data
    if len(raw) > MAX_BYTES:
        raise ValueError('XML exceeds the 80 MiB safety limit')
    if re.search(br'<!\s*(?:DOCTYPE|ENTITY)', raw, re.I):
        raise ValueError('DTD/entity declarations are not accepted')
    return ET.fromstring(raw)

def load_pages(path: str | Path) -> list[tuple[str, ET.Element]]:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise ValueError('Input missing or larger than 80 MiB')
    root = safe_xml(p.read_bytes())
    if root.tag == 'mxGraphModel':
        return [('Page-1', root)]
    if root.tag != 'mxfile':
        raise ValueError('Expected mxfile or mxGraphModel')
    pages = []
    for i, d in enumerate(root.findall('diagram'), 1):
        model = d.find('mxGraphModel')
        if model is None:
            payload = (d.text or '').strip()
            if payload.startswith('<'):
                model = safe_xml(payload)
            else:
                try:
                    compressed = base64.b64decode(payload, validate=True)
                    z = zlib.decompressobj(-15)
                    decoded = z.decompress(compressed, MAX_BYTES + 1)
                    if len(decoded) > MAX_BYTES or not z.eof:
                        raise ValueError('Compressed page too large or incomplete')
                    model = safe_xml(urllib.parse.unquote(decoded.decode('utf-8')))
                except Exception as exc:
                    raise ValueError(f'Cannot decode page {i}: {exc}') from exc
        if model.tag != 'mxGraphModel':
            raise ValueError(f'Page {i} is not mxGraphModel')
        pages.append((d.get('name', f'Page-{i}'), model))
    if not pages:
        raise ValueError('No diagram pages found')
    return pages

def cells(model: ET.Element) -> list[ET.Element]:
    """Normalize standard cells and common object/UserObject wrappers."""
    root = model.find('root')
    if root is None:
        raise ValueError('mxGraphModel is missing root')
    result = []
    for child in root:
        if child.tag == 'mxCell':
            result.append(child)
        elif child.tag in ('object', 'UserObject'):
            original = child.find('mxCell')
            if original is None:
                raise ValueError('Object wrapper missing mxCell')
            c = copy.deepcopy(original)
            if not c.get('id') and child.get('id'):
                c.set('id', child.get('id'))
            if not c.get('value') and child.get('label'):
                c.set('value', child.get('label'))
            result.append(c)
        else:
            raise ValueError(f'Unsupported root child: {child.tag}')
    return result

def style_map(style: str) -> dict[str, str]:
    # Parse only style fields, not arbitrary source content.
    return {part.split('=', 1)[0]: part.split('=', 1)[1]
            for part in style.split(';') if '=' in part}

def image_value(style: str) -> str | None:
    # Draw.io uses both data:image/png,BASE64 and standard ;base64 forms.
    m = re.search(r'(?:^|;)image=(data:image/[^;,]+(?:;base64)?,[^;]*|[^;]*)', style)
    return m.group(1) if m else None

def plain_text(value: str) -> str:
    value = re.sub(r'<(?:br|/div|/p)\b[^>]*>', '\n', value, flags=re.I)
    value = re.sub(r'<[^>]*>', '', value)
    return html.unescape(value).strip()

def wrap_model(name: str, model: ET.Element) -> ET.Element:
    root = ET.Element('mxfile', {'host': 'app.diagrams.net'})
    d = ET.SubElement(root, 'diagram', {'id': 'page-1', 'name': name})
    d.append(copy.deepcopy(model))
    return root

def write_xml(root: ET.Element, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    path.write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=True))
