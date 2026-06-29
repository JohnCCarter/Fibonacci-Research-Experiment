"""Confirm `ruler_usable` with the COMMITTED leg-agreement module (post-lock build step).

Imports the locked metric (`leg_agreement`, `auc`, `Leg`, `W_LOCKED`) — not the calibration copy —
runs the synthetic sanity table as asserts, then scores the 4h coverage-ceiling vs the random-null
and reports AUC. Read-only, seed-fixed, no facit written. Output goes into the prereg postlock.
"""

from __future__ import annotations

import glob
import json
import os
import random

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.leg_agreement import W_LOCKED, Leg, auc, leg_agreement, leg_agreement_min
from fibengine.pivots.detect import detect_pivots

random.seed(20260629)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- synthetic sanity table (the locked gate-1; selector-independent) ---------
facit = Leg(high_bar=10, low_bar=40)
assert leg_agreement(facit, facit) == 1.0, "identity"
assert 0.0 < leg_agreement(facit, Leg(10, 41)) < 1.0, "off-by-one graded"
assert leg_agreement(facit, Leg(40, 10)) == 0.0, "direction flip"
assert leg_agreement(facit, Leg(100, 130)) == 0.0, "disjoint"
_obo = leg_agreement(facit, Leg(10, 41))
print(f"sanity: PASS  identity=1.0  off-by-one={_obo}  flip=0  disjoint=0  W={W_LOCKED}")

# --- 4h real data: ceiling vs null with the committed metric ------------------
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

legs: list[Leg] = []
for path in FIBS:
    d = json.load(open(path))
    a, b = d["anchor_a"], d["anchor_b"]
    hi, lo = (a, b) if a["price"] >= b["price"] else (b, a)
    ti = ts_to_i.get(pd.Timestamp(hi["time"]))
    tj = ts_to_i.get(pd.Timestamp(lo["time"]))
    if ti is not None and tj is not None and ti != tj:
        legs.append(Leg(high_bar=ti, low_bar=tj))


def nearest(idx_arr: np.ndarray, bar: int) -> int:
    return int(idx_arr[int(np.argmin(np.abs(idx_arr - bar)))])


ceil_scores, ceil_min, null_scores = [], [], []
for leg in legs:
    ch = nearest(high_idx, leg.high_bar)
    cl = nearest(low_idx, leg.low_bar)
    if ch != cl:
        ceil = Leg(high_bar=ch, low_bar=cl)
        ceil_scores.append(leg_agreement(leg, ceil))
        ceil_min.append(leg_agreement_min(leg, ceil))
    for _ in range(50):
        rh, rl = int(random.choice(high_idx)), int(random.choice(low_idx))
        if rh != rl:
            null_scores.append(leg_agreement(leg, Leg(high_bar=rh, low_bar=rl)))

a = auc(ceil_scores, null_scores)
verdict = "ruler_usable" if a >= 0.90 else "ruler_inconclusive"
print(f"4h legs={len(legs)}  ceiling n={len(ceil_scores)}  null n={len(null_scores)}")
print(f"ceiling: mean med={np.median(ceil_scores):.3f}  min-diag med={np.median(ceil_min):.3f}")
print(f"null: median={np.median(null_scores):.3f}")
print(f"AUC(ceiling vs null) = {a:.3f}  -> {verdict}  (threshold 0.90)")
