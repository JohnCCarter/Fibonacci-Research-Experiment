#!/usr/bin/env python3
"""Pre-commit: file size / anti-blob limits (see repository-layout-policy.md §2B)."""

from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# path_glob -> (max_lines, max_bytes); checked only for paths that match
RULES: list[tuple[str, int, int]] = [
    ("premortem/reflections/*.md", 80, 8 * 1024),
    ("src/fibengine/**/*.py", 400, 25 * 1024),
    ("tests/**/*.py", 250, 15 * 1024),
    ("docs/**/*.md", 300, 20 * 1024),
    ("scripts/*.py", 120, 8 * 1024),
]

SKIP_NAMES = {"INDEX.md", "README.md"}

# Known debt — must shrink or split before adding more lines (documented in REPO_POLICY §2B)
GRANDFATHERED: dict[str, str] = {
    "src/fibengine/labeling/tool.py": "GUI + CLI i en fil; plan: dela workspace / plotting / main",
    "src/fibengine/labeling/behavior_facit.py": "Schema v3 + I/O; plan: split load/save",
    "scripts/behavior_facit.py": "CLI för behavior facit; plan: tunn wrapper",
    "scripts/compare_mtf_disambiguation.py": "Research compare CLI; plan: dela argparse vs report",
    "src/fibengine/research/human_review_level_events.py": "PR #11 review pack; plan: split",
}


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _limits_for(rel: str) -> tuple[int, int] | None:
    for pattern, max_lines, max_bytes in RULES:
        if fnmatch.fnmatch(rel, pattern):
            return max_lines, max_bytes
    return None


def check_path(path: Path) -> str | None:
    rel = _rel(path)
    if path.name in SKIP_NAMES and "premortem/reflections" in rel:
        return None
    limits = _limits_for(rel)
    if limits is None:
        return None
    if rel in GRANDFATHERED:
        return None
    text = path.read_text(encoding="utf-8")
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    size = len(text.encode("utf-8"))
    max_lines, max_bytes = limits
    if lines <= max_lines and size <= max_bytes:
        return None
    return (
        f"{rel}: {lines} lines (max {max_lines}), {size} bytes (max {max_bytes}). "
        "Dela modul, flytta detaljer till docs/ eller experiments/results/ — se REPO_POLICY §2B."
    )


def _iter_monitored() -> list[Path]:
    out: list[Path] = []
    for pattern, _, _ in RULES:
        out.extend(p for p in REPO_ROOT.glob(pattern) if p.is_file())
    return out


def main() -> int:
    paths = [Path(p).resolve() for p in sys.argv[1:]] if len(sys.argv) > 1 else _iter_monitored()
    failed = [msg for p in paths if (msg := check_path(p))]
    if failed:
        print("Repo bounds exceeded:\n" + "\n".join(f"  - {f}" for f in failed))
        if GRANDFATHERED:
            print(
                "\nGrandfathered (fix before growing):\n"
                + "\n".join(f"  - {k}: {v}" for k, v in GRANDFATHERED.items())
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
