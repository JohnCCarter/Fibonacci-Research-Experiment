import pandas as pd

from fibengine.labeling.behavior_candidates import classify_level
from fibengine.labeling.store import LegLabel, Point


def test_down_leg_continuation_candidate():
    leg = LegLabel(
        id="leg_1",
        high=Point("2026-01-15T00:00:00+00:00", 100.0),
        low=Point("2026-01-20T00:00:00+00:00", 80.0),
    )
    idx = pd.date_range("2026-01-15", periods=6, freq="D", tz="UTC")
    candles = pd.DataFrame(
        {
            "open": [100, 95, 90, 88, 84, 80],
            "high": [100, 96, 91, 89, 85, 81],
            "low": [99, 94, 89, 86, 82, 79],
            "close": [95, 90, 88, 85, 82, 80],
            "volume": [1.0] * 6,
        },
        index=idx,
    )
    # 0.618 down from 100->80 = 87.64
    result = classify_level(candles, leg, "0.618", 87.64)
    assert result.auto_candidate in {
        "continuation_candidate",
        "reaction_candidate",
        "rejection_candidate",
    }
    assert result.event_bar
