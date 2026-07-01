"""Top-down validation of Chamoun's NEW M/W/D facit (20 fibs, transcribed 2026-07-01) vs the
prominence-origin rule. EXPLORATORY (nothing locked).

Each fib: snap origin to the cache BY PRICE (tz-robust) near its approx axis date; report the
snapped bar, whether it is a detected pivot of the right kind, and its prominence RANK within
+/-N bars (several neutral N per TF). Answers: does the prominence rule find his new origins?
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.pivots.detect import detect_pivots

PCFG = load_settings("config/variants/settings.1h_recent.yaml").pivots
CACHE = {
    "1M": "data/raw/bitfinex/BTC-USD/1M/limit_500.csv",
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
}
SCALES = {"1M": [2, 3, 4], "1w": [4, 8, 12], "1d": [10, 20, 40]}
WIN_DAYS = {"1M": 130, "1w": 45, "1d": 30}

# (tf, tag, direction, origin_price, reached_price, approx_origin_date)
FIBS = [
    # MONTHLY (4)
    ("1M", "M1", "up", 9882.0, 63565.4, "2020-09-01"),
    ("1M", "M2", "down", 47600.0, 15487.0, "2022-04-01"),
    ("1M", "M3", "up", 52756.0, 109590.0, "2024-09-01"),
    ("1M", "M4", "up", 888.2, 19891.0, "2017-03-01"),
    # WEEKLY (7)
    ("1w", "W1", "down", 97850.0, 60100.0, "2026-01-05"),
    ("1w", "W2", "down", 116500.0, 80822.0, "2025-10-06"),
    ("1w", "W3", "up", 58943.0, 108100.0, "2024-09-30"),
    ("1w", "W4", "up", 16584.0, 24240.0, "2022-11-14"),
    ("1w", "W5", "up", 29313.0, 52888.0, "2021-07-19"),
    ("1w", "W6", "up", 1923.2, 4970.0, "2017-07-17"),
    ("1w", "W7", "down", 19891.0, 3215.2, "2017-12-11"),
    # DAILY (9)
    ("1d", "D1", "down", 90600.0, 60100.0, "2026-01-25"),
    ("1d", "D2", "down", 107500.0, 80822.0, "2025-10-28"),
    ("1d", "D3", "down", 126110.0, 103310.0, "2025-10-06"),
    ("1d", "D4", "up", 107630.0, 118790.0, "2025-06-22"),
    ("1d", "D5", "down", 39850.0, 26437.3, "2022-04-28"),
    ("1d", "D6", "down", 31775.0, 17605.0, "2022-06-06"),
    ("1d", "D7", "up", 2610.0, 4492.3, "2017-07-16"),
    ("1d", "D8", "down", 6485.8, 3215.2, "2018-11-14"),
    ("1d", "D9", "up", 21884.0, 41969.0, "2020-12-21"),
]

# load caches + pivots once per tf
CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    piv = detect_pivots(df, PCFG)
    highs = {p.index: p.prominence for p in piv if p.kind == "high"}
    lows = {p.index: p.prominence for p in piv if p.kind == "low"}
    CTX[tf] = {
        "df": df,
        "highs": highs,
        "lows": lows,
        "hi_idx": np.array(sorted(highs)),
        "hi_prom": np.array([highs[i] for i in sorted(highs)]),
        "lo_idx": np.array(sorted(lows)),
        "lo_prom": np.array([lows[i] for i in sorted(lows)]),
    }


def rank(idx_arr, prom_arr, i, val, N):
    m = (idx_arr >= i - N) & (idx_arr <= i + N)
    return int((prom_arr[m] > val).sum()) + 1, int(m.sum())


summary = {}
for tf in ["1M", "1w", "1d"]:
    c = CTX[tf]
    df = c["df"]
    scales = SCALES[tf]
    print(
        f"\n===== {tf}  (bars {df.index[0].date()}..{df.index[-1].date()}, "
        f"{len(c['highs'])} high / {len(c['lows'])} low pivots) ====="
    )
    print(
        f"{'':4}{'dir':<5}{'origin(label)':<20}{'snap':<13}{'dprice':<9}{'pivot?':<8}"
        + "".join(f"±{n:<7}" for n in scales)
    )
    top = {n: 0 for n in scales}
    npiv = 0
    ndet = 0
    for ftf, tag, direc, oprice, _rprice, adate in FIBS:
        if ftf != tf:
            continue
        npiv += 1
        t0 = pd.Timestamp(adate, tz="UTC")
        w = (df.index >= t0 - pd.Timedelta(days=WIN_DAYS[tf])) & (
            df.index <= t0 + pd.Timedelta(days=WIN_DAYS[tf])
        )
        widx = np.where(w)[0]
        col = "high" if direc == "down" else "low"
        j = widx[np.argmin(np.abs(df[col].to_numpy()[widx] - oprice))]
        snapprice = float(df[col].to_numpy()[j])
        pivmap = c["highs"] if direc == "down" else c["lows"]
        is_piv = j in pivmap
        cells = []
        if is_piv:
            ndet += 1
            for n in scales:
                if direc == "down":
                    r, tot = rank(c["hi_idx"], c["hi_prom"], j, pivmap[j], n)
                else:
                    r, tot = rank(c["lo_idx"], c["lo_prom"], j, pivmap[j], n)
                cells.append(f"{r}/{tot}")
                if r == 1:
                    top[n] += 1
        else:
            cells = ["-"] * len(scales)
        print(
            f"{tag:<4}{direc:<5}{f'{str(t0.date())[:7]} @{oprice:,.0f}':<20}"
            f"{str(df.index[j].date()):<13}{snapprice - oprice:>+8.0f} "
            f"{('piv' if is_piv else 'NOT-piv'):<8}" + "".join(f"{x:<8}" for x in cells)
        )
    summary[tf] = (npiv, ndet, top, scales)

print("\n===== SUMMARY: origins that are #1-prominence pivots (major-swing rule) =====")
for tf in ["1M", "1w", "1d"]:
    npiv, ndet, top, scales = summary[tf]
    s = "  ".join(f"±{n}:{top[n]}/{npiv}" for n in scales)
    print(f"  {tf}: detected-as-pivot {ndet}/{npiv}   #1-prom → {s}")
