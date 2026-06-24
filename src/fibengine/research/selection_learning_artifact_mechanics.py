"""BTC Fib SELECTION-LEARNING — artifact-probe MECHANICS pass (DESCRIPTIVE-ONLY, no verdict).

Explains the *mechanics* behind the [artifact-probe](selection_learning_artifact.py) result, per the
blind mechanics PLAN (2026-06-24, `70174df`):
  docs/research_wiki/reviews/btc-fib-selection-learning-artifact-mechanics-plan-20260624.md

Three observations to explain, on the SAME frozen data / locked detection (no refresh, no new
universe, no matched-null): (1) 4H reached legs are less clean than unreached; (2) 4H snapping
lowers cleanliness; (3) snapping flips sign on 1D. **This pass issues NO verdict and adds NO claim**
— it reports descriptive per-leg quantities (`span_bars`, `magnitude_atr`, `snap_span_delta`) and
the pre-locked summaries (PLAN P3). The headline descriptive object is the **4H↔1D `snap_span_delta`
asymmetry** (detector granularity vs human-anchoring precision); the bare span↔cleanliness
correlation is **partly arithmetic, flagged, NOT the finding**. The artifact-probe reading is
UNCHANGED; no lock is touched. **No reproduction, no edge/behaviour/PnL/backtest/Genesis/auto-fib/
1H/ETH/label-mutation.**

Run (own CLI; reuses the artifact module's rows; ``--artifact-mechanics-preflight`` for parity):
    python -m fibengine.research.selection_learning_artifact_mechanics --artifact-mechanics
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.research.selection_learning import (
    PRIMARY_K,
    RESULTS_DIR,
    SelectionConfig,
    _progress,
    load_human_legs,
)
from fibengine.research.selection_learning_artifact import (
    CONTEXT_TIMEFRAMES,
    build_artifact_rows,
)
from fibengine.research.selection_learning_gap import run_preflight

# --- small descriptive stats (numpy-only; no new deps) ----------------------------------------


def _rankdata(a: np.ndarray) -> np.ndarray:
    """Ranks with average ties (mirrors the roc_auc tie handling in selection_learning)."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="stable")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1)
    s = a[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for t in range(i, j + 1):
                ranks[order[t]] = avg
        i = j + 1
    return ranks


def _spearman(x: list[float], y: list[float]) -> float | None:
    """Spearman ρ = Pearson on average ranks. None if n<3 or a side is constant."""
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(xa) != len(ya) or len(xa) < 3:
        return None
    rx, ry = _rankdata(xa), _rankdata(ya)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def _median_iqr(vals: list[float]) -> dict[str, Any] | None:
    v = np.asarray([x for x in vals if x is not None], dtype=float)
    if v.size == 0:
        return None
    return {
        "n": int(v.size),
        "median": float(np.median(v)),
        "q25": float(np.percentile(v, 25)),
        "q75": float(np.percentile(v, 75)),
    }


# --- per-cell descriptive mechanics (PLAN P2/P3; NO verdict) -----------------------------------


def run_mechanics_cell(timeframe: str, cfg: SelectionConfig, settings: Any) -> dict:
    """Descriptive mechanics for one TF. Reuses the artifact-probe rows (same frozen data / locked
    detection). Returns descriptive summaries ONLY — no verdict, no claim (PLAN P4)."""
    _progress(f"mechanics tf={timeframe} k={cfg.k}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    legs = load_human_legs(timeframe)
    rows = build_artifact_rows(df, legs, cfg, settings.pivots)

    reached = [r for r in rows if r.reached]
    unreached = [r for r in rows if not r.reached]

    # M1 — size/length confound (reached vs unreached); confound set {span_bars, magnitude_atr}
    m1 = {
        "span_bars_reached": _median_iqr([r.span_bars for r in reached]),
        "span_bars_unreached": _median_iqr([r.span_bars for r in unreached]),
        "magnitude_atr_reached": _median_iqr([r.magnitude_atr for r in reached]),
        "magnitude_atr_unreached": _median_iqr([r.magnitude_atr for r in unreached]),
        "spearman_cleanliness_span": _spearman(
            [r.exact_clean for r in rows], [float(r.span_bars) for r in rows]
        ),
        "spearman_cleanliness_magnitude": _spearman(
            [r.exact_clean for r in rows if r.magnitude_atr is not None],
            [r.magnitude_atr for r in rows if r.magnitude_atr is not None],
        ),
    }
    # M1 attenuation — single median split on span_bars; cleanliness gap per half (honest Ns)
    spans = [r.span_bars for r in rows]
    med_span = float(np.median(spans)) if spans else 0.0
    halves = {}
    for name, keep in (
        ("short_span", lambda s: s <= med_span),
        ("long_span", lambda s: s > med_span),
    ):
        sub = [r for r in rows if keep(r.span_bars)]
        sr = [r.exact_clean for r in sub if r.reached]
        su = [r.exact_clean for r in sub if not r.reached]
        halves[name] = {
            "n_reached": len(sr),
            "n_unreached": len(su),
            "mean_clean_reached": float(np.mean(sr)) if sr else None,
            "mean_clean_unreached": float(np.mean(su)) if su else None,
            "gap": (float(np.mean(sr)) - float(np.mean(su))) if sr and su else None,
        }
    m1["median_split_span_bars"] = med_span
    m1["attenuation_by_span_half"] = halves

    # M3 (headline) — per-TF snap_span_delta sign distribution (the 4H↔1D asymmetry)
    deltas = [r.snap_span_delta for r in reached if r.snap_span_delta is not None]
    n_d = len(deltas)
    arr = np.asarray(deltas, dtype=float)
    m3 = {
        "n": n_d,
        "median_snap_span_delta": float(np.median(arr)) if n_d else None,
        "frac_extends_gt0": float(np.mean(arr > 0)) if n_d else None,
        "frac_zero": float(np.mean(arr == 0)) if n_d else None,
        "frac_shrinks_lt0": float(np.mean(arr < 0)) if n_d else None,
    }
    # M2 (completeness only — PARTLY ARITHMETIC, flagged, not the finding)
    pairs = [
        (r.snap_span_delta, r.snapped_clean - r.exact_clean)
        for r in reached
        if r.snapped_clean is not None and r.snap_span_delta is not None
    ]
    m2_spearman = (
        _spearman([float(p[0]) for p in pairs], [float(p[1]) for p in pairs]) if pairs else None
    )

    return {
        "timeframe": timeframe,
        "k": cfg.k,
        "n_legs": len(rows),
        "n_reached": len(reached),
        "n_unreached": len(unreached),
        "M1_size_length_confound": m1,
        "M3_snap_span_delta_asymmetry": m3,  # headline descriptive object (PLAN P3)
        "M2_span_vs_cleanliness_spearman_PARTLY_ARITHMETIC": m2_spearman,
        "note": "DESCRIPTIVE ONLY — no verdict/claim; artifact-probe reading unchanged (PLAN P4)",
    }


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def run_mechanics_study(config_path: str | None, cfg_in: SelectionConfig) -> dict:
    """4h primary + 1M/1w/1d context, all at k=3. Descriptive-only; NO verdict (PLAN P4)."""
    from dataclasses import replace

    cfg = replace(cfg_in, k=PRIMARY_K)
    settings = load_settings(config_path) if config_path else load_settings()
    primary = run_mechanics_cell("4h", cfg, settings)
    context = [run_mechanics_cell(tf, cfg, settings) for tf in CONTEXT_TIMEFRAMES]
    return {
        "generated_by": "fib_selection_learning_artifact_mechanics",
        "stage": "artifact_mechanics_descriptive",
        "descriptive_only": True,
        "no_verdict": True,
        "headline_object": "4H<->1D snap_span_delta asymmetry (PLAN P3)",
        "seed_note": "deterministic (no bootstrap); frozen data, locked detection",
        "primary_timeframe": "4h",
        "primary_k": PRIMARY_K,
        "results_4h": primary,
        "results_context": context,
    }


def print_mechanics(report: dict, path: Any) -> None:
    rows = [("4h", report["results_4h"])] + [("ctx", r) for r in report["results_context"]]
    for label, r in rows:
        m1, m3 = r["M1_size_length_confound"], r["M3_snap_span_delta_asymmetry"]
        print(
            f"[{label} tf={r['timeframe']}] legs={r['n_legs']} reached={r['n_reached']} "
            f"unreached={r['n_unreached']}"
        )
        print(
            f"    M1 span reached={m1['span_bars_reached']} unreached={m1['span_bars_unreached']}"
        )
        print(
            f"    M1 spearman(clean,span)={m1['spearman_cleanliness_span']} "
            f"spearman(clean,mag)={m1['spearman_cleanliness_magnitude']}"
        )
        print(f"    M1 attenuation={m1['attenuation_by_span_half']}")
        print(
            f"    M3 snap_delta median={m3['median_snap_span_delta']} "
            f"+={m3['frac_extends_gt0']} 0={m3['frac_zero']} -={m3['frac_shrinks_lt0']}"
        )
        print(
            f"    M2(arithmetic) spearman={r['M2_span_vs_cleanliness_spearman_PARTLY_ARITHMETIC']}"
        )
    print(f"DESCRIPTIVE-ONLY (no verdict)  summary={path}")


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "mechanics_summary.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=_json_default), encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    for _s in (sys.stdout, sys.stderr):
        _rc = getattr(_s, "reconfigure", None)
        if _rc is not None:
            _rc(encoding="utf-8")
    ap = argparse.ArgumentParser(description="BTC Fib artifact-probe mechanics (descriptive-only)")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR / "artifact"))
    ap.add_argument(
        "--artifact-mechanics", action="store_true", help="run the descriptive mechanics pass"
    )
    ap.add_argument(
        "--artifact-mechanics-preflight",
        action="store_true",
        help="frozen-data parity + facit fail-fast (reuses W-gap preflight; no run)",
    )
    args = ap.parse_args(argv)
    if args.artifact_mechanics_preflight:
        return run_preflight(args.config)
    if args.artifact_mechanics:
        report = run_mechanics_study(args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out))
        print_mechanics(report, path)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
