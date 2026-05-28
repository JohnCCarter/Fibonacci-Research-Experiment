import numpy as np
import pandas as pd

from fibengine.backtest.stability import (
    stability_metrics,
    walk_forward_selection,
)
from fibengine.core.config import Settings
from fibengine.core.models import Pivot, Swing


def _trending_df() -> pd.DataFrame:
    pts = [(0, 100), (40, 120), (80, 110), (120, 140), (160, 128), (200, 160)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    grid = np.arange(0, xs[-1] + 1)
    base = np.interp(grid, xs, ys)
    rng = np.random.default_rng(11)
    closes = base + rng.normal(0, 0.5, len(base))
    n = len(closes)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    wig = rng.uniform(0.3, 0.9, n)
    return pd.DataFrame(
        {
            "open": closes,
            "high": closes + wig,
            "low": closes - wig,
            "close": closes,
            "volume": np.ones(n),
        },
        index=idx,
    )


def _settings() -> Settings:
    s = Settings()
    s.scoring.weights = {
        "magnitude": 1.0,
        "recency": 0.8,
        "prominence": 0.6,
        "cleanliness": 0.5,
        "round_number": 0.2,
        "duration": -0.3,
        "structure_alignment": 0.9,
        "scale_confluence": 0.7,
    }
    s.pivots.min_prominence_atr = 0.3
    return s


def test_walk_forward_is_causal():
    df = _trending_df()
    records = walk_forward_selection(df, _settings(), warmup_bars=50, step=5)
    assert records
    # Inget val får referera barer i framtiden relativt cursorn t.
    for r in records:
        if r["swing"] is not None:
            assert r["swing"].start.index <= r["t"]
            assert r["swing"].end.index <= r["t"]


def test_future_bars_do_not_change_past_selection():
    """Look-ahead-regression: att lägga till framtida barer får INTE ändra ett
    redan fattat kausalt val. Om det gör det läcker framtid in i urvalet."""
    df = _trending_df()
    settings = _settings()
    short = df.iloc[:120]
    extended = df  # samma serie + fler framtida barer

    short_recs = walk_forward_selection(short, settings, warmup_bars=50, step=5)
    ext_recs = {r["t"]: r["swing"] for r in walk_forward_selection(extended, settings, 50, 5)}

    assert short_recs
    for r in short_recs:
        t = r["t"]
        a, b = r["swing"], ext_recs[t]
        ids_a = None if a is None else (a.start.index, a.end.index)
        ids_b = None if b is None else (b.start.index, b.end.index)
        assert ids_a == ids_b, f"val vid t={t} ändrades när framtida barer lades till"


def test_stability_metrics_shape_and_bounds():
    df = _trending_df()
    records = walk_forward_selection(df, _settings(), warmup_bars=50, step=5)
    m = stability_metrics(records)
    assert m["steps"] == len(records)
    for key in (
        "flip_rate",
        "raw_change_rate",
        "extension_rate",
        "direction_consistency",
        "confirmed_rate",
    ):
        assert 0.0 <= m[key] <= 1.0
    assert m["persistence_steps"] >= 1.0


def test_honest_flip_rate_excludes_extensions():
    df = _trending_df()
    records = walk_forward_selection(df, _settings(), warmup_bars=50, step=1)
    m = stability_metrics(records)
    # Ärlig flip_rate ska inte överstiga den råa, och endpunkt-förlängning
    # ska fångas som extension i en trendande serie.
    assert m["flip_rate"] <= m["raw_change_rate"]
    assert m["extension_rate"] > 0.0


def test_direction_consistency_ignores_none_pairs():
    df = _trending_df()
    swing_a = Swing(
        start=Pivot(0, df.index[0], 100.0, "low", 1.0),
        end=Pivot(10, df.index[10], 110.0, "high", 1.0),
    )
    swing_b = Swing(
        start=Pivot(0, df.index[0], 100.0, "low", 1.0),
        end=Pivot(12, df.index[12], 112.0, "high", 1.0),
    )
    records = [{"swing": swing_a}, {"swing": None}, {"swing": swing_b}, {"swing": swing_a}]
    m = stability_metrics(records)
    assert m["direction_consistency"] == 1.0
