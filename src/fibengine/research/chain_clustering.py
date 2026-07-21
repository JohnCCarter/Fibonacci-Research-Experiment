"""Chain-clustering probe — chaining: mode or per-leg coin flip? (prereg 2026-07-21)

Pre-registration (frozen rules — read it before touching this):
  docs/research_wiki/reviews/btc-fib-chain-clustering-probe-prereg-20260721.md

Follow-up on the SIGNED cascade result (`sequential_origin_signal`, 4h H1a 0.256): the chain
indicator sequence ``c_1..c_N`` (H1a hit per included pair, time-ordered) is tested for serial
clustering (adjacency count) against a marginal-preserving permutation null. Pair construction
and hit scoring are reused from ``cascade_conditioning`` verbatim — nothing is re-derived.

**Selection-learning probe only — no edge/behaviour/PnL/Genesis claim, no model, no facit
mutation, no auto-fib.** Verdict is advisory pending owner sign-off.

Run (deterministic; needs cached candles, never fetches):
    uv run python -m fibengine.research.chain_clustering --probe
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.research.cascade_conditioning import (
    REPO_ROOT,
    Pair,
    build_pairs,
    load_legs,
    origin_hit,
)
from fibengine.research.corpus_manifest import verify_manifest

# --- frozen constants (prereg §3/§5/§6) -------------------------------------------------------

SEED = 20260721
N_PERM = 2000
N_BOOT = 2000
MIN_PAIRS_POWERED = 50
TIMEFRAMES = ("4h", "1d", "1w")  # 4h primary; 1M dropped per prereg §3
PRIMARY_TF = "4h"
RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "chain_clustering"


def chain_sequence(df, pairs: list[Pair]) -> np.ndarray:
    """Prereg §4: chain indicator per included pair, in pair order (already time-ordered)."""
    return np.array(
        [int(origin_hit(df, p.prev.b_ts, p.prev.b_price, p.cur)[0]) for p in pairs], dtype=int
    )


def adjacency_count(c: np.ndarray) -> int:
    """Prereg §5 H2a: number of adjacent chained pairs."""
    return int(np.sum((c[:-1] == 1) & (c[1:] == 1)))


def single_file_mask(pairs: list[Pair]) -> np.ndarray:
    """Prereg §9 A1: adjacent slot i is *single-file* iff pair i's ``cur`` IS pair i+1's ``prev``.

    Hub-shared slots (two consecutive pairs testing the same ``prev`` anchor) can inflate
    adjacency mechanically without any serial cascade mode; the confound-guarded statistic
    counts only true leg-to-leg transitions. The mask is leg topology (exogenous structure),
    so it stays FIXED while ``c`` is permuted."""
    return np.array([pairs[i].cur is pairs[i + 1].prev for i in range(len(pairs) - 1)], dtype=bool)


def adjacency_count_masked(c: np.ndarray, mask: np.ndarray) -> int:
    """Adjacency over single-file slots only (prereg §9 A1)."""
    return int(np.sum((c[:-1] == 1) & (c[1:] == 1) & mask))


def hub_diagnostics(pairs: list[Pair]) -> dict:
    """Prereg §9 A1 diagnostics: how much hub-sharing exists in the adjacent-slot structure."""
    n_slots = max(0, len(pairs) - 1)
    mask = single_file_mask(pairs)
    hub_shared = sum(
        1 for i in range(n_slots) if not mask[i] and pairs[i].prev is pairs[i + 1].prev
    )
    return {
        "n_adjacent_slots": n_slots,
        "n_single_file": int(mask.sum()),
        "n_hub_shared_prev": hub_shared,
    }


def markov_gap(c: np.ndarray) -> float | None:
    """Prereg §5 H2b: P(next=1 | cur=1) - P(next=1 | cur=0); None if a condition is empty."""
    nxt, cur = c[1:], c[:-1]
    if not ((cur == 1).any() and (cur == 0).any()):
        return None
    return float(nxt[cur == 1].mean() - nxt[cur == 0].mean())


def run_lengths(c: np.ndarray) -> list[int]:
    """Lengths of maximal runs of 1s."""
    runs, n = [], 0
    for v in c:
        if v:
            n += 1
        elif n:
            runs.append(n)
            n = 0
    if n:
        runs.append(n)
    return runs


def permutation_reference(
    c: np.ndarray, n_perm: int, seed: int, mask: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Prereg §5 N3 (+§9 A1): permute the sequence; return (adjacency, markov-gap,
    masked-adjacency) per replicate. The single-file mask stays fixed (slot structure is
    exogenous); only ``c`` is permuted."""
    rng = np.random.default_rng(seed)
    adj = np.empty(n_perm)
    gaps = np.full(n_perm, np.nan)
    adj_sf = np.empty(n_perm) if mask is not None else None
    for r in range(n_perm):
        perm = rng.permutation(c)
        adj[r] = adjacency_count(perm)
        if adj_sf is not None:
            adj_sf[r] = adjacency_count_masked(perm, mask)
        g = markov_gap(perm)
        if g is not None:
            gaps[r] = g
    return adj, gaps, adj_sf


def bootstrap_markov_gap(c: np.ndarray, n_boot: int, seed: int) -> tuple[float, float] | None:
    """Prereg §5 H2b: CI via resampling adjacent (c_i, c_{i+1}) transition pairs."""
    trans = np.stack([c[:-1], c[1:]], axis=1)
    n = len(trans)
    if n == 0:
        return None
    rng = np.random.default_rng(seed)
    reps = []
    for _ in range(n_boot):
        s = trans[rng.integers(0, n, size=n)]
        cur, nxt = s[:, 0], s[:, 1]
        if (cur == 1).any() and (cur == 0).any():
            reps.append(float(nxt[cur == 1].mean() - nxt[cur == 0].mean()))
    if len(reps) < n_boot // 2:
        return None
    return float(np.quantile(reps, 0.025)), float(np.quantile(reps, 0.975))


def direction_split(pairs: list[Pair], c: np.ndarray) -> dict:
    """Descriptive: continuation vs reversal among chained pairs (prereg §5)."""
    cont = sum(
        1 for p, ci in zip(pairs, c, strict=True) if ci and p.prev.direction == p.cur.direction
    )
    total = int(c.sum())
    return {"chained": total, "continuation": cont, "reversal": total - cont}


def gap_bars(df, pairs: list[Pair], c: np.ndarray) -> dict:
    """Descriptive: inter-leg gap in bars for chained vs unchained pairs."""
    from fibengine.evaluation.bars import bar_of_timestamp

    gaps: dict[str, list[int]] = {"chained": [], "unchained": []}
    for p, ci in zip(pairs, c, strict=True):
        b_bar, _ = bar_of_timestamp(df, p.prev.b_ts.isoformat())
        a_bar, _ = bar_of_timestamp(df, p.cur.a_ts.isoformat())
        gaps["chained" if ci else "unchained"].append(a_bar - b_bar)
    return {k: {"n": len(v), "median": float(np.median(v)) if v else None} for k, v in gaps.items()}


def session_day_sensitivity(df, pairs: list[Pair], legs_meta: dict[str, str]) -> dict | None:
    """Prereg §7 sensitivity: H2a excluding pairs whose legs were drawn on different days."""
    keep = [
        (p, i)
        for i, p in enumerate(pairs)
        if legs_meta.get(p.prev.fib_id, "")[:10] == legs_meta.get(p.cur.fib_id, "")[:10]
    ]
    if len(keep) < 2:
        return None
    c = chain_sequence(df, [p for p, _ in keep])
    return {
        "n_pairs_same_day": len(keep),
        "adjacency": adjacency_count(c),
        "chain_rate": float(c.mean()),
    }


def load_created_at(timeframe: str) -> dict[str, str]:
    """fib_id -> created_at (for the labeling-day sensitivity)."""
    import glob

    from fibengine.research.corpus_manifest import HUMAN_FIB_ROOT

    meta: dict[str, str] = {}
    for p in glob.glob(str(HUMAN_FIB_ROOT / timeframe / "fib_*.json")):
        if p.endswith("_events.json"):
            continue
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        meta[str(data.get("fib_id", Path(p).stem))] = str(data.get("created_at", ""))
    return meta


def filter_in_window(df, pairs: list[Pair], excl: dict) -> list[Pair]:
    """Prereg §9 A2 (mirrors the signed probe's A4): drop pairs whose ``cur`` anchors fall
    outside the loaded candle window and COUNT them (``cur_outside_candle_window``)."""
    from fibengine.evaluation.bars import bar_of_timestamp

    excl.setdefault("cur_outside_candle_window", 0)
    kept: list[Pair] = []
    for p in pairs:
        _, a_in = bar_of_timestamp(df, p.cur.a_ts.isoformat())
        _, b_in = bar_of_timestamp(df, p.cur.b_ts.isoformat())
        if a_in and b_in:
            kept.append(p)
        else:
            excl["cur_outside_candle_window"] += 1
    return kept


def run_cell(timeframe: str, settings) -> dict:
    df = load_candles(
        settings.data.model_copy(update={"timeframe": timeframe}), fetch_if_missing=False
    )
    legs = load_legs(timeframe)
    pairs, excl = build_pairs(legs)
    pairs = filter_in_window(df, pairs, excl)
    role = "primary" if timeframe == PRIMARY_TF else "context"
    cell: dict = {"timeframe": timeframe, "role": role, "n_pairs": len(pairs), "exclusions": excl}
    if len(pairs) < 2:
        cell["verdict"] = "context_only" if role == "context" else "inconclusive_underpowered"
        return cell
    c = chain_sequence(df, pairs)
    mask = single_file_mask(pairs)
    a_obs = adjacency_count(c)
    a_sf_obs = adjacency_count_masked(c, mask)
    adj_null, gap_null, adj_sf_null = permutation_reference(c, N_PERM, SEED, mask)
    p_adj = float((adj_null >= a_obs).mean())
    p_sf = float((adj_sf_null >= a_sf_obs).mean())
    gap_obs = markov_gap(c)
    cell.update(
        {
            "chain_rate": float(c.mean()),
            "adjacency_observed": a_obs,
            "adjacency_null_mean": float(adj_null.mean()),
            "p_one_sided": p_adj,
            "adjacency_single_file_observed": a_sf_obs,
            "adjacency_single_file_null_mean": float(adj_sf_null.mean()),
            "p_one_sided_single_file": p_sf,
            "hub_diagnostics": hub_diagnostics(pairs),
            "markov_gap": gap_obs,
            "markov_gap_null_mean": float(np.nanmean(gap_null)),
            "markov_gap_ci95": bootstrap_markov_gap(c, N_BOOT, SEED),
            "run_lengths": run_lengths(c),
            "direction": direction_split(pairs, c),
            "gap_bars": gap_bars(df, pairs, c),
            "session_day_sensitivity": session_day_sensitivity(
                df, pairs, load_created_at(timeframe)
            ),
        }
    )
    # Prereg §9 A1: the positive verdict is confound-guarded — it requires the full-array
    # adjacency AND the single-file-restricted adjacency (hub-sharing excluded) to both
    # reject the permutation null.
    if role == "context":
        cell["verdict"] = "context_only"
    elif len(pairs) < MIN_PAIRS_POWERED:
        cell["verdict"] = "inconclusive_underpowered"
    elif p_adj < 0.05 and p_sf < 0.05:
        cell["verdict"] = "chain_clustering"
    else:
        cell["verdict"] = "no_chain_clustering"
    return cell


def run_probe(config_path: str | None = None) -> dict:
    mismatches = verify_manifest()
    if mismatches:
        msg = "; ".join(mismatches)
        raise SystemExit(f"corpus drift vs MANIFEST.json - refusing to run: {msg}")
    settings = load_settings(config_path) if config_path else load_settings()
    cells = [run_cell(tf, settings) for tf in TIMEFRAMES]
    summary = {"prereg": "btc-fib-chain-clustering-probe-prereg-20260721", "cells": cells}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for c in cells:
        line = f"{c['timeframe']}: pairs={c['n_pairs']} verdict={c.get('verdict')}"
        if "adjacency_observed" in c:
            line += (
                f" rate={c['chain_rate']:.3f} A={c['adjacency_observed']}"
                f" (null {c['adjacency_null_mean']:.1f}) p={c['p_one_sided']:.4f}"
                f" | A_sf={c['adjacency_single_file_observed']}"
                f" (null {c['adjacency_single_file_null_mean']:.1f})"
                f" p_sf={c['p_one_sided_single_file']:.4f}"
            )
            if c["markov_gap"] is not None:
                line += f" markov_gap={c['markov_gap']:.3f}"
        print(line)
    print(f"summary -> {out}")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chain-clustering probe (prereg 2026-07-21).")
    ap.add_argument("--probe", action="store_true", required=True, help="run all cells")
    ap.add_argument("--config", default=None, help="settings path (default: baseline)")
    args = ap.parse_args(argv)
    run_probe(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
