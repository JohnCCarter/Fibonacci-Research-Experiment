"""Measure the frozen Chamoun structure-engine against the 4h-DOWN human facit corpus.

DECISION GATE: does the engine's origin "sit" out-of-sample within the LOCKED acceptance band?
The engine was calibrated on 1h-DOWN (scratchpad cascade), and the human_fib corpus has NO 1h.
So every 4h-DOWN leg here is genuinely out-of-sample. Chamoun locked this scope 2026-07-02.

=====================  PRE-REGISTRATION (locked BEFORE scoring)  =====================
Do NOT edit these after seeing results (validity: lock-before-test).

1. TEST SET
   All 4h-DOWN base human_fib legs (anchor_a = origin "1" = high, anchor_b = "0" = low) whose
   origin time falls inside the loaded 4h df. Out-of-range legs are DROPPED and logged (not scored).

2. ENGINE PARAMS — time-faithful rescale 1h -> 4h (4x bar duration; keep PHYSICAL time/scale)
   local_scale 72 -> 18 bars   (3 days preserved)
   max_horizon 480 -> 120 bars (20 days preserved)
   min_bars     3 -> 1 bar     (1h's 3h spike-guard < one 4h bar; floor 1 => guard effectively off)
   min_move     0.02 UNCHANGED (a price fraction, TF-independent)
   Pivot detection = settings.expansion.yaml as-is (lookback 3, min_prom_atr 0.5, fractal_n 1);
   NOT re-tuned per TF (a known, logged caveat, not a free parameter).

3. MATCHING RULE
   Engine proposes ALL down-structures on the full 4h df. For each human leg, match the proposal
   whose origin_index is nearest the human origin bar, within +/- local_scale (18 bars). No proposal
   in window => MISS (no-proposal), scored as an origin MISS.

4. SCORING (evaluation.acceptance, accept_at = NEAR)
   origin   = classify_anchor(prop.origin_price, human.a.price, is_origin=True, bars)
   reached  = classify_anchor(prop.reached_price, human.b.price, is_origin=False)  # price-only
   leg      = leg_accepted(origin_tier, endpoint_tier)

5. KNOWN GAPS (note, do NOT tune away)
   - reached "0" = lowest-low vs Chamoun's sustained-low (engine docstring Q2); endpoint's looser
     2/4/6% band partly absorbs it.
   - 4h min_bars guard is off (faithful translation of a sub-bar 1h guard).
=====================================================================================
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.acceptance import (
    ACCEPT_AT,
    MatchTier,
    classify_anchor,
    leg_accepted,
)
from fibengine.pivots.detect import detect_pivots
from fibengine.research.chamoun_structure_engine import StructureConfig, propose_structures

REPO = Path(__file__).resolve().parents[1]
FACIT_DIR = REPO / "data/labels/human_fib/bitfinex/BTC-USD/4h"
CONFIG = "config/settings.expansion.yaml"

# Locked time-faithful rescale (see header §2).
SCALED = StructureConfig(local_scale=18, min_move=0.02, max_horizon=120, min_bars=1)
MATCH_WINDOW = SCALED.local_scale  # §3: match origin within +/- local_scale bars


def load_down_facit() -> list[dict]:
    legs = []
    for p in sorted(FACIT_DIR.glob("fib_*T*.json")):
        if p.stem.endswith("_events"):
            continue
        d = json.loads(p.read_text())
        if d.get("direction") != "down":
            continue
        legs.append(d)
    return legs


def bar_index(df: pd.DataFrame, iso: str) -> int:
    ts = pd.Timestamp(iso)
    return int(df.index.get_indexer([ts], method="nearest")[0])


def main() -> None:
    settings = load_settings(CONFIG)
    data4h = settings.data.model_copy(
        update={
            "timeframe": "4h",
            "timeframe_limits": {**settings.data.timeframe_limits, "4h": 20000},
        }
    )
    df = load_candles(data4h, fetch_if_missing=False)
    pivots = detect_pivots(df, settings.pivots)
    proposals = propose_structures(df, pivots, SCALED)
    lo, hi = df.index[0], df.index[-1]

    print("=== PRE-REGISTERED 4h-DOWN measurement (out-of-sample) ===")
    print(f"df: {len(df)} bars  {str(lo)[:10]} -> {str(hi)[:10]}")
    print(f"engine params: {SCALED}")
    print(f"proposals (all down-structures on df): {len(proposals)}")
    print(f"accept line: {ACCEPT_AT.name}  match window: +/-{MATCH_WINDOW} bars\n")

    facit = load_down_facit()
    prop_idx = [p.origin_index for p in proposals]

    dropped_range = 0
    no_proposal = 0
    rows = []
    for d in facit:
        a, b = d["anchor_a"], d["anchor_b"]
        origin_ts = pd.Timestamp(a["time"])
        if origin_ts < lo or origin_ts > hi:
            dropped_range += 1
            continue
        h_bar = bar_index(df, a["time"])
        # nearest proposal by origin bar within the locked window
        best, best_gap = None, None
        for p, pi in zip(proposals, prop_idx, strict=True):
            gap = abs(pi - h_bar)
            if best_gap is None or gap < best_gap:
                best, best_gap = p, gap
        if best is None or best_gap > MATCH_WINDOW:
            no_proposal += 1
            rows.append(
                ("no-proposal", MatchTier.MISS, MatchTier.MISS, d["fib_id"], a, b, None, best_gap)
            )
            continue
        o_tier = classify_anchor(
            best.origin_price,
            a["price"],
            is_origin=True,
            pred_bar=best.origin_index,
            true_bar=h_bar,
        )
        e_tier = classify_anchor(best.reached_price, b["price"], is_origin=False)
        rows.append(("matched", o_tier, e_tier, d["fib_id"], a, b, best, best_gap))

    total = len(rows)  # every in-range leg is scored (no-proposal counts as origin MISS)
    o_hist = Counter(r[1].name for r in rows)
    e_hist = Counter(r[2].name for r in rows)
    accepted = sum(1 for r in rows if leg_accepted(r[1], r[2]))
    origin_ok = sum(1 for r in rows if r[1] >= ACCEPT_AT)

    matched = total - no_proposal
    print(f"down facit total: {len(facit)}  | dropped out-of-range: {dropped_range}")
    print(f"scored in-range: {total}  | matched: {matched}  no-proposal: {no_proposal}\n")
    print(
        "ORIGIN tiers:  "
        + "  ".join(f"{k}={o_hist.get(k, 0)}" for k in ("EXACT", "SNARLIKT", "NEAR", "MISS"))
    )
    print(
        "REACHED tiers: "
        + "  ".join(f"{k}={e_hist.get(k, 0)}" for k in ("EXACT", "SNARLIKT", "NEAR", "MISS"))
    )
    acc = ACCEPT_AT.name
    if total:
        print(f"\nORIGIN sits (>= {acc}): {origin_ok}/{total} = {origin_ok / total:.0%}")
        print(f"LEG accepted (both >= {acc}): {accepted}/{total} = {accepted / total:.0%}")

    # DIAGNOSIS (post-hoc, changes NO locked number): of matched origin MISSes, how many are
    # "wrong swing" (price beyond NEAR's 2%) vs "right region, bar-units artifact" (price <= 2%
    # but bar offset > ORIGIN.near.max_bars=3). The bar band was locked at 1h scale.
    from fibengine.evaluation.acceptance import ORIGIN, price_pct

    price_miss = bars_only_miss = 0
    origin_ok_price_only = 0
    for kind, ot, _et, _fid, a, _b, p, _gap in rows:
        if kind != "matched":
            continue
        dp = price_pct(p.origin_price, a["price"])
        if dp <= ORIGIN.near.max_price_pct:  # price within NEAR (2%)
            origin_ok_price_only += 1
            if ot == MatchTier.MISS:
                bars_only_miss += 1
        elif ot == MatchTier.MISS:
            price_miss += 1
    print("\n-- origin miss decomposition (matched legs only) --")
    print(f"  wrong-swing (price > {ORIGIN.near.max_price_pct}%): {price_miss}")
    nb = ORIGIN.near.max_bars
    print(f"  right-region bar-units MISS (price ok, bars > {nb}): {bars_only_miss}")
    print(
        f"  origin within NEAR price band (bars ignored): {origin_ok_price_only}/{total}"
        f" = {origin_ok_price_only / total:.0%}  <- upper bound if bar-tolerance were TF-rescaled"
    )

    # a few concrete matched misses to eyeball the failure mode
    print("\n-- sample matched ORIGIN misses (engine vs human origin/reached) --")
    shown = 0
    for kind, ot, et, fid, a, b, p, gap in rows:
        if kind == "matched" and ot == MatchTier.MISS and shown < 10:
            print(
                f"  {fid[-15:]}  origin eng={p.origin_price:>9.0f} hum={a['price']:>9.0f}"
                f"  reached eng={p.reached_price:>9.0f} hum={b['price']:>9.0f}"
                f"  bar_gap={gap:>3}  ot={ot.name} et={et.name}"
            )
            shown += 1


if __name__ == "__main__":
    main()
