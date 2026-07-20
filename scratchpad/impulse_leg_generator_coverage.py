"""Chamoun's rule as a candidate GENERATOR, not a ranking feature (advisor-reframed 2026-07-01).

His rule (his words): a fib leg = retracement/swing extreme (1) -> next fresh impulse endpoint (0),
and the leg must be a CLEAN directed impulse (net/path high), not chop. cleanliness (net/path) IS
his rule verbatim, so "his legs cleaner than random" is DEFINITIONAL — not a result.

Non-circular north-star question (step-1 = learn to select meaningful legs): does a clean-impulse
GENERATOR CONTAIN his facit legs, does cleanliness preferentially KEEP his legs vs cutting others,
and does it reach the CONTINUATION-MODE origins (not major pivots) every pivot test missed?

Generator (does NOT depend on major-pivot detection, so it can see continuation origins):
  - fine local extrema (fractal_n=1, no prominence filter) = candidate anchors (incl. mid-trend)
  - candidate leg = fine extreme -> opposite fine extreme within H, magnitude>=M, cleanliness>=C
  - M = his p10 magnitude, H = his p90 duration (locked to his facit so they never cap it); C swept.

Coverage = his leg is generable (both anchors on fine extrema + magnitude>=M + cleanliness>=C),
per his leg (decoupled from horizon), vs candidates/real-fib (precision) as C rises, split out for
continuation origins. Cleanliness is a real GENERATIVE filter only if raising C holds coverage while
slashing candidates.
"""

from __future__ import annotations

import json
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
ATOL = 2  # origin must land: bars
BTOL = 4  # endpoint "0" looser (his acceptance bar): bars
# M and H are LOCKED to his facit so they do NOT cap coverage of his own legs (the first-run bug):
# M = his 10th-percentile magnitude (90% of his legs magnitude-eligible), H = his 90th-pct duration.
MPCT = 10
HPCT = 90
CSWEEP = [0.0, 0.3, 0.5, 0.7, 0.9]


def load_facit(tf):
    out = []
    for fp in sorted((FACIT / tf).glob("fib_*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if d.get("created_by") != "human" or d.get("source") not in GOOD_SOURCE:
            continue
        out.append((d["direction"], d["anchor_a"], d["anchor_b"]))
    return out


def fine_extrema(high, low):
    """fractal_n=1 local highs/lows — finest scale, so continuation-mode extrema are included."""
    n = len(high)
    highs, lows = [], []
    for i in range(1, n - 1):
        if high[i] >= high[i - 1] and high[i] >= high[i + 1]:
            highs.append(i)
        if low[i] <= low[i - 1] and low[i] <= low[i + 1]:
            lows.append(i)
    return np.array(highs), np.array(lows)


def cleanliness(close, i, j):
    seg = close[i : j + 1]
    path = np.abs(np.diff(seg)).sum()
    return abs(seg[-1] - seg[0]) / path if path > 0 else 0.0


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
        "close": df["close"].to_numpy(),
        "piv_bars": {p.index for p in piv},
        "fine_highs": fh,
        "fine_lows": fl,
        "fh_set": set(fh.tolist()),
        "fl_set": set(fl.tolist()),
    }


def bar_of(tf, t):
    return int(CTX[tf]["df"].index.get_indexer([pd.Timestamp(t)], method="nearest")[0])


def near(bar_set, b, tol):
    return any((b + d) in bar_set for d in range(-tol, tol + 1))


def facit_legs(tf):
    """His legs as (dir, a_bar, b_bar, frac, dur, cont_origin, clean, origin_ok, endpoint_ok).
    origin_ok/endpoint_ok = his anchors sit on a fine extremum of the right kind (within tol) — a
    precondition for the generator to ever propose the leg (regardless of magnitude/clean)."""
    c = CTX[tf]
    legs = []
    for direc, a, b in load_facit(tf):
        ia, ib = bar_of(tf, a["time"]), bar_of(tf, b["time"])
        pa, pb = float(a["price"]), float(b["price"])
        frac = abs(pa - pb) / max(pa, pb)
        cont = ia not in c["piv_bars"]
        clean = cleanliness(c["close"], min(ia, ib), max(ia, ib))
        oset, eset = (c["fh_set"], c["fl_set"]) if direc == "down" else (c["fl_set"], c["fh_set"])
        legs.append(
            (
                direc,
                ia,
                ib,
                frac,
                abs(ib - ia),
                cont,
                clean,
                near(oset, ia, ATOL),
                near(eset, ib, BTOL),
            )
        )
    return legs


def n_candidates(tf, m_frac, horizon, cthr):
    """Total candidate legs emitted (magnitude>=M, cleanliness>=C), horizon-bounded for a finite
    count — the PRECISION cost, decoupled from coverage of his own legs."""
    c = CTX[tf]
    hi, lo, close = c["high"], c["low"], c["close"]
    highs, lows = c["fine_highs"], c["fine_lows"]
    total = 0
    for oi in highs:
        ends = lows[(lows > oi) & (lows <= oi + horizon)]
        for ej in ends:
            if (hi[oi] - lo[ej]) / hi[oi] >= m_frac and cleanliness(close, oi, ej) >= cthr:
                total += 1
    for oi in lows:
        ends = highs[(highs > oi) & (highs <= oi + horizon)]
        for ej in ends:
            if (hi[ej] - lo[oi]) / lo[oi] >= m_frac and cleanliness(close, oi, ej) >= cthr:
                total += 1
    return total


print("IMPULSE-LEG GENERATOR coverage — his rule as a PROPOSER, not a ranker")
print(
    f"fine fractal_n=1; ATOL={ATOL} BTOL={BTOL}; M=p{MPCT} mag, H=p{HPCT} dur (locked to facit)\n"
)
for tf in CACHE:
    legs = facit_legs(tf)
    if not legs:
        continue
    m_frac = float(np.percentile([x[3] for x in legs], MPCT))
    horizon = int(max(2, np.percentile([x[4] for x in legs], HPCT)))
    n_cont = sum(1 for x in legs if x[5])
    anchors_ok = np.mean([x[7] and x[8] for x in legs])
    print(
        f"[{tf}]  {len(legs)} facit legs  (continuation-origin: {n_cont})  "
        f"M={m_frac:.0%}  H={horizon}b   his anchors on fine extrema: {anchors_ok:.0%}"
    )
    for cthr in CSWEEP:
        # coverage = his leg is generable: both anchors on fine extrema + magnitude>=M + clean>=C
        cov = [x[7] and x[8] and x[3] >= m_frac and x[6] >= cthr for x in legs]
        cov_all = np.mean(cov)
        cov_cont = np.mean([cov[k] for k, x in enumerate(legs) if x[5]]) if n_cont else float("nan")
        per_fib = n_candidates(tf, m_frac, horizon, cthr) / len(legs)
        print(
            f"   C>={cthr:.1f}: coverage all {cov_all:.0%}  cont {cov_cont:.0%}   "
            f"candidates/fib {per_fib:.1f}"
        )
    print()
