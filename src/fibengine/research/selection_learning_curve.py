"""BTC Fib SELECTION-LEARNING — learning-curve diagnostic (facit data-sensitivity).

Is the current Stage-2 selection model **data-starved or saturated** w.r.t. facit size — i.e. would
more human-labeled 4h legs plausibly raise pooled OOS Average Precision against the human facit? A
**data-sensitivity diagnostic** toward the north star (does the engine select legs like the human),
fixed blind in the learning-curve LOCK before any AP at any fraction existed:
  docs/research_wiki/reviews/btc-fib-selection-learning-learning-curve-lock-20260625.md

Method (LOCK L2/L3): reuse the Stage-2 cell **verbatim** (universe, ε, purged split, the 5 live
features, the interpretable logreg, pooled AP); **fix the held-out test set** so AP is comparable
across fractions; **vary only the training facit** — drop whole human legs and relabel train rows
(a train candidate is positive iff it ε-matches a *retained* human leg). **Build-once-vary-labels:**
the candidate universe and feature matrices are built once; per (fraction, repeat) only the train
labels, the logreg fit, and the test AP recompute.

Verdict is ASYMMETRIC (LOCK L4): the Stage-2 lift is carried almost entirely by ONE feature
(``cleanliness``) → ≈1 effective parameter → **saturation is the EXPECTED default**. So a flat curve
means "this 1-feature model is capacity-bound → back to the feature/crux", NOT "don't grow facit".
Only a curve still rising at full facit (``data_starved``) is a genuine green light. With 65 test
positives ``inconclusive_underpowered`` is a live, likely outcome.

**Diagnostic only — no edge / behaviour / PnL / backtest / Genesis / auto-fib-as-truth / 1H / ETH
/ label-mutation (LOCK L7).** Does NOT resolve the ``cleanliness`` crux. Frozen data, no refresh.

Run (own CLI):
    uv run python -m fibengine.research.selection_learning_curve --curve-preflight
    uv run python -m fibengine.research.selection_learning_curve --curve
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

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.research.selection_learning import (
    PRIMARY_K,
    RESULTS_DIR,
    Candidate,
    SelectionConfig,
    _progress,
    average_precision,
    build_candidates,
    fit_logreg,
    live_feature_names,
    load_human_legs,
    predict_proba,
    roc_auc,
    window_of,
)
from fibengine.research.selection_learning_gap import run_preflight

# LOCK L3: finer grid near the top — the local slope at f=1.0 is what speaks to "would the NEXT
# labels help". f=1.0 is the single full-facit point (deterministic; reproduces the Stage-2 AP).
FRACTIONS: tuple[float, ...] = (0.25, 0.50, 0.75, 0.80, 0.90, 0.95, 1.00)
REPEATS = 64  # independent subsamples per fraction (<1.0); build is once, relabel+refit is cheap
CONTEXT_TIMEFRAMES = ("1M", "1w", "1d")  # underpowered context only (LOCK L2), at primary k=3
_FTOL = 1e-9


def _seed_for(base_seed: int, frac_idx: int, repeat: int) -> int:
    """Deterministic per-(fraction, repeat) seed (LOCK L3): base + frac_idx*1000 + repeat."""
    return base_seed + frac_idx * 1000 + repeat


def _band_halfwidth(stats: dict[str, Any]) -> float:
    """Half the [p5, p95] AP band for a fraction — the which-legs-dropped train-subsample noise."""
    return (stats["ap_p95"] - stats["ap_p5"]) / 2.0


def _frac_stats(per_fraction: list[dict[str, Any]], frac: float) -> dict[str, Any] | None:
    return next((s for s in per_fraction if abs(s["fraction"] - frac) < _FTOL), None)


# --- per-cell driver (build once, vary only the training-facit fraction) -----------------------


def run_curve_cell(timeframe: str, k: int, cfg_in: SelectionConfig, settings: Any) -> dict:
    """One learning-curve cell. Build the candidate universe + feature matrices ONCE; the held-out
    test set is FIXED (full facit labels). For each fraction f and repeat r, retain ``round(f *
    n_train_legs)`` whole human legs (uniform, no replacement, seeded), relabel the train rows,
    refit the 5-feature logreg, recompute pooled test AP on the fixed test set (LOCK L2/L3)."""
    cfg = replace(cfg_in, k=k)
    t_cell = time.perf_counter()
    feat_names = live_feature_names(k)
    _progress(f"cell START tf={timeframe} k={k} features={feat_names}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    human_legs = load_human_legs(timeframe)
    cands = build_candidates(df, human_legs, settings.pivots, settings.scoring, cfg)

    n = len(df)
    split_idx = int(n * cfg.train_frac)
    reach = cfg.k  # live viewport — Stage-2 parity (no W embargo)
    train, test = [], []
    for c in cands:
        win = window_of(c.anchor_b_pos, split_idx, n, reach)
        if win == "train":
            train.append(c)
        elif win == "test":
            test.append(c)

    def _x(rows: list[Candidate]) -> np.ndarray:
        if not rows:
            return np.zeros((0, len(feat_names)))
        return np.array([[c.features[f] for f in feat_names] for c in rows], dtype=float)

    # FIXED test set (full facit labels — never subsampled, LOCK L2)
    x_te = _x(test)
    y_te = np.array([c.label for c in test], dtype=float)
    x_tr = _x(train)  # feature matrix fixed; only labels vary across subsamples
    tr_human_idx = np.array([c.human_idx for c in train], dtype=int)  # -1 = negative row
    train_legs = sorted({int(h) for h in tr_human_idx if h >= 0})  # facit legs in the train period
    n_train_legs = len(train_legs)
    n_test_pos = int(y_te.sum())
    powered = n_test_pos >= cfg.min_test_positives

    matched_humans = {c.human_idx for c in cands if c.human_idx >= 0}
    reachable_fraction = len(matched_humans) / len(human_legs) if human_legs else None

    per_fraction: list[dict[str, Any]] = []
    can_run = bool(len(train) and len(test) and n_test_pos > 0 and n_train_legs > 0)
    if can_run:
        legs_arr = np.array(train_legs, dtype=int)
        for f_idx, frac in enumerate(FRACTIONS):
            n_retain = max(0, min(n_train_legs, round(frac * n_train_legs)))
            full = frac >= 1.0 - _FTOL
            reps = 1 if full else REPEATS  # f=1.0 is the deterministic single full-facit point
            aps: list[float] = []
            aucs: list[float] = []
            n_pos_list: list[int] = []
            for r in range(reps):
                if full:
                    retained = set(train_legs)
                else:
                    rng = np.random.default_rng(_seed_for(cfg.seed, f_idx, r))
                    picked = rng.choice(legs_arr, size=n_retain, replace=False)
                    retained = {int(x) for x in picked}
                y_tr = np.array(
                    [1.0 if (h >= 0 and int(h) in retained) else 0.0 for h in tr_human_idx],
                    dtype=float,
                )
                n_pos_list.append(int(y_tr.sum()))
                model = fit_logreg(x_tr, y_tr, cfg)
                p_te = predict_proba(model, x_te)
                ap = average_precision(y_te, p_te)
                auc = roc_auc(y_te, p_te)
                if ap is not None:
                    aps.append(ap)
                if auc is not None:
                    aucs.append(auc)
            ap_arr = np.array(aps, dtype=float)
            per_fraction.append(
                {
                    "fraction": float(frac),
                    "repeats": reps,
                    "n_retain": int(n_retain),
                    "n_train_pos_mean": float(np.mean(n_pos_list)) if n_pos_list else None,
                    "ap_mean": float(ap_arr.mean()) if ap_arr.size else None,
                    "ap_p5": float(np.percentile(ap_arr, 5)) if ap_arr.size else None,
                    "ap_p95": float(np.percentile(ap_arr, 95)) if ap_arr.size else None,
                    "ap_std": float(ap_arr.std()) if ap_arr.size else None,
                    "auc_mean": float(np.mean(aucs)) if aucs else None,
                }
            )
            _progress(
                f"  f={frac:.2f} reps={reps} n_retain={n_retain} "
                f"ap_mean={per_fraction[-1]['ap_mean']}"
            )

    full_stats = _frac_stats(per_fraction, 1.0)
    _progress(
        f"cell DONE tf={timeframe} k={k} in {time.perf_counter() - t_cell:.0f}s "
        f"(test_pos={n_test_pos} powered={powered} "
        f"ap_full={full_stats['ap_mean'] if full_stats else None})"
    )
    return {
        "timeframe": timeframe,
        "k": k,
        "features": feat_names,
        "n_bars": n,
        "n_human_legs": len(human_legs),
        "n_candidates": len(cands),
        "n_train": len(train),
        "n_test": len(test),
        "n_test_positives": n_test_pos,
        "n_train_legs": n_train_legs,  # facit legs available to subsample in the train period
        "reachable_fraction": reachable_fraction,
        "powered": powered,
        "repeats": REPEATS,
        "fractions": list(FRACTIONS),
        "per_fraction": per_fraction,
        "ap_full_facit": full_stats["ap_mean"] if full_stats else None,
        # LOCK L6 addable-supply context (reported, not a gate)
        "addable_supply": {
            "labeled_human_legs": len(human_legs),
            "candidate_universe": len(cands),
            "train_period_facit_legs": n_train_legs,
            "note": "true human-meaningful count needs a human pass; capped by available history",
        },
    }


def curve_verdict(cell: dict[str, Any]) -> str:
    """ASYMMETRIC blind verdict (LOCK L4), read from the 4h primary. Reads DIFFERENCES of fraction
    means against the f=0.95 train-subsample band (LOCK L5), not absolute AP levels.

    - ``inconclusive_underpowered`` — not powered, or the f=0.95 band half-width is >= the full
      spread of fraction means (per-fraction noise dwarfs the curve; likely at 65 test positives).
    - ``data_starved`` — ``AP(1.0) − AP(0.95)`` exceeds the f=0.95 band half-width and the curve is
      increasing: genuinely informative green light (more facit helps even this 1-feature model).
    - ``saturated`` — last increment within the band (flat): ambiguous AND EXPECTED → routes to the
      feature / ``cleanliness`` crux, NOT away from labeling.
    """
    if not cell.get("powered"):
        return "inconclusive_underpowered"
    per = cell.get("per_fraction") or []
    s_top = _frac_stats(per, 1.0)
    s_95 = _frac_stats(per, 0.95)
    means = [s["ap_mean"] for s in per if s.get("ap_mean") is not None]
    if s_top is None or s_95 is None or s_top["ap_mean"] is None or len(means) < 2:
        return "inconclusive_underpowered"
    spread = max(means) - min(means)
    hw95 = _band_halfwidth(s_95)
    if hw95 >= spread:  # noise dominates the whole curve range
        return "inconclusive_underpowered"
    last_increment = s_top["ap_mean"] - s_95["ap_mean"]
    if last_increment > hw95 and s_top["ap_mean"] > s_95["ap_mean"]:
        return "data_starved"
    return "saturated"


# --- checkpointed study -----------------------------------------------------------------------


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _run_or_load_cell(
    timeframe: str, k: int, cfg: SelectionConfig, settings: Any, ckpt_dir: Path
) -> dict:
    """Run one cell or load a same-seed checkpoint (atomic write), mirroring the enrich/W-gap resume
    pattern so an interrupted long 4h build loses at most the in-flight cell."""
    path = ckpt_dir / f"{timeframe}_k{k}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("seed") == cfg.seed:
            _progress(f"RESUME tf={timeframe} k={k}: loaded checkpoint {path.name}")
            return saved["cell"]
        _progress(f"stale ckpt {path.name}: seed {saved.get('seed')}!={cfg.seed}, recompute")
    result = run_curve_cell(timeframe, k, cfg, settings)
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


def run_curve_study(
    config_path: str | None, cfg: SelectionConfig, ckpt_dir: Path | None = None
) -> dict:
    """Learning-curve study (LOCK L2): 4h primary at k=3 (the single powered, verdict-bearing cell);
    1M/1w/1d at k=3 as underpowered context only, never refuted. Verdict from the 4h k=3 cell."""
    settings = load_settings(config_path) if config_path else load_settings()
    if ckpt_dir is None:
        ckpt_dir = RESULTS_DIR / "curve" / "cells"
    primary = _run_or_load_cell("4h", PRIMARY_K, cfg, settings, ckpt_dir)
    context = [
        _run_or_load_cell(tf, PRIMARY_K, cfg, settings, ckpt_dir) for tf in CONTEXT_TIMEFRAMES
    ]
    return {
        "generated_by": "fib_selection_learning_curve",
        "stage": "facit_data_sensitivity_learning_curve",
        "metric": "pooled_test_average_precision",
        "design": "fixed test set; vary only training-facit fraction (whole legs); build-once",
        "seed": cfg.seed,
        "primary_timeframe": "4h",
        "primary_k": PRIMARY_K,
        "learning_curve_verdict": curve_verdict(primary),
        "results_4h_primary": primary,
        "results_context_underpowered": context,
    }


def print_curve(report: dict, path: Any) -> None:
    rows = [("4h", report["results_4h_primary"])]
    rows += [("ctx", c) for c in report["results_context_underpowered"]]
    for label, r in rows:
        print(
            f"[{label} tf={r['timeframe']} k={r['k']}] n_cands={r['n_candidates']} "
            f"n_train_legs={r['n_train_legs']} test_pos={r['n_test_positives']} "
            f"powered={r['powered']} ap_full={r['ap_full_facit']}"
        )
        for s in r["per_fraction"]:
            print(
                f"    f={s['fraction']:.2f} reps={s['repeats']} n_retain={s['n_retain']} "
                f"n_pos~{s['n_train_pos_mean']} ap_mean={s['ap_mean']} "
                f"[p5={s['ap_p5']}, p95={s['ap_p95']}] auc={s['auc_mean']}"
            )
        print(f"    addable_supply={r['addable_supply']}")
    print(f"learning_curve_verdict={report['learning_curve_verdict']}  summary={path}")


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
    ap = argparse.ArgumentParser(description="BTC Fib selection-learning learning-curve diagnostic")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR / "curve"))
    ap.add_argument("--curve", action="store_true", help="run the facit learning-curve diagnostic")
    ap.add_argument(
        "--curve-preflight",
        action="store_true",
        help="frozen-data parity + facit fail-fast (reuses W-gap preflight; no run)",
    )
    args = ap.parse_args(argv)
    if args.curve_preflight:
        return run_preflight(args.config)
    if args.curve:
        report = run_curve_study(args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out))
        print_curve(report, path)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
