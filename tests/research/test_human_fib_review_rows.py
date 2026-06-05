from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.research import human_review_level_events as hr
from fibengine.research.human_review_level_events import REVIEW_COLUMNS


def _trend_df() -> pd.DataFrame:
    grid = np.arange(0, 80)
    closes = np.interp(grid, [0, 40, 79], [100, 150, 120])
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "close": closes,
            "volume": np.ones(len(closes)),
        },
        index=idx,
    )


def test_human_fib_event_payload_rows_keep_anchor_and_candidate_separate():
    df = _trend_df()
    event_bar = 50
    level_price = float(df["close"].iloc[event_bar])
    payload = {
        "fib_id": "human_fib_001",
        "symbol": "BTC/USD",
        "timeframe": "1h",
        "exchange": "bitfinex",
        "direction": "up",
        "anchor_a": {"time": df.index[0].isoformat(), "price": float(df["low"].iloc[0])},
        "anchor_b": {"time": df.index[40].isoformat(), "price": float(df["high"].iloc[40])},
        "source": "human_fib_events",
        "levels": [
            {
                "level": "0.5",
                "price": level_price,
                "events": [
                    {
                        "event_bar": df.index[event_bar].isoformat(),
                        "bar_index": event_bar,
                        "touch_type": "wick_below",
                        "approach_side": "above",
                        "auto_candidate": "rejection_candidate",
                        "note": "Touched level and rejected back to the approach side",
                        "evidence": {
                            "forward_bars": 5,
                            "closes_beyond": 0,
                            "closes_back": 2,
                            "max_penetration_atr": 0.1,
                        },
                    }
                ],
            }
        ],
    }

    rows = hr._rows_from_human_fib_events_payload(df, payload)

    assert len(rows) == 1
    row = rows[0]
    assert set(row.keys()) == set(REVIEW_COLUMNS)
    assert row["fib_id"] == "human_fib_001"
    assert row["fib_source"] == "human_fib_events"
    assert row["relation"] == "touch"
    assert row["auto_candidate"] == "rejection_candidate"
    assert row["anchor_a_bar"] == 0
    assert row["anchor_b_bar"] == 40
    assert row["human_label"] == ""
