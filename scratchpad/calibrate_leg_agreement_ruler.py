"""Pre-lock instrument calibration for the leg-agreement ruler (selector-independent, read-only).

Sets the ruler's three knobs from the DATA, not a guess: aggregator AGG in {mean,min,product}, the
tolerance form (absolute bars vs relative to leg length), and the window W. Each maximizes
AUC(coverage-ceiling vs random-null) on the 4h facit — pure instrument design, no learned/heuristic
selector involved, so it cannot be result-tuning. Also reports inter-pivot spacing to bound W.

A leg = (high-bar, low-bar); direction derived from bar order. leg_agreement compares facit vs a
candidate leg by per-endpoint bar distance with decay, direction-gated. No facit is written.
"""

from __future__ import annotations

import glob
import json
import os
import random

import numpy as np

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.pivots.detect import detect_pivots

random.seed(20260629)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIBS = sorted(glob.glob(f"{ROOT}/data/labels/human_fib/bitfinex/BTC-USD/4h/fib_*.json"))

settings = load_settings(f"{ROOT}/config/settings.expansion.yaml")
cfg = settings.data.model_copy(
    update={"exchange": "bitfinex", "symbol": "BTC/USD", "timeframe": "4h"}
)
df = load_candles(cfg, fetch_if_missing=False)
ts_to_i = {ts: i for i, ts in enumerate(df.index)}

pivots = detect_pivots(df, settings.pivots)
high_idx = np.array([p.index for p in pivots if p.kind == "high"])
low_idx = np.array([p.index for p in pivots if p.kind == "low"])

# --- facit legs as (high-bar, low-bar) -------------------------------------------------------
legs: list[tuple[int, int]] = []
skipped = 0
for path in FIBS:
    d = json.load(open(path))
    a, b = d["anchor_a"], d["anchor_b"]
    hi, lo = (a, b) if a["price"] >= b["price"] else (b, a)
    import pandas as pd

    ti = ts_to_i.get(pd.Timestamp(hi["time"]))
    tj = ts_to_i.get(pd.Timestamp(lo["time"]))
    if ti is None or tj is None:
        skipped += 1
        continue
    legs.append((ti, tj))


def direction(h: int, low: int) -> str:
    return "down" if h < low else "up"  # high earlier -> down


def score(
    dh: int, dl: int, fdir: str, cdir: str, *, w: float, rel: bool, agg: str, leg_bars: int
) -> float:
    if fdir != cdir:
        return 0.0
    if rel:
        denom = max(1, leg_bars)
        sh = max(0.0, 1 - (dh / denom) / w)
        sl = max(0.0, 1 - (dl / denom) / w)
    else:
        sh = max(0.0, 1 - dh / w)
        sl = max(0.0, 1 - dl / w)
    if agg == "mean":
        return (sh + sl) / 2
    if agg == "min":
        return min(sh, sl)
    return sh * sl


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """Exact tie-aware AUC = P(pos>neg) + 0.5 P(pos==neg)."""
    neg_sorted = np.sort(neg)
    lt = np.searchsorted(neg_sorted, pos, side="left")
    le = np.searchsorted(neg_sorted, pos, side="right")
    return float((lt + 0.5 * (le - lt)).sum() / (len(pos) * len(neg)))


# --- per-leg ceiling (nearest same-role pivot) + random null -----------------------------------
def nearest(idx_arr: np.ndarray, bar: int) -> tuple[int, int]:
    j = int(np.argmin(np.abs(idx_arr - bar)))
    return int(idx_arr[j]), int(abs(idx_arr[j] - bar))


N_NULL = 50
ceil_legs, null_legs = [], []  # (dh, dl, fdir, cdir, leg_bars)
for fh, fl in legs:
    fdir = direction(fh, fl)
    leg_bars = abs(fh - fl)
    ch, dh = nearest(high_idx, fh)
    cl, dl = nearest(low_idx, fl)
    ceil_legs.append((dh, dl, fdir, direction(ch, cl), leg_bars))
    for _ in range(N_NULL):
        rh = int(random.choice(high_idx))
        rl = int(random.choice(low_idx))
        null_legs.append((abs(rh - fh), abs(rl - fl), fdir, direction(rh, rl), leg_bars))


# --- sweep AGG x tolerance-form x W -> AUC(ceiling vs null) ------------------------------------
GRID = [("abs", w) for w in (1, 2, 3, 5)] + [("rel", r) for r in (0.02, 0.05, 0.1, 0.2)]
print(
    f"4h facit legs: {len(legs)} (skipped {skipped})  pivots: {len(pivots)} "
    f"(highs {len(high_idx)}, lows {len(low_idx)})"
)
spacing = np.diff(np.sort(np.concatenate([high_idx, low_idx])))
print(
    f"inter-pivot spacing (bars): median={np.median(spacing):.1f} "
    f"p10={np.percentile(spacing, 10):.1f} p90={np.percentile(spacing, 90):.1f}"
)
print(f"null pairs: {len(null_legs)}\n")
print(f"{'agg':8s} {'form':4s} {'W':>5s} {'AUC':>6s} {'ceil_med':>9s} {'null_med':>9s}")

best = None
for agg in ("mean", "min", "product"):
    for form, w in GRID:
        rel = form == "rel"
        cs = np.array([score(*c[:4], w=w, rel=rel, agg=agg, leg_bars=c[4]) for c in ceil_legs])
        ns = np.array([score(*n[:4], w=w, rel=rel, agg=agg, leg_bars=n[4]) for n in null_legs])
        a = auc(cs, ns)
        tag = f"{agg:8s} {form:4s} {w:>5} {a:>6.3f} {np.median(cs):>9.3f} {np.median(ns):>9.3f}"
        print(tag)
        if best is None or a > best[0]:
            best = (a, agg, form, w)

print(f"\nBEST: AUC={best[0]:.3f}  agg={best[1]}  form={best[2]}  W={best[3]}")
