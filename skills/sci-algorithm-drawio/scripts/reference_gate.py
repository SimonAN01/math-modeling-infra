"""Check reference-record completeness, not online facts or visual understanding.

No networking, image decoding, OCR, or implicit approval occurs here. The actual
search, source inspection and mechanism comparison must precede these records.
"""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from contracts import named

PRIMARY_TYPES = {'primary_paper', 'author_resource', 'official_documentation', 'academic_teaching'}
ROLES = {'mechanism', 'structure', 'style'}
MATCHES = {'same_mechanism', 'compatible_submechanism', 'custom_composition'}
METHODS = {'pdf_page_screenshot', 'web_image_view', 'local_image_view', 'browser_view'}


def topology_fingerprint(topology: dict) -> str:
    raw = json.dumps(topology, ensure_ascii=False, sort_keys=True,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _http(value) -> bool:
    if not _text(value):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme in {'http', 'https'} and bool(parsed.hostname)
                and not parsed.username and not parsed.password)
    except ValueError:
        return False


def _timestamp(value) -> bool:
    if not _text(value):
        return False
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def _strings(value, name, errors, *, empty=False) -> list[str]:
    if (not isinstance(value, list) or (not value and not empty)
            or any(not _text(x) for x in value)):
        errors.append(f'{name}: expected '+('a' if empty else 'a nonempty')+' list of nonempty strings')
        return []
    if len(value) != len(set(value)):
        errors.append(f'{name}: duplicate values')
    return value


def audit_reference_records(manifest: dict, topology: dict, *, base_dir: Path | None = None) -> dict:
    """Return a fail-closed structural report. Does not authenticate declarations."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        if manifest.get('schema_version') != '4.0':
            errors.append('references.schema_version must be 4.0')
        task = manifest.get('task')
        if not isinstance(task, dict) or any(not _text(task.get(k)) for k in ('algorithm', 'variant', 'figure_purpose')):
            errors.append('task requires explicit algorithm, variant, and figure_purpose')
        search = manifest.get('search', {})
        if not isinstance(search, dict):
            raise ValueError('search must be an object')
        if search.get('status') != 'completed':
            errors.append('online reference search is not recorded as completed')
        runs = named(search.get('runs'), 'search.runs')
        sources = named(manifest.get('sources'), 'sources')
        coverage = named(manifest.get('coverage'), 'coverage')
        pages = named(topology.get('pages'), 'topology.pages')
        if not all((runs, sources, coverage, pages)):
            errors.append('search runs, inspected sources, coverage, and topology pages must all be nonempty')
        targets_by_run: dict[str, set[str]] = {}
        for rid, run in runs.items():
            for field in ('query', 'tool_record', 'result_summary'):
                if not _text(run.get(field)):
                    errors.append(f'{rid}: missing {field}')
            if not _timestamp(run.get('searched_at')):
                errors.append(f'{rid}: missing/invalid searched_at (ISO date/time)')
            ids = _strings(run.get('target_ids'), f'{rid}.target_ids', errors)
            targets_by_run[rid] = set(ids)
            for ident in set(ids) - set(coverage):
                errors.append(f'{rid}: search target does not exist: {ident}')
        for sid, source in sources.items():
            for field in ('title', 'figure_locator', 'reuse_note'):
                if not _text(source.get(field)):
                    errors.append(f'{sid}: missing {field}')
            if not _http(source.get('url')):
                errors.append(f'{sid}: requires original HTTP(S) source URL without credentials')
            roles = set(_strings(source.get('roles'), f'{sid}.roles', errors))
            if roles - ROLES:
                errors.append(f'{sid}: unsupported reference role')
            if source.get('source_type') not in PRIMARY_TYPES | {'secondary_source'}:
                errors.append(f'{sid}: unknown source_type')
            if roles & {'mechanism', 'structure'} and source.get('source_type') not in PRIMARY_TYPES:
                errors.append(f'{sid}: secondary source cannot serve as mechanism/structure authority')
            search_ids = _strings(source.get('search_ids'), f'{sid}.search_ids', errors)
            for ident in set(search_ids) - set(runs):
                errors.append(f'{sid}: unknown search record {ident}')
            view = source.get('inspection', {})
            if not isinstance(view, dict):
                errors.append(f'{sid}: inspection must be an object')
                continue
            if view.get('status') != 'viewed':
                errors.append(f'{sid}: actual figure viewing is not recorded')
            if view.get('method') not in METHODS:
                errors.append(f'{sid}: inspection method is not a pixel-view method (text/thumbnail alone rejected)')
            for field in ('visual_record', 'visual_notes', 'caption_notes', 'context_notes'):
                if not _text(view.get(field)):
                    errors.append(f'{sid}: missing inspection.{field}')
            if not _timestamp(view.get('inspected_at')):
                errors.append(f'{sid}: missing/invalid inspected_at')
            # A local evidence copy is optional. If declared, verify it strictly.
            local = view.get('local_evidence')
            if local is not None:
                if not isinstance(local, dict) or not _text(local.get('path')):
                    errors.append(f'{sid}: local_evidence requires path and sha256')
                elif base_dir is None:
                    errors.append(f'{sid}: base directory required to verify local evidence')
                else:
                    root = base_dir.resolve()
                    path = (root / local['path']).resolve()
                    if not path.is_relative_to(root):
                        errors.append(f'{sid}: local evidence must stay within reference task directory')
                    elif not path.is_file() or path.stat().st_size == 0 or path.stat().st_size > 40_000_000:
                        errors.append(f'{sid}: missing/empty/oversized local evidence')
                    elif hashlib.sha256(path.read_bytes()).hexdigest() != local.get('sha256'):
                        errors.append(f'{sid}: local evidence sha256 mismatch')
        covered_nodes = {pid: set() for pid in pages}
        covered_edges = {pid: set() for pid in pages}
        used_sources: set[str] = set()
        for mid, item in coverage.items():
            if item.get('status') != 'verified':
                errors.append(f'{mid}: unresolved mechanism coverage blocks final output')
            if item.get('match') not in MATCHES:
                errors.append(f'{mid}: unsupported/unresolved mechanism match')
            for field in ('name', 'mapping_notes', 'material_evidence', 'adaptation_notes'):
                if not _text(item.get(field)):
                    errors.append(f'{mid}: missing {field}')
            _strings(item.get('excluded_details'), f'{mid}.excluded_details', errors)
            if item.get('match') == 'custom_composition' and not _text(item.get('custom_spec')):
                errors.append(f'{mid}: custom composition requires a current-method specification')
            pid = item.get('page_id')
            if pid not in pages:
                errors.append(f'{mid}: unknown topology page {pid!r}')
                continue
            node_ids = _strings(item.get('node_ids'), f'{mid}.node_ids', errors, empty=True)
            edge_ids = _strings(item.get('edge_ids'), f'{mid}.edge_ids', errors, empty=True)
            if not node_ids and not edge_ids:
                errors.append(f'{mid}: empty mapping scope')
            tnodes = named(pages[pid].get('nodes'), f'{pid}.nodes')
            tedges = named(pages[pid].get('edges', []), f'{pid}.edges')
            for kind, ids, known, marked in (
                    ('node', node_ids, tnodes, covered_nodes[pid]),
                    ('edge', edge_ids, tedges, covered_edges[pid])):
                for ident in set(ids) - set(known):
                    errors.append(f'{mid}: unknown {kind} {ident}')
                marked.update(ids)
            ref_ids = _strings(item.get('source_ids'), f'{mid}.source_ids', errors)
            matched = False
            for sid in ref_ids:
                source = sources.get(sid)
                if source is None:
                    errors.append(f'{mid}: unknown source {sid}')
                    continue
                used_sources.add(sid)
                if (isinstance(source.get('roles'), list)
                        and set(source['roles']) & {'mechanism', 'structure'}
                        and source.get('source_type') in PRIMARY_TYPES):
                    matched = True
                    searches = source.get('search_ids', [])
                    if not any(mid in targets_by_run.get(rid, set()) for rid in searches):
                        errors.append(f'{mid}: cited source has no search record targeting this mechanism')
            if not matched:
                errors.append(f'{mid}: style-only/no eligible mechanism or structure source cannot pass coverage')
        for pid, page in pages.items():
            n = named(page.get('nodes'), f'{pid}.nodes')
            e = named(page.get('edges', []), f'{pid}.edges')
            for ident in set(n) - covered_nodes[pid]:
                errors.append(f'{pid}: semantic node not mapped to reviewed mechanism scope: {ident}')
            for ident in set(e) - covered_edges[pid]:
                errors.append(f'{pid}: relation not mapped to reviewed mechanism scope: {ident}')
        for sid in set(sources) - used_sources:
            warnings.append(f'{sid}: source is not used by mechanism coverage (may be style-only; do not count as coverage)')
        review = manifest.get('review', {})
        if not isinstance(review, dict):
            raise ValueError('review must be an object')
        if review.get('status') != 'complete' or not _text(review.get('notes')):
            errors.append('reference-to-current-method review is incomplete')
        if review.get('topology_sha256') != topology_fingerprint(topology):
            errors.append('review topology fingerprint is stale/missing; re-review before updating it')
    except (ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
        errors.append('Invalid reference record: '+str(exc))
    return {
        'reference_record_pass': not errors,
        'errors': errors,
        'warnings': warnings,
        'scope': 'record completeness, role separation, mapped topology coverage and fingerprint only',
        'source_truth': 'NOT determined: no URL access or image viewing is performed by this script',
        'scientific_acceptance': 'NOT determined: actually inspect sources and current algorithm',
    }
