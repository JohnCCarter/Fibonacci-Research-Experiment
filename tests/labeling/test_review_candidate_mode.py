"""Tests for the review-candidate promote mode (labeling tool).

GUI rendering is not exercised (the tool ends in plt.show()); these cover the pure,
testable units: the fail-closed candidate loader, the CLI arg, and that 'w' promotes a
candidate to facit with honest provenance (created_by=human, source records the
transcription method) plus an overwrite-confirm guard. Normal labeling stays unaffected.
"""

from __future__ import annotations

import json
import sys

import pandas as pd
import pytest

import fibengine.labeling.tool as tool
from fibengine.core.config import load_settings
from fibengine.labeling import store
from fibengine.labeling.human_fib import FibAnchor, make_annotation

PROMOTE_SOURCE = "manual_screenshot_transcription_reviewed"
HIGH_T = "2025-10-06T00:00:00+00:00"
LOW_T = "2025-10-10T00:00:00+00:00"


def _candidate_dict(*, candidate: bool = True) -> dict:
    ann = make_annotation(
        symbol="BTC/USD",
        timeframe="1d",
        anchor_a=FibAnchor(time=HIGH_T, price=126110.0),
        anchor_b=FibAnchor(time=LOW_T, price=103310.0),
    )
    d = ann.to_dict()
    if not candidate:
        return d
    return {
        "_candidate": True,
        "_transcription": {
            "confidence": "exact",
            "matches": [
                {
                    "role": "high",
                    "price": 126110.0,
                    "n_within_near": 1,
                    "confidence": "exact",
                    "rel_delta": 0.0,
                },
                {
                    "role": "low",
                    "price": 103310.0,
                    "n_within_near": 2,
                    "confidence": "exact",
                    "rel_delta": 0.0,
                },
            ],
        },
        **d,
    }


def _write_candidate(path, *, candidate: bool = True):
    path.write_text(json.dumps(_candidate_dict(candidate=candidate), indent=2), encoding="utf-8")
    return path


# --- loader (fail-closed) ----------------------------------------------------------------


def test_load_candidate_returns_annotation_and_audit(tmp_path):
    p = _write_candidate(tmp_path / "cand.json")
    ann, audit = tool._load_candidate_for_review(p)
    assert ann.symbol == "BTC/USD" and ann.timeframe == "1d"
    assert ann.fib_id == "fib_BTC-USD_1d_20251006T000000"
    assert audit["confidence"] == "exact"
    assert len(audit["matches"]) == 2
    # the guessed-bar flag survives so the reviewer can scrutinise it
    assert any(m["n_within_near"] > 1 for m in audit["matches"])


def test_load_refuses_non_candidate(tmp_path):
    p = _write_candidate(tmp_path / "facit.json", candidate=False)
    with pytest.raises(SystemExit, match="not a candidate"):
        tool._load_candidate_for_review(p)


def test_load_refuses_missing_file(tmp_path):
    with pytest.raises(SystemExit, match="file not found"):
        tool._load_candidate_for_review(tmp_path / "nope.json")


# --- CLI arg -----------------------------------------------------------------------------


def test_review_candidate_arg_parses_and_defaults_none(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tool"])
    assert tool._parse_args().review_candidate is None
    monkeypatch.setattr(sys, "argv", ["tool", "--review-candidate", "c.json"])
    assert tool._parse_args().review_candidate == "c.json"


# --- promote on 'w' (provenance + overwrite guard) ---------------------------------------


def _workspace_with_picks(monkeypatch, tmp_path):
    df = pd.DataFrame(
        {"high": [126110.0, 103310.0], "low": [120000.0, 103310.0]},
        index=pd.to_datetime([HIGH_T, LOW_T], utc=True),
    )
    monkeypatch.setattr(tool.LabelWorkspace, "_load_chart_candles", lambda self: df)
    settings = load_settings()
    settings.data.exchange = "bitfinex"
    settings.data.symbol = "BTC/USD"
    settings.data.timeframe = "1d"
    ws = tool.LabelWorkspace(settings, ["BTC/USD"], ["1d"])
    ws.picks = {"high": (0, 126110.0), "low": (1, 103310.0)}  # high earlier -> down fib
    return ws


def test_promote_writes_facit_with_honest_provenance(monkeypatch, tmp_path):
    store.set_labels_dir(tmp_path)
    try:
        ws = _workspace_with_picks(monkeypatch, tmp_path)
        ws.promote_source = PROMOTE_SOURCE
        ws.save_human_fib_annotation()
        saved = tmp_path / "human_fib/bitfinex/BTC-USD/1d/fib_BTC-USD_1d_20251006T000000.json"
        assert saved.exists()
        d = json.loads(saved.read_text(encoding="utf-8"))
        assert d["created_by"] == "human"  # selection is human
        assert d["source"] == PROMOTE_SOURCE  # but the method is recorded, not erased
        assert "_candidate" not in d and "_transcription" not in d  # clean facit
        assert d["direction"] == "down"
    finally:
        store.set_labels_dir(None)


def test_overwrite_needs_second_confirm(monkeypatch, tmp_path):
    store.set_labels_dir(tmp_path)
    try:
        ws = _workspace_with_picks(monkeypatch, tmp_path)
        ws.promote_source = PROMOTE_SOURCE
        ws.save_human_fib_annotation()  # first write
        assert ws._pending_overwrite is False
        ws.save_human_fib_annotation()  # target exists -> guard arms, no write
        assert ws._pending_overwrite is True
        ws.save_human_fib_annotation()  # confirmed -> overwrites, resets
        assert ws._pending_overwrite is False
    finally:
        store.set_labels_dir(None)


def test_normal_labeling_source_unaffected(monkeypatch, tmp_path):
    store.set_labels_dir(tmp_path)
    try:
        ws = _workspace_with_picks(monkeypatch, tmp_path)  # promote_source stays None
        ws.save_human_fib_annotation()
        saved = tmp_path / "human_fib/bitfinex/BTC-USD/1d/fib_BTC-USD_1d_20251006T000000.json"
        d = json.loads(saved.read_text(encoding="utf-8"))
        assert d["source"] == "manual_labeling_tool"  # default unchanged
    finally:
        store.set_labels_dir(None)


# --- windowed view fits Y to the window (readable review) --------------------------------


def test_window_fit_view_brackets_window_prices():
    df = pd.DataFrame(
        {"high": [126110.0, 110000.0, 103310.0], "low": [120000.0, 104000.0, 103310.0]},
        index=pd.to_datetime(
            ["2025-10-06T00:00:00+00:00", "2025-10-08T00:00:00+00:00", "2025-10-10T00:00:00+00:00"],
            utc=True,
        ),
    )
    (x0, x1), (y0, y1) = tool._window_fit_view(df)
    assert (x0, x1) == (-0.5, 2.5)  # n=3 candles framed
    assert y0 < 103310.0 and y1 > 126110.0  # brackets the window low/high
    assert y1 / y0 < 1.5  # tight to the window, not the full-history squish
