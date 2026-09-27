#!/usr/bin/env python3
"""Copy this skill to a local host skill directory; never contact accounts or overwrite."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

ALLOW = {"SKILL.md", "README.md", "LICENSE", "requirements.txt", "agents", "references", "scripts", "templates", "tests"}


def install(source: Path, root: Path) -> Path:
    source = source.resolve(); root = root.expanduser().resolve(); target = root / "ir-script"
    if not (source / "SKILL.md").is_file(): raise ValueError("Missing SKILL.md")
    if target.exists() or target.is_symlink(): raise FileExistsError("Existing skill preserved: " + str(target))
    if source == root or source in root.parents: raise ValueError("Destination cannot be within source")
    def ignore(directory, names):
        return [n for n in names if n == "__pycache__" or n.endswith(".pyc") or (Path(directory) == source and n not in ALLOW)]
    if any(p.is_symlink() for p in source.rglob("*")): raise ValueError("Symlinked source not supported by safe installer")
    root.mkdir(parents=True, exist_ok=True); shutil.copytree(source, target, ignore=ignore)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("host", choices=["codex", "claude"])
    parser.add_argument("--root", type=Path, help="Alternative parent skills directory")
    args = parser.parse_args()
    root = args.root or Path.home() / (".agents" if args.host == "codex" else ".claude") / "skills"
    try: print("Copied to", install(Path(__file__).resolve().parents[1], root), "\nCheck host discovery; this does not register ChatGPT/Cowork account skills.")
    except (OSError, ValueError) as exc: parser.exit(1, str(exc) + "\n")
