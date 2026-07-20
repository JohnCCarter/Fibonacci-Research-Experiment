"""EXPLORATORY (no locked verdict): does the prominence-origin rule resemble Chamoun's
monthly facit origins? Top-down step 1 = Monthly.

For each committed 1M facit fib, locate its origin anchor (anchor_a) bar, check whether it
coincides with a detected pivot of the right kind (high for down / low for up), and report its
prominence RANK within +/-N months for several N. Pure read; nothing locked.
"""

from __future__ import annotations

import glob
import json

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.pivots.detect import detect_pivots

CSV = "data/raw/bitfinex/BTC-USD/1M/limit_500.csv"
FACIT = "data/labels/human_fib/bitfinex/BTC-USD/1M/fib_BTC-USD_1M_*.json"
SCALES = [2, 3, 4, 6]

df = pd.read_csv(CSV, parse_dates=["timestamp"], index_col="timestamp")
pcfg = load_settings("config/variants/settings.1h_recent.yaml").pivots
pivots = detect_pivots(df, pcfg)
highs = {p.index: p for p in pivots if p.kind == "high"}
lows = {p.index: p for p in pivots if p.kind == "low"}
hi_idx = np.array(sorted(highs))
hi_prom = np.array([highs[i].prominence for i in hi_idx])
lo_idx = np.array(sorted(lows))
lo_prom = np.array([lows[i].prominence for i in lo_idx])
pos = {t: k for k, t in enumerate(df.index)}


def rank(idx_arr, prom_arr, i, val, N):
    m = (idx_arr >= i - N) & (idx_arr <= i + N)
    return int((prom_arr[m] > val).sum()) + 1, int(m.sum())


files = sorted(f for f in glob.glob(FACIT) if "_events" not in f)
print(
    f"monthly facit: {len(files)}   bars {df.index[0].date()}..{df.index[-1].date()}   "
    f"high pivots {len(highs)}  low pivots {len(lows)}\n"
)
print(f"{'fib_id':<26}{'dir':<5}{'origin':<20}{'pivot?':<8}" + "".join(f"±{n:<7}" for n in SCALES))
hits = {n: 0 for n in SCALES}
downs = 0
for f in files:
    d = json.load(open(f))
    direc = d["direction"]
    a = d["anchor_a"]
    t = pd.Timestamp(a["time"])
    i = pos.get(t)
    tag = f"{str(t.date())} @{a['price']:,.0f}"
    if i is None:
        print(f"{d['fib_id'][-14:]:<26}{direc:<5}{tag:<20}{'NO BAR':<8}")
        continue
    if direc == "down":
        downs += 1
        is_piv = i in highs
        cells = []
        for n in SCALES:
            if is_piv:
                r, tot = rank(hi_idx, hi_prom, i, highs[i].prominence, n)
                cells.append(f"{r}/{tot}")
                if r == 1:
                    hits[n] += 1
            else:
                cells.append("-")
        print(
            f"{d['fib_id'][-14:]:<26}{direc:<5}{tag:<20}{('high' if is_piv else 'not-piv'):<8}"
            + "".join(f"{c:<8}" for c in cells)
        )
    else:  # up: origin = low
        is_piv = i in lows
        cells = [
            (
                f"{rank(lo_idx, lo_prom, i, lows[i].prominence, n)[0]}/"
                f"{rank(lo_idx, lo_prom, i, lows[i].prominence, n)[1]}"
            )
            if is_piv
            else "-"
            for n in SCALES
        ]
        print(
            f"{d['fib_id'][-14:]:<26}{direc:<5}{tag:<20}{('low' if is_piv else 'not-piv'):<8}"
            + "".join(f"{c:<8}" for c in cells)
        )

print(f"\nDOWN facit origins that are #1-prominence high within +/-N  (n_down={downs}):")
for n in SCALES:
    print(f"   +/-{n}mo: {hits[n]}/{downs}")
