"""BTC Fib SELECTION-LEARNING — ``cleanliness`` artifact-probe (cheap-first track B, diagnostic).

Tests the single open campaign CRUX (checkpoint 2026-06-24): is the Stage-2 ``cleanliness`` lead a
genuine human leg-selection signal, or a detection / anchoring artifact? Decomposes that crux into
two contrasts on **existing facit data, NO new candidate universe** (artifact LOCK, b533385):

  1. SURFACING-bias — reached-vs-unreached human-leg cleanliness (ALL legs; unreached are the
     signal, never filtered). Does the detector preferentially *surface* cleaner human legs?
  2. SNAPPING-bias — exact-anchor vs detector-snapped cleanliness, paired over reached legs. Does
     snapping a human anchor to the nearest detector pivot mechanically *raise* cleanliness?

Frozen blind in the artifact LOCK (Commit 1, b533385):
  docs/research_wiki/reviews/btc-fib-selection-learning-artifact-lock-20260624.md

Diagnostic, NOT a headline. ``artifact_risk_reduced`` is NOT "cleanliness proven human intuition" —
it only narrows the artifact risk on two specific mechanisms (LOCK A9). The matched-null / new
candidate universe is NOT built here (gated, A8). **No reproduction, no edge/behaviour/PnL/backtest/
Genesis/auto-fib-as-truth/1H/ETH/label-mutation.** Shared machinery (facit loader, anchor positions,
frozen-data preflight) is imported; this module owns only the artifact-probe pieces.

Run (own CLI — ``selection_learning.py`` is byte-capped, LOCK A10):
    uv run python -m fibengine.research.selection_learning_artifact --artifact-preflight
    uv run python -m fibengine.research.selection_learning_artifact --artifact
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.core.models import Pivot
from fibengine.data.loader import atr, load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.selection_learning import (
    PRIMARY_K,
    RESULTS_DIR,
    HumanLeg,
    SelectionConfig,
    _pos_of_ts,
    _progress,
    load_human_legs,
)
from fibengine.research.selection_learning_gap import run_preflight

CONTEXT_TIMEFRAMES = ("1M", "1w", "1d")  # underpowered context only (LOCK A6), at primary k=3
# Stage-2 leg-reachability fidelity band (LOCK A2 / advisor): reached ≈ 0.83. Outside this band the
# reached/unreached definition has drifted from Stage-2 intent → stop-and-report, don't interpret.
FIDELITY_LOW, FIDELITY_HIGH = 0.75, 0.90
SURF_MIN_UNREACHED_QUARTERS = 3  # block bootstrap must see unreached spread across ≥3 quarters (A6)


# --- cleanliness (LOCK A1: source-bound formula; span-only, so inherently causal) -------------


def _cleanliness_idx(closes: np.ndarray, i: int, j: int) -> float:
    """``core.features._cleanliness`` reduced to a bar-index span: net close-move ÷ total close-path
    over ``[lo, hi]`` (LOCK A1, verbatim — sorts endpoints, 1.0 for <2 bars / zero path). Depends
    ONLY on the span, never the click-price; the span is pre-``anchor_b`` so this is causal."""
    lo, hi = sorted((int(i), int(j)))
    seg = closes[lo : hi + 1]
    if len(seg) < 2:
        return 1.0
    path = float(np.abs(np.diff(seg)).sum())
    if path == 0.0:
        return 1.0
    return float(abs(seg[-1] - seg[0]) / path)


def _anchor_kinds(leg: HumanLeg) -> tuple[str, str]:
    """Pivot kind expected at (anchor_a, anchor_b). Prefer the leg ``direction``; fall back to the
    price order when blank (build-time resolution — the ``direction`` sidecar field can be empty).
    Up-leg a=low→b=high; down-leg a=high→b=low."""
    d = leg.direction.lower()
    if d == "up":
        return ("low", "high")
    if d == "down":
        return ("high", "low")
    return ("low", "high") if leg.anchor_b_price >= leg.anchor_a_price else ("high", "low")


def _nearest_match(
    pivots: list[Pivot], pos: int, price: float, kind: str, eps_time: int, price_tol: float
) -> Pivot | None:
    """Nearest detected pivot of matching ``kind`` within ε of an anchor (time bars + price ATR
    units). Tie-break: smallest time distance, then smallest price distance. None if no match."""
    cands = [
        p
        for p in pivots
        if p.kind == kind and abs(p.index - pos) <= eps_time and abs(p.price - price) <= price_tol
    ]
    if not cands:
        return None
    return min(cands, key=lambda p: (abs(p.index - pos), abs(p.price - price)))


# --- per-leg artifact rows --------------------------------------------------------------------


@dataclass
class ArtifactRow:
    quarter: str  # calendar quarter of anchor_b (detector-free block-bootstrap unit, LOCK A5)
    pos_a: int
    pos_b: int
    exact_clean: float
    reached: bool  # both anchors ε-reconstructable by the detector (Stage-2 rule, LOCK A2)
    snapped_clean: float | None = (
        None  # cleanliness on the ε-matched detector pivots (reached only)
    )
    drop: str | None = None  # snapping-contrast drop reason (degenerate snap), logged not imputed
    # Descriptive-only mechanics fields (mechanics PLAN P3) — NOT used by any contrast/verdict.
    span_bars: int = 0  # |pos_b - pos_a| (duration proxy)
    magnitude_atr: float | None = None  # |close[b] - close[a]| / causal ATR at anchor_b
    snap_span_delta: int | None = None  # |snapped span| - |exact span| (reached, non-degenerate)


def _quarter_of(ts: pd.Timestamp) -> str:
    t = pd.Timestamp(ts)
    return f"{t.year}Q{(t.month - 1) // 3 + 1}"


def build_artifact_rows(
    df: pd.DataFrame, human_legs: list[HumanLeg], cfg: SelectionConfig, pivot_cfg: Any
) -> list[ArtifactRow]:
    """One row per human leg. exact_clean on the human anchors; reached + snapped_clean from the
    causal detector at ``anchor_b + k`` (LOCK A2–A4). Unreached legs are KEPT (the signal); only the
    paired snapping contrast drops degenerate / unreached snaps (logged, no imputation, LOCK A3)."""
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    closes = df["close"].to_numpy()
    n = len(df)
    rows: list[ArtifactRow] = []
    n_legs = len(human_legs)
    _progress(f"  build_artifact_rows: {n_legs} human legs, df={n} bars (per-leg causal detect)")
    t0 = time.perf_counter()
    for li, leg in enumerate(human_legs):
        if (li + 1) % 50 == 0 or li + 1 == n_legs:
            _progress(f"    leg {li + 1}/{n_legs} ({time.perf_counter() - t0:.0f}s)")
        pos_a = _pos_of_ts(index_ns, leg.anchor_a_ts)
        pos_b = _pos_of_ts(index_ns, leg.anchor_b_ts)
        kind_a, kind_b = _anchor_kinds(leg)
        exact_clean = _cleanliness_idx(closes, pos_a, pos_b)
        cutoff = min(pos_b + cfg.k, n - 1)  # truncate at anchor_b+k (clamp at data end), causal
        df_t = df.iloc[: cutoff + 1]
        atr_t = atr(df_t, period=cfg.atr_period).to_numpy()
        atr_at_b = float(atr_t[pos_b]) if 0 <= pos_b < len(atr_t) else float("nan")
        span_bars = abs(int(pos_b) - int(pos_a))  # descriptive (mechanics P3)
        magnitude_atr = (
            abs(float(closes[pos_b]) - float(closes[pos_a])) / atr_at_b
            if atr_at_b > 0 and np.isfinite(atr_at_b)
            else None
        )
        reached, snapped, drop, snap_span_delta = False, None, None, None
        if atr_at_b > 0 and np.isfinite(atr_at_b):  # fail-closed on degenerate ATR
            price_tol = cfg.eps_price_atr * atr_at_b
            pivots = detect_pivots(df_t, pivot_cfg)
            piv_a = _nearest_match(
                pivots, pos_a, leg.anchor_a_price, kind_a, cfg.eps_time_bars, price_tol
            )
            piv_b = _nearest_match(
                pivots, pos_b, leg.anchor_b_price, kind_b, cfg.eps_time_bars, price_tol
            )
            reached = piv_a is not None and piv_b is not None
            if reached:
                if piv_a.index == piv_b.index:  # degenerate snap — drop from snapping, keep reached
                    drop = "degenerate_snap_pa_eq_pb"
                else:
                    snapped = _cleanliness_idx(closes, piv_a.index, piv_b.index)
                    snap_span_delta = abs(piv_b.index - piv_a.index) - span_bars  # descriptive (P3)
        rows.append(
            ArtifactRow(
                quarter=_quarter_of(leg.anchor_b_ts),
                pos_a=pos_a,
                pos_b=pos_b,
                exact_clean=exact_clean,
                reached=reached,
                snapped_clean=snapped,
                drop=drop,
                span_bars=span_bars,
                magnitude_atr=magnitude_atr,
                snap_span_delta=snap_span_delta,
            )
        )
    return rows


# --- statistics + detector-free block bootstrap (LOCK A5; NOT row-level) ----------------------


def _surf_stat(rows: list[ArtifactRow]) -> float | None:
    r = [x.exact_clean for x in rows if x.reached]
    u = [x.exact_clean for x in rows if not x.reached]
    if not r or not u:  # degenerate resample (one group empty) — skip, not impute (advisor)
        return None
    return float(np.mean(r) - np.mean(u))


def _snap_stat(rows: list[ArtifactRow]) -> float | None:
    d = [x.snapped_clean - x.exact_clean for x in rows if x.reached and x.snapped_clean is not None]
    if not d:
        return None
    return float(np.mean(d))


def _block_bootstrap(
    rows: list[ArtifactRow], stat, n_boot: int, seed: int
) -> dict[str, Any] | None:
    """Quarter-block bootstrap (LOCK A5): resample whole calendar quarters of ``anchor_b`` with
    replacement, recompute ``stat`` on the pooled rows. Degenerate resamples (``stat`` None — e.g. a
    draw with no unreached legs) are skipped and counted out via ``n_boot_effective`` (advisor)."""
    point = stat(rows)
    if point is None:
        return None
    groups: dict[str, list[ArtifactRow]] = {}
    for r in rows:
        groups.setdefault(r.quarter, []).append(r)
    keys = list(groups.keys())
    m = len(keys)
    rng = np.random.default_rng(seed)
    samples: list[float] = []
    for _ in range(n_boot):
        pick = rng.integers(0, m, size=m)
        pooled: list[ArtifactRow] = []
        for idx in pick:
            pooled.extend(groups[keys[idx]])
        s = stat(pooled)
        if s is not None and np.isfinite(s):
            samples.append(s)
    arr = np.array(samples, dtype=float)
    if arr.size == 0:
        return None
    return {
        "point": float(point),
        "mean": float(arr.mean()),
        "ci95_low": float(np.percentile(arr, 2.5)),
        "ci95_high": float(np.percentile(arr, 97.5)),
        "p_one_sided_le_0": float(np.mean(arr <= 0.0)),
        "n_boot": n_boot,
        "n_boot_effective": int(arr.size),
        "n_quarters": m,
        "cluster_unit": "calendar quarter of anchor_b (LOCK A5)",
        "method": "quarter_block_bootstrap",
    }


# --- verdicts (LOCK A7) -----------------------------------------------------------------------


def _surfacing_verdict(inf: dict[str, Any] | None) -> str:
    if inf is None:
        return "underpowered"
    if inf["ci95_high"] < 0.0:
        return "inverse_surfacing"  # direction guard — investigate, not a finding
    if inf["ci95_low"] > 0.0:
        return "detector_surfacing_artifact"  # reached significantly cleaner
    return "no_surfacing_artifact"  # CI includes 0


def _snapping_verdict(inf: dict[str, Any] | None) -> str:
    if inf is None:
        return "underpowered"
    if inf["ci95_high"] < 0.0:
        return "snapping_deflates"  # direction guard — investigate, not a finding
    if inf["ci95_low"] > 0.0:
        return "snapping_inflates_cleanliness"
    return "no_snapping_inflation"  # CI includes 0


# Descriptive META status (NOT a locked verdict): A7 registered only the three locked combined
# outcomes below; it did NOT pre-register a combined label for a POWERED cell where a per-contrast
# direction guard fired (CI excludes 0 BELOW). We must not relabel that as inconclusive_underpowered
# (the cell IS powered — a misnomer) and must not invent a new locked verdict (that would change the
# lock). So this case carries a ``meta:`` status; the BINDING reading is the two per-contrast
# direction guards, verbatim "investigate, not a finding" (LOCK A7).
META_POWERED_DIRECTION_GUARD = "meta:a7_unregistered_powered_direction_guard"


def artifact_verdict(surf_v: str, snap_v: str, surf_powered: bool, snap_powered: bool) -> str:
    """Combined reading. The three LOCKED outcomes (LOCK A7): underpowered first; either artifact
    branch → detector_artifact_supported; both 'no_*' → artifact_risk_reduced. A powered cell with a
    direction guard is A7-UNREGISTERED → a descriptive ``meta:`` status (NOT a locked verdict, NOT
    inconclusive_underpowered); the binding reading is the two per-contrast guards (investigate)."""
    if not surf_powered and not snap_powered:
        return "inconclusive_underpowered"  # locked (A7) — genuinely underpowered
    if surf_v == "detector_surfacing_artifact" or snap_v == "snapping_inflates_cleanliness":
        return "detector_artifact_supported"  # locked (A7)
    if surf_v == "no_surfacing_artifact" and snap_v == "no_snapping_inflation":
        return "artifact_risk_reduced"  # locked (A7) — both CIs include 0
    return META_POWERED_DIRECTION_GUARD  # A7-unregistered; see sub-verdicts (investigate)


# --- per-cell driver --------------------------------------------------------------------------


def run_artifact_cell(timeframe: str, cfg_in: SelectionConfig, settings: Any) -> dict:
    """One TF cell: build per-leg rows, the surfacing + snapping contrasts (quarter-block boot),
    and the locked verdicts. Reports the reached fraction PROMINENTLY (the Stage-2 ≈0.83 fidelity
    check, LOCK A2 / advisor) — separate from both contrasts."""
    cfg = replace(cfg_in, k=PRIMARY_K)
    t_cell = time.perf_counter()
    _progress(f"cell START tf={timeframe} k={cfg.k}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    legs = load_human_legs(timeframe)
    rows = build_artifact_rows(df, legs, cfg, settings.pivots)

    n_legs = len(rows)
    n_reached = sum(r.reached for r in rows)
    n_unreached = n_legs - n_reached
    reached_fraction = (n_reached / n_legs) if n_legs else None
    clean_reached = [r.exact_clean for r in rows if r.reached]
    clean_unreached = [r.exact_clean for r in rows if not r.reached]
    n_snap = sum(r.reached and r.snapped_clean is not None for r in rows)
    n_drop = sum(r.drop is not None for r in rows)
    unreached_quarters = len({r.quarter for r in rows if not r.reached})

    # SURFACING contrast (LOCK A7) — powered if both groups ≥10 and unreached over ≥3 quarters
    surf_powered = (
        min(n_reached, n_unreached) >= cfg.min_test_positives
        and unreached_quarters >= SURF_MIN_UNREACHED_QUARTERS
    )
    surf_inf = _block_bootstrap(rows, _surf_stat, cfg.n_boot, cfg.seed) if surf_powered else None
    surf_v = _surfacing_verdict(surf_inf)

    # SNAPPING contrast (LOCK A7) — powered if ≥10 reached legs carry a (non-degenerate) snap
    snap_powered = n_snap >= cfg.min_test_positives
    snap_inf = _block_bootstrap(rows, _snap_stat, cfg.n_boot, cfg.seed) if snap_powered else None
    snap_v = _snapping_verdict(snap_inf)

    fidelity_ok = reached_fraction is not None and FIDELITY_LOW <= reached_fraction <= FIDELITY_HIGH
    verdict = artifact_verdict(surf_v, snap_v, surf_powered, snap_powered)
    combined_note = (
        "A7 did not pre-register a combined powered direction-guard outcome. No new combined "
        "verdict is assigned. Read the two locked per-contrast direction-guards verbatim as "
        "'investigate, not a finding'."
        if verdict == META_POWERED_DIRECTION_GUARD
        else None
    )
    _progress(
        f"cell DONE tf={timeframe} in {time.perf_counter() - t_cell:.0f}s "
        f"reached={reached_fraction} (fidelity_ok={fidelity_ok}) surf={surf_v} snap={snap_v} "
        f"verdict={verdict}"
    )
    return {
        "timeframe": timeframe,
        "k": cfg.k,
        "n_human_legs": n_legs,
        "n_reached": n_reached,
        "n_unreached": n_unreached,
        "reached_fraction": reached_fraction,  # Stage-2 ≈0.83 fidelity check (LOCK A2)
        "fidelity_band": [FIDELITY_LOW, FIDELITY_HIGH],
        "fidelity_ok": fidelity_ok,
        "mean_cleanliness_reached": float(np.mean(clean_reached)) if clean_reached else None,
        "mean_cleanliness_unreached": float(np.mean(clean_unreached)) if clean_unreached else None,
        "n_snap_pairs": n_snap,
        "n_snap_dropped_degenerate": n_drop,
        "unreached_quarters": unreached_quarters,
        "surfacing_powered": surf_powered,
        "surfacing_gap_inference": surf_inf,  # gap = mean(clean|reached) − mean(clean|unreached)
        "surfacing_verdict": surf_v,
        "snapping_powered": snap_powered,
        "snapping_gap_inference": snap_inf,  # gap = mean(snapped − exact), paired (reached only)
        "snapping_verdict": snap_v,
        "artifact_verdict": verdict,
        "combined_note": combined_note,
    }


# --- checkpointed study -----------------------------------------------------------------------


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _run_or_load_cell(timeframe: str, cfg: SelectionConfig, settings: Any, ckpt_dir: Path) -> dict:
    """Run one cell or load a same-seed checkpoint (atomic write) — mirrors the Stage-1/W-gap resume
    pattern. (This run is minutes, not hours; checkpointing is harmless insurance.)"""
    path = ckpt_dir / f"{timeframe}_k{PRIMARY_K}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("seed") == cfg.seed:
            _progress(f"RESUME tf={timeframe}: loaded checkpoint {path.name}")
            return saved["cell"]
        _progress(f"stale ckpt {path.name}: seed {saved.get('seed')}!={cfg.seed}, recompute")
    result = run_artifact_cell(timeframe, cfg, settings)
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


def run_artifact_study(
    config_path: str | None, cfg: SelectionConfig, ckpt_dir: Path | None = None
) -> dict:
    """Cleanliness artifact-probe. 4h primary; 1M/1w/1d at primary k=3 as underpowered context only
    (LOCK A6). Verdict from the 4h cell. Matched-null NOT built (gated, LOCK A8)."""
    settings = load_settings(config_path) if config_path else load_settings()
    if ckpt_dir is None:
        ckpt_dir = RESULTS_DIR / "artifact" / "cells"
    primary = _run_or_load_cell("4h", cfg, settings, ckpt_dir)
    context = [_run_or_load_cell(tf, cfg, settings, ckpt_dir) for tf in CONTEXT_TIMEFRAMES]
    return {
        "generated_by": "fib_selection_learning_artifact",
        "stage": "cleanliness_artifact_probe_cheap_first",
        "question": "is the Stage-2 cleanliness lead a genuine human signal or a "
        "detector/anchoring artifact (LOCK A0)",
        "surfacing_definition": "gap_surface = mean(cleanliness|reached) − mean(cleanliness|"
        "unreached); ALL human legs, exact anchors, Stage-2 eps-reconstruction split (LOCK A2)",
        "snapping_definition": "gap_snap = mean(snapped − exact cleanliness), paired over reached "
        "legs; no imputation (LOCK A3)",
        "bootstrap": "quarter_block_bootstrap (detector-free, LOCK A5)",
        "matched_null": "NOT built — gated optional rung, own separate blind lock (LOCK A8)",
        "seed": cfg.seed,
        "primary_timeframe": "4h",
        "primary_k": PRIMARY_K,
        "artifact_verdict": primary.get("artifact_verdict"),
        "results_4h": primary,
        "results_context_underpowered": context,
    }


def print_artifact(report: dict, path: Any) -> None:
    rows = [("4h", report["results_4h"])] + [
        ("ctx", r) for r in report["results_context_underpowered"]
    ]
    for label, r in rows:
        print(
            f"[{label} tf={r['timeframe']} k={r['k']}] legs={r['n_human_legs']} "
            f"reached={r['n_reached']} unreached={r['n_unreached']} "
            f"reached_frac={r['reached_fraction']} fidelity_ok={r['fidelity_ok']}"
        )
        print(
            f"    SURFACING clean_reached={r['mean_cleanliness_reached']} "
            f"clean_unreached={r['mean_cleanliness_unreached']} powered={r['surfacing_powered']} "
            f"verdict={r['surfacing_verdict']}"
        )
        print(f"    surf_inf={r['surfacing_gap_inference']}")
        print(
            f"    SNAPPING n_pairs={r['n_snap_pairs']} dropped={r['n_snap_dropped_degenerate']} "
            f"powered={r['snapping_powered']} verdict={r['snapping_verdict']}"
        )
        print(f"    snap_inf={r['snapping_gap_inference']}")
        print(f"    artifact_verdict={r['artifact_verdict']}")
        if r.get("combined_note"):
            print(f"    combined_note={r['combined_note']}")
    print(f"artifact_verdict={report['artifact_verdict']}  summary={path}")


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=_json_default), encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    for _s in (sys.stdout, sys.stderr):  # UTF-8 console
        _rc = getattr(_s, "reconfigure", None)
        if _rc is not None:
            _rc(encoding="utf-8")
    ap = argparse.ArgumentParser(
        description="BTC Fib selection-learning cleanliness artifact-probe"
    )
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR / "artifact"))
    ap.add_argument("--artifact", action="store_true", help="run the cleanliness artifact-probe")
    ap.add_argument(
        "--artifact-preflight",
        action="store_true",
        help="frozen-data parity + facit fail-fast (reuses W-gap preflight; no run)",
    )
    args = ap.parse_args(argv)
    if args.artifact_preflight:
        return run_preflight(args.config)
    if args.artifact:
        report = run_artifact_study(args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out))
        print_artifact(report, path)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
