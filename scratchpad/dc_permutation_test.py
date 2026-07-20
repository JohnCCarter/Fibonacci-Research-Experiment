"""Permutation test: are Chamoun's W/D origins DC-swings at theta~5-8% MORE than chance?

Conservative null: draw random DETECTED PIVOTS of the same kind (controls for "he picks
extremes") and measure their DC-theta capture rate. Observed = his origins' capture rate.
p = P(null capture >= observed). Locked theta in {0.05, 0.08}; seed fixed; tol=+/-2 bars.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.pivots.detect import detect_pivots

SEED = 20260701
B = 20000
TOL = 2
THETAS = [0.05, 0.08]
PCFG = load_settings("config/variants/settings.1h_recent.yaml").pivots
CACHE = {
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
}
WIN_DAYS = {"1w": 45, "1d": 30}
FIBS = [
    ("1w", "down", 97850.0, "2026-01-05"),
    ("1w", "down", 116500.0, "2025-10-06"),
    ("1w", "up", 58943.0, "2024-09-30"),
    ("1w", "up", 16584.0, "2022-11-14"),
    ("1w", "up", 29313.0, "2021-07-19"),
    ("1w", "up", 1923.2, "2017-07-17"),
    ("1w", "down", 19891.0, "2017-12-11"),
    ("1d", "down", 90600.0, "2026-01-25"),
    ("1d", "down", 107500.0, "2025-10-28"),
    ("1d", "down", 126110.0, "2025-10-06"),
    ("1d", "up", 107630.0, "2025-06-22"),
    ("1d", "down", 39850.0, "2022-04-28"),
    ("1d", "down", 31775.0, "2022-06-06"),
    ("1d", "up", 2610.0, "2017-07-16"),
    ("1d", "down", 6485.8, "2018-11-14"),
    ("1d", "up", 21884.0, "2020-12-21"),
]


def dc_swings(high, low, theta):
    n = len(high)
    hi_s, lo_s = set(), set()
    mode, ext_i, ext_p = "up", 0, high[0]
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
    return {"high": np.array(sorted(hi_s)), "low": np.array(sorted(lo_s))}


def cap(sw, idxs):
    """fraction of idxs within +/-TOL of any swing in sw (sorted array)."""
    if len(sw) == 0 or len(idxs) == 0:
        return 0.0
    hit = 0
    for j in idxs:
        k = np.searchsorted(sw, j)
        near = False
        for kk in (k - 1, k):
            if 0 <= kk < len(sw) and abs(sw[kk] - j) <= TOL:
                near = True
                break
        hit += int(near)
    return hit / len(idxs)


CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    piv = detect_pivots(df, PCFG)
    CTX[tf] = {
        "df": df,
        "sw": {th: dc_swings(df["high"].to_numpy(), df["low"].to_numpy(), th) for th in THETAS},
        "pool": {
            "high": np.array([p.index for p in piv if p.kind == "high"]),
            "low": np.array([p.index for p in piv if p.kind == "low"]),
        },
    }

# snap his origins -> (tf, kind, bar_index)
origins = {tf: [] for tf in CACHE}
for tf, direc, oprice, adate in FIBS:
    df = CTX[tf]["df"]
    t0 = pd.Timestamp(adate, tz="UTC")
    w = (df.index >= t0 - pd.Timedelta(days=WIN_DAYS[tf])) & (
        df.index <= t0 + pd.Timedelta(days=WIN_DAYS[tf])
    )
    widx = np.where(w)[0]
    col = "high" if direc == "down" else "low"
    j = int(widx[np.argmin(np.abs(df[col].to_numpy()[widx] - oprice))])
    origins[tf].append(("high" if direc == "down" else "low", j))

rng = np.random.default_rng(SEED)
print(
    f"Permutation test  B={B}  seed={SEED}  tol=+/-{TOL}  null=random same-kind detected pivots\n"
)


def run(cells, label):
    for th in THETAS:
        obs_hits = obs_n = 0
        null = np.zeros(B)
        # build per-cell arrays
        cell_data = []
        for tf in cells:
            sw = CTX[tf]["sw"][th]
            pool = CTX[tf]["pool"]
            idx_by_kind = {"high": [], "low": []}
            for kind, j in origins[tf]:
                idx_by_kind[kind].append(j)
            for kind in ("high", "low"):
                ks = idx_by_kind[kind]
                if not ks:
                    continue
                obs_hits += cap(sw[kind], np.array(ks)) * len(ks)
                obs_n += len(ks)
                cell_data.append((sw[kind], pool[kind], len(ks)))
        obs = obs_hits / obs_n
        for b in range(B):
            h = tot = 0
            for sw_k, pool_k, m in cell_data:
                draw = rng.choice(pool_k, size=m, replace=False) if len(pool_k) >= m else pool_k
                h += cap(sw_k, draw) * len(draw)
                tot += len(draw)
            null[b] = h / tot
        p = (np.sum(null >= obs) + 1) / (B + 1)
        print(
            f"  {label}  theta={th:.2f}: observed {obs:.0%} ({obs_n} origins)  "
            f"null mean {null.mean():.0%}  p={p:.4f}  {'***' if p < 0.05 else ''}"
        )
    print()


run(["1w"], "Weekly     ")
run(["1d"], "Daily      ")
run(["1w", "1d"], "Pooled W+D ")
