"""Tests for source_fib_projection_review (issue #30 Phase 2)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.research.source_fib_projection_review import (
    PROJECTION_COLUMNS,
    _event_label,
    _level_role,
    run_source_fib_projection_review,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _df(closes: list[float], *, start: str = "2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(closes), freq="D", tz="UTC")
    arr = np.array(closes, dtype=float)
    return pd.DataFrame(
        {
            "open": arr,
            "high": arr + 1.0,
            "low": arr - 1.0,
            "close": arr,
            "volume": np.ones(len(arr)),
        },
        index=idx,
    )


def _write_fib_json(path: Path, *, timeframe: str = "1M", symbol: str = "BTC/USD") -> Path:
    """Minimal 1M annotation with 6 levels (tradingview_log_chamoun set)."""
    payload = {
        "fib_id": "fib_BTC-USD_1M_test",
        "symbol": symbol,
        "timeframe": timeframe,
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "scale_mode": "log",
        "levels_profile": "tradingview_log_chamoun",
        "human_highlights": [],
        "anchor_a": {"time": "2020-01-01T00:00:00Z", "price": 10000.0},
        "anchor_b": {"time": "2020-03-01T00:00:00Z", "price": 5000.0},
        "direction": "down",
        "levels": [
            {"ratio": 0.0, "price": 5000.0},
            {"ratio": 0.382, "price": 6910.0},
            {"ratio": 0.5, "price": 7071.0},
            {"ratio": 0.618, "price": 7236.0},
            {"ratio": 0.786, "price": 7492.0},
            {"ratio": 1.0, "price": 10000.0},
        ],
    }
    fib_path = path / "fib_BTC-USD_1M_test.json"
    fib_path.write_text(json.dumps(payload), encoding="utf-8")
    return fib_path


# ---------------------------------------------------------------------------
# Unit tests — pure helpers
# ---------------------------------------------------------------------------


def test_level_role_boundary():
    assert _level_role("0") == "boundary"
    assert _level_role("0.0") == "boundary"
    assert _level_role("1") == "boundary"
    assert _level_role("1.0") == "boundary"


def test_level_role_retracement():
    for r in ("0.382", "0.5", "0.618", "0.786"):
        assert _level_role(r) == "retracement", r


def test_event_label_verb_mapping():
    assert _event_label("1M", "0.5", "touch", "1d") == "1M 0.5 touched by 1d candle"
    assert _event_label("1M", "0.618", "cross", "1w") == "1M 0.618 crossed by 1w candle"
    assert _event_label("1M", "0.0", "above", "4h") == "1M 0.0 held above by 4h candle"
    assert _event_label("1M", "1.0", "below", "4h") == "1M 1.0 held below by 4h candle"


# ---------------------------------------------------------------------------
# Integration test — rows decorated correctly
# ---------------------------------------------------------------------------


def test_rows_decorated_correctly(tmp_path, monkeypatch):
    """detect_ltf_level_interactions rows get source_tf, chart_tf, level_role, event_label."""
    fib_path = _write_fib_json(tmp_path)

    # Synthetic df — one bar touches the 0.5 level (price ~7071)
    closes = [8000.0] * 5 + [7072.0] + [8000.0] * 5
    df = _df(closes, start="2020-04-01")  # after anchor_b (2020-03-01)

    # Patch load_candles to return our synthetic df without needing cache files
    import fibengine.research.source_fib_projection_review as mod

    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    summary = run_source_fib_projection_review(
        source_fib_path=fib_path,
        chart_timeframes=["1d"],
        out_root=tmp_path / "out",
    )

    csv_path = Path(summary["output_dir"]) / "review_sample.csv"
    assert csv_path.exists()

    import csv as _csv

    with csv_path.open(encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))

    # Must have at least the touch row
    assert rows, "Expected at least one interaction row"
    for row in rows:
        assert row["source_tf"] == "1M"
        assert row["chart_tf"] == "1d"
        assert row["level_role"] in ("boundary", "retracement")
        assert "by 1d candle" in row["event_label"]
        # Raw projection columns must be present and non-empty
        for col in ("fib_level", "fib_price", "event_time", "relation", "auto_candidate"):
            assert row[col], f"Column {col!r} must not be empty"


# ---------------------------------------------------------------------------
# Integration test — boundary levels marked
# ---------------------------------------------------------------------------


def test_boundary_levels_marked(tmp_path, monkeypatch):
    """Rows with ratio 0 or 1 get level_role='boundary'; others get 'retracement'."""
    fib_path = _write_fib_json(tmp_path)

    # df that touches all levels: prices span 4999–10001
    mid = 7500.0
    closes = [mid] * 4 + [4999.0, 6900.0, 7070.0, 7235.0, 7490.0, 9999.0] + [mid] * 4
    df = _df(closes, start="2020-04-01")

    import fibengine.research.source_fib_projection_review as mod

    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    summary = run_source_fib_projection_review(
        source_fib_path=fib_path,
        chart_timeframes=["1d"],
        out_root=tmp_path / "out2",
    )

    csv_path = Path(summary["output_dir"]) / "review_sample.csv"
    import csv as _csv

    with csv_path.open(encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))

    by_level = {r["fib_level"]: r["level_role"] for r in rows}
    for level_str, role in by_level.items():
        expected = "boundary" if float(level_str) in (0.0, 1.0) else "retracement"
        assert role == expected, f"fib_level={level_str!r} got role={role!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# Smoke test — REVIEW_INDEX.md and summary.json are produced
# ---------------------------------------------------------------------------


def test_review_index_smoke(tmp_path, monkeypatch):
    """run_source_fib_projection_review writes all four output files."""
    fib_path = _write_fib_json(tmp_path)
    closes = [8000.0] * 5 + [7072.0] + [8000.0] * 5
    df = _df(closes, start="2020-04-01")

    import fibengine.research.source_fib_projection_review as mod

    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    out = tmp_path / "smoke_out"
    summary = run_source_fib_projection_review(
        source_fib_path=fib_path,
        chart_timeframes=["1d"],
        out_root=out,
    )

    out_dir = Path(summary["output_dir"])
    assert (out_dir / "REVIEW_INDEX.md").exists()
    assert (out_dir / "review_sample.csv").exists()
    assert (out_dir / "review_sample.jsonl").exists()
    assert (out_dir / "summary.json").exists()

    index_text = (out_dir / "REVIEW_INDEX.md").read_text(encoding="utf-8")
    assert "SOURCE FIB" in index_text
    assert "PROJECTED LEVELS" in index_text
    assert "fib_BTC-USD_1M_test" in index_text
    assert "CURRENT CHART: 1d" in index_text

    loaded_summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert "run_id" in loaded_summary
    assert loaded_summary["source_tf"] == "1M"
    assert loaded_summary["chart_timeframes"] == ["1d"]

    # CSV header must match PROJECTION_COLUMNS
    import csv as _csv

    with (out_dir / "review_sample.csv").open(encoding="utf-8") as f:
        header = next(_csv.reader(f))
    assert header == PROJECTION_COLUMNS
