"""Origin-selection RANK probe — the CRUX (advisor-guarded 2026-07-01). Mirror of endpoint probe.

Question: given his impulse ending at "0" (anchor b), which fine extremum did he anchor "1" (origin,
anchor a) to, among the plausible origins? For a down leg the origin is a fine HIGH the impulse
retraced from; walking backward from "0", fine highs form a backward-running-max sequence (each
higher than everything to its right up to "0") = the swing highs the fall came from. His origin
should be one.

PRE-REGISTERED GUARDS (locked before looking at output — advisor):
 (1) NEUTRAL orderings, no recency-flip pre-commitment. Rank his origin among backward-fresh extrema
     by HEIGHT (most extreme first = prominence-like) and by RECENCY (closest to "0" first =
     last-push). Prior (four prior probes): prominence/height wins for major-swing; continuation
     underpowered. Recency must BEAT that prior, not confirm the tidy HO-B (n=1) symmetry story.
 (2) Continuation is the cell that matters and is underpowered (endpoint-continuation was p=0.35 at
     n=20). POOL continuation across TFs for power; report per-TF too. A z~+0.8 p~0.3 continuation
     result is "INCONCLUSIVE, n too small" — NOT "trends the right way".
 (3) origin-is-backward-fresh-high will be ~100% (his rule verbatim) = admissibility, a precision
     lever, NOT signal. The fresh-conditioned rank (null = random backward-fresh pick,
     p_i=1/n_fresh_i) is THE test. Anything vs 1/n_all leaks the definitional admissibility as fake
     lift (trap #4 this session).

Launch magnitude/cleanliness are deliberately NOT used as orderings (his rule verbatim + circular
with the leg). This probe conditions the origin on his endpoint, so it characterizes leg geometry
GIVEN an anchor — not the unconditioned "which leg with nothing given" (the ultimate bottleneck).
Descriptive, no edge / PnL claim.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.pivots.detect import detect_pivots

SETTINGS = load_settings()
FACIT = Path("data/labels/human_fib/bitfinex/BTC-USD")
CACHE = {
    "1M": "data/raw/bitfinex/BTC-USD/1M/limit_500.csv",
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
}
GOOD_SOURCE = {"manual_labeling_tool", "manual_screenshot_transcription_reviewed"}
ATOL = 2  # origin must land: his "1" snaps to a fine extreme within this many bars
HPCT = 90  # backward horizon H = his 90th-pct leg duration (locked to facit)


def load_facit(tf):
    out = []
    for fp in sorted((FACIT / tf).glob("fib_*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if d.get("created_by") != "human" or d.get("source") not in GOOD_SOURCE:
            continue
        out.append((d["direction"], d["anchor_a"], d["anchor_b"]))
    return out


def fine_extrema(high, low):
    n = len(high)
    highs, lows = [], []
    for i in range(1, n - 1):
        if high[i] >= high[i - 1] and high[i] >= high[i + 1]:
            highs.append(i)
        if low[i] <= low[i - 1] and low[i] <= low[i + 1]:
            lows.append(i)
    return np.array(highs), np.array(lows)


CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    piv = detect_pivots(df, SETTINGS.pivots)
    high_a, low_a = df["high"].to_numpy(), df["low"].to_numpy()
    fh, fl = fine_extrema(high_a, low_a)
    CTX[tf] = {
        "df": df,
        "high": high_a,
        "low": low_a,
        "piv_bars": {p.index for p in piv},
        "fine_highs": fh,
        "fine_lows": fl,
    }


def bar_of(tf, t):
    return int(CTX[tf]["df"].index.get_indexer([pd.Timestamp(t)], method="nearest")[0])


def backward_fresh(tf, direc, ib, horizon):
    """Backward-running-extreme sequence from his '0' (ib), closest-to-ib FIRST. For a down leg:
    fine highs in [ib-H, ib) that set a new running MAX walking backward (higher than all highs to
    their right up to ib) = the swing highs the fall retraced from. Up: fine lows, running min."""
    c = CTX[tf]
    if direc == "down":
        cand, px, better = c["fine_highs"], c["high"], (lambda v, r: v > r)
    else:
        cand, px, better = c["fine_lows"], c["low"], (lambda v, r: v < r)
    win = cand[(cand >= ib - horizon) & (cand < ib)]
    bars = sorted(win.tolist(), reverse=True)  # nearest to ib first (walk backward)
    fresh, run = [], None
    for e in bars:
        v = px[e]
        if run is None or better(v, run):
            fresh.append(e)
            run = v
    return fresh, px


def rank_origin(fresh, px, direc, his_origin):
    """His origin's rank among backward-fresh extrema by HEIGHT (most extreme first) and RECENCY
    (closest to '0' first). Returns (is_fresh, rank_height, rank_recency, n_fresh)."""
    if his_origin not in fresh:
        return False, None, None, len(fresh)
    # recency: fresh is already closest-to-'0' first
    rank_rec = fresh.index(his_origin) + 1
    # height: most extreme first (highest high for down, lowest low for up)
    key = px[np.array(fresh)] if direc == "down" else -px[np.array(fresh)]
    order = np.array(fresh)[np.argsort(-key, kind="stable")]  # descending extremeness
    rank_h = int(np.where(order == his_origin)[0][0]) + 1
    return True, rank_h, rank_rec, len(fresh)


def pb_test(hits, pvec):
    """Poisson-binomial one-sided test: is the rank-1 count above chance when each fresh leg picks
    uniformly among its own backward-fresh extrema (p_i = 1/n_fresh_i)? Exact null mean/var, normal
    z-approx. Isolates any height/recency selector BEYOND the definitional fresh admissibility."""
    p = np.asarray(pvec, dtype=float)
    if len(p) == 0:
        return 0.0, 0.0, float("nan"), float("nan")
    obs, exp = float(np.sum(hits)), float(np.sum(p))
    var = float(np.sum(p * (1 - p)))
    z = (obs - exp) / math.sqrt(var) if var > 0 else float("nan")
    p_one = 0.5 * (1 - math.erf(z / math.sqrt(2))) if var > 0 else float("nan")
    return obs, exp, z, p_one


def report(sub, label):
    """sub = list of (rank_height, rank_recency, n_fresh) for FRESH-admissible legs only."""
    if not sub:
        print(f"   {label:22s} n=0")
        return
    pvec = [1.0 / r[2] for r in sub]
    hit_h = [1 if r[0] == 1 else 0 for r in sub]
    hit_r = [1 if r[1] == 1 else 0 for r in sub]
    _, exp_h, z_h, p_h = pb_test(hit_h, pvec)
    _, exp_r, z_r, p_r = pb_test(hit_r, pvec)
    nf = len(sub)
    print(
        f"   {label:22s} n={nf:2d}  fresh/leg={np.mean([r[2] for r in sub]):4.1f}\n"
        f"      most-extreme {np.mean(hit_h):.0%} vs null {exp_h / nf:.0%} z={z_h:+.2f} p={p_h:.3f}"
        f"   |   last-push {np.mean(hit_r):.0%} vs null {exp_r / nf:.0%} z={z_r:+.2f} p={p_r:.3f}"
    )


print("ORIGIN-SELECTION rank probe (CRUX) — his '1' = MOST-EXTREME or LAST-PUSH backward extreme?")
print(f"fine fractal_n=1; origin snap tol={ATOL}b; backward horizon H=p{HPCT} of his durations\n")

pool_cont = []  # (rank_height, rank_recency, n_fresh) across all TFs, continuation origins only
for tf in CACHE:
    legs = load_facit(tf)
    if not legs:
        continue
    durs = [abs(bar_of(tf, b["time"]) - bar_of(tf, a["time"])) for _, a, b in legs]
    horizon = int(max(2, np.percentile(durs, HPCT)))

    rows_major, rows_cont, n_notfresh, n_excl = [], [], 0, 0
    for direc, a, b in legs:
        ia, ib = bar_of(tf, a["time"]), bar_of(tf, b["time"])
        fresh, px = backward_fresh(tf, direc, ib, horizon)
        cand = CTX[tf]["fine_highs"] if direc == "down" else CTX[tf]["fine_lows"]
        near = cand[(np.abs(cand - ia) <= ATOL)]
        if len(near) == 0:  # his "1" is not on a fine extremum in-scale — outside this test
            n_excl += 1
            continue
        his_origin = int(near[np.argmin(np.abs(near - ia))])
        is_fresh, rk_h, rk_r, nf = rank_origin(fresh, px, direc, his_origin)
        if not is_fresh:
            n_notfresh += 1
            continue
        cont = ia not in CTX[tf]["piv_bars"]
        (rows_cont if cont else rows_major).append((rk_h, rk_r, nf))
        if cont:
            pool_cont.append((rk_h, rk_r, nf))

    n_ok = len(rows_major) + len(rows_cont)
    fresh_rate = n_ok / max(1, n_ok + n_notfresh)
    print(
        f"[{tf}]  H={horizon}b  origin-is-backward-fresh-high {fresh_rate:.0%} "
        f"({n_notfresh} not-fresh, {n_excl} origin off-scale)"
    )
    report(rows_major + rows_cont, "ALL")
    report(rows_major, "major-swing")
    report(rows_cont, "continuation")
    print()

print("POOLED continuation (across 1M+1w+1d) — the power-buy for the cell that matters (guard 2):")
report(pool_cont, "continuation-pooled")
