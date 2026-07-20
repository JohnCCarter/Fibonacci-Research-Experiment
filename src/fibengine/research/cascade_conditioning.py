"""Cascade-conditioning probe — does the previous fib predict the next origin? (prereg 2026-07-20)

Pre-registration (frozen rules — read it before touching this):
  docs/research_wiki/reviews/btc-fib-cascade-conditioning-probe-prereg-20260720.md

Tests the SEQUENTIAL hypothesis (style-doc U1, untested) on existing facit — no new labels:
for each human leg ``cur``, is ``cur.anchor_a`` predicted by the endpoint (``anchor_b``) of the
most recently completed leg, scored on the LOCKED acceptance origin band, against a
sequence-destroying permutation null (N1)? H1b (fresh extreme) and N2 (prominence pivot) are
secondary/descriptive only and never bear the verdict.

**Selection-learning probe only — no edge/behaviour/PnL/Genesis claim, no model, no cascade data
model, no facit mutation, no auto-fib.** Verdict is advisory pending owner sign-off.

Pre-run amendments A1-A5 (leakage-validity review 2026-07-20, before any run): see prereg §9.

Run (deterministic; needs cached candles, never fetches):
    uv run python -m fibengine.research.cascade_conditioning --probe
"""

from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.acceptance import ACCEPT_AT, MatchTier, classify_anchor
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.pivots.detect import detect_pivots
from fibengine.research.corpus_manifest import HUMAN_FIB_ROOT, verify_manifest

# --- frozen constants (prereg §3/§5/§6) -------------------------------------------------------

SEED = 20260720
N_PERM = 2000
N_BOOT = 2000
MIN_PAIRS_POWERED = 50
TIMEFRAMES = ("4h", "1d", "1w", "1M")  # 4h primary first
PRIMARY_TF = "4h"  # prereg §3: only the 4h cell may bear a §6 verdict (amendment A3)
REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "cascade_conditioning"


@dataclass(frozen=True)
class Leg:
    fib_id: str
    a_ts: pd.Timestamp
    a_price: float
    b_ts: pd.Timestamp
    b_price: float
    direction: str

    @property
    def degenerate(self) -> bool:
        return self.a_ts == self.b_ts


@dataclass(frozen=True)
class Pair:
    prev: Leg
    cur: Leg


def load_legs(timeframe: str, root: Path | None = None) -> list[Leg]:
    """Facit legs for a TF, fail-closed on non-human files (mirrors ``load_human_legs``)."""
    root = root or HUMAN_FIB_ROOT
    paths = [
        p
        for p in sorted(glob.glob(str(root / timeframe / "fib_*.json")))
        if not p.endswith("_events.json")
    ]
    if not paths:
        raise ValueError(f"no source fibs for {timeframe} under {root}")
    legs: list[Leg] = []
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        if data.get("created_by") != "human":
            raise ValueError(f"refusing non-human fib: {p}")
        legs.append(
            Leg(
                fib_id=str(data.get("fib_id", Path(p).stem)),
                a_ts=pd.Timestamp(data["anchor_a"]["time"]),
                a_price=float(data["anchor_a"]["price"]),
                b_ts=pd.Timestamp(data["anchor_b"]["time"]),
                b_price=float(data["anchor_b"]["price"]),
                direction=str(data.get("direction", "")),
            )
        )
    return legs


def order_legs(legs: list[Leg]) -> list[Leg]:
    """Prereg §4.1: sort by anchor_a.time, ties by anchor_b.time then fib_id."""
    return sorted(legs, key=lambda x: (x.a_ts.value, x.b_ts.value, x.fib_id))


def predecessor_of(cur: Leg, legs: list[Leg]) -> Leg | None:
    """Prereg §4.2: the leg with the latest anchor_b.time <= cur.anchor_a.time (equality allowed
    — exact chains count); ties by latest anchor_a.time, then fib_id. Never ``cur`` itself."""
    eligible = [x for x in legs if x is not cur and x.b_ts <= cur.a_ts]
    if not eligible:
        return None
    return max(eligible, key=lambda x: (x.b_ts.value, x.a_ts.value, x.fib_id))


def build_pairs(legs: list[Leg]) -> tuple[list[Pair], dict[str, int]]:
    """Prereg §4: consecutive pairs + exclusion counts. Degenerate ``cur`` excluded; a degenerate
    leg MAY serve as predecessor."""
    ordered = order_legs(legs)
    pairs: list[Pair] = []
    excl = {"no_predecessor": 0, "degenerate_cur": 0}
    for cur in ordered:
        if cur.degenerate:
            excl["degenerate_cur"] += 1
            continue
        prev = predecessor_of(cur, ordered)
        if prev is None:
            excl["no_predecessor"] += 1
            continue
        pairs.append(Pair(prev=prev, cur=cur))
    return pairs, excl


def origin_hit(
    df: pd.DataFrame,
    cand_ts: pd.Timestamp,
    cand_price: float,
    cur: Leg,
    accept_at: MatchTier = ACCEPT_AT,
) -> tuple[bool, MatchTier]:
    """Score ONE candidate origin point vs cur.anchor_a on the LOCKED origin band (prereg §5)."""
    cand_bar, cand_in = bar_of_timestamp(df, cand_ts.isoformat())
    true_bar, true_in = bar_of_timestamp(df, cur.a_ts.isoformat())
    if not (cand_in and true_in):
        return False, MatchTier.MISS
    tier = classify_anchor(
        cand_price, cur.a_price, is_origin=True, pred_bar=cand_bar, true_bar=true_bar
    )
    return tier >= accept_at, tier


def h1a_hits(df: pd.DataFrame, pairs: list[Pair]) -> list[MatchTier]:
    """PRIMARY: predecessor's anchor_b as the candidate origin."""
    return [origin_hit(df, p.prev.b_ts, p.prev.b_price, p.cur)[1] for p in pairs]


def permutation_null(
    df: pd.DataFrame, pairs: list[Pair], legs: list[Leg], n_perm: int, seed: int
) -> np.ndarray:
    """PRIMARY NULL N1 (prereg §5): per pair, swap in the anchor_b of a uniformly drawn OTHER leg
    with anchor_b.time <= cur.anchor_a.time (causality kept, sequence destroyed). Returns the
    pooled hit-rate of each permutation replicate."""
    rng = np.random.default_rng(seed)
    ordered = order_legs(legs)
    donors_per_pair: list[list[Leg]] = []
    for p in pairs:
        donors = [x for x in ordered if x is not p.cur and x.b_ts <= p.cur.a_ts]
        donors_per_pair.append(donors)
    rates = np.empty(n_perm)
    for r in range(n_perm):
        hits = 0
        for p, donors in zip(pairs, donors_per_pair, strict=True):
            donor = donors[int(rng.integers(len(donors)))]
            ok, _ = origin_hit(df, donor.b_ts, donor.b_price, p.cur)
            hits += int(ok)
        rates[r] = hits / len(pairs)
    return rates


def fresh_extreme_candidate(df: pd.DataFrame, pair: Pair) -> tuple[pd.Timestamp, float] | None:
    """SECONDARY H1b: most extreme same-side extreme strictly between prev.anchor_b and
    cur.anchor_a (exclusive of cur.anchor_a's own bar). Conditions on cur's origin time AND
    eventual direction — both future info at the origin; non-causal calibration context only,
    never verdict-bearing (prereg §5 + amendment A2)."""
    lo_bar, _ = bar_of_timestamp(df, pair.prev.b_ts.isoformat())
    hi_bar, _ = bar_of_timestamp(df, pair.cur.a_ts.isoformat())
    window = df.iloc[lo_bar + 1 : hi_bar]  # excludes cur.anchor_a's bar
    if window.empty:
        return None
    col = "high" if pair.cur.direction == "down" else "low"
    ts = window[col].idxmax() if col == "high" else window[col].idxmin()
    return ts, float(window[col].loc[ts])


def prominence_candidate(
    df: pd.DataFrame, pair: Pair, pivot_cfg
) -> tuple[pd.Timestamp, float] | None:
    """SECONDARY CONTROL N2: most ATR-prominent pivot in the same inter-leg window. Detection
    runs on the frame truncated at cur.anchor_a's bar so no post-origin bar can certify or rank
    a pivot (centered prominence window would otherwise look ahead — amendment A1, matching the
    ``selection_learning*`` truncate-then-detect convention)."""
    lo_bar, _ = bar_of_timestamp(df, pair.prev.b_ts.isoformat())
    hi_bar, _ = bar_of_timestamp(df, pair.cur.a_ts.isoformat())
    pivots = [
        q for q in detect_pivots(df.iloc[: hi_bar + 1], pivot_cfg) if lo_bar < q.index < hi_bar
    ]
    if not pivots:
        return None
    best = max(pivots, key=lambda q: q.prominence)
    return df.index[best.index], float(best.price)


def bootstrap_gap(
    hit_flags: list[bool], null_mean: float, n_boot: int, seed: int
) -> tuple[float, float]:
    """95% CI of HR(H1a) - mean HR(N1) via pair-resample bootstrap (prereg §6)."""
    rng = np.random.default_rng(seed)
    flags = np.asarray(hit_flags, dtype=float)
    n = len(flags)
    reps = np.empty(n_boot)
    for r in range(n_boot):
        reps[r] = flags[rng.integers(0, n, size=n)].mean() - null_mean
    return float(np.quantile(reps, 0.025)), float(np.quantile(reps, 0.975))


def run_cell(timeframe: str, settings) -> dict:
    df = load_candles(
        settings.data.model_copy(update={"timeframe": timeframe}), fetch_if_missing=False
    )
    legs = load_legs(timeframe)
    pairs, excl = build_pairs(legs)
    # prereg §4.3 third exclusion (amendment A4): cur anchors outside the loaded candle window
    # are excluded and counted, not silently scored as MISS (which would inflate n_pairs).
    excl["cur_outside_candle_window"] = 0
    in_window: list[Pair] = []
    for p in pairs:
        _, a_in = bar_of_timestamp(df, p.cur.a_ts.isoformat())
        _, b_in = bar_of_timestamp(df, p.cur.b_ts.isoformat())
        if a_in and b_in:
            in_window.append(p)
        else:
            excl["cur_outside_candle_window"] += 1
    pairs = in_window
    role = "primary" if timeframe == PRIMARY_TF else "context"
    cell: dict = {
        "timeframe": timeframe,
        "role": role,
        "n_legs": len(legs),
        "n_pairs": len(pairs),
        "exclusions": excl,
        "bars": len(df),
        "first_ts": df.index[0].isoformat(),
        "last_ts": df.index[-1].isoformat(),
    }
    if not pairs:
        cell["verdict"] = "context_only" if role == "context" else "inconclusive_underpowered"
        return cell
    tiers = h1a_hits(df, pairs)
    flags = [t >= ACCEPT_AT for t in tiers]
    hr = sum(flags) / len(flags)
    null_rates = permutation_null(df, pairs, legs, N_PERM, SEED)
    p_one_sided = float((null_rates >= hr).mean())
    ci_lo, ci_hi = bootstrap_gap(flags, float(null_rates.mean()), N_BOOT, SEED)
    cell.update(
        {
            "h1a_hit_rate": hr,
            "h1a_tiers": {t.name: sum(1 for x in tiers if x == t) for t in MatchTier},
            "h1a_exact_rate": sum(1 for t in tiers if t == MatchTier.EXACT) / len(tiers),
            "n1_null_mean": float(null_rates.mean()),
            "p_one_sided": p_one_sided,
            "gap_ci95": [ci_lo, ci_hi],
        }
    )
    # secondary/descriptive (never verdict-bearing): H1b fresh extreme + N2 prominence control
    h1b = [fresh_extreme_candidate(df, p) for p in pairs]
    cell["h1b_hit_rate"] = sum(
        int(origin_hit(df, ts, price, p.cur)[0])
        for p, c in zip(pairs, h1b, strict=True)
        if c is not None
        for ts, price in [c]
    ) / len(pairs)
    n2 = [prominence_candidate(df, p, settings.pivots) for p in pairs]
    cell["n2_hit_rate"] = sum(
        int(origin_hit(df, ts, price, p.cur)[0])
        for p, c in zip(pairs, n2, strict=True)
        if c is not None
        for ts, price in [c]
    ) / len(pairs)
    # prereg §3 + amendment A3: context cells are reported but never bear a §6 verdict,
    # regardless of pair count — "context_only" is a status marker, not a verdict.
    if role == "context":
        cell["verdict"] = "context_only"
    elif len(pairs) < MIN_PAIRS_POWERED:
        cell["verdict"] = "inconclusive_underpowered"
    elif p_one_sided < 0.05 and ci_lo > 0:
        cell["verdict"] = "sequential_origin_signal"
    else:
        cell["verdict"] = "no_sequential_signal"
    return cell


def run_probe(config_path: str | None = None) -> dict:
    mismatches = verify_manifest()
    if mismatches:
        msg = "; ".join(mismatches)
        raise SystemExit(f"corpus drift vs MANIFEST.json - refusing to run: {msg}")
    settings = load_settings(config_path) if config_path else load_settings()
    cells = [run_cell(tf, settings) for tf in TIMEFRAMES]
    summary = {"prereg": "btc-fib-cascade-conditioning-probe-prereg-20260720", "cells": cells}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for c in cells:
        line = f"{c['timeframe']}: pairs={c['n_pairs']} verdict={c.get('verdict')}"
        if "h1a_hit_rate" in c:
            line += (
                f" H1a={c['h1a_hit_rate']:.3f} null={c['n1_null_mean']:.3f}"
                f" p={c['p_one_sided']:.4f} gapCI=[{c['gap_ci95'][0]:.3f},{c['gap_ci95'][1]:.3f}]"
                f" | H1b={c['h1b_hit_rate']:.3f} N2={c['n2_hit_rate']:.3f}"
            )
        print(line)
    print(f"summary -> {out}")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cascade-conditioning probe (prereg 2026-07-20).")
    ap.add_argument("--probe", action="store_true", required=True, help="run all cells")
    ap.add_argument("--config", default=None, help="settings path (default: baseline)")
    args = ap.parse_args(argv)
    run_probe(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
