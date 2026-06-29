"""BTC Fib SELECTION-LEARNING — Stage-1 per-pivot diagnostic (diagnostic floor, NOT headline).

Secondary / diagnostic slice (prereg §2; **not** in the four-TF Holm headline family). Decomposes
the Stage-2 agreement ceiling into two **separately-reported** halves (Stage-1 LOCK S0):

  1. detection / coverage — are the human's anchors present in the detector's pivot universe at all?
  2. ranking / selection — *given* they are present, do human-anchored pivots rank above the
     prominence baseline OOS?

Frozen blind in the Stage-1 LOCK (Commit 1, 00a97d7):
  docs/research_wiki/reviews/btc-fib-selection-learning-stage1-lock-20260624.md

A detection miss is **not** a ranking failure, and a ranking lift is **not** a reproduction. The
per-pivot feature set is the per-pivot-definable subset of the frozen eight (LOCK S4); leg features
(magnitude/cleanliness/duration/exclusivity) are structurally undefined on a single pivot and are
EXCLUDED — so the Stage-2 ``cleanliness`` lead CANNOT appear here. **No reproduction,
no edge/behaviour/PnL/backtest/Genesis/auto-fib-as-truth/1H/ETH/label-mutation** (LOCK S8). Shared
machinery (model, AP/AUC, cluster bootstrap, frozen-data preflight) is imported from
``selection_learning`` / ``selection_learning_gap``; this module owns only the per-pivot pieces.

Run (own CLI — ``selection_learning.py`` is byte-capped, LOCK S9):
    uv run python -m fibengine.research.selection_learning_stage1 --stage1-preflight
    uv run python -m fibengine.research.selection_learning_stage1 --stage1
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import PivotConfig, ScoringConfig, load_settings
from fibengine.core.features import _round_number_proximity
from fibengine.core.models import Pivot
from fibengine.core.scale import detect_pivots_multi
from fibengine.core.structure import structure_alignment
from fibengine.data.loader import atr, load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.selection_learning import (
    PRIMARY_K,
    RESULTS_DIR,
    SelectionConfig,
    _pos_of_ts,
    _progress,
    average_precision,
    decision_point_bootstrap,
    fit_logreg,
    load_human_legs,
    predict_proba,
    roc_auc,
    window_of,
)
from fibengine.research.selection_learning_gap import run_preflight

# Stage-1 k-sweep (LOCK S3) — same {0,3,6,12} as Stage-2/W-gap, primary k=3. k=0 is DEGENERATE for
# Stage-1 (empty usable feature set: prominence k*=3 not mature, round_number interaction-only) →
# reported degenerate, excluded from the verdict (LOCK S3; differs from "earliest-confirmed pivot").
STAGE1_K_SWEEP = (0, 3, 6, 12)
CONTEXT_TIMEFRAMES = ("1M", "1w", "1d")  # underpowered context only (LOCK S6), at primary k=3

# Per-pivot subset of the frozen eight (LOCK S4), with the addendum-A2 k* buffers. Leg/set-level
# features (magnitude, cleanliness, duration, exclusivity) are NOT per-pivot definable → excluded by
# construction (not a choice). round_number is interaction-only (§3); recency is k*=inf (dropped).
STAGE1_K_STAR: dict[str, float] = {
    "prominence": 3,  # the pivot's own ATR-prominence — ALSO the primary baseline (LOCK S5)
    "structure_alignment": 3,  # per-pivot alignment with recent structure
    "scale_confluence": 12,  # pivot coincides with a higher-degree (deg-12) fractal
    "round_number": 0,  # interaction-only — never a primary input
    "recency": math.inf,  # dataset-relative / omniscient as coded → dropped at every k
}
_INTERACTION_ONLY = ("round_number",)
BASELINE_FEATURE = "prominence"  # LOCK S5: single primary baseline = detector prominence ranking
RECALL_FLOOR = 0.50  # LOCK S7: below this on the powered cell → detector_coverage_limited


def stage1_feature_names(k: int) -> list[str]:
    """Per-pivot live features at confirmation buffer ``k``: every feature with ``k*(f) <= k`` minus
    interaction-only ones. k=0 → [] (degenerate). k=3/6 → [prominence, structure_alignment].
    k>=12 → + [scale_confluence]. Sorted, deterministic (LOCK S3/S4)."""
    return sorted(f for f, ks in STAGE1_K_STAR.items() if ks <= k and f not in _INTERACTION_ONLY)


# --- per-pivot features (faithful single-pivot projections of the frozen eight; NO new feature) ---


def _pivot_confluence(
    pivot: Pivot, multi_pivots: dict[int, list[Pivot]] | None, tol_bars: int
) -> float:
    """Per-pivot projection of ``scale.endpoint_confluence``: fraction of larger fractal degrees at
    which THIS pivot (by its kind) is confirmed within ``tol_bars``. Neutral 0.5 when no larger
    degrees exist. Same confluence mechanism as the leg feature, restricted to one endpoint (LOCK
    S4 — a definitional projection, not a new feature)."""
    if not multi_pivots:
        return 0.5
    scores: list[float] = []
    for pivots in multi_pivots.values():
        if not pivots:
            continue
        conf = any(p.kind == pivot.kind and abs(p.index - pivot.index) <= tol_bars for p in pivots)
        scores.append(float(conf))
    return sum(scores) / len(scores) if scores else 0.5


def compute_pivot_features(
    pivot: Pivot,
    pivots: list[Pivot],
    multi_pivots: dict[int, list[Pivot]] | None,
    cfg: ScoringConfig,
) -> dict[str, float]:
    """Per-pivot features = single-pivot reductions of the leg formulas in ``core.features`` (S4):

    - ``prominence`` = ``tanh(pivot.prominence / 2.0)`` — the leg's ``tanh((p_s+p_e)/4)`` with one
      endpoint (monotone with raw prominence → AP-equivalent as the baseline rank).
    - ``structure_alignment`` = ``structure_alignment(pivots, pivot.index, window, dir)`` with
      ``dir = up`` for a high (top of an up-move), ``down`` for a low — the leg formula is already
      endpoint-indexed; here the endpoint is the pivot itself.
    - ``scale_confluence`` = per-pivot confluence (above).
    - ``round_number`` = the pivot's own price proximity (interaction-only).
    ``recency`` is dropped (k*=inf). All causal on the truncated frame's pivot set."""
    direction = "up" if pivot.kind == "high" else "down"
    return {
        "prominence": float(np.tanh(pivot.prominence / 2.0)),
        "structure_alignment": float(
            structure_alignment(pivots, pivot.index, cfg.structure_window, direction)
        ),
        "scale_confluence": float(_pivot_confluence(pivot, multi_pivots, cfg.confluence_tol_bars)),
        "round_number": float(_round_number_proximity(pivot.price)),
    }


# --- per-pivot targets / candidates -----------------------------------------------------------


@dataclass
class PivotCandidate:
    pivot_pos: int
    kind: str
    chunk: int  # structural-chunk id for the cluster bootstrap (LOCK S6)
    features: dict[str, float]
    label: int  # 1 if within ε of any human anchor (a/b pooled), else 0
    human_anchor_idx: int = -1  # first matched human anchor (for reference), else -1
    prominence_raw: float = 0.0


def _human_anchor_points(human_legs: list[Any], index_ns: np.ndarray) -> list[tuple[int, float]]:
    """Unique human anchor points (a/b pooled, LOCK S1): every ``anchor_a`` and ``anchor_b`` as
    ``(bar_pos, price)``, deduplicated on exact ``(pos, price)`` (a swing extreme shared by two legs
    is one anchor). Direction/role is dropped — Stage-1 asks only 'is this extreme one the human
    anchors on'."""
    seen: set[tuple[int, float]] = set()
    out: list[tuple[int, float]] = []
    for leg in human_legs:
        for ts, price in (
            (leg.anchor_a_ts, leg.anchor_a_price),
            (leg.anchor_b_ts, leg.anchor_b_price),
        ):
            key = (_pos_of_ts(index_ns, ts), float(price))
            if key not in seen:
                seen.add(key)
                out.append(key)
    return out


def _matched_anchors(
    pivot: Pivot, anchors: list[tuple[int, float]], atr_at: float, cfg: SelectionConfig
) -> list[int]:
    """Indices of ALL human anchors this pivot is within ε of (ε_time bars, ε_price ATR units,
    causal ATR). Distance is used ONLY here for the label / coverage — it is NEVER a feature
    (LOCK S1 label-leakage guard)."""
    if atr_at <= 0 or not np.isfinite(atr_at):
        return []
    price_tol = cfg.eps_price_atr * atr_at
    return [
        h
        for h, (apos, aprice) in enumerate(anchors)
        if abs(pivot.index - apos) <= cfg.eps_time_bars and abs(pivot.price - aprice) <= price_tol
    ]


def build_pivot_candidates(
    df: pd.DataFrame,
    human_legs: list[Any],
    pivot_cfg: PivotConfig,
    scoring_cfg: ScoringConfig,
    cfg: SelectionConfig,
) -> tuple[list[PivotCandidate], set[int], int]:
    """Causal per-pivot candidates at the live viewport ``pivot + max(k, fractal_n)`` (LOCK S2).

    For every base pivot: truncate the frame at the cutoff, **re-detect pivots on the truncated
    frame** (so a pivot's existence is never look-ahead), confirm the pivot survives, and compute
    per-pivot features on that truncated pivot set. Returns ``(candidates, covered_anchor_idxs,
    n_anchors)`` — ``covered_anchor_idxs`` is the detection-coverage set (every human anchor within
    ε of ANY surfaced pivot), reported SEPARATELY from ranking (LOCK S6)."""
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    n = len(df)
    fractal_n = int(pivot_cfg.fractal_n)
    full_pivots = detect_pivots(df, pivot_cfg)
    anchors = _human_anchor_points(human_legs, index_ns)
    need_confluence = "scale_confluence" in stage1_feature_names(cfg.k)
    out: list[PivotCandidate] = []
    covered: set[int] = set()
    n_piv = len(full_pivots)
    _progress(f"  build_pivot_candidates: {n_piv} pivots, df={n} bars (per-pivot detect)")
    t0 = time.perf_counter()
    for i_piv, piv in enumerate(full_pivots):
        if (i_piv + 1) % 50 == 0 or i_piv + 1 == n_piv:
            _progress(f"    pivot {i_piv + 1}/{n_piv} ({time.perf_counter() - t0:.0f}s)")
        j = piv.index
        cutoff = j + max(cfg.k, fractal_n)
        if cutoff >= n:  # cannot be confirmed live within the data — skip (no peeking)
            continue
        df_t = df.iloc[: cutoff + 1]
        atr_arr = atr(df_t, period=cfg.atr_period).to_numpy()
        piv_t = detect_pivots(df_t, pivot_cfg)
        end_piv = next((q for q in piv_t if q.index == j and q.kind == piv.kind), None)
        if end_piv is None:  # dedupe/edge dropped it on the truncated frame — not live-confirmable
            continue
        multi_t = (
            detect_pivots_multi(df_t, pivot_cfg, scoring_cfg.confluence_degrees)
            if need_confluence
            else None
        )
        atr_at = float(atr_arr[j]) if 0 <= j < len(atr_arr) else float("nan")
        matched = _matched_anchors(end_piv, anchors, atr_at, cfg)
        covered.update(matched)
        out.append(
            PivotCandidate(
                pivot_pos=j,
                kind=end_piv.kind,
                chunk=i_piv // max(int(scoring_cfg.structure_window), 1),
                features=compute_pivot_features(end_piv, piv_t, multi_t, scoring_cfg),
                label=1 if matched else 0,
                human_anchor_idx=matched[0] if matched else -1,
                prominence_raw=float(end_piv.prominence),
            )
        )
    return out, covered, len(anchors)


# --- per-cell driver --------------------------------------------------------------------------


def run_stage1_cell(timeframe: str, k: int, cfg_in: SelectionConfig, settings: Any) -> dict:
    """One Stage-1 per-pivot cell. Reports detection-recall (coverage) SEPARATELY from the ranking
    lift = AP(model) − AP(prominence baseline), cluster-bootstrapped by structural chunk (LOCK
    S5/S6). k=0 is returned as a degenerate stub (empty usable feature set) — no build, no model."""
    cfg = replace(cfg_in, k=k)
    feat_names = stage1_feature_names(k)
    if not feat_names:  # k=0 degenerate (LOCK S3) — no usable feature, no mature baseline
        _progress(f"cell tf={timeframe} k={k}: DEGENERATE (empty usable feature set) — skipped")
        return {
            "timeframe": timeframe,
            "k": k,
            "degenerate": True,
            "reason": "empty usable feature set at k=0 (prominence k*=3 not mature; "
            "round_number interaction-only) — excluded from verdict (LOCK S3)",
            "features": [],
            "powered": False,
        }
    t_cell = time.perf_counter()
    _progress(f"cell START tf={timeframe} k={k} feats={feat_names}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    human_legs = load_human_legs(timeframe)
    cands, covered, n_anchors = build_pivot_candidates(
        df, human_legs, settings.pivots, settings.scoring, cfg
    )
    detection_recall = (len(covered) / n_anchors) if n_anchors else None

    n = len(df)
    split_idx = int(n * cfg.train_frac)
    reach = max(k, int(settings.pivots.fractal_n))  # forward feature reach (LOCK S2/S6)
    train, test = [], []
    for c in cands:
        win = window_of(c.pivot_pos, split_idx, n, reach)
        if win == "train":
            train.append(c)
        elif win == "test":
            test.append(c)

    def _xy(rows: list[PivotCandidate]) -> tuple[np.ndarray, np.ndarray]:
        if not rows:
            return np.zeros((0, len(feat_names))), np.zeros(0)
        x = np.array([[c.features[f] for f in feat_names] for c in rows], dtype=float)
        return x, np.array([c.label for c in rows], dtype=float)

    x_tr, y_tr = _xy(train)
    x_te, y_te = _xy(test)
    n_test_pos = int(y_te.sum())
    powered = n_test_pos >= cfg.min_test_positives

    ap_model = ap_base = lift = auc_model = None
    inference = model_weights = None
    if len(train) and len(test) and y_tr.sum() > 0 and y_te.sum() > 0:
        model = fit_logreg(x_tr, y_tr, cfg)  # train-only standardization inherited (LOCK S4 guard)
        model_weights = {f: float(w) for f, w in zip(feat_names, model["w"], strict=True)}
        p_model = predict_proba(model, x_te)
        ap_model = average_precision(y_te, p_model)
        auc_model = roc_auc(y_te, p_model)
        base = x_te[:, feat_names.index(BASELINE_FEATURE)]  # LOCK S5 single primary baseline
        ap_base = average_precision(y_te, base)
        if ap_model is not None and ap_base is not None:
            lift = ap_model - ap_base
        if powered:
            groups = np.array([c.chunk for c in test])  # structural-chunk cluster (LOCK S6)
            inference = decision_point_bootstrap(y_te, p_model, base, groups, cfg.n_boot, cfg.seed)
            if inference is not None:  # relabel: this is the structural-chunk unit, not anchor_b
                inference["method"] = "structural_chunk_cluster_bootstrap"
                inference["cluster_unit"] = "structure_window base-pivot chunk (LOCK S6)"

    _progress(
        f"cell DONE tf={timeframe} k={k} in {time.perf_counter() - t_cell:.0f}s "
        f"(test_pos={n_test_pos} powered={powered} recall={detection_recall} lift={lift})"
    )
    return {
        "timeframe": timeframe,
        "k": k,
        "degenerate": False,
        "features": feat_names,
        "n_pivots_universe": len(cands),
        "n_human_anchors": n_anchors,
        "detection_recall": detection_recall,  # COVERAGE half (LOCK S0.1) — separate from ranking
        "n_train": len(train),
        "n_test": len(test),
        "n_test_positives": n_test_pos,
        "powered": powered,
        "ap_model": ap_model,  # RANKING half (LOCK S0.2)
        "ap_baseline_prominence": ap_base,
        "ap_lift_vs_prominence": lift,
        "auc_model_secondary": auc_model,
        "model_weights_standardized": model_weights,
        "ranking_lift_inference": inference,
    }


def stage1_verdict(cell_primary: dict[str, Any]) -> str:
    """Locked Stage-1 verdict (LOCK S7), read from the 4h primary k=3 cell. Exact conditions:
    underpowered first; then coverage floor; then the ranking-lift CI."""
    if cell_primary.get("degenerate") or not cell_primary.get("powered"):
        return "inconclusive_underpowered"
    recall = cell_primary.get("detection_recall")
    if recall is not None and recall < RECALL_FLOOR:
        return "detector_coverage_limited"
    inf = cell_primary.get("ranking_lift_inference")
    if inf is None:
        return "inconclusive_underpowered"
    if inf["ci95_high"] < 0.0:  # prominence significantly beats the model
        return "artifact_check_needed"
    if inf["ci95_low"] > 0.0:  # lift CI excludes 0 above
        return "pivot_selection_learnable"
    return "no_pivot_signal_above_prominence"  # CI includes 0 — expected/publishable null


# --- checkpointed study -----------------------------------------------------------------------


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _run_or_load_cell(
    timeframe: str, k: int, cfg: SelectionConfig, settings: Any, ckpt_dir: Path
) -> dict:
    """Run one Stage-1 cell or load a same-seed checkpoint (atomic write), mirroring the W-gap
    resume pattern so an interrupted run loses at most the in-flight cell."""
    path = ckpt_dir / f"{timeframe}_k{k}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("seed") == cfg.seed:
            _progress(f"RESUME tf={timeframe} k={k}: loaded checkpoint {path.name}")
            return saved["cell"]
        _progress(f"stale ckpt {path.name}: seed {saved.get('seed')}!={cfg.seed}, recompute")
    result = run_stage1_cell(timeframe, k, cfg, settings)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(
            {"seed": cfg.seed, "cell": result}, indent=2, sort_keys=True, default=_json_default
        ),
        encoding="utf-8",
    )
    tmp.replace(path)
    _progress(f"checkpoint written {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))["cell"]


def run_stage1_study(
    config_path: str | None, cfg: SelectionConfig, ckpt_dir: Path | None = None
) -> dict:
    """Stage-1 per-pivot diagnostic. 4h primary over the k-sweep {0,3,6,12} (k=0 degenerate);
    1M/1w/1d at primary k=3 as underpowered context only (LOCK S6). Verdict from the 4h k=3 cell.
    Checkpoints each cell so the ~2-3h study resumes without recomputing finished cells."""
    settings = load_settings(config_path) if config_path else load_settings()
    if ckpt_dir is None:
        ckpt_dir = RESULTS_DIR / "stage1" / "cells"
    primary = [_run_or_load_cell("4h", k, cfg, settings, ckpt_dir) for k in STAGE1_K_SWEEP]
    context = [
        _run_or_load_cell(tf, PRIMARY_K, cfg, settings, ckpt_dir) for tf in CONTEXT_TIMEFRAMES
    ]
    cell_k3 = next((c for c in primary if c.get("k") == PRIMARY_K), {})
    return {
        "generated_by": "fib_selection_learning_stage1",
        "stage": "stage1_per_pivot_diagnostic",
        "metric": "pooled_test_average_precision",
        "ranking_definition": "lift = AP(model) - AP(prominence baseline) on identical test pivots",
        "coverage_definition": "detection_recall = human anchors (a/b pooled) within eps of any "
        "detected pivot / unique human anchors — reported SEPARATELY from ranking (LOCK S6)",
        "seed": cfg.seed,
        "primary_timeframe": "4h",
        "primary_k": PRIMARY_K,
        "k_sweep": list(STAGE1_K_SWEEP),
        "stage1_verdict": stage1_verdict(cell_k3),
        "results_4h": primary,
        "results_context_underpowered": context,
    }


def print_stage1(report: dict, path: Any) -> None:
    groups = (("4h", report["results_4h"]), ("ctx", report["results_context_underpowered"]))
    for label, rows in groups:
        for r in rows:
            if r.get("degenerate"):
                print(f"[{label} tf={r['timeframe']} k={r['k']}] DEGENERATE — {r['reason']}")
                continue
            print(
                f"[{label} tf={r['timeframe']} k={r['k']}] feats={r['features']} "
                f"universe={r['n_pivots_universe']} anchors={r['n_human_anchors']} "
                f"recall={r['detection_recall']} | n_test={r['n_test']} "
                f"test_pos={r['n_test_positives']} powered={r['powered']}"
            )
            print(
                f"    RANKING ap_model={r['ap_model']} ap_prom={r['ap_baseline_prominence']} "
                f"lift={r['ap_lift_vs_prominence']} auc={r['auc_model_secondary']}"
            )
            print(f"    lift_inf={r['ranking_lift_inference']}")
            print(f"    weights={r['model_weights_standardized']}")
    print(f"stage1_verdict={report['stage1_verdict']}  summary={path}")


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=_json_default), encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    for _s in (sys.stdout, sys.stderr):  # UTF-8 console (multi-hour run safety)
        _rc = getattr(_s, "reconfigure", None)
        if _rc is not None:
            _rc(encoding="utf-8")
    ap = argparse.ArgumentParser(description="BTC Fib selection-learning Stage-1 per-pivot")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR / "stage1"))
    ap.add_argument("--stage1", action="store_true", help="run the per-pivot diagnostic study")
    ap.add_argument(
        "--stage1-preflight",
        action="store_true",
        help="frozen-data parity + facit fail-fast (reuses W-gap preflight; no run)",
    )
    args = ap.parse_args(argv)
    if args.stage1_preflight:
        return run_preflight(args.config)
    if args.stage1:
        report = run_stage1_study(args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out))
        print_stage1(report, path)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
