"""Probe the HO-B miss: origin ~2026-06-25 @61,773 (screenshot 172932).

Why did the engine not propose it? Show (a) all high pivots in late Jun 2026 with
prominence + rank within +/-72b, (b) which bar actually carries the 61,773 high,
(c) what structures the engine proposed with origin in late Jun.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.chamoun_structure_engine import DEFAULT_CONFIG, propose_structures

settings = load_settings("config/variants/settings.1h_recent.yaml")
df = load_candles(settings.data, fetch_if_missing=False)
pivots = detect_pivots(df, settings.pivots)
structs = propose_structures(df, pivots, DEFAULT_CONFIG)
SCALE = DEFAULT_CONFIG.local_scale

high = df["high"].to_numpy()
highs = [p for p in pivots if p.kind == "high"]
hi_idx = np.array([p.index for p in highs])
hi_prom = np.array([p.prominence for p in highs])

lo = pd.Timestamp("2026-06-22", tz="UTC")
hi = pd.Timestamp("2026-06-30", tz="UTC")

print(f"cache ends {df.index[-1]}\n")

# (a) bar with high closest to 61,773 anywhere in +/-4d
win = (df.index >= lo) & (df.index <= hi)
widx = np.where(win)[0]
j = widx[np.argmin(np.abs(high[widx] - 61773.0))]
print(f"(b) bar closest to 61,773 in window: {df.index[j]}  high={high[j]:,.0f}")
print(
    f"    highest high in whole window: {high[widx].max():,.0f} "
    f"at {df.index[widx[np.argmax(high[widx])]]}\n"
)

print("(a) high pivots 2026-06-22..30  [prom, rank within +/-72b]:")
for k, p in enumerate(highs):
    if not (lo <= df.index[p.index] <= hi):
        continue
    i = p.index
    in_scale = (hi_idx >= i - SCALE) & (hi_idx <= i + SCALE)
    rank = int((hi_prom[in_scale] > hi_prom[k]).sum()) + 1
    fwd = min(i + SCALE, len(df) - 1) - i
    tag = "  <-- #1 origin-eligible" if rank == 1 else ""
    print(
        f"   {str(df.index[i])[:16]}  high={high[i]:>8,.0f}  prom={hi_prom[k]:>5.1f}  "
        f"rank {rank:>2}/{in_scale.sum():>2}  fwd_avail={fwd}b{tag}"
    )

print("\n(c) engine proposals with origin in Jun 2026:")
for s in structs:
    if pd.Timestamp("2026-06-01", tz="UTC") <= s.origin_ts <= hi:
        print(
            f"   origin {str(s.origin_ts)[:16]} @{s.origin_price:>8,.0f} -> "
            f"reached {str(s.reached_ts)[:16]} @{s.reached_price:>8,.0f} "
            f"move={s.move:.1%} bars={s.bars} {'ACTIVE' if s.active else 'broken'}"
        )
