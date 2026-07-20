"""PROTOTYPE (descriptive, nothing locked): does MULTI-SCALE Directional-Change swing detection
capture Chamoun's 20 M/W/D origins better than single-scale prominence?

DC swing detector (single-pass O(n), one threshold theta): standard percentage-ZigZag on
high/low extremes. Run at a FIXED neutral theta ladder (locked before measuring). For each facit
origin, find the SMALLEST theta whose DC swing (right kind) lands within +/-tol bars of it = its
natural scale. Coverage = fraction of origins captured at any theta.

Baseline to beat (single-scale prominence, detected-as-pivot): 1M 1/4, 1w 5/7, 1d 6/9.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# NEUTRAL theta ladder, locked here before any measurement (fib-spaced % moves).
THETAS = [0.03, 0.05, 0.08, 0.13, 0.21, 0.34]
TOL_BARS = 2  # snapping/week-convention slack

CACHE = {
    "1M": "data/raw/bitfinex/BTC-USD/1M/limit_500.csv",
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
}
WIN_DAYS = {"1M": 130, "1w": 45, "1d": 30}

FIBS = [
    ("1M", "M1", "up", 9882.0, "2020-09-01"),
    ("1M", "M2", "down", 47600.0, "2022-04-01"),
    ("1M", "M3", "up", 52756.0, "2024-09-01"),
    ("1M", "M4", "up", 888.2, "2017-03-01"),
    ("1w", "W1", "down", 97850.0, "2026-01-05"),
    ("1w", "W2", "down", 116500.0, "2025-10-06"),
    ("1w", "W3", "up", 58943.0, "2024-09-30"),
    ("1w", "W4", "up", 16584.0, "2022-11-14"),
    ("1w", "W5", "up", 29313.0, "2021-07-19"),
    ("1w", "W6", "up", 1923.2, "2017-07-17"),
    ("1w", "W7", "down", 19891.0, "2017-12-11"),
    ("1d", "D1", "down", 90600.0, "2026-01-25"),
    ("1d", "D2", "down", 107500.0, "2025-10-28"),
    ("1d", "D3", "down", 126110.0, "2025-10-06"),
    ("1d", "D4", "up", 107630.0, "2025-06-22"),
    ("1d", "D5", "down", 39850.0, "2022-04-28"),
    ("1d", "D6", "down", 31775.0, "2022-06-06"),
    ("1d", "D7", "up", 2610.0, "2017-07-16"),
    ("1d", "D8", "down", 6485.8, "2018-11-14"),
    ("1d", "D9", "up", 21884.0, "2020-12-21"),
]


def dc_swings(high, low, theta):
    """Standard directional-change ZigZag. Returns dict kind->set(indices) of confirmed swings."""
    n = len(high)
    hi_s, lo_s = set(), set()
    mode = "up"
    ext_i, ext_p = 0, high[0]
    for i in range(1, n):
        if mode == "up":
            if high[i] > ext_p:
                ext_i, ext_p = i, high[i]
            elif low[i] <= ext_p * (1 - theta):
                hi_s.add(ext_i)
                mode, ext_i, ext_p = "down", i, low[i]
        else:
            if low[i] < ext_p:
                ext_i, ext_p = i, low[i]
            elif high[i] >= ext_p * (1 + theta):
                lo_s.add(ext_i)
                mode, ext_i, ext_p = "up", i, high[i]
    return {"high": hi_s, "low": lo_s}


CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    swings = {th: dc_swings(df["high"].to_numpy(), df["low"].to_numpy(), th) for th in THETAS}
    CTX[tf] = {"df": df, "swings": swings}


def covered(sw_set, j):
    return any(abs(s - j) <= TOL_BARS for s in sw_set)


def null_coverage(df, sw_set, kind):
    """Fraction of ALL bars within +/-TOL of a swing of this kind = chance level."""
    n = len(df)
    if not sw_set:
        return 0.0
    hit = np.zeros(n, dtype=bool)
    for s in sw_set:
        hit[max(0, s - TOL_BARS) : min(n, s + TOL_BARS + 1)] = True
    return hit.mean()


print(f"DC theta ladder (locked): {THETAS}   tol=+/-{TOL_BARS} bars\n")

# --- density + null per theta per TF ---
print("===== DENSITY / NULL: swing count and chance-coverage per theta =====")
for tf in ["1M", "1w", "1d"]:
    c = CTX[tf]
    df = c["df"]
    n = len(df)
    print(f"  {tf} ({n} bars):")
    for th in THETAS:
        nh = len(c["swings"][th]["high"])
        nl = len(c["swings"][th]["low"])
        nul_h = null_coverage(df, c["swings"][th]["high"], "high")
        nul_l = null_coverage(df, c["swings"][th]["low"], "low")
        print(
            f"     theta={th:.2f}: highs={nh:>4} lows={nl:>4}  "
            f"null-cov high={nul_h:.0%} low={nul_l:.0%}"
        )
    print()

# --- his origins: capture vs null, per theta ---
print("===== HIS ORIGINS: captured (Y) vs chance, per theta =====")
print(f"{'':16}" + "".join(f"th{th:.2f} ".replace("th0", "θ") for th in THETAS))
sel = {tf: {th: [0, 0, 0.0] for th in THETAS} for tf in CACHE}  # [hits, n, summed-null]
for tf in ["1M", "1w", "1d"]:
    c = CTX[tf]
    df = c["df"]
    for ftf, tag, direc, oprice, adate in FIBS:
        if ftf != tf:
            continue
        t0 = pd.Timestamp(adate, tz="UTC")
        w = (df.index >= t0 - pd.Timedelta(days=WIN_DAYS[tf])) & (
            df.index <= t0 + pd.Timedelta(days=WIN_DAYS[tf])
        )
        widx = np.where(w)[0]
        col = "high" if direc == "down" else "low"
        j = widx[np.argmin(np.abs(df[col].to_numpy()[widx] - oprice))]
        kind = "high" if direc == "down" else "low"
        row = []
        for th in THETAS:
            hit = covered(c["swings"][th][kind], j)
            row.append("Y " if hit else ". ")
            sel[tf][th][0] += int(hit)
            sel[tf][th][1] += 1
            sel[tf][th][2] += null_coverage(df, c["swings"][th][kind], kind)
        print(f"  {tf} {tag} {direc:<4} " + "  ".join(row))

print("\n===== SELECTIVITY: his capture rate vs chance (mean null), per theta =====")
for tf in ["1M", "1w", "1d"]:
    print(f"  {tf}:")
    for th in THETAS:
        h, nn, snull = sel[tf][th]
        print(
            f"     theta={th:.2f}: his {h}/{nn} = {h / nn:.0%}   vs chance {snull / nn:.0%}"
            f"   {'<-- beats chance' if h / nn - snull / nn > 0.15 else ''}"
        )
