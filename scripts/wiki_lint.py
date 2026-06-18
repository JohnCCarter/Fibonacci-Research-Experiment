#!/usr/bin/env python3
"""Mechanical wiki lint: the deterministic half of Karpathy's "lint" operation.

Catches the rot that discipline-based scanning reliably misses — **dead internal links** and
**orphan pages** under `docs/research_wiki/`. The *semantic* half (stale claims, contradictions vs
source, missing concept pages, wrong section refs like "§6") stays an agent operation — see
docs/research_wiki/README.md "Lint". Pure functions + a thin CLI so it is unit-testable.

Run:  uv run python scripts/wiki_lint.py
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI = REPO_ROOT / "docs" / "research_wiki"

# Pages reachable from these are "linked"; an orphan is reachable from none of them.
# index = content map; log + archives = chronological hubs that link the review corpus.
ROOT_NAMES = ("index.md", "log.md", "handoff.md", "README.md", "glossary.md")

_LINK = re.compile(r"\]\(([^)]+)\)")  # markdown ](target)


def _is_archive(p: Path) -> bool:
    """Frozen log history: immutable, links pre-reset pages since deleted — not lint targets
    (still traversed for reachability of live pages they link)."""
    return p.name.startswith("log-archive-")


def _targets(text: str) -> list[str]:
    """Relative link targets in markdown text (skips http(s)/mailto and pure #anchors)."""
    out: list[str] = []
    for raw in _LINK.findall(text):
        t = raw.strip().split()[0]  # drop optional "title"
        if t.startswith("#") or t.startswith(("http://", "https://", "mailto:")) or "://" in t:
            continue
        out.append(t.split("#", 1)[0])  # strip anchor
    return out


def _resolve(md: Path, target: str) -> Path:
    return (md.parent / target).resolve()


def _disp(p: Path) -> str:
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def dead_links(wiki: Path) -> list[str]:
    """(file -> target) where a relative link points at something that does not exist."""
    fails: list[str] = []
    for md in sorted(wiki.rglob("*.md")):
        if _is_archive(md):
            continue
        for t in _targets(md.read_text(encoding="utf-8")):
            if not t:
                continue
            if not _resolve(md, t).exists():
                fails.append(f"dead link: {_disp(md)} -> {t}")
    return fails


def _wiki_md_links(md: Path, wiki: Path) -> list[Path]:
    """Resolved targets of `md` that are .md files inside the wiki (for reachability)."""
    out: list[Path] = []
    for t in _targets(md.read_text(encoding="utf-8")):
        if not t.endswith(".md"):
            continue
        dest = _resolve(md, t)
        if dest.exists() and wiki in dest.parents:
            out.append(dest)
    return out


def orphans(wiki: Path) -> list[str]:
    """Wiki .md pages not reachable from any spine root via internal links."""
    roots = [wiki / n for n in ROOT_NAMES if (wiki / n).exists()]
    seen: set[Path] = set()
    stack = list(roots)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(_wiki_md_links(cur, wiki))
    all_md = {p for p in wiki.rglob("*.md") if not _is_archive(p)}
    return sorted(
        f"orphan page (link it from index.md or log.md): {_disp(p)}"
        for p in all_md - seen - set(roots)
    )


def main() -> int:
    fails = dead_links(WIKI) + orphans(WIKI)
    if fails:
        print("Wiki lint failed:\n" + "\n".join(f"  - {f}" for f in fails))
        return 1
    print("Wiki lint OK: no dead internal links, no orphan pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
