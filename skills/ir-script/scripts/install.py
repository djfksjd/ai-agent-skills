#!/usr/bin/env python3
"""Local copy only: no network, package installation, account registration or overwrite."""
import argparse
import shutil
from pathlib import Path


def install(host, root=None):
    if host not in ('codex', 'claude'):
        raise ValueError('host must be codex or claude')
    source = Path(__file__).resolve().parents[1]
    parent = Path(root).expanduser() if root else Path.home()/('.agents' if host == 'codex' else '.claude')/'skills'
    target = parent/'ir-script'
    if target.exists() or target.is_symlink():
        raise FileExistsError('Already exists; inspect and back up before replacing: '+str(target))
    allowed_files = ('SKILL.md', 'README.md', 'LICENSE', 'requirements.txt', 'CHANGELOG.md')
    allowed_dirs = ('agents', 'references', 'templates', 'scripts', 'tests')
    for sub in allowed_dirs:
        if any(p.is_symlink() for p in (source/sub).rglob('*')):
            raise ValueError('Symlinks are not allowed in install payload')
    parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    try:
        for name in allowed_files:
            shutil.copy2(source/name, target/name)
        for name in allowed_dirs:
            shutil.copytree(source/name, target/name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    except Exception:
        shutil.rmtree(target)
        raise
    return target


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('host', choices=['codex','claude']); ap.add_argument('--root', type=Path)
    a = ap.parse_args()
    try:
        print('Copied to '+str(install(a.host, a.root)))
        print('Confirm discovery in your local host. This does not enable an account/Cowork skill.')
    except (ValueError, OSError) as exc:
        ap.exit(2, str(exc)+'\n')
