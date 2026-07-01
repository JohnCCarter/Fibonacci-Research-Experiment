"""Structure-context as a SELECTION signal on the COMMITTED facit corpus (descriptive, no edge).

Advisor-shaped (2026-07-01):
  - Use the repo's OWN canonical, already-tested feature `core.structure.structure_alignment`
    (BOS/CHoCH is its coarse discrete form) — not a hand-rolled re-encoding.
  - PRIMARY = committed M/W/D facit (1M+1w+1d ≈ 113 fibs), the north-star deliberate-selection
    regime; 4h is CONTEXT only (denser / more mechanical) and cannot override the M/W/D read.
  - NULL must be PROMINENCE-MATCHED, not a raw pivot null: prominence and structure-alignment are
    correlated (big swings sit in trends), so a raw null could just re-capture the prominence signal
    that ALREADY survived (Stage-1). Report BOTH nulls; the prominence-matched one is the verdict.
  - Origin = anchor_a (ratio 1.0), exact time+price. Scope to origins that ARE detected pivots
    (structure-context is silent on non-pivot / continuation-mode origins) — report the excluded N.

Prior (Stage-1, 4h, powered): structure_alignment + prominence → `no_pivot_signal_above_prominence`
(lift +0.023, CI incl 0). So the expected result here is a POWERED NULL CONFIRMATION in the M/W/D
regime Stage-1 lacked. A surprise would be structure-alignment separating from prominence at M/W/D.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.core.structure import structure_alignment
from fibengine.pivots.detect import detect_pivots

SEED = 20260701
B = 20000
SNAP_TOL = 1  # bars: exact anchor time should hit a bar; allow +/-1 for alignment noise
QBINS = 4  # prominence quantile bins for the matched null (locked, minimal DoF)
SETTINGS = load_settings()  # canonical settings.yaml: pivots lookback=3, scoring.structure_window=6
WINDOW = SETTINGS.scoring.structure_window  # = 6
FACIT = Path("data/labels/human_fib/bitfinex/BTC-USD")
CACHE = {
    "1M": "data/raw/bitfinex/BTC-USD/1M/limit_500.csv",
    "1w": "data/raw/bitfinex/BTC-USD/1w/limit_1000.csv",
    "1d": "data/raw/bitfinex/BTC-USD/1d/limit_3500.csv",
    "4h": "data/raw/bitfinex/BTC-USD/4h/limit_20000.csv",
}
GOOD_SOURCE = {"manual_labeling_tool", "manual_screenshot_transcription_reviewed"}


def load_origins(tf):
    """Committed facit → (fib_id, direction, kind, a_time, a_price, b_time, b_price) tuples."""
    out = []
    for fp in sorted((FACIT / tf).glob("fib_*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if d.get("created_by") != "human" or d.get("source") not in GOOD_SOURCE:
            continue
        a, b = d["anchor_a"], d["anchor_b"]  # a = ratio 1.0 origin, b = ratio 0.0 reached
        direc = d["direction"]
        kind = "high" if direc == "down" else "low"
        out.append(
            (
                d["fib_id"],
                direc,
                kind,
                pd.Timestamp(a["time"]),
                float(a["price"]),
                pd.Timestamp(b["time"]),
                float(b["price"]),
            )
        )
    return out


def facit_move_thresholds(tf):
    """Neutral plausible-origin thresholds LOCKED to his facit at this tf: M = median drawn-move
    fraction |a-b|/max(a,b); H = median duration in bars. A 'plausible origin' = any same-kind pivot
    whose forward move over H bars is >= M (a swing that launches a his-sized leg), so the null is
    'among plausible origins', not all pivots."""
    df = CTX[tf]["df"]
    fracs, durs = [], []
    for _fid, _direc, _kind, ta, pa, tb, pb in load_origins(tf):
        fracs.append(abs(pa - pb) / max(pa, pb))
        ia = df.index.get_indexer([ta], method="nearest")[0]
        ib = df.index.get_indexer([tb], method="nearest")[0]
        durs.append(abs(ib - ia))
    return float(np.median(fracs)), int(max(1, np.median(durs)))


CTX = {}
for tf, path in CACHE.items():
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    piv = detect_pivots(df, SETTINGS.pivots)
    # per-pivot structure_alignment (direction implied by kind: high->down origin, low->up)
    align = {}
    prom = {}
    idx_by_kind = {"high": [], "low": []}
    for p in piv:
        d = "down" if p.kind == "high" else "up"
        align[p.index] = structure_alignment(piv, p.index, WINDOW, d)
        prom[p.index] = p.prominence
        idx_by_kind[p.kind].append(p.index)
    # prominence quantile bin per (kind, pivot index)
    binof = {}
    for _kind, idxs in idx_by_kind.items():
        if len(idxs) >= QBINS:
            proms = np.array([prom[i] for i in idxs])
            edges = np.quantile(proms, np.linspace(0, 1, QBINS + 1)[1:-1])
            for i in idxs:
                binof[i] = int(np.digitize(prom[i], edges))
        else:
            for i in idxs:
                binof[i] = 0
    CTX[tf] = {
        "df": df,
        "piv_index": {p.index: p for p in piv},
        "align": align,
        "prom": prom,
        "idx_by_kind": idx_by_kind,
        "binof": binof,
    }

# plausible-origin flag per pivot (forward move >= his median facit move over his median duration).
# Advisor's discriminating check: restrict the null to swings that launch a his-size leg, so we ask
# 'among plausible origins does he prefer low-alignment ones', not the ~definitional 'fib origins
# are trend-terminating vs random mid-trend pivots'.
for tf in CACHE:
    df = CTX[tf]["df"]
    hi = df["high"].to_numpy()
    lo = df["low"].to_numpy()
    n = len(df)
    m_frac, h_bars = facit_move_thresholds(tf)
    plausible = set()  # forward move >= M (advisor v1: leaves backward move unconstrained)
    plausible2 = set()  # TWO-SIDED: backward AND forward move >= M (advisor v2: drawable reversals)
    for kind, idxs in CTX[tf]["idx_by_kind"].items():
        for i in idxs:
            end = min(n, i + h_bars + 1)
            start = max(0, i - h_bars)
            if end <= i + 1 or start >= i:
                continue
            if kind == "high":
                fwd = (hi[i] - lo[i + 1 : end].min()) / hi[i]  # drop after
                bwd = (hi[i] - lo[start:i].min()) / hi[i]  # rise into the high
            else:
                fwd = (hi[i + 1 : end].max() - lo[i]) / lo[i]  # rise after
                bwd = (hi[start:i].max() - lo[i]) / lo[i]  # drop into the low
            if fwd >= m_frac:
                plausible.add(i)
            if fwd >= m_frac and bwd >= m_frac:
                plausible2.add(i)
    CTX[tf]["plausible"] = plausible
    CTX[tf]["plausible2"] = plausible2
    CTX[tf]["thr"] = (m_frac, h_bars)


def snap_to_pivot(tf, kind, t0):
    """Map an origin anchor time to a DETECTED pivot bar of `kind` within +/-SNAP_TOL; else None."""
    df = CTX[tf]["df"]
    pos = df.index.get_indexer([t0], method="nearest")[0]
    if pos < 0:
        return None
    piv_set = set(CTX[tf]["idx_by_kind"][kind])
    for d in range(SNAP_TOL + 1):
        for cand in {pos - d, pos + d} if d else {pos}:
            if cand in piv_set:
                return cand
    return None


rng = np.random.default_rng(SEED)


def collect(tfs, use_b=False):
    """Swing anchors → per-anchor (tf, kind, j=pivot index) + counts. use_b picks anchor_b (reached,
    OPPOSITE kind) instead of anchor_a (origin)."""
    anchors = []
    n_total = n_swing = 0
    for tf in tfs:
        for _fid, _direc, kind, ta, _pa, tb, _pb in load_origins(tf):
            n_total += 1
            k = ({"high": "low", "low": "high"}[kind]) if use_b else kind
            j = snap_to_pivot(tf, k, tb if use_b else ta)
            if j is not None:
                n_swing += 1
                anchors.append((tf, k, j))
    return anchors, n_total, n_swing


def perm(anchors, matched, defined_only=False, plausible_only=False, caliper=None, two_sided=False):
    """Permutation mean-alignment null. matched → draw within same prom-quantile-bin;
    caliper (float) → draw within |prom-prom_anchor|<=caliper instead (tighter prom match);
    defined_only → drop 0.5-fallback both sides; plausible_only → null from plausible pivots
    (two_sided → the TWO-SIDED plausible set: other drawable reversal extremes — the real check).
    Returns (obs, null_mean, p_high, p_low, n) or None if too few defined anchors."""
    kept = []
    for tf, kind, j in anchors:
        a = CTX[tf]["align"][j]
        if defined_only and a == 0.5:
            continue
        kept.append((tf, kind, j, a, CTX[tf]["prom"][j], CTX[tf]["binof"][j]))
    if len(kept) < 3:
        return None
    obs = np.mean([a for *_, a, _p, _b in kept])
    pkey = "plausible2" if two_sided else "plausible"
    pools = []
    for tf, kind, _j, a, prom_a, b in kept:
        idxs = CTX[tf]["idx_by_kind"][kind]
        if plausible_only:
            idxs = [i for i in idxs if i in CTX[tf][pkey]]
        if caliper is not None:
            idxs = [i for i in idxs if abs(CTX[tf]["prom"][i] - prom_a) <= caliper]
        elif matched:
            idxs = [i for i in idxs if CTX[tf]["binof"][i] == b]
        vals = [CTX[tf]["align"][i] for i in idxs]
        if defined_only:
            vals = [v for v in vals if v != 0.5]
        pools.append(vals if vals else [a])  # degenerate guard
    null = np.zeros(B)
    for k in range(B):
        null[k] = np.mean([pool[rng.integers(len(pool))] for pool in pools])
    p_high = (np.sum(null >= obs) + 1) / (B + 1)
    p_low = (np.sum(null <= obs) + 1) / (B + 1)
    return obs, null.mean(), p_high, p_low, len(kept)


def _line(tag, res):
    if res is None:
        print(f"  {tag}: too few defined anchors")
        return
    obs, nmean, p_high, p_low, nu = res
    star = "***" if min(p_high, p_low) < 0.05 else ""
    print(
        f"  {tag}: obs {obs:.3f}  null {nmean:.3f}  "
        f"p(hi)={p_high:.4f}  p(lo)={p_low:.4f}  n={nu}  {star}"
    )


def report(label, tfs, use_b=False):
    anchors, n_total, n_swing = collect(tfs, use_b)
    print(
        f"[{label}]  swing-anchors {n_swing}/{n_total}  (non-pivot excluded: {n_total - n_swing})"
    )
    if n_swing < 3:
        print("  too few swing-anchors to test\n")
        return
    _line("raw null              ", perm(anchors, False, False, False))
    _line("prom-q4               ", perm(anchors, True, False, False))
    _line("prom-q4 + 1side-plaus ", perm(anchors, True, True, True))
    # caliper tightness (residual-prominence leakage check — effect is not local prominence)
    _line("prom-caliper<=0.5     ", perm(anchors, False, False, False, caliper=0.5))
    # DECISIVE (advisor): two-sided plausible null = other DRAWABLE reversal extremes (backward AND
    # forward move >= his median). If the gap collapses here, the low-align is the trend-termination
    # tautology (every fib anchor bounds a real move), not a selection preference among candidates.
    _line("TWO-SIDED plausible   ", perm(anchors, False, False, True, two_sided=True))
    _line("TWO-SIDED + defined   ", perm(anchors, False, True, True, two_sided=True))
    print()


print(f"structure_alignment SELECTION test  window={WINDOW}  B={B}  seed={SEED}  Qbins={QBINS}")
print("PRIMARY = committed M/W/D; 4h = context. Verdict = prominence-matched null.\n")
report("PRIMARY  M/W/D pooled  (anchor_a = ORIGIN)", ["1M", "1w", "1d"])
report("  1M", ["1M"])
report("  1w", ["1w"])
report("  1d", ["1d"])
report("CONTEXT  4h", ["4h"])
print("=== a-vs-b reconciliation: same test on anchor_b (REACHED) — Stage-1 pooled a+b ===\n")
report("REACHED  M/W/D pooled  (anchor_b)", ["1M", "1w", "1d"], use_b=True)
report("CONTEXT  4h  (anchor_b)", ["4h"], use_b=True)
