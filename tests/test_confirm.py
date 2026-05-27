import numpy as np
import pandas as pd

from fibengine.confirm import classify_swing
from fibengine.models import Pivot, Swing


def _df(closes: list[float]) -> pd.DataFrame:
    arr = np.array(closes, dtype=float)
    n = len(arr)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": arr, "high": arr + 0.5, "low": arr - 0.5, "close": arr,
         "volume": np.ones(n)},
        index=idx,
    )


def _up_swing(df, start_i, end_i) -> Swing:
    return Swing(
        start=Pivot(start_i, df.index[start_i], float(df["low"].iloc[start_i]), "low", 3.0),
        end=Pivot(end_i, df.index[end_i], float(df["high"].iloc[end_i]), "high", 3.0),
    )


def test_confirmed_when_retraced_with_bars_after():
    # Upp till bar 10 (pris 120), sedan tydlig pullback ner mot 108.
    closes = [100 + i * 2 for i in range(11)] + [118, 114, 110, 108, 109]
    df = _df(closes)
    swing = _up_swing(df, 0, 10)  # low@0 -> high@10
    assert classify_swing(df, swing, fractal_n=2, min_retrace=0.1) == "confirmed"


def test_provisional_when_end_is_last_bar():
    closes = [100 + i * 2 for i in range(11)]  # slutar på toppen (bar 10 = sista)
    df = _df(closes)
    swing = _up_swing(df, 0, 10)
    assert classify_swing(df, swing, fractal_n=2, min_retrace=0.1) == "provisional"


def test_provisional_when_no_pullback():
    # Tillräckligt med barer efter, men priset håller sig kvar uppe (ingen retrace).
    closes = [100 + i * 2 for i in range(11)] + [120, 120, 120, 120]
    df = _df(closes)
    swing = _up_swing(df, 0, 10)
    assert classify_swing(df, swing, fractal_n=2, min_retrace=0.1) == "provisional"
