"""Tester fÃ¶r label-batch: sÃ¤ker id, sha256-manifest, sista jsonl-rad, end-to-end."""

import hashlib
import json

from fibengine.labeling import batch as batch_mod
from fibengine.labeling.batch import (
    _file_sha256,
    _label_manifest,
    _last_jsonl_row,
    _safe_batch_id,
    create_label_batch,
)


def test_safe_batch_id_sanitizes():
    assert _safe_batch_id("round 4!!") == "round-4"
    assert _safe_batch_id("a//b").startswith("a-b") or _safe_batch_id("a//b") == "a-b"
    # Tomt/skrÃ¤p faller tillbaka till en default (icke-tom).
    assert _safe_batch_id("///") != ""


def test_file_sha256_matches_hashlib(tmp_path):
    f = tmp_path / "x.json"
    f.write_bytes(b'{"a": 1}')
    assert _file_sha256(f) == hashlib.sha256(b'{"a": 1}').hexdigest()


def test_last_jsonl_row_returns_last(tmp_path):
    p = tmp_path / "x.jsonl"
    assert _last_jsonl_row(p) is None  # saknas
    p.write_text('{"i": 1}\n{"i": 2}\n\n')
    assert _last_jsonl_row(p) == {"i": 2}


def test_label_manifest_has_hash_and_relpath(tmp_path, monkeypatch):
    labels_dir = tmp_path / "labels"
    (labels_dir / "Bitfinex" / "BTC-USD").mkdir(parents=True)
    f = labels_dir / "Bitfinex" / "BTC-USD" / "1h.json"
    f.write_text('{"x": 1}')
    monkeypatch.setattr(batch_mod, "LABELS_DIR", labels_dir)
    monkeypatch.setattr(batch_mod, "REPO_ROOT", tmp_path)

    manifest = _label_manifest([f])
    assert manifest[0]["file"] == "Bitfinex/BTC-USD/1h.json"
    assert manifest[0]["sha256"] == hashlib.sha256(b'{"x": 1}').hexdigest()
    assert manifest[0]["size_bytes"] == len(b'{"x": 1}')


def test_create_label_batch_writes_manifest_and_metadata(tmp_path, monkeypatch):
    labels_dir = tmp_path / "labels"
    (labels_dir / "Bitfinex" / "BTC-USD").mkdir(parents=True)
    f = labels_dir / "Bitfinex" / "BTC-USD" / "1h.json"
    f.write_text('{"exchange": "Bitfinex"}')

    batches_dir = tmp_path / "batches"
    monkeypatch.setattr(batch_mod, "LABELS_DIR", labels_dir)
    monkeypatch.setattr(batch_mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(batch_mod, "BATCHES_DIR", batches_dir)
    monkeypatch.setattr(batch_mod, "iter_label_files", lambda: [f])
    monkeypatch.setattr(batch_mod, "PIVOT_RECALL_JSONL", tmp_path / "missing_pr.jsonl")
    monkeypatch.setattr(batch_mod, "LEADERBOARD_JSONL", tmp_path / "missing_lb.jsonl")

    out_dir = create_label_batch(batch_id="round-test", note="hej")
    meta = json.loads((out_dir / "metadata.json").read_text())
    assert meta["batch_id"] == "round-test"
    assert meta["label_count"] == 1
    assert meta["note"] == "hej"
    assert (out_dir / "labels_manifest.json").exists()
    assert (out_dir / "notes.md").exists()
    # Manifest-only by default (ingen snapshot).
    assert not (out_dir / "labels_snapshot").exists()
