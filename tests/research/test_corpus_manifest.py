"""Tests for the human-fib corpus manifest (write / verify, fail-closed drift detection)."""

from __future__ import annotations

import json
from pathlib import Path

from fibengine.research.corpus_manifest import (
    TIMEFRAMES,
    _base_fib_paths,
    build_manifest,
    verify_manifest,
)


def _make_corpus(root: Path, counts: dict[str, int]) -> None:
    for tf, n in counts.items():
        d = root / tf
        d.mkdir(parents=True)
        for i in range(n):
            (d / f"fib_BTC-USD_{tf}_2020010{i}T000000.json").write_text(
                json.dumps({"fib_id": f"{tf}-{i}", "created_by": "human"}),
                encoding="utf-8",
            )


def test_base_fib_paths_excludes_events_sidecars(tmp_path: Path) -> None:
    _make_corpus(tmp_path, {"1d": 2})
    (tmp_path / "1d" / "fib_BTC-USD_1d_20200101T000000_events.json").write_text(
        "{}", encoding="utf-8"
    )
    paths = _base_fib_paths(tmp_path, "1d")
    assert len(paths) == 2
    assert all(not p.name.endswith("_events.json") for p in paths)


def test_build_manifest_counts_and_total(tmp_path: Path) -> None:
    _make_corpus(tmp_path, {tf: i + 1 for i, tf in enumerate(TIMEFRAMES)})
    manifest = build_manifest(tmp_path)
    assert [manifest["timeframes"][tf]["count"] for tf in TIMEFRAMES] == [1, 2, 3, 4]
    assert manifest["total"] == 10
    for tf in TIMEFRAMES:
        assert len(manifest["timeframes"][tf]["sha256"]) == 64


def test_verify_passes_on_unchanged_corpus(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    _make_corpus(root, dict.fromkeys(TIMEFRAMES, 2))
    mpath = tmp_path / "MANIFEST.json"
    mpath.write_text(json.dumps(build_manifest(root)), encoding="utf-8")
    assert verify_manifest(root, mpath) == []


def test_verify_fails_closed_on_missing_manifest(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    _make_corpus(root, dict.fromkeys(TIMEFRAMES, 1))
    mismatches = verify_manifest(root, tmp_path / "MISSING.json")
    assert len(mismatches) == 1
    assert "no manifest" in mismatches[0]


def test_verify_detects_added_file(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    _make_corpus(root, dict.fromkeys(TIMEFRAMES, 2))
    mpath = tmp_path / "MANIFEST.json"
    mpath.write_text(json.dumps(build_manifest(root)), encoding="utf-8")
    (root / "4h" / "fib_BTC-USD_4h_20990101T000000.json").write_text("{}", encoding="utf-8")
    mismatches = verify_manifest(root, mpath)
    assert any(m.startswith("4h: count 3 != manifest 2") for m in mismatches)


def test_verify_detects_in_place_edit(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    _make_corpus(root, dict.fromkeys(TIMEFRAMES, 2))
    mpath = tmp_path / "MANIFEST.json"
    mpath.write_text(json.dumps(build_manifest(root)), encoding="utf-8")
    target = _base_fib_paths(root, "1d")[0]
    target.write_text(json.dumps({"fib_id": "edited", "created_by": "human"}), encoding="utf-8")
    mismatches = verify_manifest(root, mpath)
    assert mismatches == ["1d: sha256 drift (files added/removed/edited vs manifest)"]


def test_fingerprint_is_line_ending_invariant(tmp_path: Path) -> None:
    """CRLF checkout (Windows autocrlf) must fingerprint identically to an LF checkout."""
    root = tmp_path / "corpus"
    _make_corpus(root, dict.fromkeys(TIMEFRAMES, 1))
    for tf in TIMEFRAMES:
        _base_fib_paths(root, tf)[0].write_bytes(
            b'{\n  "fib_id": "' + tf.encode() + b'",\n  "created_by": "human"\n}\n'
        )
    mpath = tmp_path / "MANIFEST.json"
    mpath.write_text(json.dumps(build_manifest(root)), encoding="utf-8")
    for tf in TIMEFRAMES:
        p = _base_fib_paths(root, tf)[0]
        p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    assert verify_manifest(root, mpath) == []


def test_committed_manifest_matches_repo_corpus() -> None:
    """The committed manifest must always match the committed facit (guards silent drift)."""
    assert verify_manifest() == []
