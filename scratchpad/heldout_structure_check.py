"""Held-out check for chamoun_structure_engine v1 (DOWN-only).

For each held-out origin read off Chamoun's dated 1h screenshots, answer the two
questions the acceptance bar cares about:
  Q1 (headline, his bar): does the frozen engine PROPOSE a down-structure whose origin
      lands on/near his origin candle (right region)?
  Q2 (neutral, non-circular): is his chosen origin high the #1 max-prominence high
      within +/-local_scale (72) bars among detected pivots? (the property calibration used)

Approximate (date, price) come from the screenshot axis labels; we snap to the real
high pivot nearest that date whose price is closest to the labelled origin price.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.chamoun_structure_engine import DEFAULT_CONFIG, propose_structures

CFG = "config/variants/settings.1h_recent.yaml"
SCALE = DEFAULT_CONFIG.local_scale

# (label, screenshot, approx origin date, approx origin price)
HELDOUT = [
    ("HO-A", "172907", "2026-03-27", 68940.0),
    ("HO-B", "172932", "2026-06-25", 61773.0),
    ("HO-C", "172955", "2025-11-03", 110870.0),
    ("HO-D", "173131", "2025-07-31", 118960.0),
]

settings = load_settings(CFG)
df = load_candles(settings.data, fetch_if_missing=False)
pivots = detect_pivots(df, settings.pivots)
structs = propose_structures(df, pivots, DEFAULT_CONFIG)

highs = [p for p in pivots if p.kind == "high"]
hi_idx = np.array([p.index for p in highs])
hi_prom = np.array([p.prominence for p in highs])

print(f"cache bars: {len(df)}  range {df.index[0]} .. {df.index[-1]}")
print(f"high pivots: {len(highs)}   proposed DOWN structures: {len(structs)}\n")

for label, shot, date, price in HELDOUT:
    t0 = pd.Timestamp(date, tz="UTC")
    win = (df.index >= t0 - pd.Timedelta(days=3)) & (df.index <= t0 + pd.Timedelta(days=3))
    if not win.any():
        print(f"{label} ({shot}) origin ~{date} @{price:,.0f}: NOT IN CACHE\n")
        continue
    # candidate high pivots inside the +/-3d window
    cand = [(k, p) for k, p in enumerate(highs) if win[p.index]]
    if not cand:
        print(f"{label} ({shot}): no high pivot within +/-3d of {date}\n")
        continue
    # snap to the pivot whose high is closest to the labelled origin price
    k_star, p_star = min(cand, key=lambda kp: abs(df["high"].to_numpy()[kp[1].index] - price))
    i = p_star.index
    ts = df.index[i]
    ph = float(df["high"].to_numpy()[i])
    # Q2: prominence rank within +/-SCALE bars (1 = most prominent)
    in_scale = (hi_idx >= i - SCALE) & (hi_idx <= i + SCALE)
    proms = hi_prom[in_scale]
    rank = int((proms > hi_prom[k_star]).sum()) + 1
    is_top = rank == 1
    # Q1: did the engine propose a structure whose origin is near this candle?
    near = [s for s in structs if abs(s.origin_index - i) <= 12]
    q1 = "YES" if near else "no"
    matched = min(near, key=lambda s: abs(s.origin_index - i)) if near else None
    print(
        f"{label} ({shot})  origin snap -> {str(ts)[:16]}  high={ph:,.0f}  "
        f"(label {price:,.0f}, dp={ph - price:+,.0f})"
    )
    print(
        f"   Q2 prominence: rank {rank}/{in_scale.sum()} within +/-{SCALE}b  "
        f"-> {'#1 (generalizes)' if is_top else 'NOT #1 (fails neutral test)'}"
    )
    if matched is not None:
        print(
            f"   Q1 engine proposes origin: {str(matched.origin_ts)[:16]} "
            f"@{matched.origin_price:,.0f} -> reached {str(matched.reached_ts)[:16]} "
            f"@{matched.reached_price:,.0f}  move={matched.move:.1%} "
            f"(origin off by {matched.origin_index - i:+d} bars)"
        )
    else:
        print("   Q1 engine proposes: NO structure with origin within +/-12 bars")
    print()
