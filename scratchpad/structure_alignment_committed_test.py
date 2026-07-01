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
    """Committed human facit → list of (fib_id, direction, kind, anchor_a_time, anchor_a_price)."""
    out = []
    for fp in sorted((FACIT / tf).glob("fib_*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if d.get("created_by") != "human" or d.get("source") not in GOOD_SOURCE:
            continue
        a = d["anchor_a"]  # ratio 1.0 = origin
        direc = d["direction"]
        kind = "high" if direc == "down" else "low"
        out.append((d["fib_id"], direc, kind, pd.Timestamp(a["time"]), float(a["price"])))
    return out


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


def collect(tfs):
    """Gather swing-origins across tfs → per-origin (tf, kind, bin, obs_align) + bookkeeping."""
    origins = []
    n_total = n_swing = 0
    for tf in tfs:
        for _fid, _direc, kind, t0, _price in load_origins(tf):
            n_total += 1
            j = snap_to_pivot(tf, kind, t0)
            if j is not None:
                n_swing += 1
                origins.append((tf, kind, CTX[tf]["binof"][j], CTX[tf]["align"][j]))
    return origins, n_total, n_swing


def perm(origins, matched, defined_only=False):
    """Permutation mean-alignment null. matched=True → draw within same (tf,kind,prom-bin);
    defined_only=True → drop the neutral 0.5 fallback from BOTH origins and pools (artifact guard).
    Returns (obs_mean, null_mean, p_high, p_low, n_used) or None if too few defined origins."""
    kept = [(tf, kind, b, a) for tf, kind, b, a in origins if not (defined_only and a == 0.5)]
    if len(kept) < 3:
        return None
    obs = np.mean([a for *_, a in kept])
    pools = []
    for tf, kind, b, _a in kept:
        idxs = CTX[tf]["idx_by_kind"][kind]
        if matched:
            idxs = [i for i in idxs if CTX[tf]["binof"][i] == b]
        vals = [CTX[tf]["align"][i] for i in idxs]
        if defined_only:
            vals = [v for v in vals if v != 0.5]
        pools.append(vals if vals else [_a])  # degenerate guard
    null = np.zeros(B)
    for k in range(B):
        null[k] = np.mean([pool[rng.integers(len(pool))] for pool in pools])
    p_high = (np.sum(null >= obs) + 1) / (B + 1)
    p_low = (np.sum(null <= obs) + 1) / (B + 1)
    return obs, null.mean(), p_high, p_low, len(kept)


def report(label, tfs):
    origins, n_total, n_swing = collect(tfs)
    print(
        f"[{label}]  swing-origins {n_swing}/{n_total}  (non-pivot excluded: {n_total - n_swing})"
    )
    if n_swing < 3:
        print("  too few swing-origins to test\n")
        return
    # 0.5-fallback diagnostic: neutral fraction among his origins vs the whole pivot pool
    frac_o = np.mean([a == 0.5 for *_, a in origins])
    allvals = [
        CTX[tf]["align"][i]
        for tf in tfs
        for k in ("high", "low")
        for i in CTX[tf]["idx_by_kind"][k]
    ]
    frac_p = np.mean([v == 0.5 for v in allvals])
    print(f"  neutral(0.5) share: origins {frac_o:.0%}  pivot-pool {frac_p:.0%}")
    rows = (
        (False, False, "raw null       "),
        (True, False, "prom-matched   "),
        (True, True, "prom+defined   "),  # artifact guard: 0.5-fallback removed
    )
    for matched, defined, tag in rows:
        res = perm(origins, matched, defined)
        if res is None:
            print(f"  {tag}: too few defined origins")
            continue
        obs, nmean, p_high, p_low, nu = res
        star = "***" if min(p_high, p_low) < 0.05 else ""
        print(
            f"  {tag}: obs {obs:.3f}  null {nmean:.3f}  "
            f"p(hi)={p_high:.4f}  p(lo)={p_low:.4f}  n={nu}  {star}"
        )
    print()


print(f"structure_alignment SELECTION test  window={WINDOW}  B={B}  seed={SEED}  Qbins={QBINS}")
print("PRIMARY = committed M/W/D; 4h = context. Verdict = prominence-matched null.\n")
report("PRIMARY  M/W/D pooled", ["1M", "1w", "1d"])
report("  1M", ["1M"])
report("  1w", ["1w"])
report("  1d", ["1d"])
report("CONTEXT  4h", ["4h"])
