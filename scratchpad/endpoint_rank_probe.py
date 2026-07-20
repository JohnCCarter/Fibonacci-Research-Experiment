"""Endpoint-selection-given-origin RANK probe (advisor-reordered 2026-07-01).

Chamoun's words: swing extreme (1) -> the *next fresh* impulse endpoint (0). Decompose selection
into origin-selection vs endpoint-given-origin, and probe the endpoint half first — it is the one
branch that is structurally NEITHER prominence NOR cleanliness (his "next fresh low/high" = a
recency / fresh-break rule, not max-magnitude), so after three definitional nulls it is the angle
that can actually surprise.

Given his ORIGIN (anchor a), enumerate candidate endpoints = fine extrema of the endpoint kind
within a forward horizon H. Where does his "0" (anchor b) RANK among them?
  - magnitude : deepest low / highest high first  (the prominence-like ordering)
  - recency   : earliest first                     (raw "next")
  - fresh-seq : position in the running-extreme sequence (1 = first fresh break, len = deepest/last)
THE honest test conditions on his own fresh-break rule: among his fresh breaks only, does he pick
the deepest / first MORE than a random fresh pick (p_i = 1/n_fresh_i)? Anything vs 1/n_all leaks the
definitional fresh-break admissibility in as fake lift (trap #4 this session).

Cleanliness is deliberately NOT used here (it is his rule verbatim; keeping it out of the ranker
keeps this non-circular). Split by continuation-origin flag so a major-swing-dominated aggregate
can't hide a continuation hole. Descriptive only — no edge / PnL claim.
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
BTOL = 4  # his "0" snaps to a fine extreme within this many bars (his acceptance bar)
HPCT = 90  # horizon H = his 90th-pct leg duration (locked to facit so it rarely drops his own "0")


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


def candidate_endpoints(tf, direc, ia, horizon):
    """Fine extrema of the endpoint kind in (ia, ia+H]; for a down leg endpoints are fine lows."""
    c = CTX[tf]
    kind = c["fine_lows"] if direc == "down" else c["fine_highs"]
    return kind[(kind > ia) & (kind <= ia + horizon)]


def ranks_for(tf, direc, ia, ends, his_end):
    """His endpoint's rank (1-based) among `ends` under three orderings, plus fresh-seq details."""
    c = CTX[tf]
    px = c["low"] if direc == "down" else c["high"]

    # magnitude: deepest low / highest high first
    key_mag = px[ends] if direc == "down" else -px[ends]  # ascending -> deepest/highest first
    order_mag = ends[np.argsort(key_mag, kind="stable")]
    rank_mag = int(np.where(order_mag == his_end)[0][0]) + 1

    # recency: earliest first
    order_rec = ends[np.argsort(ends, kind="stable")]
    rank_rec = int(np.where(order_rec == his_end)[0][0]) + 1

    # fresh-seq: running-extreme lows/highs in bar order (each sets a new min/max since origin)
    fresh, run = [], None
    for e in sorted(ends.tolist()):
        v = px[e]
        if run is None or (v < run if direc == "down" else v > run):
            fresh.append(e)
            run = v
    his_is_fresh = his_end in fresh
    # recency-among-fresh (1 = his "0" is the FIRST fresh break); depth-among-fresh (1 = deepest).
    rank_fresh_rec = (fresh.index(his_end) + 1) if his_is_fresh else None
    n_fresh = len(fresh)
    if his_is_fresh:
        fkey = px[np.array(fresh)] if direc == "down" else -px[np.array(fresh)]
        order_fd = np.array(fresh)[np.argsort(fkey, kind="stable")]
        rank_fresh_depth = int(np.where(order_fd == his_end)[0][0]) + 1
    else:
        rank_fresh_depth = None
    return (rank_mag, rank_rec, len(ends), his_is_fresh, rank_fresh_rec, rank_fresh_depth, n_fresh)


def pb_test(hits, pvec):
    """Poisson-binomial one-sided test: is the rank-1 count above chance when each fresh leg picks
    uniformly at random among its own fresh breaks (p_i = 1/n_fresh_i)? Exact null mean/var, normal
    z-approx (cheaper + no seed vs 20k perms; advisor-approved). Isolates any depth/recency selector
    BEYOND the definitional fresh-break admissibility."""
    p = np.asarray(pvec, dtype=float)
    obs = float(np.sum(hits))
    exp = float(np.sum(p))
    var = float(np.sum(p * (1 - p)))
    z = (obs - exp) / np.sqrt(var) if var > 0 else float("nan")
    # one-sided normal survival (upper tail), no scipy dep
    p_one = 0.5 * (1 - math.erf(z / math.sqrt(2))) if var > 0 else float("nan")
    return obs, exp, z, p_one


print(
    "ENDPOINT-GIVEN-ORIGIN rank probe — is his '0' the NEXT-FRESH extreme, the DEEPEST, or neither?"
)  # noqa: E501
print(f"fine fractal_n=1; his '0' snap tol={BTOL}b; horizon H=p{HPCT} of his durations\n")

for tf in CACHE:
    legs = load_facit(tf)
    if not legs:
        continue
    durs = [abs(bar_of(tf, b["time"]) - bar_of(tf, a["time"])) for _, a, b in legs]
    horizon = int(max(2, np.percentile(durs, HPCT)))

    rows = []  # (cont, rank_mag, rank_rec, n_ends, his_is_fresh, rank_fresh, n_fresh)
    n_excl = 0
    for direc, a, b in legs:
        ia, ib = bar_of(tf, a["time"]), bar_of(tf, b["time"])
        ends = candidate_endpoints(tf, direc, ia, horizon)
        if len(ends) == 0:
            n_excl += 1
            continue
        his_end = int(ends[np.argmin(np.abs(ends - ib))])
        if abs(his_end - ib) > BTOL:  # his "0" is not near any candidate endpoint in-window
            n_excl += 1
            continue
        cont = ia not in CTX[tf]["piv_bars"]
        rows.append((cont, *ranks_for(tf, direc, ia, ends, his_end)))

    if not rows:
        print(f"[{tf}] no usable legs\n")
        continue

    def block(sub, label):
        if not sub:
            print(f"   {label:11s} (n=0)")
            return
        n_ends = np.mean([r[3] for r in sub])
        fresh_rate = np.mean([r[4] for r in sub])
        n_fresh = np.mean([r[7] for r in sub])
        # THE honest test: among his fresh breaks only (his rule's admissible set), does he pick the
        # deepest / first MORE than a random fresh pick? Baseline p_i = 1/n_fresh_i (not 1/n_all).
        fresh_legs = [r for r in sub if r[4]]
        pvec = [1.0 / r[7] for r in fresh_legs]
        hit_depth = [1 if r[6] == 1 else 0 for r in fresh_legs]
        hit_rec = [1 if r[5] == 1 else 0 for r in fresh_legs]
        _, exp_d, z_d, p_d = pb_test(hit_depth, pvec)
        _, exp_r, z_r, p_r = pb_test(hit_rec, pvec)
        nf = max(1, len(fresh_legs))
        null_d, null_r = exp_d / nf, exp_r / nf
        obs_d, obs_r = np.mean(hit_depth), np.mean(hit_rec)
        print(
            f"   {label:11s} n={len(sub):2d}  cand/leg={n_ends:4.1f}  "
            f"his-'0'-is-fresh-break {fresh_rate:.0%} (fresh/leg={n_fresh:.1f})\n"
            f"      among-fresh  deepest {obs_d:.0%} vs null {null_d:.0%} z={z_d:+.2f} p={p_d:.3f}"
            f"   |   first {obs_r:.0%} vs null {null_r:.0%} z={z_r:+.2f} p={p_r:.3f}"
        )

    print(f"[{tf}]  {len(rows)} usable legs  ({n_excl} excluded: '0' outside H)  H={horizon}b")
    block(rows, "ALL")
    block([r for r in rows if not r[0]], "major-swing")
    block([r for r in rows if r[0]], "continuation")
    print()
