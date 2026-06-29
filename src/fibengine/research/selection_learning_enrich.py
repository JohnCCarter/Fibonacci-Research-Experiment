"""BTC Fib SELECTION-LEARNING — model-ENRICHMENT shot (leg-completeness / ``exclusivity``).

The single directly north-star-aligned modeling step left: does adding ONE causal
leg-completeness / ``exclusivity`` feature raise pooled OOS Average Precision against the human
facit **over the CURRENT Stage-2 model** (nested, not the trivial baseline) on the 4h primary at
live ``k = 3``? One feature, one operationalization, one nested baseline, one blind verdict — all
fixed in the enrichment LOCK before any enriched value existed:
  docs/research_wiki/reviews/btc-fib-selection-learning-enrichment-lock-20260624.md

``exclusivity`` is **pivot-structural** (counts only *detected* interior counter-retracements, not
raw close-to-close path) — this is what makes it distinct from ``cleanliness`` (net ÷ total path).
A human analyst anchors a fib on a *complete* impulse, not a fragment interrupted by a deep
counter-move. A lift means only that ``exclusivity`` adds OOS ranking signal over the current
model — **NOT** a reproduction of human selection, and **no edge / behaviour / PnL / backtest /
Genesis / auto-fib-as-truth / 1H / ETH / label-mutation** (LOCK E7). A clean
``no_enrichment_signal`` is the **expected, publishable** outcome and routes (LOCK E8) to growing
the facit, not to more per-leg features.

Shared machinery (candidate universe, the interpretable model + AP/AUC, the decision-point cluster
bootstrap, ε, the frozen-data preflight) is imported **verbatim** from ``selection_learning`` /
``selection_learning_gap``; this module owns only the ``exclusivity`` column + the nested AP-lift
comparison (LOCK E9 — no code added to byte-capped ``selection_learning.py``).

Run (own CLI):
    uv run python -m fibengine.research.selection_learning_enrich --enrich-preflight
    uv run python -m fibengine.research.selection_learning_enrich --enrich
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import PivotConfig, load_settings
from fibengine.core.models import Pivot
from fibengine.data.loader import load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.selection_learning import (
    PRIMARY_K,
    RESULTS_DIR,
    Candidate,
    SelectionConfig,
    _progress,
    average_precision,
    build_candidates,
    decision_point_bootstrap,
    fit_logreg,
    live_feature_names,
    load_human_legs,
    predict_proba,
    roc_auc,
    window_of,
)
from fibengine.research.selection_learning_gap import run_preflight

ENRICH_FEATURE = "exclusivity"  # LOCK E1: the ONE new feature (locked, no formula swapping)
CONTEXT_TIMEFRAMES = ("1M", "1w", "1d")  # underpowered context only (LOCK E3), at primary k=3


def enrich_feature_names(k: int) -> list[str]:
    """Enriched input features at confirmation buffer ``k`` = the CURRENT Stage-2 live feature set
    (``live_feature_names(k)`` — the nested baseline, LOCK E2) **plus** ``exclusivity``.
    At k=3: [cleanliness, duration, magnitude, prominence, structure_alignment, exclusivity]."""
    return [*live_feature_names(k), ENRICH_FEATURE]


# --- the new feature: causal leg-completeness / exclusivity (LOCK E1) --------------------------


def exclusivity_value(
    interior: list[Pivot], a_price: float, b_price: float, direction: str
) -> float:
    """``exclusivity = clip(1 − R / net, 0, 1)`` (1 = dominant/complete leg; →0 = interrupted).

    ``net = |b_price − a_price|`` is the leg magnitude. ``R`` is the deepest interior structural
    counter-retracement reached by a **detected opposite-kind pivot** strictly between the anchors
    (LOCK E1): for an up-leg (a=low, b=high), among interior detected LOW pivots,
    ``R = max(running_interior_high_before_low − low_price)``; symmetric for a down-leg. No interior
    counter-move → ``R = 0`` (uninterrupted single impulse → exclusivity 1).

    Pivot-structural by construction (only *detected* retracements, not raw path) — the property
    that makes it distinct from ``cleanliness``. ``interior`` must be index-ascending.
    """
    net = abs(b_price - a_price)
    if not np.isfinite(net) or net <= 0:  # degenerate leg (cannot occur for distinct anchors)
        return 0.0
    reach = 0.0
    if direction == "up":  # counter-move = a pullback: interior high, then a lower interior low
        running_high: float | None = None
        for q in interior:
            if q.kind == "high":
                running_high = q.price if running_high is None else max(running_high, q.price)
            elif running_high is not None:  # an interior low with a preceding interior peak
                reach = max(reach, running_high - q.price)
    else:  # down-leg: counter-move = a bounce: interior low, then a higher interior high
        running_low: float | None = None
        for q in interior:
            if q.kind == "low":
                running_low = q.price if running_low is None else min(running_low, q.price)
            elif running_low is not None:
                reach = max(reach, q.price - running_low)
    return float(np.clip(1.0 - reach / net, 0.0, 1.0))


def build_exclusivity(
    df: pd.DataFrame,
    live_cands: list[Candidate],
    pivot_cfg: PivotConfig,
    cfg: SelectionConfig,
) -> tuple[dict[tuple[int, int], float], dict[str, int]]:
    """``exclusivity`` for the **same rows** as ``live_cands``, on the identical frame truncated at
    ``anchor_b + k`` and re-detected with ``detect_pivots`` (LOCK E1 causal viewport — every
    interior pivot is ``< anchor_b``, so this is causal at ``k* = 3``, same maturity as the baseline
    k≤3 set). Mirrors ``build_retro_features``: group by endpoint, detect once per endpoint, rebuild
    each (start→end) pair from the truncated pivot set. Returns ``{(anchor_b_pos, start_pos):
    exclusivity}`` + exclusion counts (rows whose endpoint/start cannot be reconstructed — expected
    empty since the universe is identical to ``build_candidates``)."""
    n = len(df)
    out: dict[tuple[int, int], float] = {}
    excl_endpoint_rows = 0  # endpoint's anchor_b+k runs past the data
    excl_pivot_rows = 0  # endpoint/start pivot not reconstructible on the truncated frame
    by_end: dict[int, list[Candidate]] = {}
    for c in live_cands:
        by_end.setdefault(c.anchor_b_pos, []).append(c)
    n_end = len(by_end)
    _progress(f"  build_exclusivity: {n_end} endpoints (per-endpoint truncated detect)")
    t0 = time.perf_counter()
    for i_end, (j, group) in enumerate(by_end.items(), start=1):
        if i_end % 20 == 0 or i_end == n_end:
            _progress(f"    endpoint {i_end}/{n_end} ({time.perf_counter() - t0:.0f}s elapsed)")
        end_view = j + cfg.k
        if end_view >= n:  # not live-confirmable within the data — exclude (no peeking)
            excl_endpoint_rows += len(group)
            continue
        df_t = df.iloc[: end_view + 1]
        piv_t = detect_pivots(df_t, pivot_cfg)
        end_piv = next((q for q in piv_t if q.index == j), None)
        if end_piv is None:  # dedupe/edge dropped it — not live-confirmable
            excl_pivot_rows += len(group)
            continue
        for c in group:
            start = next(
                (q for q in piv_t if q.index == c.start_pos and q.kind != end_piv.kind), None
            )
            if start is None:
                excl_pivot_rows += 1
                continue
            interior = sorted(
                (q for q in piv_t if start.index < q.index < end_piv.index), key=lambda q: q.index
            )
            direction = "up" if end_piv.price > start.price else "down"
            out[(j, c.start_pos)] = exclusivity_value(
                interior, start.price, end_piv.price, direction
            )
    excl = {
        "rows_excluded_endpoint_beyond_data": excl_endpoint_rows,
        "rows_excluded_pivot_not_reconstructible": excl_pivot_rows,
    }
    return out, excl


# --- per-cell driver --------------------------------------------------------------------------


def _train_corr(x_excl: np.ndarray, x_clean: np.ndarray) -> float | None:
    """``corr(exclusivity, cleanliness)`` on the TRAIN fold (LOCK E1 distinctness check — reported,
    NOT a gate). Near ±1 ⇒ exclusivity is largely a cleanliness proxy; the verdict still rests on
    the nested AP-lift (E4). None when either column is constant (corr undefined)."""
    if x_excl.size == 0 or x_excl.std() == 0 or x_clean.std() == 0:
        return None
    return float(np.corrcoef(x_excl, x_clean)[0, 1])


def run_enrich_cell(timeframe: str, k: int, cfg_in: SelectionConfig, settings: Any) -> dict:
    """One enrichment cell: AP-lift = AP(enriched) − AP(baseline) on the **identical** test legs
    (nested; both models trained once on the same train rows, then held fixed). Baseline = current
    Stage-2 model (LOCK E2); enriched = baseline + ``exclusivity``. Decision-point cluster bootstrap
    by ``anchor_b`` group (LOCK E4). Universe / ε / split / metric reused verbatim from Stage-2."""
    cfg = replace(cfg_in, k=k)
    t_cell = time.perf_counter()
    base_names = live_feature_names(k)
    enr_names = enrich_feature_names(k)
    _progress(f"cell START tf={timeframe} k={k} base={base_names} +{ENRICH_FEATURE}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    human_legs = load_human_legs(timeframe)
    cands = build_candidates(df, human_legs, settings.pivots, settings.scoring, cfg)
    excl_map, excl = build_exclusivity(df, cands, settings.pivots, cfg)
    paired = [c for c in cands if (c.anchor_b_pos, c.start_pos) in excl_map]

    n = len(df)
    split_idx = int(n * cfg.train_frac)
    reach = cfg.k  # live viewport — Stage-2 parity (no W embargo here)
    train, test = [], []
    for c in paired:
        win = window_of(c.anchor_b_pos, split_idx, n, reach)
        if win == "train":
            train.append(c)
        elif win == "test":
            test.append(c)

    def _xy(rows: list[Candidate], names: list[str]) -> tuple[np.ndarray, np.ndarray]:
        if not rows:
            return np.zeros((0, len(names))), np.zeros(0)
        cols = []
        for c in rows:
            ex = excl_map[(c.anchor_b_pos, c.start_pos)]
            cols.append([(ex if f == ENRICH_FEATURE else c.features[f]) for f in names])
        return np.array(cols, dtype=float), np.array([c.label for c in rows], dtype=float)

    n_test_pos = int(sum(c.label for c in test))
    powered = n_test_pos >= cfg.min_test_positives

    # descriptive distribution of the new feature over the paired universe (E1 spirit):
    # a near-constant exclusivity (most legs pinned at 1.0) explains a null as no-variance,
    # not as no-signal — reported, never a gate.
    excl_vals = np.array([excl_map[(c.anchor_b_pos, c.start_pos)] for c in paired], dtype=float)
    excl_dist = {
        "n": int(excl_vals.size),
        "mean": float(excl_vals.mean()) if excl_vals.size else None,
        "std": float(excl_vals.std()) if excl_vals.size else None,
        "frac_at_1": float(np.mean(excl_vals == 1.0)) if excl_vals.size else None,
        "frac_at_0": float(np.mean(excl_vals == 0.0)) if excl_vals.size else None,
    }

    ap_base = ap_enr = lift = auc_enr = None
    inference = model_weights = None
    excl_clean_train_corr = None
    if len(train) and len(test):
        x_tr_b, y_tr = _xy(train, base_names)
        x_te_b, y_te = _xy(test, base_names)
        if y_tr.sum() > 0 and y_te.sum() > 0:
            x_tr_e, _ = _xy(train, enr_names)
            x_te_e, _ = _xy(test, enr_names)
            m_base = fit_logreg(x_tr_b, y_tr, cfg)
            m_enr = fit_logreg(x_tr_e, y_tr, cfg)
            p_base = predict_proba(m_base, x_te_b)
            p_enr = predict_proba(m_enr, x_te_e)
            ap_base = average_precision(y_te, p_base)
            ap_enr = average_precision(y_te, p_enr)
            auc_enr = roc_auc(y_te, p_enr)
            if ap_base is not None and ap_enr is not None:
                lift = ap_enr - ap_base
            model_weights = {f: float(w) for f, w in zip(enr_names, m_enr["w"], strict=True)}
            # distinctness: corr on the train fold (E1 — reported, not a gate)
            excl_clean_train_corr = _train_corr(
                x_tr_e[:, enr_names.index(ENRICH_FEATURE)],
                x_tr_e[:, enr_names.index("cleanliness")],
            )
            if powered:
                groups = np.array([c.anchor_b_pos for c in test])  # decision-point clusters (E4)
                inference = decision_point_bootstrap(
                    y_te, p_enr, p_base, groups, cfg.n_boot, cfg.seed
                )

    _progress(
        f"cell DONE tf={timeframe} k={k} in {time.perf_counter() - t_cell:.0f}s "
        f"(test_pos={n_test_pos} powered={powered} lift={lift})"
    )
    return {
        "timeframe": timeframe,
        "k": k,
        "baseline_features": base_names,  # LOCK E2: the CURRENT Stage-2 model
        "enriched_features": enr_names,
        "n_candidates": len(cands),
        "n_paired_rows": len(paired),
        "n_rows_excluded": len(cands) - len(paired),
        "exclusions": excl,
        "n_train": len(train),
        "n_test": len(test),
        "n_test_positives": n_test_pos,
        "powered": powered,
        "ap_baseline_stage2": ap_base,
        "ap_enriched": ap_enr,
        "ap_lift_vs_stage2": lift,  # nested lift = AP(enriched) − AP(baseline)
        "exclusivity_distribution": excl_dist,  # variance sanity (distinguishes null causes)
        "auc_enriched_secondary": auc_enr,
        "model_weights_standardized": model_weights,  # E1/E4: exclusivity weight vs cleanliness
        "exclusivity_cleanliness_train_corr": excl_clean_train_corr,  # E1 distinctness (not a gate)
        "ap_lift_inference": inference,  # decision-point cluster bootstrap of the nested lift
    }


def enrich_verdict(cell_primary: dict[str, Any]) -> str:
    """Locked blind verdict (LOCK E4), read from the 4h primary k=3 cell. ``enrichment_helps`` (CI
    excludes 0 above) / ``no_enrichment_signal`` (CI includes 0 — expected, routes to facit growth,
    E8) / ``enriched_worse_check`` (CI excludes 0 below — investigate, not a finding)."""
    if cell_primary.get("degenerate") or not cell_primary.get("powered"):
        return "inconclusive_underpowered"
    inf = cell_primary.get("ap_lift_inference")
    if inf is None:
        return "inconclusive_underpowered"
    if inf["ci95_high"] < 0.0:
        return "enriched_worse_check"
    if inf["ci95_low"] > 0.0:
        return "enrichment_helps"
    return "no_enrichment_signal"


# --- checkpointed study -----------------------------------------------------------------------


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _run_or_load_cell(
    timeframe: str, k: int, cfg: SelectionConfig, settings: Any, ckpt_dir: Path
) -> dict:
    """Run one cell or load a same-seed checkpoint (atomic write), mirroring the W-gap / Stage-1
    resume pattern so an interrupted long 4h run loses at most the in-flight cell."""
    path = ckpt_dir / f"{timeframe}_k{k}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("seed") == cfg.seed:
            _progress(f"RESUME tf={timeframe} k={k}: loaded checkpoint {path.name}")
            return saved["cell"]
        _progress(f"stale ckpt {path.name}: seed {saved.get('seed')}!={cfg.seed}, recompute")
    result = run_enrich_cell(timeframe, k, cfg, settings)
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


def run_enrich_study(
    config_path: str | None, cfg: SelectionConfig, ckpt_dir: Path | None = None
) -> dict:
    """Enrichment shot (LOCK E3): 4h primary at k=3 only (the single powered, verdict-bearing cell);
    1M/1w/1d at k=3 as **underpowered context only**, never refuted. Verdict from the 4h k=3 cell.
    Checkpoints each cell so the long 4h build resumes without recomputing finished cells."""
    settings = load_settings(config_path) if config_path else load_settings()
    if ckpt_dir is None:
        ckpt_dir = RESULTS_DIR / "enrich" / "cells"
    primary = _run_or_load_cell("4h", PRIMARY_K, cfg, settings, ckpt_dir)
    context = [
        _run_or_load_cell(tf, PRIMARY_K, cfg, settings, ckpt_dir) for tf in CONTEXT_TIMEFRAMES
    ]
    return {
        "generated_by": "fib_selection_learning_enrich",
        "stage": "model_enrichment_leg_completeness",
        "metric": "pooled_test_average_precision",
        "feature_added": ENRICH_FEATURE,
        "baseline": "current Stage-2 model (nested, NOT the trivial baseline) — LOCK E2",
        "lift_definition": "lift = AP(enriched) - AP(baseline) on identical test legs (nested)",
        "seed": cfg.seed,
        "primary_timeframe": "4h",
        "primary_k": PRIMARY_K,
        "enrichment_verdict": enrich_verdict(primary),
        "results_4h_primary": primary,
        "results_context_underpowered": context,
    }


def print_enrich(report: dict, path: Any) -> None:
    rows = [("4h", report["results_4h_primary"])]
    rows += [("ctx", c) for c in report["results_context_underpowered"]]
    for label, r in rows:
        print(
            f"[{label} tf={r['timeframe']} k={r['k']}] "
            f"paired={r['n_paired_rows']}/{r['n_candidates']} excl={r['n_rows_excluded']} "
            f"test_pos={r['n_test_positives']} powered={r['powered']} "
            f"ap_base={r['ap_baseline_stage2']} ap_enr={r['ap_enriched']} "
            f"lift={r['ap_lift_vs_stage2']}"
        )
        print(
            f"    excl={r['exclusions']} excl_clean_corr={r['exclusivity_cleanliness_train_corr']}"
        )
        print(f"    excl_dist={r['exclusivity_distribution']}")
        print(f"    lift_inf={r['ap_lift_inference']}")
        print(f"    weights={r['model_weights_standardized']}")
    print(f"enrichment_verdict={report['enrichment_verdict']}  summary={path}")


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=_json_default), encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    for _s in (sys.stdout, sys.stderr):  # UTF-8 console (long-run safety)
        _rc = getattr(_s, "reconfigure", None)
        if _rc is not None:
            _rc(encoding="utf-8")
    ap = argparse.ArgumentParser(description="BTC Fib selection-learning model-enrichment shot")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR / "enrich"))
    ap.add_argument("--enrich", action="store_true", help="run the leg-completeness shot")
    ap.add_argument(
        "--enrich-preflight",
        action="store_true",
        help="frozen-data parity + facit fail-fast (reuses W-gap preflight; no run)",
    )
    args = ap.parse_args(argv)
    if args.enrich_preflight:
        return run_preflight(args.config)
    if args.enrich:
        report = run_enrich_study(args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out))
        print_enrich(report, path)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
