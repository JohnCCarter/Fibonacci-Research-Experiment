"""Hard-null check for the leg-agreement ruler (leakage-review HIGH finding remediation).

The locked gate scored ceiling vs a RANDOM null — near-tautological (exact-match vs random). The
regime a future selector actually lives in is NEAR-MISS: can the ruler tell the human's pick from a
*plausible-but-wrong* neighbouring pick? This scores ceiling (nearest pivot per endpoint) vs a HARD
null (2nd-nearest pivot per endpoint) with the COMMITTED metric, and characterizes how near-binary
the ruler is at W=2. Read-only, seed-fixed. Output goes into the postlock.
"""

from __future__ import annotations

import glob
import json
import os

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.leg_agreement import Leg, auc, leg_agreement
from fibengine.pivots.detect import detect_pivots

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIBS = sorted(glob.glob(f"{ROOT}/data/labels/human_fib/bitfinex/BTC-USD/4h/fib_*.json"))
settings = load_settings(f"{ROOT}/config/settings.expansion.yaml")
cfg = settings.data.model_copy(
    update={"exchange": "bitfinex", "symbol": "BTC/USD", "timeframe": "4h"}
)
df = load_candles(cfg, fetch_if_missing=False)
ts_to_i = {ts: i for i, ts in enumerate(df.index)}
pivots = detect_pivots(df, settings.pivots)
high_idx = np.sort(np.array([p.index for p in pivots if p.kind == "high"]))
low_idx = np.sort(np.array([p.index for p in pivots if p.kind == "low"]))


def two_nearest(idx_arr: np.ndarray, bar: int) -> tuple[int, int, int]:
    """Return (nearest, second_nearest, dist_of_second) bar indices for `bar`."""
    order = np.argsort(np.abs(idx_arr - bar))
    n0, n1 = int(idx_arr[order[0]]), int(idx_arr[order[1]])
    return n0, n1, int(abs(n1 - bar))


legs = []
for path in FIBS:
    d = json.load(open(path))
    a, b = d["anchor_a"], d["anchor_b"]
    hi, lo = (a, b) if a["price"] >= b["price"] else (b, a)
    ti = ts_to_i.get(pd.Timestamp(hi["time"]))
    tj = ts_to_i.get(pd.Timestamp(lo["time"]))
    if ti is not None and tj is not None and ti != tj:
        legs.append((ti, tj))

ceil_s, hard_s, second_dists = [], [], []
for fh, fl in legs:
    ch0, ch1, dh = two_nearest(high_idx, fh)
    cl0, cl1, dl = two_nearest(low_idx, fl)
    second_dists += [dh, dl]
    facit = Leg(high_bar=fh, low_bar=fl)
    if ch0 != cl0:
        ceil_s.append(leg_agreement(facit, Leg(high_bar=ch0, low_bar=cl0)))
    if ch1 != cl1:
        hard_s.append(leg_agreement(facit, Leg(high_bar=ch1, low_bar=cl1)))

sd = np.array(second_dists)
print(f"4h legs={len(legs)}  ceiling n={len(ceil_s)}  hard-null n={len(hard_s)}")
print(
    f"second-nearest pivot distance (bars): median={np.median(sd):.1f} "
    f"p25={np.percentile(sd, 25):.1f} share<=1bar={(sd <= 1).mean():.1%}"
)
print(f"ceiling score: median={np.median(ceil_s):.3f}  mean={np.mean(ceil_s):.3f}")
print(
    f"hard-null score: median={np.median(hard_s):.3f}  mean={np.mean(hard_s):.3f}  "
    f">0 share={(np.array(hard_s) > 0).mean():.1%}"
)
print(f"AUC(ceiling vs HARD-null 2nd-nearest) = {auc(ceil_s, hard_s):.3f}")
cs = np.array(ceil_s)
b0 = (cs == 0.0).mean()
b50 = ((cs > 0.0) & (cs < 1.0)).mean()
b1 = (cs == 1.0).mean()
print(f"ceiling buckets: =0 {b0:.1%}  in(0,1) {b50:.1%}  =1.0 {b1:.1%}  (sub-1.0 = coverage gap)")
