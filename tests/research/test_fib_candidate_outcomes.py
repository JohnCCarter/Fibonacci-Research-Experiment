"""Tests for fib level candidate forward outcome analysis (#22)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.research import fib_candidate_outcomes as fco
from fibengine.research.fib_candidate_outcomes import (
    OutcomeConfig,
    analyze_events,
    compute_outcomes,
    expected_direction,
    run_fib_candidate_outcomes,
    summarize_outcomes,
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


def test_expected_direction_separates_candidate_semantics():
    assert expected_direction("continuation_candidate", "above") == "down"
    assert expected_direction("rejection_candidate", "above") == "up"
    assert expected_direction("failure_candidate", "below") == "down"
    assert expected_direction("reaction_candidate", "above") is None
    assert expected_direction("continuation_candidate", "") is None


def test_compute_outcomes_forward_return_and_approach_side():
    closes = [110.0] * 5 + [100.0] * 5 + [105.0] * 10
    df = _df(closes)
    level = 100.0
    metrics = compute_outcomes(
        df,
        event_bar=5,
        fib_price=level,
        auto_candidate="rejection_candidate",
        approach_side="above",
        horizons=[5, 10],
    )
    assert metrics[5].forward_return == 0.05
    assert metrics[5].close_on_approach_side is True
    assert metrics[5].direction_inferred is True
    assert metrics[5].mfe is not None and metrics[5].mae is not None


def test_analyze_events_skips_missing_forward_bars():
    df = _df([100.0] * 3)
    row = {
        "fib_id": "fib_test",
        "symbol": "BTC/USD",
        "timeframe": "1d",
        "exchange": "bitfinex",
        "fib_level": "0.5",
        "fib_price": 100.0,
        "relation": "touch",
        "auto_candidate": "rejection_candidate",
        "approach_side": "above",
        "touch_type": "wick_below",
        "event_bar": 2,
        "event_time": df.index[2].isoformat(),
    }
    outcomes, skipped = analyze_events([row], {("bitfinex", "BTC/USD", "1d"): df}, OutcomeConfig())
    assert not outcomes
    assert len(skipped) == 1
    assert skipped[0].reason == "no_forward_bars"


def test_summarize_outcomes_groups_by_candidate_and_horizon():
    outcomes = [
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "symbol": "BTC/USD",
            "timeframe": "1d",
            "horizon": 5,
            "forward_return": 0.01,
            "mfe": 0.02,
            "mae": 0.01,
            "close_on_approach_side": True,
            "crossed_back": False,
        },
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "symbol": "BTC/USD",
            "timeframe": "1d",
            "horizon": 5,
            "forward_return": 0.03,
            "mfe": 0.04,
            "mae": 0.02,
            "close_on_approach_side": False,
            "crossed_back": True,
        },
    ]
    summary = summarize_outcomes(outcomes)
    assert len(summary) == 1
    assert summary[0]["n_events"] == 2
    assert summary[0]["mean_forward_return"] == 0.02
    assert summary[0]["rate_close_on_approach_side"] == 0.5


def test_run_end_to_end_writes_artifacts(monkeypatch, tmp_path):
    closes = [110.0] * 6 + [100.0] + [105.0] * 20
    df = _df(closes)
    event_time = df.index[6].isoformat()
    payload = {
        "fib_id": "fib_outcome_test",
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
                        "bar_index": 6,
                        "touch_type": "wick_below",
                        "approach_side": "above",
                        "auto_candidate": "rejection_candidate",
                        "note": "test",
                        "evidence": {"forward_bars": 5},
                    }
                ],
            }
        ],
    }
    events_path = tmp_path / "fib_test_events.json"
    events_path.write_text(json.dumps(payload), encoding="utf-8")

    def load(_cfg, fetch_if_missing=False):
        return df

    monkeypatch.setattr(fco, "FIB_OUTCOMES_RUNS", tmp_path / "runs")
    monkeypatch.setattr(fco, "FIB_OUTCOMES_RESULTS", tmp_path / "results.jsonl")
    monkeypatch.setattr(fco, "load_candles", load)
    monkeypatch.setattr("fibengine.research.human_review_level_events.load_candles", load)

    result = run_fib_candidate_outcomes(
        [events_path],
        cfg=OutcomeConfig(horizons=[5, 10]),
    )
    run_dir = Path(result["run_dir"])
    assert (run_dir / "config.json").exists()
    assert (run_dir / "event_outcomes.jsonl").exists()
    assert (run_dir / "summary.csv").exists()
    assert (run_dir / "run_summary.json").exists()
    assert result["events_tested"] == 1
    assert result["outcome_rows"] == 2
