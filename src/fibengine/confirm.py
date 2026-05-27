"""Bekräftad vs provisorisk swing.

En vald swing är *provisorisk* så länge dess senaste extrem fortfarande kan
växa (priset gör nya highs/lows). Den blir *bekräftad* först när (a) det finns
tillräckligt med barer efter extremen för att en fraktal kunde ha bildats, och
(b) priset faktiskt dragit tillbaka en bit från extremen. Då — och först då — är
Fib:en klar att handla på.
"""

from __future__ import annotations

import pandas as pd

from fibengine.models import Swing


def classify_swing(
    df: pd.DataFrame, swing: Swing, fractal_n: int, min_retrace: float
) -> str:
    """Returnera "confirmed" eller "provisional" för den valda legen."""
    n = len(df)
    bars_after = (n - 1) - swing.end.index
    if bars_after < fractal_n:
        return "provisional"

    price_range = swing.price_range
    if price_range <= 0:
        return "provisional"

    after_high = df["high"].to_numpy()[swing.end.index + 1 :]
    after_low = df["low"].to_numpy()[swing.end.index + 1 :]
    if swing.end.kind == "high":
        retrace = (swing.end.price - after_low.min()) / price_range
    else:
        retrace = (after_high.max() - swing.end.price) / price_range

    return "confirmed" if retrace >= min_retrace else "provisional"
