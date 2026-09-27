#!/usr/bin/env python3
"""Report existing local capabilities without installing or changing anything."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

def probe():
    fonts=[]
    if shutil.which('fc-list'):
        try:
            out=subprocess.run(['fc-list',':lang=zh','family'],capture_output=True,text=True,timeout=10)
            if out.returncode==0:fonts=sorted(set(out.stdout.splitlines()))
        except (OSError,subprocess.TimeoutExpired):pass
    binary=os.environ.get('DRAWIO_BIN') or shutil.which('drawio') or shutil.which('draw.io')
    if binary and not (Path(binary).is_file() and os.access(binary,os.X_OK)):
        binary=shutil.which(binary)
    return {'python':platform.python_version(),'platform':platform.platform(),'drawio_binary':binary,
        'display':bool(os.environ.get('DISPLAY')),'xvfb_run':shutil.which('xvfb-run'),
        'chinese_font_families':fonts,'no_installation_performed':True,
        'note':'Presence only, not a successful render or font-appearance test; inspect actual CLI help before export.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
    data=json.dumps(probe(),ensure_ascii=False,indent=2)+'\n'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(data,encoding='utf-8')
    print(data,end='');return 0
if __name__=='__main__':raise SystemExit(main())
