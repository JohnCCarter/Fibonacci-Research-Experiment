"""Tests for joining fib fingerprints (#23) with forward outcomes (#22)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.research import fib_fingerprint_outcomes as fpo
from fibengine.research.fib_candidate_outcomes import OutcomeConfig
from fibengine.research.fib_fingerprint_outcomes import (
    join_fingerprints_outcomes,
    run_fib_fingerprint_outcomes,
    summarize_joined,
)
from fibengine.research.fib_level_fingerprints import FingerprintConfig


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


def test_join_matches_on_event_id_one_to_many_horizons():
    fingerprints = [
        {
            "event_id": "fib_x|0.5|10|rejection_candidate",
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.5",
            "timeframe": "1d",
            "pre_distance_atr_norm": 1.2,
            "post_retest_count": 3,
            "run_id": "fp_sub",
        }
    ]
    outcomes = [
        {
            "event_id": "fib_x|0.5|10|rejection_candidate",
            "horizon": 5,
            "forward_return": -0.01,
        },
        {
            "event_id": "fib_x|0.5|10|rejection_candidate",
            "horizon": 10,
            "forward_return": -0.02,
        },
    ]
    joined, unmatched = join_fingerprints_outcomes(fingerprints, outcomes)
    assert len(joined) == 2
    assert unmatched == []
    assert {r["horizon"] for r in joined} == {5, 10}
    # fingerprint fields carried, sub run_id dropped
    assert all(r["post_retest_count"] == 3 for r in joined)
    assert all("run_id" not in r for r in joined)


def test_join_reports_unmatched_both_directions():
    fingerprints = [{"event_id": "a", "timeframe": "1d"}]
    outcomes = [{"event_id": "b", "horizon": 5, "forward_return": 0.0}]
    joined, unmatched = join_fingerprints_outcomes(fingerprints, outcomes)
    assert joined == []
    reasons = {u["reason"] for u in unmatched}
    assert reasons == {"outcome_without_fingerprint", "fingerprint_without_outcome"}


def test_summarize_joined_groups_with_outcome_and_fingerprint_means():
    joined = [
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "timeframe": "1d",
            "horizon": 5,
            "forward_return": -0.01,
            "mfe": 0.02,
            "mae": 0.01,
            "close_on_approach_side": True,
            "crossed_back": False,
            "pre_distance_atr_norm": 1.0,
            "post_retest_count": 2,
        },
        {
            "auto_candidate": "rejection_candidate",
            "relation": "touch",
            "fib_level": "0.236",
            "timeframe": "1d",
            "horizon": 5,
            "forward_return": -0.03,
            "mfe": 0.04,
            "mae": 0.02,
            "close_on_approach_side": False,
            "crossed_back": True,
            "pre_distance_atr_norm": 3.0,
            "post_retest_count": 4,
        },
    ]
    summary = summarize_joined(joined)
    assert len(summary) == 1
    row = summary[0]
    assert row["n_events"] == 2
    assert row["mean_forward_return"] == -0.02
    assert row["rate_close_on_approach_side"] == 0.5
    assert row["mean_pre_distance_atr_norm"] == 2.0
    assert row["mean_post_retest_count"] == 3.0


def test_run_end_to_end_joins_same_events(monkeypatch, tmp_path):
    closes = [110.0] * 10 + [100.0] + [105.0] * 20
    df = _df(closes)
    event_time = df.index[10].isoformat()
    payload = {
        "fib_id": "fib_join_test",
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

    monkeypatch.setattr(fpo, "JOIN_RUNS", tmp_path / "runs")
    monkeypatch.setattr(fpo, "JOIN_RESULTS", tmp_path / "results.jsonl")
    monkeypatch.setattr(fpo, "load_candles", load)
    monkeypatch.setattr("fibengine.research.human_review_level_events.load_candles", load)

    result = run_fib_fingerprint_outcomes(
        [events_path],
        fingerprint_cfg=FingerprintConfig(pre_bars=5, post_bars=10),
        outcome_cfg=OutcomeConfig(horizons=[5, 10]),
    )
    run_dir = Path(result["run_dir"])
    assert (run_dir / "fingerprint_outcomes.jsonl").exists()
    assert (run_dir / "summary.csv").exists()
    assert result["joined_events"] == 1
    assert result["joined_rows"] == 2
    assert result["unmatched"] == 0

    rows = [
        json.loads(line)
        for line in (run_dir / "fingerprint_outcomes.jsonl").read_text().splitlines()
    ]
    # Joined row carries both layers
    assert "pre_approach_direction" in rows[0]
    assert "forward_return" in rows[0]
    assert "horizon" in rows[0]
