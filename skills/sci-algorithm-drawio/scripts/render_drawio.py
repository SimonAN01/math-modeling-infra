#!/usr/bin/env python3
"""Export one page with an existing Draw.io Desktop CLI; never call image generation."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from drawio_common import load_pages, wrap_model, write_xml, safe_xml

def run_export(source:Path,out:Path,*,page=1,scale=2,binary=None,timeout=90,force=False,no_sandbox=False):
    if out.exists() and not force:raise ValueError('Output exists; choose a new name or --force after review')
    if source.resolve()==out.resolve():raise ValueError('Do not overwrite the source Draw.io')
    fmt=out.suffix.lower().lstrip('.')
    if fmt not in ('png','svg'):raise ValueError('This wrapper exports .png or .svg only')
    if not math.isfinite(scale) or scale<=0:raise ValueError('scale must be finite and positive')
    if timeout<=0:raise ValueError('timeout must be positive')
    pages=load_pages(source)
    if not 1<=page<=len(pages):raise ValueError('page is 1-based and must exist')
    exe=binary or os.environ.get('DRAWIO_BIN') or shutil.which('drawio') or shutil.which('draw.io')
    if exe:exe=shutil.which(exe) or (str(Path(exe).resolve()) if Path(exe).is_file() and os.access(exe,os.X_OK) else None)
    if not exe:raise RuntimeError('No Draw.io Desktop CLI found. XML can still be delivered; official rendering was NOT performed.')
    command=[]
    if sys.platform.startswith('linux') and not os.environ.get('DISPLAY'):
        xvfb=shutil.which('xvfb-run')
        if not xvfb:raise RuntimeError('No DISPLAY or xvfb-run available; use an existing local GUI/editor instead')
        command.extend([xvfb,'-a'])
    command.append(exe)
    if no_sandbox:command.append('--no-sandbox')  # Explicit opt-in only; not the normal mode.
    help_result=subprocess.run(command+['--help'],capture_output=True,text=True,timeout=timeout)
    help_text=help_result.stdout+'\n'+help_result.stderr
    if help_result.returncode:raise RuntimeError('CLI help failed; do not guess flags:\n'+help_text[-2000:])
    for option in ('--export','--format','--output','--scale','--border'):
        if option not in help_text:raise RuntimeError(f'Existing CLI does not advertise {option}; inspect it before export')
    out.parent.mkdir(parents=True,exist_ok=True)
    # Isolate the selected page. Avoid version-sensitive --page-index conventions.
    with tempfile.TemporaryDirectory(prefix='.drawio-render-',dir=out.parent) as td:
        td=Path(td);one=td/'selected-page.drawio';tmpout=td/('preview.'+fmt)
        name,model=pages[page-1];write_xml(wrap_model(name,model),one)
        cmd=command+['--export','--format',fmt,'--scale',str(scale),'--border','10','--output',str(tmpout.resolve()),str(one.resolve())]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        if result.returncode or not tmpout.is_file() or tmpout.stat().st_size==0:
            raise RuntimeError('CLI export failed or produced no file:\n'+(result.stdout+'\n'+result.stderr)[-3000:])
        raw=tmpout.read_bytes()
        if fmt=='png':
            if not raw.startswith(b'\x89PNG\r\n\x1a\n') or len(raw)<33:raise RuntimeError('Output is not a recognizable PNG')
        else:
            # Renderer output can include a benign SVG DOCTYPE; stdlib parses without fetching it.
            import xml.etree.ElementTree as ET
            if b'<!ENTITY' in raw.upper():raise RuntimeError('Unexpected entity declarations in SVG export')
            if not ET.fromstring(raw).tag.endswith('svg'):raise RuntimeError('Output is not SVG')
        os.replace(tmpout,out)
    return {'source':str(source),'output':str(out),'page':page,'page_name':name,'renderer':exe,
        'rendered':True,'format_signature_checked':True,'visual_review':'not performed by wrapper',
        'interactive_edit_test':'not performed by wrapper','note':'Selected page exported from a temporary single-page file; source retained.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--page',type=int,default=1);ap.add_argument('--scale',type=float,default=2);ap.add_argument('--binary')
    ap.add_argument('--timeout',type=int,default=90);ap.add_argument('--force',action='store_true')
    ap.add_argument('--no-sandbox',action='store_true',help='Explicitly disable Electron sandbox only in a trusted isolated runtime')
    args=ap.parse_args()
    try:
        result=run_export(args.source,args.out,page=args.page,scale=args.scale,binary=args.binary,timeout=args.timeout,force=args.force,no_sandbox=args.no_sandbox)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        print(f'render_drawio: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
