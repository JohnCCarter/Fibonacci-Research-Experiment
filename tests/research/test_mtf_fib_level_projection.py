"""Tests for MTF fib level projection (HTF human fib -> LTF candle behavior)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.research import mtf_fib_level_projection as mtf
from fibengine.research.mtf_fib_level_projection import (
    detect_ltf_level_interactions,
    run_mtf_fib_level_projection,
)


def _df(closes: list[float], *, start: str = "2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(closes), freq="D", tz="UTC")
    arr = np.array(closes, dtype=float)
    return pd.DataFrame(
        {
            "open": arr,
            "high": arr + 1,
            "low": arr - 1,
            "close": arr,
            "volume": np.ones(len(arr)),
        },
        index=idx,
    )


def _write_human_fib(path: Path, df: pd.DataFrame, *, leg_end_idx: int, level_price: float) -> Path:
    """A minimal base human fib JSON (anchor_b = LTF leg end, one 0.5 level)."""
    payload = {
        "fib_id": "fib_mtf_test",
        "symbol": "BTC/USD",
        "timeframe": "1w",
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "anchor_a": {"time": df.index[0].isoformat(), "price": level_price + 10.0},
        "anchor_b": {
            "time": df.index[leg_end_idx].isoformat(),
            "price": level_price - 10.0,
        },
        "direction": "down",
        "levels": [{"ratio": 0.5, "price": level_price}],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_detect_scans_after_leg_end_and_sets_approach_side():
    # Price sits above the level, dips to touch it at bar 12 from above.
    closes = [110.0] * 10 + [108.0, 106.0, 100.0] + [104.0] * 6
    df = _df(closes)
    levels = [{"ratio": 0.5, "price": 100.0}]
    rows, skip = detect_ltf_level_interactions(
        df,
        levels,
        start_time=df.index[5].isoformat(),
        fib_id="fib_mtf_test",
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        direction="down",
        projected_from_timeframe="1w",
    )
    assert skip is None
    assert rows, "expected at least one LTF interaction"
    first = rows[0]
    assert first["event_bar"] >= 6  # strictly after the leg-end bar (index 5)
    assert first["approach_side"] == "above"
    assert first["fib_level"] == "0.5"
    assert first["projected_from_timeframe"] == "1w"
    assert first["timeframe"] == "1d"
    assert first["auto_candidate"].endswith("_candidate")
    assert first["event_id"].startswith("fib_mtf_test|0.5|")


def test_detect_skips_when_leg_end_after_cache():
    df = _df([100.0] * 10)
    rows, skip = detect_ltf_level_interactions(
        df,
        [{"ratio": 0.5, "price": 100.0}],
        start_time="2030-01-01T00:00:00+00:00",
        fib_id="x",
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        direction="down",
        projected_from_timeframe="1w",
    )
    assert rows == []
    assert skip == "leg_end_after_cache"


def test_run_end_to_end_writes_artifacts(monkeypatch, tmp_path):
    closes = [110.0] * 10 + [108.0, 104.0, 100.0] + [96.0] * 12
    df = _df(closes)
    fib_path = _write_human_fib(tmp_path / "fib.json", df, leg_end_idx=5, level_price=100.0)

    def load(_cfg, fetch_if_missing=False):
        return df

    monkeypatch.setattr(mtf, "MTF_RUNS", tmp_path / "runs")
    monkeypatch.setattr(mtf, "MTF_RESULTS", tmp_path / "results.jsonl")
    monkeypatch.setattr(mtf, "load_candles", load)

    result = run_mtf_fib_level_projection([fib_path], ["1d"])

    run_dir = Path(result["run_dir"])
    assert (run_dir / "interactions.jsonl").exists()
    assert (run_dir / "fingerprint_outcomes.jsonl").exists()
    assert (run_dir / "run_summary.json").exists()
    assert result["projected_from_timeframes"] == ["1w"]
    assert result["projected_levels"] == 1
    assert result["ltf_interactions"] >= 1
    assert result["joined_rows"] >= 1
    assert result["ltf_timeframes_seen"] == ["1d"]

    joined = [
        json.loads(line)
        for line in (run_dir / "fingerprint_outcomes.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    row = joined[0]
    # Layers present on the joined row: projected_level + relation + fingerprint + outcome.
    assert row["projected_from_timeframe"] == "1w"
    assert row["timeframe"] == "1d"
    assert "relation" in row
    assert "horizon" in row
    assert "post_bars_on_break_side" in row


def test_run_records_missing_candle_cache_skip(monkeypatch, tmp_path):
    df = _df([100.0] * 20)
    fib_path = _write_human_fib(tmp_path / "fib.json", df, leg_end_idx=5, level_price=100.0)

    def load(_cfg, fetch_if_missing=False):
        raise FileNotFoundError("no cache for 4h")

    monkeypatch.setattr(mtf, "MTF_RUNS", tmp_path / "runs")
    monkeypatch.setattr(mtf, "MTF_RESULTS", tmp_path / "results.jsonl")
    monkeypatch.setattr(mtf, "load_candles", load)

    result = run_mtf_fib_level_projection([fib_path], ["4h"])
    assert result["ltf_interactions"] == 0
    assert result["skipped"] == 1
    assert result["skipped_reasons"] == {"missing_candle_cache": 1}
