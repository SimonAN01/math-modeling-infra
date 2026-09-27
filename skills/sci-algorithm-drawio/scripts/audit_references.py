#!/usr/bin/env python3
"""Audit reference records. Does not search, browse, see images or certify science."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from contracts import load_json
from reference_gate import audit_reference_records, topology_fingerprint


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('references', type=Path, nargs='?')
    ap.add_argument('--topology', type=Path, required=True)
    ap.add_argument('--report', type=Path)
    ap.add_argument('--print-fingerprint', action='store_true',
                    help='Print topology fingerprint only; never edits/approves a review')
    args = ap.parse_args()
    try:
        topology = load_json(args.topology)
        if args.print_fingerprint:
            if args.references or args.report:
                raise ValueError('--print-fingerprint does not take a references file or report')
            print(topology_fingerprint(topology))
            return 0
        if args.references is None:
            raise ValueError('references JSON is required unless printing fingerprint')
        if args.report and args.report.resolve() in {args.references.resolve(), args.topology.resolve()}:
            raise ValueError('Report must not overwrite inputs')
        report = audit_reference_records(load_json(args.references), topology,
                                         base_dir=args.references.parent)
        data = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(data, encoding='utf-8')
        print(data, end='')
        return 0 if report['reference_record_pass'] else 2
    except (OSError, ValueError, TypeError) as exc:
        print(f'audit_references: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
