#!/usr/bin/env python3
"""Copy this skill into a local host directory; no network or account registration."""
from __future__ import annotations
import argparse,shutil,sys
from pathlib import Path
ALLOW={'SKILL.md','README.md','LICENSE','requirements.txt','scripts','templates','references','agents','VALIDATION.md'}

def install(host: str, root: Path|None=None, dry_run: bool=False) -> Path:
    if host not in {'codex','claude'}:raise ValueError('Host must be codex or claude')
    source=Path(__file__).resolve().parents[1]
    root=Path(root).expanduser() if root is not None else Path.home()/('.agents' if host=='codex' else '.claude')/'skills'
    dest=root.absolute()/'ir-script'
    if dest.exists() or dest.is_symlink():raise FileExistsError(f'Refusing to overwrite {dest}')
    if source==dest or source in dest.parents:raise ValueError('Destination cannot be inside source skill')
    selected=[]
    for name in sorted(ALLOW):
        p=source/name
        if not p.exists():raise FileNotFoundError(p)
        paths=[p] if p.is_file() else list(p.rglob('*'))
        for f in paths:
            if f.is_symlink():raise ValueError('Refusing symlink in package')
            if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':selected.append(f)
    if dry_run:return dest
    dest.mkdir(parents=True,exist_ok=False)
    try:
        for f in selected:
            q=dest/f.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,q)
    except Exception:
        shutil.rmtree(dest);raise
    return dest

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('host',choices=['codex','claude']);a.add_argument('--root',type=Path);a.add_argument('--dry-run',action='store_true');x=a.parse_args()
    try:
        p=install(x.host,x.root,x.dry_run);print(('Would copy to: ' if x.dry_run else 'Copied to: ')+str(p));print('Confirm discovery in the host; this is not Cowork/account registration.');return 0
    except (OSError,ValueError) as e:print('ERROR: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
