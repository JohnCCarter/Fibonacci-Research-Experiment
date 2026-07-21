"""Negative-audit of track-A implicit negatives (audit item, owner GO 2026-07-21).

QUESTION: in the Stage-2 selection-learning design every candidate leg that does not match a
facit leg within ε is an *implicit negative* (label=0). How exposed is that labeling to
unlabeled-positive contamination — negatives that are "never reviewed" rather than "rejected"?

METHOD (frozen in this docstring BEFORE any number was computed; descriptive audit ONLY —
no verdict family, no AP recompute, no alternate-negative re-scoring, nothing here may be
cited as a study result):

1. Facit legs via `selection_learning.load_human_legs` (fail-closed); candles from the frozen
   2026-07-21 cache (`config/settings.expansion.yaml`, pivots identical to baseline).
2. Candidate-universe PROXY: one full-frame `detect_pivots` pass (baseline PivotConfig);
   each pivot as anchor_b paired with its <= 12 most recent prior opposite pivots
   (mirrors `max_legs_per_point`). DISCLOSED difference vs the causal Stage-2 universe:
   no per-endpoint truncated re-detection (hours of compute); the full-frame universe is the
   same generator without the live-confirmability filter, fine for a coverage audit,
   NOT for reproducing study metrics.
3. Match vs facit exactly as `_matches_human`: eps_time = 3 bars, eps_price = 0.5 * ATR(14)
   at anchor_b, both anchors + direction. NEAR-MISS shell: matches at 2x both tolerances
   that are not matches at 1x.
4. Coverage geometry: facit anchor_b bar positions; inter-facit gap distribution; for every
   negative, distance in bars from its anchor_b to the nearest facit anchor_b.
   "Coverage-weak" negative: nearest-facit distance > G where G = median inter-facit-b gap
   (formula frozen a priori; value computed from data and reported).
5. Report per TF (4h primary, 1d context): counts, near-miss contamination, coverage-weak
   fraction, top-5 facit deserts (date ranges), facit-b count per calendar year.

Output: printout + experiments/review/negative_audit/summary.json (gitignored).
Run: uv run --no-sync python scratchpad/negative_audit_track_a.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fibengine.core.config import load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.selection_learning import SelectionConfig, load_human_legs

CONFIG = "config/settings.expansion.yaml"
TIMEFRAMES = ("4h", "1d")
MAX_LEGS_PER_POINT = 12
OUT_DIR = Path("experiments/review/negative_audit")


def pos_of_ts(index_ns: np.ndarray, ts) -> int:
    import pandas as pd

    return int(np.argmin(np.abs(index_ns - np.int64(pd.Timestamp(ts).value))))


def audit_tf(timeframe: str, settings, cfg: SelectionConfig) -> dict:
    df = load_candles(
        settings.data.model_copy(update={"timeframe": timeframe}), fetch_if_missing=False
    )
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    n = len(df)
    legs = load_human_legs(timeframe)
    atr_arr = atr(df, period=cfg.atr_period).to_numpy()
    pivots = detect_pivots(df, settings.pivots)

    # facit anchor positions
    facit = [
        {
            "a_pos": pos_of_ts(index_ns, leg.anchor_a_ts),
            "b_pos": pos_of_ts(index_ns, leg.anchor_b_ts),
            "a_price": leg.anchor_a_price,
            "b_price": leg.anchor_b_price,
            "direction": leg.direction,
        }
        for leg in legs
    ]
    facit_b = np.array(sorted(f["b_pos"] for f in facit))

    def match_at(start, end, mult: float) -> bool:
        ab = float(atr_arr[end.index]) if 0 <= end.index < len(atr_arr) else float("nan")
        if not np.isfinite(ab) or ab <= 0:
            return False
        tol_t = cfg.eps_time_bars * mult
        tol_p = cfg.eps_price_atr * ab * mult
        cand_dir = "up" if end.price > start.price else "down"
        for f in facit:
            if abs(end.index - f["b_pos"]) > tol_t:
                continue
            if abs(start.index - f["a_pos"]) > tol_t:
                continue
            if abs(end.price - f["b_price"]) > tol_p:
                continue
            if abs(start.price - f["a_price"]) > tol_p:
                continue
            if f["direction"] and f["direction"] != cand_dir:
                continue
            return True
        return False

    n_pos = n_neg = n_nearmiss = 0
    neg_dist: list[int] = []
    for piv in pivots:
        prior_opp = [q for q in pivots if q.kind != piv.kind and q.index < piv.index]
        for start in prior_opp[-MAX_LEGS_PER_POINT:]:
            if match_at(start, piv, 1.0):
                n_pos += 1
            else:
                n_neg += 1
                if match_at(start, piv, 2.0):
                    n_nearmiss += 1
                d = int(np.min(np.abs(facit_b - piv.index))) if len(facit_b) else -1
                neg_dist.append(d)

    gaps = np.diff(facit_b) if len(facit_b) > 1 else np.array([])
    g_thresh = float(np.median(gaps)) if len(gaps) else float("nan")
    neg_dist_arr = np.array(neg_dist)
    coverage_weak = (
        float((neg_dist_arr > g_thresh).mean())
        if len(neg_dist_arr) and np.isfinite(g_thresh)
        else None
    )
    # top-5 deserts as date ranges
    desert_idx = np.argsort(gaps)[::-1][:5] if len(gaps) else []
    deserts = [
        {
            "from": str(df.index[int(facit_b[i])].date()),
            "to": str(df.index[int(facit_b[i + 1])].date()),
            "bars": int(gaps[i]),
        }
        for i in desert_idx
    ]
    per_year: dict[str, int] = {}
    for f in facit:
        y = str(df.index[f["b_pos"]].year)
        per_year[y] = per_year.get(y, 0) + 1

    return {
        "timeframe": timeframe,
        "bars": n,
        "n_facit": len(legs),
        "n_candidates": n_pos + n_neg,
        "n_pos_proxy": n_pos,
        "n_neg": n_neg,
        "n_nearmiss_2x": n_nearmiss,
        "nearmiss_frac_of_neg": n_nearmiss / n_neg if n_neg else None,
        "median_facit_gap_bars": g_thresh,
        "coverage_weak_frac_of_neg": coverage_weak,
        "neg_nearest_facit_quartiles": (
            [float(q) for q in np.percentile(neg_dist_arr, [25, 50, 75, 90])]
            if len(neg_dist_arr)
            else None
        ),
        "facit_b_per_year": dict(sorted(per_year.items())),
        "top_deserts": deserts,
    }


def main() -> None:
    settings = load_settings(CONFIG)
    cfg = SelectionConfig()
    cells = [audit_tf(tf, settings, cfg) for tf in TIMEFRAMES]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "summary.json"
    out.write_text(json.dumps({"cells": cells}, indent=2) + "\n", encoding="utf-8")
    for c in cells:
        print(json.dumps(c, indent=2))
    print(f"summary -> {out}")


if __name__ == "__main__":
    main()
