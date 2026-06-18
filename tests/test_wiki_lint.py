"""Tests for the mechanical wiki lint (scripts/wiki_lint.py).

Loaded by path because `scripts/` is not an importable package. Exercises dead-link and orphan
detection on tmp fixtures, plus the archive exclusion.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "wiki_lint", Path(__file__).resolve().parents[1] / "scripts" / "wiki_lint.py"
)
wl = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(wl)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_targets_skips_external_and_anchors():
    text = "[a](b.md) [x](https://e.com) [y](#sec) [z](mailto:a@b.c) [w](../c.md#frag)"
    assert wl._targets(text) == ["b.md", "../c.md"]


def test_dead_links_flags_only_missing(tmp_path):
    _write(tmp_path / "index.md", "[ok](b.md) [bad](missing.md)")
    _write(tmp_path / "b.md", "leaf")
    fails = wl.dead_links(tmp_path)
    assert len(fails) == 1 and "missing.md" in fails[0]


def test_dead_links_ignores_external_anchors(tmp_path):
    _write(tmp_path / "index.md", "[x](https://example.com) [y](#section)")
    assert wl.dead_links(tmp_path) == []


def test_orphans_flags_unreachable(tmp_path):
    _write(tmp_path / "index.md", "[reachable](a.md)")
    _write(tmp_path / "a.md", "linked")
    _write(tmp_path / "b.md", "nobody links me")
    fails = wl.orphans(tmp_path)
    assert len(fails) == 1 and "b.md" in fails[0]


def test_orphans_transitive_reachability(tmp_path):
    _write(tmp_path / "index.md", "[a](a.md)")
    _write(tmp_path / "a.md", "[b](b.md)")  # reachable via a
    _write(tmp_path / "b.md", "leaf")
    assert wl.orphans(tmp_path) == []


def test_archive_excluded_from_both_checks(tmp_path):
    # archive has a dead link and is itself unlinked — must be ignored on both counts
    _write(tmp_path / "index.md", "map")
    _write(tmp_path / "log-archive-old.md", "[gone](deleted.md)")
    assert wl.dead_links(tmp_path) == []
    assert wl.orphans(tmp_path) == []


def test_archive_still_provides_reachability(tmp_path):
    # a live page reachable only through an archive (which log.md links) is not an orphan
    _write(tmp_path / "index.md", "[log](log.md)")
    _write(tmp_path / "log.md", "[arch](log-archive-x.md)")
    _write(tmp_path / "log-archive-x.md", "[review](r.md)")
    _write(tmp_path / "r.md", "live review")
    assert wl.orphans(tmp_path) == []


def test_clean_wiki_passes(tmp_path):
    _write(tmp_path / "index.md", "[a](a.md)")
    _write(tmp_path / "a.md", "leaf")
    assert wl.dead_links(tmp_path) == [] and wl.orphans(tmp_path) == []
