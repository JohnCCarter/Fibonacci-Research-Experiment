"""Sequential-conditioning selection feature — `chained_origin` (prereg 2026-07-21).

Pre-registration (frozen rules — read it before touching this):
  docs/research_wiki/reviews/btc-fib-sequential-feature-prereg-20260721.md

Does *"this candidate's origin sits on the most recently completed human leg's endpoint"* add
OOS ranking signal at the live k=3 viewport, over the identical Stage-2 model without it?
**TEACHER-FORCED (prereg §2, binding):** the feature conditions on the human's own prior
selections (hindsight-drawn facit) — a reproduction question, never a live-availability,
edge, or behaviour claim.

The candidate build mirrors ``selection_learning.build_candidates`` verbatim in logic; it is
re-implemented here only because the byte-capped module's ``Candidate`` does not carry the
start pivot's price, which the sequential feature needs (prereg §4).

Run (deterministic; needs cached candles, never fetches; hours on 4h):
    PYTHONUNBUFFERED=1 uv run --no-sync python -u -m fibengine.research.selection_sequential \\
        --sequential --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from fibengine.core.config import load_settings
from fibengine.core.features import compute_features
from fibengine.core.models import Swing
from fibengine.data.loader import atr, load_candles
from fibengine.evaluation.acceptance import ACCEPT_AT, classify_anchor
from fibengine.pivots.detect import detect_pivots
from fibengine.research.corpus_manifest import verify_manifest
from fibengine.research.selection_learning import (
    REPO_ROOT,
    HumanLeg,
    SelectionConfig,
    _matches_human,
    _pos_of_ts,
    _progress,
    average_precision,
    decision_point_bootstrap,
    fit_logreg,
    live_feature_names,
    load_human_legs,
    predict_proba,
    roc_auc,
    window_of,
)

# --- frozen constants (prereg §3/§5/§6) -------------------------------------------------------

SEED = 20260721
PRIMARY_TF = "4h"
TIMEFRAMES = ("4h", "1d")  # 4h primary, 1d context (prereg §3)
RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "selection_sequential"


@dataclass
class SeqCandidate:
    anchor_b_pos: int
    start_pos: int
    start_price: float
    features: dict[str, float]
    label: int
    human_idx: int = -1


def build_candidates_seq(
    df, human_legs: list[HumanLeg], pivot_cfg, scoring_cfg, cfg: SelectionConfig
) -> list[SeqCandidate]:
    """Stage-2 causal candidate build (mirrors ``selection_learning.build_candidates``; k=3 →
    no confluence branch), additionally recording the start pivot's price (prereg §4)."""
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    n = len(df)
    full_pivots = detect_pivots(df, pivot_cfg)
    out: list[SeqCandidate] = []
    n_piv = len(full_pivots)
    _progress(f"  build_candidates_seq: {n_piv} pivots, df={n} bars (per-endpoint detect)")
    t0 = time.perf_counter()
    for i_piv, piv in enumerate(full_pivots, start=1):
        if i_piv % 50 == 0 or i_piv == n_piv:
            _progress(f"    pivot {i_piv}/{n_piv} ({time.perf_counter() - t0:.0f}s)")
        j = piv.index
        end_view = j + cfg.k
        if end_view >= n:  # cannot be confirmed live within the data — skip (no peeking)
            continue
        df_t = df.iloc[: end_view + 1]
        atr_t = atr(df_t, period=cfg.atr_period)
        atr_arr = atr_t.to_numpy()
        piv_t = detect_pivots(df_t, pivot_cfg)
        end_piv = next((q for q in piv_t if q.index == j and q.kind == piv.kind), None)
        if end_piv is None:  # not live-confirmable on the truncated frame
            continue
        prior_opp = [q for q in piv_t if q.kind != end_piv.kind and q.index < end_piv.index]
        atr_at_b = float(atr_arr[j]) if 0 <= j < len(atr_arr) else float("nan")
        # prom_max deliberately omitted vs the mirrored build (prereg §9 A4):
        # the prominence-family baselines are not part of this study's §6 statistic.
        for start in prior_opp[-cfg.max_legs_per_point :]:
            swing = Swing(start=start, end=end_piv)
            feats = compute_features(df_t, swing, atr_t, scoring_cfg, piv_t, None)
            h = _matches_human(start, end_piv, human_legs, index_ns, atr_at_b, cfg)
            out.append(
                SeqCandidate(
                    anchor_b_pos=j,
                    start_pos=start.index,
                    start_price=float(start.price),
                    features=feats,
                    label=1 if h >= 0 else 0,
                    human_idx=h,
                )
            )
    return out


# --- the sequential feature (prereg §5) -------------------------------------------------------


def nondegenerate_legs(legs: list[HumanLeg]) -> tuple[list[HumanLeg], int]:
    """Prereg §9 A3: the owner-classified misclick fibs (same-candle, ``a_ts == b_ts``;
    handoff 2026-07-21) are excluded from THIS STUDY entirely — both from label matching and
    from the predecessor pool — as known-invalid annotations (study-level exclusion, no facit
    mutation). Returns (kept, n_excluded)."""
    kept = [leg for leg in legs if leg.anchor_a_ts != leg.anchor_b_ts]
    return kept, len(legs) - len(kept)


def facit_positions(df, human_legs: list[HumanLeg]) -> list[tuple[int, int, float, str]]:
    """(b_pos, a_pos, b_price, fib-order-key) per leg, sorted by (b_pos, a_pos, key)."""
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    rows = []
    for i, leg in enumerate(human_legs):
        rows.append(
            (
                _pos_of_ts(index_ns, leg.anchor_b_ts),
                _pos_of_ts(index_ns, leg.anchor_a_ts),
                leg.anchor_b_price,
                f"{i:06d}",
            )
        )
    return sorted(rows)


def chained_origin_features(
    cands: list[SeqCandidate],
    facit_pos: list[tuple[int, int, float, str]],
    eps_time_bars: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Per candidate: (binary `chained_origin`, secondary `chain_prox`, rule-exclusion count).

    Predecessor = human leg with the latest b_pos satisfying the LOCKED label-blind rule
    (prereg §9 A1): ``b_pos <= start_pos`` AND ``b_pos < anchor_b_pos - eps_time_bars``.
    The second condition guarantees the predecessor can never be a leg able to ε-match this
    candidate's own endpoint (self-leg label leakage at the short-leg edge); it uses only
    candidate geometry, so positives and negatives get identically defined features.
    Binary = LOCKED origin band vs the predecessor endpoint; prox = 1/(1+bar_dist);
    0/0 when no qualifying predecessor. Returns how many candidates had their *nearest*
    unrestricted predecessor banned by the rule (``predecessor_rule_exclusions``)."""
    b_positions = np.array([r[0] for r in facit_pos])
    chained = np.zeros(len(cands))
    prox = np.zeros(len(cands))
    n_rule_excluded = 0
    for i, c in enumerate(cands):
        idx_unrestricted = int(np.searchsorted(b_positions, c.start_pos, side="right")) - 1
        ceiling = min(c.start_pos, c.anchor_b_pos - eps_time_bars - 1)
        idx = int(np.searchsorted(b_positions, ceiling, side="right")) - 1
        if idx != idx_unrestricted:
            n_rule_excluded += 1
        if idx < 0:
            continue
        b_pos, _, b_price, _ = facit_pos[idx]
        tier = classify_anchor(
            c.start_price, b_price, is_origin=True, pred_bar=c.start_pos, true_bar=b_pos
        )
        chained[i] = 1.0 if tier >= ACCEPT_AT else 0.0
        prox[i] = 1.0 / (1.0 + abs(c.start_pos - b_pos))
    return chained, prox, n_rule_excluded


# --- cell runner (prereg §6) ------------------------------------------------------------------


def _fit_eval(
    x_tr: np.ndarray,
    y_tr: np.ndarray,
    x_te: np.ndarray,
    y_te: np.ndarray,
    cfg: SelectionConfig,
) -> tuple[dict[str, Any], np.ndarray, float | None]:
    model = fit_logreg(x_tr, y_tr, cfg)
    p = predict_proba(model, x_te)
    return model, p, average_precision(y_te, p)


def run_cell(timeframe: str, settings, cfg: SelectionConfig) -> dict[str, Any]:
    df = load_candles(
        settings.data.model_copy(update={"timeframe": timeframe}), fetch_if_missing=False
    )
    human_legs, n_degenerate = nondegenerate_legs(load_human_legs(timeframe))
    cands = build_candidates_seq(df, human_legs, settings.pivots, settings.scoring, cfg)
    facit_pos = facit_positions(df, human_legs)
    chained, prox, n_rule_excluded = chained_origin_features(cands, facit_pos, cfg.eps_time_bars)

    feat_names = live_feature_names(cfg.k)
    split_idx = int(len(df) * cfg.train_frac)
    tr_idx, te_idx = [], []
    for i, c in enumerate(cands):
        win = window_of(c.anchor_b_pos, split_idx, len(df), cfg.k)
        if win == "train":
            tr_idx.append(i)
        elif win == "test":
            te_idx.append(i)
    tr, te = np.array(tr_idx, dtype=int), np.array(te_idx, dtype=int)

    x_base = np.array([[c.features[f] for f in feat_names] for c in cands], dtype=float)
    y = np.array([c.label for c in cands], dtype=float)
    x_enh = np.column_stack([x_base, chained])
    x_prox = np.column_stack([x_base, prox])

    role = "primary" if timeframe == PRIMARY_TF else "context"
    cell: dict[str, Any] = {
        "timeframe": timeframe,
        "role": role,
        "n_bars": len(df),
        "n_human_legs": len(human_legs),
        "n_candidates": len(cands),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
        "n_test_positives": int(y[te].sum()) if len(te) else 0,
        "features_base": feat_names,
        "chained_rate_all": float(chained.mean()) if len(cands) else None,
        "n_degenerate_legs_excluded": n_degenerate,
        "predecessor_rule_exclusions": n_rule_excluded,
    }
    if not len(tr) or not len(te) or y[tr].sum() == 0 or y[te].sum() == 0:
        cell["verdict"] = "context_only" if role == "context" else "inconclusive_underpowered"
        return cell

    y_tr, y_te = y[tr], y[te]
    _, p_base, ap_base = _fit_eval(x_base[tr], y_tr, x_base[te], y_te, cfg)
    model_enh, p_enh, ap_enh = _fit_eval(x_enh[tr], y_tr, x_enh[te], y_te, cfg)
    _, p_prox, ap_prox = _fit_eval(x_prox[tr], y_tr, x_prox[te], y_te, cfg)

    groups = np.array([cands[i].anchor_b_pos for i in te])
    inference = decision_point_bootstrap(y_te, p_enh, p_base, groups, cfg.n_boot, SEED)

    te_pos = te[y_te == 1]
    te_neg = te[y_te == 0]
    cell.update(
        {
            "ap_base": ap_base,
            "ap_enhanced": ap_enh,
            "ap_lift": (ap_enh - ap_base) if (ap_enh is not None and ap_base is not None) else None,
            "ap_lift_inference": inference,
            "ap_enhanced_prox_variant": ap_prox,
            "auc_base": roc_auc(y_te, p_base),
            "auc_enhanced": roc_auc(y_te, p_enh),
            "chained_origin_weight_standardized": float(model_enh["w"][-1]),
            "ap_chained_alone": average_precision(y_te, chained[te]),
            "ap_magnitude_alone": average_precision(
                y_te, x_base[te][:, feat_names.index("magnitude")]
            ),
            "chained_rate_test_pos": float(chained[te_pos].mean()) if len(te_pos) else None,
            "chained_rate_test_neg": float(chained[te_neg].mean()) if len(te_neg) else None,
        }
    )
    powered = cell["n_test_positives"] >= cfg.min_test_positives
    cell["powered"] = powered
    if role == "context":
        cell["verdict"] = "context_only"
    elif not powered:
        cell["verdict"] = "inconclusive_underpowered"
    elif inference is None:
        # prereg §9 A6: degenerate bootstrap on a powered cell is NOT silently conflated
        # with a clean null — the meta note travels with the verdict.
        cell["verdict"] = "no_sequential_feature_signal"
        cell["meta"] = "powered cell but inference degenerate (bootstrap returned None)"
    elif inference["ci95_low"] > 0:
        cell["verdict"] = "sequential_feature_signal"
    elif inference["ci95_high"] < 0:
        cell["verdict"] = "sequential_feature_worse"
    else:
        cell["verdict"] = "no_sequential_feature_signal"
    return cell


def run_study(config_path: str | None = None) -> dict:
    mismatches = verify_manifest()
    if mismatches:
        msg = "; ".join(mismatches)
        raise SystemExit(f"corpus drift vs MANIFEST.json - refusing to run: {msg}")
    settings = load_settings(config_path) if config_path else load_settings()
    cells = [run_cell(tf, settings, SelectionConfig()) for tf in TIMEFRAMES]
    summary = {"prereg": "btc-fib-sequential-feature-prereg-20260721", "cells": cells}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for c in cells:
        line = f"{c['timeframe']}: verdict={c.get('verdict')}"
        if c.get("ap_lift") is not None:
            inf = c.get("ap_lift_inference") or {}
            line += (
                f" AP {c['ap_base']:.4f}->{c['ap_enhanced']:.4f} lift={c['ap_lift']:+.4f}"
                f" CI=[{inf.get('ci95_low', float('nan')):.4f},"
                f"{inf.get('ci95_high', float('nan')):.4f}]"
                f" p={inf.get('p_one_sided_lift_le_0', float('nan')):.4f}"
            )
        print(line)
    print(f"summary -> {out}")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sequential-conditioning feature (prereg 2026-07-21).")
    ap.add_argument("--sequential", action="store_true", required=True, help="run all cells")
    ap.add_argument("--config", default=None, help="settings path (default: baseline)")
    args = ap.parse_args(argv)
    run_study(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
