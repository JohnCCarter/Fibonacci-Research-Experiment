"""Tests for fib level interaction fingerprint extraction (#23)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.research import fib_level_fingerprints as flf
from fibengine.research.fib_level_fingerprints import (
    FingerprintConfig,
    extract_at_features,
    extract_post_features,
    extract_pre_features,
    run_fib_level_fingerprints,
    summarize_fingerprints,
)


def _df(closes: list[float]) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="D", tz="UTC")
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


def _atr_series(df: pd.DataFrame) -> pd.Series:
    from fibengine.data.loader import atr

    return atr(df, 14)


def test_extract_pre_features_approach_from_above():
    closes = [110.0] * 15 + [105.0] * 5 + [100.0]
    df = _df(closes)
    atr_s = _atr_series(df)
    pre = extract_pre_features(
        df, atr_s, event_bar=20, level=100.0, approach_side="above", pre_bars=10
    )
    assert pre["pre_approach_side"] == "above"
    assert pre["pre_approach_direction"] == "down"
    assert pre["pre_bars_approaching_level"] >= 1


def test_extract_at_features_relation_and_wick():
    df = _df([100.0] * 5)
    atr_s = _atr_series(df)
    row = {
        "relation": "touch",
        "touch_type": "wick_below",
        "approach_side": "above",
    }
    at = extract_at_features(df, atr_s, event_bar=2, level=100.0, row=row)
    assert at["at_relation"] == "touch"
    assert at["at_wick_touch"] is True
    assert at["at_body_touch"] is False


def test_extract_post_features_break_side_counts():
    closes = [100.0] + [98.0] * 5 + [102.0] * 5
    df = _df(closes)
    atr_s = _atr_series(df)
    post = extract_post_features(
        df,
        atr_s,
        event_bar=0,
        level=100.0,
        approach_side="above",
        post_bars=8,
        near_level_atr=0.25,
    )
    assert post["post_bars_available"] == 8
    assert post["post_bars_on_break_side"] >= 1
    assert post["post_retest_count"] >= 0


def test_summarize_fingerprints_groups_by_candidate():
    fps = [
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "timeframe": "1d",
            "pre_bars_approaching_level": 3,
            "post_retest_count": 1,
        },
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "timeframe": "1d",
            "pre_bars_approaching_level": 5,
            "post_retest_count": 2,
        },
    ]
    summary = summarize_fingerprints(fps)
    assert len(summary) == 1
    assert summary[0]["n_events"] == 2
    assert summary[0]["mean_pre_bars_approaching_level"] == 4.0


def test_run_end_to_end_writes_fingerprint_artifacts(monkeypatch, tmp_path):
    closes = [110.0] * 10 + [100.0] + [105.0] * 20
    df = _df(closes)
    event_time = df.index[10].isoformat()
    payload = {
        "fib_id": "fib_fp_test",
        "symbol": "BTC/USD",
        "timeframe": "1d",
        "exchange": "bitfinex",
        "direction": "down",
        "anchor_a": {"time": df.index[0].isoformat(), "price": 110.0},
        "anchor_b": {"time": df.index[5].isoformat(), "price": 100.0},
        "source": "human_fib_events",
        "levels": [
            {
                "level": "0.5",
                "price": 100.0,
                "events": [
                    {
                        "event_bar": event_time,
                        "bar_index": 10,
                        "touch_type": "wick_below",
                        "approach_side": "above",
                        "auto_candidate": "rejection_candidate",
                        "note": "test",
                        "evidence": {},
                    }
                ],
            }
        ],
    }
    events_path = tmp_path / "fib_test_events.json"
    events_path.write_text(json.dumps(payload), encoding="utf-8")

    def load(_cfg, fetch_if_missing=False):
        return df

    monkeypatch.setattr(flf, "FIB_FINGERPRINTS_RUNS", tmp_path / "runs")
    monkeypatch.setattr(flf, "FIB_FINGERPRINTS_RESULTS", tmp_path / "results.jsonl")
    monkeypatch.setattr(flf, "load_candles", load)
    monkeypatch.setattr("fibengine.research.human_review_level_events.load_candles", load)

    result = run_fib_level_fingerprints(
        [events_path],
        cfg=FingerprintConfig(pre_bars=5, post_bars=10),
    )
    run_dir = Path(result["run_dir"])
    assert (run_dir / "fingerprints.jsonl").exists()
    assert (run_dir / "summary.csv").exists()
    assert result["fingerprints_extracted"] == 1
    lines = (run_dir / "fingerprints.jsonl").read_text(encoding="utf-8").strip().splitlines()
    fp = json.loads(lines[0])
    assert "pre_approach_direction" in fp
    assert "at_relation" in fp
    assert "post_retest_count" in fp
