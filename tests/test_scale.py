import numpy as np
import pandas as pd

from fibengine.config import PivotConfig
from fibengine.models import Pivot, Swing
from fibengine.scale import detect_pivots_multi, endpoint_confluence


def _df_with_one_big_swing() -> pd.DataFrame:
    # En stor, ren sväng (low@0 -> high@60) med småbrus ovanpå.
    pts = [(0, 100), (60, 140), (120, 110)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    grid = np.arange(0, xs[-1] + 1)
    base = np.interp(grid, xs, ys)
    rng = np.random.default_rng(3)
    closes = base + rng.normal(0, 0.4, len(base))
    n = len(closes)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    wig = rng.uniform(0.3, 0.9, n)
    return pd.DataFrame(
        {"open": closes, "high": closes + wig, "low": closes - wig,
         "close": closes, "volume": np.ones(n)},
        index=idx,
    )


def test_larger_degree_has_fewer_pivots():
    df = _df_with_one_big_swing()
    base = PivotConfig(min_prominence_atr=0.3)
    multi = detect_pivots_multi(df, base, degrees=[2, 12])
    assert len(multi[12]) <= len(multi[2])


def test_major_leg_endpoints_score_higher_than_noise_leg():
    df = _df_with_one_big_swing()
    base = PivotConfig(min_prominence_atr=0.3)
    multi = detect_pivots_multi(df, base, degrees=[12])

    # Den stora legen: low@0 -> high@60 (endpunkter sammanfaller med stora fraktaler).
    major = Swing(
        start=Pivot(0, df.index[0], float(df["low"].iloc[0]), "low", 5.0),
        end=Pivot(60, df.index[60], float(df["high"].iloc[60]), "high", 5.0),
    )
    # En liten brus-leg långt från de stora vändpunkterna.
    noise = Swing(
        start=Pivot(95, df.index[95], float(df["low"].iloc[95]), "low", 1.0),
        end=Pivot(100, df.index[100], float(df["high"].iloc[100]), "high", 1.0),
    )

    major_score = endpoint_confluence(major, multi, tol_bars=3)
    noise_score = endpoint_confluence(noise, multi, tol_bars=3)
    assert major_score > noise_score


def test_empty_degrees_is_neutral():
    df = _df_with_one_big_swing()
    swing = Swing(
        start=Pivot(0, df.index[0], 100.0, "low", 5.0),
        end=Pivot(60, df.index[60], 140.0, "high", 5.0),
    )
    assert endpoint_confluence(swing, {}, tol_bars=3) == 0.5
