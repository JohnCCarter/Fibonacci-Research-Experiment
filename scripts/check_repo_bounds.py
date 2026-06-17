#!/usr/bin/env python3
"""Repo-bound contract: file-size limits + LLM Wiki boundary.

Protects the LLM Wiki pattern: required schema/wiki files must exist, and
local/private artifacts must not be tracked (see repository-layout-policy.md §2B,
docs/research_wiki/reference/source-authority.md).
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# path_glob -> (max_lines, max_bytes); first match wins — put specific paths before broad ones
RULES: list[tuple[str, int, int]] = [
    ("premortem/reflections/*.md", 80, 8 * 1024),
    ("src/fibengine/research/*.py", 750, 32 * 1024),
    ("src/fibengine/labeling/*.py", 600, 32 * 1024),
    ("tests/research/*.py", 300, 20 * 1024),
    ("docs/research_wiki/log.md", 500, 28 * 1024),
    ("src/fibengine/**/*.py", 450, 28 * 1024),
    ("tests/**/*.py", 280, 18 * 1024),
    ("docs/**/*.md", 300, 20 * 1024),
    ("scripts/*.py", 120, 8 * 1024),
]

SKIP_NAMES = {"INDEX.md", "README.md"}

# Legacy debt only — research/labeling tiers above; do not grow these without a split plan
GRANDFATHERED: dict[str, str] = {
    "src/fibengine/labeling/tool.py": "GUI + CLI i en fil; plan: dela workspace / plotting / main",
    "src/fibengine/labeling/behavior_facit.py": "Schema v3 + I/O; plan: split load/save",
    "scripts/behavior_facit.py": "CLI för behavior facit; plan: tunn wrapper",
    "scripts/compare_mtf_disambiguation.py": "Research compare CLI; plan: dela argparse vs report",
}

# Local/private artifacts that must never be tracked (they pollute repo memory).
POLLUTION_GLOBS = (
    ".env .venv/* .coverage .coverage.* .pytest_cache/* "
    ".ruff_cache/* dist/* .claude/* *.log ._*.png"
).split()

# LLM Wiki contract: schema + wiki spine + source authority must exist.
REQUIRED_FILES = (
    "AGENTS.md CLAUDE.md README.md "
    "docs/research_wiki/README.md docs/research_wiki/index.md "
    "docs/research_wiki/log.md docs/research_wiki/handoff.md "
    "docs/research_wiki/reference/source-authority.md"
).split()


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


def check_boundary() -> list[str]:
    """LLM Wiki boundary: required files present, no private artifact tracked."""
    fails = [f"missing required file: {f}" for f in REQUIRED_FILES if not (REPO_ROOT / f).is_file()]
    res = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"], capture_output=True, text=True, check=False
    )
    for rel in res.stdout.splitlines():
        if any(fnmatch.fnmatch(rel, g) for g in POLLUTION_GLOBS):
            fails.append(f"local/private artifact tracked: {rel}")
    return fails


def main() -> int:
    paths = [Path(p).resolve() for p in sys.argv[1:]] if len(sys.argv) > 1 else _iter_monitored()
    failed = [msg for p in paths if (msg := check_path(p))]
    failed += check_boundary()
    if failed:
        print("Repo bounds exceeded:\n" + "\n".join(f"  - {f}" for f in failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
