#!/usr/bin/env python3
"""Offline local skill installation. Never registers a cloud/Cowork account."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

FILES = ("SKILL.md", "README.md", "requirements.txt", "LICENSE", "TESTED.md")
DIRS = ("agents", "references", "scripts", "templates", "tests")


def install(source: Path, root: Path) -> Path:
    source = source.resolve(); root = root.expanduser().absolute()
    if source == root or source in root.parents: raise ValueError("Destination must be outside the source package")
    for name in FILES:
        if not (source / name).is_file() or (source / name).is_symlink(): raise ValueError(f"Missing/unsafe source: {name}")
    root.mkdir(parents=True, exist_ok=True)
    dest = root / "ir-script"
    dest.mkdir(exist_ok=False)  # reserve exclusively; no overwrite, including race conditions
    try:
        for name in FILES: shutil.copy2(source / name, dest / name)
        for dirname in DIRS:
            folder = source / dirname
            if folder.is_symlink(): raise ValueError("Source symlinks are not allowed")
            if not folder.exists(): continue
            for path in folder.rglob("*"):
                if path.is_symlink(): raise ValueError("Source symlinks are not allowed")
            shutil.copytree(folder, dest / dirname, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    except Exception:
        shutil.rmtree(dest); raise
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("host", choices=["codex", "claude"])
    p.add_argument("--root", type=Path, help="Parent skills directory, not ir-script itself")
    a = p.parse_args()
    root = a.root or Path.home() / (".agents/skills" if a.host == "codex" else ".claude/skills")
    try:
        dest = install(Path(__file__).resolve().parents[1], root)
        print(f"Copied to {dest}\nCheck the host skill list; restart it if necessary. Cloud/Cowork registration was not changed.")
    except (OSError, ValueError) as exc: p.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__": main()
