"""BTC Fib SELECTION-LEARNING — retrospective ``W`` / causal-availability-gap study (side-quest #1).

Secondary / sensitivity slice (addendum A5; **not** in the four-TF Holm headline family). Computes
**gap(k) = AP(retrospective_W) − AP(live_k)** on the **identical** live-equivalent-at-``k``
candidate rows, common embargo = ``W``, models held fixed (no refit in bootstrap). Frozen,
blind-to-output, in the W-gap LOCK:
  docs/research_wiki/reviews/btc-fib-selection-learning-w-gap-lock-20260622.md

Split out of ``selection_learning.py`` (2026-06-22) to keep both modules under the research size cap
(repository-layout-policy §6). All shared machinery (candidate generation, the interpretable model +
AP/AUC metrics, the decision-point cluster bootstrap, the feature whitelist, ``_progress``) is
**imported from** ``selection_learning`` — this module owns only the retrospective-``W`` additions.
**No edge/behaviour/PnL/backtest/strategy claim, no Genesis, no 1H, no auto-fib-as-truth, no label
mutation** (W-gap lock L6).

Run (CLI stays in ``selection_learning``):
    uv run python -m fibengine.research.selection_learning --w-gap
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import PivotConfig, ScoringConfig, load_settings
from fibengine.core.features import compute_features
from fibengine.core.models import Swing
from fibengine.core.scale import detect_pivots_multi
from fibengine.data.fetch import cache_path
from fibengine.data.loader import atr, load_candles
from fibengine.pivots.detect import detect_pivots
from fibengine.research.selection_learning import (
    _INTERACTION_ONLY,
    _TF_W_BARS,
    K_STAR,
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

# Gap cells for the retrospective-W / causal-availability-gap study (W-gap lock 2026-06-22, L4).
# k=0 is degenerate (empty universe, reachable 0.0) → excluded, not a null.
GAP_K_CELLS = (3, 6, 12)


def retro_feature_names() -> list[str]:
    """Input features for the bounded-retrospective ``W`` model: **all** non-interaction features
    (addendum A2.2 — all eight computable within ``W``, minus interaction-only ``round_number``).
    ``recency`` enters in its viewport-relative form (see ``viewport_relative_recency``); it is
    retrospective-only and never appears in any live model. Sorted, deterministic."""
    return sorted(f for f in K_STAR if f not in _INTERACTION_ONLY)


def viewport_relative_recency(anchor_a_pos: int, anchor_b_pos: int, w_bars: int) -> float:
    """Viewport-relative recency for the retrospective model (W-gap lock L9, ``viewport_start =
    anchor_a``): ``(anchor_b - anchor_a) / (W + (anchor_b - anchor_a)) = leg / (W + leg)``.

    Bounded to the realistic labeling viewport, **not** the dataset end — this replaces the engine's
    default ``end.index/(n-1)`` (which is dataset-relative / omniscient) for the retrospective model
    only. Locked before code, not chosen after output."""
    leg = anchor_b_pos - anchor_a_pos
    denom = w_bars + leg
    return float(leg / denom) if denom > 0 else 0.0


def build_retro_features(
    df: pd.DataFrame,
    live_cands: list[Candidate],
    pivot_cfg: PivotConfig,
    scoring_cfg: ScoringConfig,
    cfg: SelectionConfig,
    w_bars: int,
) -> tuple[dict[tuple[int, int], dict[str, float]], dict[str, int]]:
    """Bounded-retrospective features for the **same rows** as ``live_cands``, on a frame truncated
    at ``anchor_b + W`` (W-gap lock L0/L2 — same mechanism as live, reach ``W`` not ``k``).

    Same-row reconstruction rule (L9): a row is kept only if its endpoint's ``anchor_b + W``
    viewport is inside the data **and** both endpoint and start pivots are re-detectable on
    ``df_W``; else it is excluded (counted, no imputation). ``recency`` is overridden to its
    viewport-relative form. Returns ``{(anchor_b_pos, start_pos): retro_features}`` + exclusions."""
    n = len(df)
    retro: dict[tuple[int, int], dict[str, float]] = {}
    excl_endpoint_rows = 0  # endpoint's anchor_b+W runs past the data
    excl_pivot_rows = 0  # endpoint/start pivot not reconstructible on df_W
    excl_positives = 0  # of all excluded rows, how many were human-matched positives
    by_end: dict[int, list[Candidate]] = {}
    for c in live_cands:
        by_end.setdefault(c.anchor_b_pos, []).append(c)
    n_end = len(by_end)
    _progress(f"  retro features: {n_end} endpoints (per-endpoint W-truncated detect)")
    t0 = time.perf_counter()
    for i_end, (j, group) in enumerate(by_end.items(), start=1):
        if i_end % 20 == 0 or i_end == n_end:
            _progress(f"    endpoint {i_end}/{n_end} ({time.perf_counter() - t0:.0f}s elapsed)")
        end_view = j + w_bars
        if end_view >= n:  # bounded retrospective viewport not available — exclude (no peeking)
            excl_endpoint_rows += len(group)
            excl_positives += sum(1 for c in group if c.label == 1)
            continue
        df_w = df.iloc[: end_view + 1]
        atr_w = atr(df_w, period=cfg.atr_period)
        piv_w = detect_pivots(df_w, pivot_cfg)
        end_piv = next((q for q in piv_w if q.index == j), None)
        if end_piv is None:  # endpoint not reconstructible on the W frame
            excl_pivot_rows += len(group)
            excl_positives += sum(1 for c in group if c.label == 1)
            continue
        # retrospective model always admits scale_confluence (k*=12 ≤ W) → multi-degree needed
        multi_w = detect_pivots_multi(df_w, pivot_cfg, scoring_cfg.confluence_degrees)
        for c in group:
            start = next(
                (q for q in piv_w if q.index == c.start_pos and q.kind != end_piv.kind), None
            )
            if start is None:
                excl_pivot_rows += 1
                excl_positives += 1 if c.label == 1 else 0
                continue
            feats = compute_features(
                df_w, Swing(start=start, end=end_piv), atr_w, scoring_cfg, piv_w, multi_w
            )
            feats["recency"] = viewport_relative_recency(c.start_pos, j, w_bars)
            retro[(j, c.start_pos)] = feats
    excl = {
        "rows_excluded_endpoint_W_beyond_data": excl_endpoint_rows,
        "rows_excluded_pivot_not_reconstructible": excl_pivot_rows,
        "positives_excluded": excl_positives,
    }
    return retro, excl


def run_gap_cell(
    timeframe: str, k: int, w_bars: int, cfg_in: SelectionConfig, settings: Any
) -> dict:
    """One causal-availability-gap cell: gap(k) = AP(retro W) − AP(live k) on **identical rows**,
    common embargo = ``W`` (W-gap lock L1–L5). Models held fixed; bootstrap by decision point."""
    cfg = replace(cfg_in, k=k)
    t_cell = time.perf_counter()
    _progress(f"cell START tf={timeframe} k={k} W={w_bars}")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    human_legs = load_human_legs(timeframe)
    live_cands = build_candidates(df, human_legs, settings.pivots, settings.scoring, cfg)
    _progress(f"  live universe: {len(live_cands)} candidate rows (df={len(df)} bars)")
    retro_map, excl = build_retro_features(
        df, live_cands, settings.pivots, settings.scoring, cfg, w_bars
    )
    paired = [c for c in live_cands if (c.anchor_b_pos, c.start_pos) in retro_map]

    n = len(df)
    split_idx = int(n * cfg.train_frac)
    reach = w_bars  # common embargo = W for BOTH models (L2) → identical train/test rows
    live_names, retro_names = live_feature_names(k), retro_feature_names()

    train, test = [], []
    for c in paired:
        win = window_of(c.anchor_b_pos, split_idx, n, reach)
        if win == "train":
            train.append(c)
        elif win == "test":
            test.append(c)

    def _xy(rows: list[Candidate], names: list[str], source: str) -> tuple[np.ndarray, np.ndarray]:
        if not rows:
            return np.zeros((0, len(names))), np.zeros(0)
        if source == "live":
            x = np.array([[c.features[f] for f in names] for c in rows], dtype=float)
        else:  # retro features for the same row key
            x = np.array(
                [[retro_map[(c.anchor_b_pos, c.start_pos)][f] for f in names] for c in rows],
                dtype=float,
            )
        return x, np.array([c.label for c in rows], dtype=float)

    n_test_pos = int(sum(c.label for c in test))
    powered = n_test_pos >= cfg.min_test_positives

    ap_live = ap_retro = gap = auc_retro = None
    gap_inf = attribution = None
    if len(train) and len(test):
        x_tr_l, y_tr = _xy(train, live_names, "live")
        x_te_l, y_te = _xy(test, live_names, "live")
        if y_tr.sum() > 0 and y_te.sum() > 0:
            m_live = fit_logreg(x_tr_l, y_tr, cfg)
            p_live = predict_proba(m_live, x_te_l)
            ap_live = average_precision(y_te, p_live)

            x_tr_r, _ = _xy(train, retro_names, "retro")
            x_te_r, _ = _xy(test, retro_names, "retro")
            m_retro = fit_logreg(x_tr_r, y_tr, cfg)
            p_retro = predict_proba(m_retro, x_te_r)
            ap_retro = average_precision(y_te, p_retro)
            auc_retro = roc_auc(y_te, p_retro)
            if ap_live is not None and ap_retro is not None:
                gap = ap_retro - ap_live

            # gap = AP(retro) − AP(live): reuse the cluster bootstrap with model=retro, base=live.
            groups = np.array([c.anchor_b_pos for c in test])
            if powered:
                gap_inf = decision_point_bootstrap(
                    y_te, p_retro, p_live, groups, cfg.n_boot, cfg.seed
                )

            # fixed two-group attribution (L9): shared live-k features on the W frame vs full retro
            x_tr_sh, _ = _xy(train, live_names, "retro")
            x_te_sh, _ = _xy(test, live_names, "retro")
            m_sh = fit_logreg(x_tr_sh, y_tr, cfg)
            ap_shared = average_precision(y_te, predict_proba(m_sh, x_te_sh))
            attribution = {
                "ap_retro_shared_features_on_W_frame": ap_shared,
                "gap_from_wider_frame": (
                    ap_shared - ap_live if ap_shared is not None and ap_live is not None else None
                ),
                "gap_from_right_edge_features": (
                    ap_retro - ap_shared if ap_retro is not None and ap_shared is not None else None
                ),
                "right_edge_only_features": sorted(set(retro_names) - set(live_names)),
                "retro_weights_standardized": {
                    f: float(w) for f, w in zip(retro_names, m_retro["w"], strict=True)
                },
                "live_weights_standardized": {
                    f: float(w) for f, w in zip(live_names, m_live["w"], strict=True)
                },
            }

    _progress(
        f"cell DONE tf={timeframe} k={k} in {time.perf_counter() - t_cell:.0f}s "
        f"(paired={len(paired)} test_pos={n_test_pos} powered={powered} gap={gap})"
    )
    return {
        "timeframe": timeframe,
        "k": k,
        "w_bars": w_bars,
        "n_live_rows": len(live_cands),
        "n_paired_rows": len(paired),
        "n_rows_excluded": len(live_cands) - len(paired),
        "exclusions": excl,
        "n_test": len(test),
        "n_test_positives": n_test_pos,
        "powered": powered,
        "ap_live": ap_live,
        "ap_retro": ap_retro,
        "auc_retro_secondary": auc_retro,
        "gap": gap,
        "gap_inference": gap_inf,  # decision-point cluster bootstrap of AP(retro)−AP(live)
        "gap_attribution": attribution,
    }


def gap_verdict(per_k: list[dict[str, Any]]) -> str:
    """Locked causal-availability-gap verdict (W-gap lock L5), read from the 4h primary cell k=3 and
    the k=12 cell. A gap "exists" if its bootstrap CI excludes 0 (lower bound > 0)."""
    by_k = {int(r["k"]): r for r in per_k}
    c3, c12 = by_k.get(3), by_k.get(12)

    def _inf(c: dict[str, Any] | None) -> dict[str, Any] | None:
        return c.get("gap_inference") if c else None

    # direction guard: any cell with a robustly NEGATIVE gap (CI upper bound < 0) → artifact
    for c in (c3, c12):
        inf = _inf(c)
        if inf is not None and inf["ci95_high"] < 0.0:
            return "artifact_check_needed"

    inf3 = _inf(c3)
    if c3 is None or not c3.get("powered") or inf3 is None:
        return "inconclusive"
    if inf3["ci95_low"] <= 0.0:  # gap(k=3) CI includes 0
        return "no_causal_gap"
    # gap(k=3) excludes 0 (>0) — resolve with k=12
    inf12 = _inf(c12)
    if c12 is None or not c12.get("powered") or inf12 is None:
        return "inconclusive"
    return "gap_persists" if inf12["ci95_low"] > 0.0 else "gap_closes_with_buffer"


def _json_default(o: Any) -> Any:
    """numpy scalars so a ~70-min cell never fails to JSON-serialize at checkpoint time."""
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _run_or_load_cell(
    timeframe: str, k: int, w_bars: int, cfg: SelectionConfig, settings: Any, ckpt_dir: Path
) -> dict:
    """Run one gap cell, or load it from a per-cell checkpoint if a same-seed one exists.

    Each ~70-min 4h cell is the unit of work that survives an interrupted run (accidental kill,
    sleep): on completion its result is written **atomically** to ``ckpt_dir/{tf}_k{k}.json`` and a
    later ``--w-gap`` run skips it. Seed-stamped — a config/seed change forces a clean recompute.
    Data drift is guarded by ``--w-gap-preflight``; clear ``cells/`` to force a full rerun.
    The returned cell is always JSON-round-tripped, so the aggregated summary stays serializable."""
    path = ckpt_dir / f"{timeframe}_k{k}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("seed") == cfg.seed:
            _progress(f"RESUME tf={timeframe} k={k}: loaded checkpoint {path.name}")
            return saved["cell"]
        _progress(f"stale ckpt {path.name}: seed {saved.get('seed')}!={cfg.seed}, recompute")
    result = run_gap_cell(timeframe, k, w_bars, cfg, settings)
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


def run_w_gap_study(
    config_path: str | None, cfg: SelectionConfig, ckpt_dir: Path | None = None
) -> dict:
    """Retrospective-W / causal-availability-gap study (side-quest #1). 4h primary over the gap
    cells {3,6,12}; 1M/1w/1d at primary k=3 as **underpowered context only** (W-gap lock L4).

    Checkpoints each cell under ``ckpt_dir`` (default ``RESULTS_DIR/w_gap/cells``) so an interrupted
    run resumes without recomputing finished cells (study ~3.5h, longer than one sitting)."""
    settings = load_settings(config_path) if config_path else load_settings()
    if ckpt_dir is None:
        ckpt_dir = RESULTS_DIR / "w_gap" / "cells"
    primary = [
        _run_or_load_cell("4h", k, _TF_W_BARS["4h"], cfg, settings, ckpt_dir) for k in GAP_K_CELLS
    ]
    context = [
        _run_or_load_cell(tf, PRIMARY_K, _TF_W_BARS[tf], cfg, settings, ckpt_dir)
        for tf in ("1M", "1w", "1d")
    ]
    return {
        "generated_by": "fib_selection_learning_w_gap",
        "metric": "pooled_test_average_precision",
        "gap_definition": "gap(k) = AP(retrospective_W) - AP(live_k) on identical rows, embargo=W",
        "seed": cfg.seed,
        "primary_timeframe": "4h",
        "gap_k_cells": list(GAP_K_CELLS),
        "gap_verdict": gap_verdict(primary),
        "results_4h": primary,
        "results_context_underpowered": context,
    }


def print_w_gap(report: dict, path: Any) -> None:
    """Console summary for the W-gap study (mirrors the k-sweep printer)."""
    groups = (("4h", report["results_4h"]), ("ctx", report["results_context_underpowered"]))
    for label, rows in groups:
        for r in rows:
            print(
                f"[{label} tf={r['timeframe']} k={r['k']} W={r['w_bars']}] "
                f"paired={r['n_paired_rows']}/{r['n_live_rows']} excl={r['n_rows_excluded']} "
                f"test_pos={r['n_test_positives']} powered={r['powered']} "
                f"ap_live={r['ap_live']} ap_retro={r['ap_retro']} gap={r['gap']}"
            )
            print(f"    excl={r['exclusions']}")
            print(f"    gap_inf={r['gap_inference']}")
            if r["gap_attribution"] is not None:
                a = r["gap_attribution"]
                print(
                    f"    attribution: frame={a['gap_from_wider_frame']} "
                    f"right_edge={a['gap_from_right_edge_features']} "
                    f"({a['right_edge_only_features']})"
                )
                print(f"    retro_weights={a['retro_weights_standardized']}")
    print(f"gap_verdict={report['gap_verdict']}  summary={path}")


# --- frozen-data parity preflight (fail-fast before the inherent ~2-3h run) --------------------

# ``run_w_gap_study`` loads candles via ``load_candles``/``cache_path`` under
# ``config/settings.expansion.yaml`` — which resolves 4h→limit_8000, 1d→limit_3500, 1w→limit_1000,
# 1M→limit_500 and trims at history_start=2016-11-05 — and ε-matches the human facit. These
# fingerprints are the **committed, independent** parity anchor: a ``data.fetch --refresh`` rewrites
# the same CSV **and** its sidecar ``manifest.json`` together, so only a reference kept in version
# control (here) can catch silent drift that would change the universe/split vs the locked k-sweep.
# Captured 2026-06-22 from the verified snapshot (post-load: trim + OHLCV validation applied).
PREFLIGHT_TIMEFRAMES = ("4h", "1w", "1d", "1M")  # run order: 4h primary first, then context cells
FROZEN_SNAPSHOT: dict[str, dict[str, Any]] = {
    "4h": {
        "bars": 21015,
        "first_ts": "2016-11-05T00:00:00+00:00",
        "last_ts": "2026-06-08T12:00:00+00:00",
    },
    "1w": {
        "bars": 500,
        "first_ts": "2016-11-10T00:00:00+00:00",
        "last_ts": "2026-06-04T00:00:00+00:00",
    },
    "1d": {
        "bars": 3503,
        "first_ts": "2016-11-05T00:00:00+00:00",
        "last_ts": "2026-06-08T00:00:00+00:00",
    },
    "1M": {
        "bars": 115,
        "first_ts": "2016-12-01T00:00:00+00:00",
        "last_ts": "2026-06-01T00:00:00+00:00",
    },
}
FROZEN_FACIT_COUNT: dict[str, int] = {"4h": 365, "1w": 21, "1d": 67, "1M": 9}


@dataclass
class PreflightCheck:
    timeframe: str
    ok: bool
    message: str


def compare_fingerprint(
    timeframe: str, bars: int, first_ts: str, last_ts: str, n_facit: int
) -> list[str]:
    """Pure parity check vs the committed frozen reference. Returns mismatch strings (empty ⇒ OK).
    Exact match required (strict FAIL): any bar-count / span / facit drift means the on-disk data is
    no longer the locked k-sweep snapshot and the gap run would be incomparable to it."""
    ref = FROZEN_SNAPSHOT[timeframe]
    out: list[str] = []
    if bars != ref["bars"]:
        out.append(f"bars {bars} != frozen {ref['bars']}")
    if first_ts != ref["first_ts"]:
        out.append(f"first_ts {first_ts} != frozen {ref['first_ts']}")
    if last_ts != ref["last_ts"]:
        out.append(f"last_ts {last_ts} != frozen {ref['last_ts']}")
    want = FROZEN_FACIT_COUNT[timeframe]
    if n_facit != want:
        out.append(f"facit {n_facit} != frozen {want}")
    return out


def check_frozen_cell(timeframe: str, settings: Any) -> PreflightCheck:
    """Load the exact cache + facit the W-gap run would use for ``timeframe`` and compare to the
    frozen reference. Never fetches (fail-closed) and never builds the candidate universe (so it
    stays cheap — the ~2-3h cost is in build_candidates/build_retro_features, skipped here)."""
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    path = cache_path(data_cfg)
    try:
        df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    except FileNotFoundError:
        return PreflightCheck(timeframe, False, f"no cache at {path} - copy the frozen snapshot")
    if df.empty:
        return PreflightCheck(timeframe, False, f"empty frame at {path.name}")
    try:
        n_facit = len(load_human_legs(timeframe))
    except ValueError as exc:
        return PreflightCheck(timeframe, False, f"facit load failed: {exc}")
    mism = compare_fingerprint(
        timeframe, len(df), df.index[0].isoformat(), df.index[-1].isoformat(), n_facit
    )
    if mism:
        return PreflightCheck(timeframe, False, f"{path.name}: " + "; ".join(mism))
    return PreflightCheck(
        timeframe, True, f"{path.name}: {len(df)} bars, {n_facit} facit (frozen-parity OK)"
    )


def run_preflight(config_path: str | None) -> int:
    """Fail-fast preflight for the W-gap run: verify every TF the study touches (4h primary +
    1M/1w/1d context) loads the frozen snapshot and the facit corpus is intact **before** paying the
    inherent ~2-3h per-endpoint-detect cost. Strict — any drift on any TF ⇒ NOT READY (exit 1).
    Pair with ``--w-gap-probe`` (times one real cell + ETA) for full pre-run confidence."""
    settings = load_settings(config_path) if config_path else load_settings()
    print("=== W-gap preflight (frozen-data parity, cache-only) ===")
    print(f"config: {config_path or 'config/settings.yaml (default)'}")
    failures = 0
    for tf in PREFLIGHT_TIMEFRAMES:
        chk = check_frozen_cell(tf, settings)
        print(f"[{'OK' if chk.ok else 'FAIL'}] {tf}: {chk.message}")
        failures += 0 if chk.ok else 1
    print()
    if failures:
        print(f"NOT READY: {failures} TF(s) drifted or missing - do NOT run --w-gap.")
        print("Restore the exact frozen CSVs (do NOT data.fetch --refresh), then re-run preflight.")
    else:
        print("READY: all TFs match the frozen k-sweep snapshot. Next: --w-gap-probe for the ETA.")
    return 1 if failures else 0
