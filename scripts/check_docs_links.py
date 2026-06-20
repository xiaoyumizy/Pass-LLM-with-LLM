#!/usr/bin/env python3
"""Scan docs/**/*.md for broken internal links.

Builds the file index from the filesystem (rglob) so gitignored files are included.

Usage:
    python scripts/check_docs_links.py
    python scripts/check_docs_links.py --dir docs --dir docs/archive

Exit code: 0 = all links valid, 1 = broken links found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_LINK_RE = re.compile(r"\]\(([^)]+)\)")

_SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "!", "<")
_SKIP_FULL = {"...", ""}
_LOCAL_ONLY_SEGMENTS = (".codex/", ".serena/", ".claude/", ".chatmem/")


def _is_skip_link(link: str) -> bool:
    if link.strip() in _SKIP_FULL:
        return True
    for p in _SKIP_PREFIXES:
        if link.startswith(p):
            return True
    for seg in _LOCAL_ONLY_SEGMENTS:
        if seg in link:
            return True
    return False


def _build_file_index(root: Path) -> set[Path]:
    all_paths: set[Path] = set()
    for d in (root / "docs", root / "skills", root / "shared"):
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file():
                    all_paths.add(f.resolve())
    return all_paths


def _find_target(md_file: Path, target: str, all_paths: set[Path], root: Path) -> bool:
    """Resolve relative to md_file, then repo root."""
    direct = (md_file.parent / target).resolve()
    if direct in all_paths:
        return True
    from_root = (root / target).resolve()
    return from_root in all_paths


def check_links(root: Path, dirs: list[Path]) -> list[tuple[str, str]]:
    all_paths = _build_file_index(root)
    issues: list[tuple[str, str]] = []
    for d in dirs:
        if not d.exists():
            continue
        for md_file in sorted(d.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            for m in _LINK_RE.finditer(text):
                link = m.group(1)
                if _is_skip_link(link):
                    continue
                target = link.split("#")[0]
                if not target:
                    continue
                if not _find_target(md_file, target, all_paths, root):
                    issues.append((link, f"target not found: {target}"))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Check docs/**/*.md internal links")
    ap.add_argument("--dir", action="append", type=Path, default=[],
                    help="Root dir to scan (repeatable)")
    args = ap.parse_args()
    dirs = args.dir or [Path("docs"), Path("skills"), Path("shared/exam_memory")]
    root = Path(".").resolve()
    dirs = [d if d.is_absolute() else root / d for d in dirs]
    issues = check_links(root, dirs)
    if issues:
        for link, msg in issues:
            print(f"BROKEN  ({link}) — {msg}", file=sys.stderr)
        return 1
    print("check_docs_links: all internal links valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
