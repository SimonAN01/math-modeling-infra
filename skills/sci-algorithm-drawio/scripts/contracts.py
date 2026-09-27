"""Scene/topology consistency only; this module cannot verify scientific evidence."""
from __future__ import annotations
import json
import math
from pathlib import Path
from drawio_common import MAX_BYTES

RELATION_KINDS = {'data', 'control', 'feedback', 'annotation'}
CONTAINERS = {'group', 'container', 'dashed_group'}

def load_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError('JSON input missing or larger than safety limit')
    obj = json.loads(path.read_text(encoding='utf-8'),
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: '+x)))
    if not isinstance(obj, dict):
        raise ValueError('JSON document must be an object')
    return obj

def finite(x, what: str) -> float:
    if isinstance(x, bool):
        raise ValueError(f'{what}: boolean is not a number')
    try:
        n = float(x)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{what}: expected finite number') from exc
    if not math.isfinite(n):
        raise ValueError(f'{what}: expected finite number')
    return n

def named(items, what: str) -> dict:
    if not isinstance(items, list):
        raise ValueError(f'{what}: expected a list')
    result = {}
    for obj in items:
        if not isinstance(obj, dict):
            raise ValueError(f'{what}: item must be an object')
        ident = obj.get('id')
        if not isinstance(ident, str) or not ident or ident in result:
            raise ValueError(f'{what}: invalid/duplicate ID {ident!r}')
        result[ident] = obj
    return result

def anchors_for_edge(edge: dict, nodes: dict) -> dict[str, str]:
    result = {}
    for terminal, prefix in (('source', 'exit'), ('target', 'entry')):
        ident, portname = edge.get(terminal), edge.get(terminal+'_port')
        if ident not in nodes or not isinstance(portname, str) or not portname:
            raise ValueError(f'{edge.get("id")}: missing {terminal} or named port')
        port = nodes[ident].get('ports', {}).get(portname)
        if not isinstance(port, dict):
            raise ValueError(f'{edge.get("id")}: undefined {terminal} port {ident}.{portname}')
        x, y = finite(port.get('x'), 'port.x'), finite(port.get('y'), 'port.y')
        if not (0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError(f'{edge.get("id")}: relative port coordinates must be within [0,1]')
        per = finite(port.get('perimeter', 1), 'port.perimeter')
        if per not in (0, 1):
            raise ValueError('port.perimeter must be 0 or 1')
        result.update({prefix+'X':format(x, '.10g'), prefix+'Y':format(y, '.10g'),
                       prefix+'Dx':'0', prefix+'Dy':'0', prefix+'Perimeter':str(int(per))})
    return result

def scene_contract_errors(scene: dict, topology: dict) -> list[str]:
    errors = []
    try:
        pages = named(scene.get('pages'), 'scene.pages')
        tpages = named(topology.get('pages'), 'topology.pages')
    except (ValueError, TypeError, AttributeError) as exc:
        return [str(exc)]
    if not pages or not tpages:
        return ['Both scene and topology must contain real pages']
    if set(pages) != set(tpages):
        errors.append('Page IDs differ between scene and topology')
    for pid in pages.keys() & tpages.keys():
        p, t = pages[pid], tpages[pid]
        try:
            sn = named(p.get('nodes'), 'scene.nodes')
            tn = named(t.get('nodes'), 'topology.nodes')
            se = named(p.get('edges', []), 'scene.edges')
            te = named(t.get('edges', []), 'topology.edges')
        except (ValueError, TypeError, AttributeError) as exc:
            errors.append(f'{pid}: {exc}')
            continue
        if not tn:
            errors.append(f'{pid}: topology requires actual semantic nodes')
        if p.get('name') != t.get('name'):
            errors.append(f'{pid}: page name differs')
        for ident in tn.keys() - sn.keys():
            errors.append(f'{pid}: missing semantic node {ident}')
        for ident in tn.keys() & sn.keys():
            if sn[ident].get('kind') in CONTAINERS:
                errors.append(f'{pid}/{ident}: semantic terminal must be a real module/interface, not a nonconnectable container')
            ports = tn[ident].get('ports')
            if not isinstance(ports, dict):
                errors.append(f'{pid}/{ident}: logical ports must be an object')
                continue
            for portname, port in ports.items():
                if not isinstance(port, dict) or port.get('direction') not in ('in', 'out', 'inout') or not port.get('channel'):
                    errors.append(f'{pid}/{ident}.{portname}: declare direction and channel')
        for ident in te.keys() - se.keys():
            errors.append(f'{pid}: missing relation {ident}')
        for ident in se.keys() - te.keys():
            errors.append(f'{pid}: extra unregistered relation {ident}')
        for eid, e in te.items():
            at = f'{pid}/{eid}'
            if e.get('status') != 'confirmed':
                errors.append(f'{at}: unresolved relation is not allowed in final build')
            for field in ('meaning', 'evidence'):
                if not isinstance(e.get(field), str) or not e[field].strip():
                    errors.append(f'{at}: missing {field}')
            kind = e.get('kind')
            if kind not in RELATION_KINDS:
                errors.append(f'{at}: unknown relation kind {kind!r}')
            if not isinstance(e.get('label', ''), str) or not isinstance(e.get('condition', ''), str):
                errors.append(f'{at}: label and condition must be text')
            declared_ports = []
            for terminal, direction in (('source', 'out'), ('target', 'in')):
                node = tn.get(e.get(terminal), {})
                ports = node.get('ports', {})
                port = ports.get(e.get(terminal+'_port')) if isinstance(ports, dict) else None
                if not isinstance(port, dict):
                    errors.append(f'{at}: undeclared logical {terminal} port')
                    continue
                if kind != 'annotation' and port.get('direction') not in (direction, 'inout'):
                    errors.append(f'{at}: wrong {terminal} port direction')
                declared_ports.append(port)
            if len(declared_ports) == 2 and kind != 'annotation':
                if declared_ports[0].get('channel') != declared_ports[1].get('channel'):
                    errors.append(f'{at}: incompatible declared channels')
            if tn.get(e.get('source'), {}).get('role') == 'decision' and kind in ('control', 'feedback'):
                if not str(e.get('condition', '')).strip() or not str(e.get('label', '')).strip():
                    errors.append(f'{at}: decision branch requires condition and visible label')
            if eid not in se:
                continue
            rendered = se[eid]
            for field in ('source', 'target', 'source_port', 'target_port', 'kind'):
                if rendered.get(field) != e.get(field):
                    errors.append(f'{at}: scene {field} differs from frozen relation')
            if rendered.get('label', '') != e.get('label', ''):
                errors.append(f'{at}: scene edge label differs from relation')
            try:
                expected = anchors_for_edge(rendered, sn)
                overrides = rendered.get('style', {})
                if not isinstance(overrides, dict):
                    raise ValueError('style must be an object')
                for key, value in expected.items():
                    if key in overrides and finite(overrides[key], key) != float(value):
                        errors.append(f'{at}: style overrides fixed port {key}')
                if str(overrides.get('startArrow', 'none')) != 'none':
                    errors.append(f'{at}: reverse/bidirectional arrow is not permitted; declare two one-way relations')
                end = str(overrides.get('endArrow', 'none' if kind == 'annotation' else 'block'))
                if kind == 'annotation' and end != 'none':
                    errors.append(f'{at}: annotation must not introduce an arrow')
                if kind != 'annotation' and end not in ('block','blockThin','classic','classicThin','open','openThin'):
                    errors.append(f'{at}: directed relation requires a directional end arrow')
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                errors.append(f'{at}: {exc}')
    return errors
