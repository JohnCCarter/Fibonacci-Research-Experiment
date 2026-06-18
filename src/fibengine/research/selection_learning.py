"""BTC Fib SELECTION-LEARNING harness — Stage 2 headline cell (research-only, Lean Fib).

Can an interpretable model reproduce **which leg/range the human marked** (the fib annotation),
out-of-sample, better than a structural baseline? **Selection learning — NOT a behaviour/edge
claim, no backtest/PnL, no Genesis, no 1H, no auto-fib-as-truth, no label mutation.**

Pre-registration (frozen rules):
  docs/research_wiki/reviews/btc-fib-selection-learning-prereg-20260617.md
§12 addendum (frozen feature/provenance/k/W/ε + pinned metric, blind):
  docs/research_wiki/reviews/btc-fib-selection-learning-addendum-20260618.md

This module builds the **single pre-registered headline test only**: Stage 2 (leg gestalt),
live-equivalent viewport at primary ``k = 3``, vs the §6 trivial-leg baseline, primary metric =
pooled test **Average Precision** (AP; ROC-AUC secondary). The k-sweep, retrospective ``W`` model,
per-feature causal-availability gap, and the Stage-1 per-pivot diagnostic are SECONDARY and bolt on
later (addendum A5). Everything here is causal: each candidate leg's features are computed on a
frame **truncated at ``anchor_b + k``** (truncate-and-whitelist, advisor-confirmed), and the
candidate universe at each decision point is re-detected on that truncated frame.

Run:
    uv run python -m fibengine.research.selection_learning \\
        --timeframes 1d,4h --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import REPO_ROOT, PivotConfig, ScoringConfig, load_settings
from fibengine.core.features import compute_features
from fibengine.core.models import Pivot, Swing
from fibengine.core.scale import detect_pivots_multi
from fibengine.data.loader import atr, load_candles
from fibengine.pivots.detect import detect_pivots

# --- frozen constants (see prereg + addendum) -------------------------------------------------

ALLOWED_TIMEFRAMES = ("1M", "1w", "1d", "4h")  # 1H rejected fail-closed (§13)
SEED = 20260618
HUMAN_FIB_ROOT = REPO_ROOT / "data" / "labels" / "human_fib" / "bitfinex" / "BTC-USD"
RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "fib_selection_learning"

PRIMARY_K = 3  # addendum A5: base detector confirmation buffer (= lookback)
K_SWEEP = (0, 3, 6, 12)  # addendum A5 (only PRIMARY_K used in this headline slice)

# Per-feature minimum confirmation buffer k* (addendum A2). live model at buffer k uses k*(f) <= k.
# round_number is interaction-only (§3) → excluded from the primary live model.
# scale_confluence (k*=12) and recency (k*=inf) excluded at k=3. exclusivity is a set-level OUTPUT
# diagnostic (A3), reported with the gestalt — NOT a per-candidate input (its A3 definition uses
# human marks → would leak), so it is not in the input matrix here.
K_STAR: dict[str, float] = {
    "magnitude": 0,
    "cleanliness": 0,
    "duration": 0,
    "round_number": 0,  # interaction-only — never a primary input
    "prominence": 3,
    "structure_alignment": 3,
    "scale_confluence": 12,
    "recency": math.inf,
}
_INTERACTION_ONLY = ("round_number",)

# Retrospective viewport per TF (addendum A5; not exercised in this headline slice — pinned here so
# the secondary W-model bolts on without re-deciding, blind).
_TF_W_BARS: dict[str, int] = {"1M": 24, "1w": 52, "1d": 120, "4h": 180}


def live_feature_names(k: int) -> list[str]:
    """Causal input features for the live-equivalent model at confirmation buffer ``k``:
    every feature with ``k*(f) <= k``, minus interaction-only ones (§3). Sorted, deterministic."""
    return sorted(f for f, ks in K_STAR.items() if ks <= k and f not in _INTERACTION_ONLY)


@dataclass(frozen=True)
class SelectionConfig:
    """Frozen knobs (prereg + addendum). None tuned on the test window."""

    k: int = PRIMARY_K  # confirmation buffer (bars)
    eps_time_bars: int = 3  # ε_time — reused from EvaluationConfig.time_tol_bars (A4)
    eps_price_atr: float = 0.5  # ε_price (ATR units) — reused from EvaluationConfig.price_tol_atr
    atr_period: int = 14
    train_frac: float = 0.70
    min_test_positives: int = 10  # power floor on test positives (power honesty, §9)
    max_legs_per_point: int = 12  # cap prior opposite pivots paired per decision point (logged)
    l2: float = 1.0  # logistic ridge penalty
    n_iter: int = 500
    lr: float = 0.1
    n_boot: int = 2000  # decision-point cluster-bootstrap resamples for the AP-lift CI/p
    seed: int = SEED


# --- human-leg targets ------------------------------------------------------------------------


@dataclass(frozen=True)
class HumanLeg:
    anchor_a_ts: pd.Timestamp
    anchor_a_price: float
    anchor_b_ts: pd.Timestamp
    anchor_b_price: float
    direction: str


def load_human_legs(timeframe: str) -> list[HumanLeg]:
    """Human fib legs (anchor_a→anchor_b) for a TF — the Stage-2 targets. Fail-closed on
    candidate / non-human / auto sidecars (mirrors the behaviour study's facit discipline)."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {timeframe!r} not allowed (1H rejected fail-closed)")
    paths = [
        p
        for p in sorted(glob.glob(str(HUMAN_FIB_ROOT / timeframe / "fib_*.json")))
        if not p.endswith("_events.json")
    ]
    if not paths:
        raise ValueError(f"no source fibs found for {timeframe} under {HUMAN_FIB_ROOT}")
    legs: list[HumanLeg] = []
    for p in paths:
        if "_candidate" in Path(p).name:
            raise ValueError(f"refusing non-human candidate fib: {p}")
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        if data.get("created_by") != "human":
            raise ValueError(f"refusing non-human fib (created_by != human): {p}")
        a, b = data["anchor_a"], data["anchor_b"]
        legs.append(
            HumanLeg(
                anchor_a_ts=pd.Timestamp(a["time"]),
                anchor_a_price=float(a["price"]),
                anchor_b_ts=pd.Timestamp(b["time"]),
                anchor_b_price=float(b["price"]),
                direction=str(data.get("direction", "")),
            )
        )
    return legs


def _pos_of_ts(index_ns: np.ndarray, ts: pd.Timestamp) -> int:
    """Nearest bar position to a timestamp (anchors fall on bar opens; robust to tz/us)."""
    return int(np.argmin(np.abs(index_ns - np.int64(pd.Timestamp(ts).value))))


# --- causal candidate generation + features ---------------------------------------------------


@dataclass
class Candidate:
    anchor_b_pos: int  # endpoint bar position (decision point is anchor_b_pos + k)
    start_pos: int  # paired opposite-pivot position
    features: dict[str, float]
    label: int  # 1 if matches a human leg within ε, else 0
    human_idx: int = -1  # which human leg it matched (for coverage), else -1
    prom_max: float = 0.0  # max(start, end) raw endpoint ATR-prominence (§6 prominence baseline B)


def _matches_human(
    start: Pivot,
    end: Pivot,
    human_legs: list[HumanLeg],
    index_ns: np.ndarray,
    atr_at_b: float,
    cfg: SelectionConfig,
) -> int:
    """Index of the human leg this (start→end) candidate matches within ε on BOTH anchors and
    direction, else -1. ε_time in bars, ε_price in ATR units (A4); ε absorbs wick-vs-body (§7)."""
    if atr_at_b <= 0 or not np.isfinite(atr_at_b):
        return -1
    price_tol = cfg.eps_price_atr * atr_at_b
    cand_dir = "up" if end.price > start.price else "down"
    for h, leg in enumerate(human_legs):
        b_pos = _pos_of_ts(index_ns, leg.anchor_b_ts)
        a_pos = _pos_of_ts(index_ns, leg.anchor_a_ts)
        if abs(end.index - b_pos) > cfg.eps_time_bars:
            continue
        if abs(start.index - a_pos) > cfg.eps_time_bars:
            continue
        if abs(end.price - leg.anchor_b_price) > price_tol:
            continue
        if abs(start.price - leg.anchor_a_price) > price_tol:
            continue
        if leg.direction and leg.direction != cand_dir:
            continue
        return h
    return -1


def build_candidates(
    df: pd.DataFrame,
    human_legs: list[HumanLeg],
    pivot_cfg: PivotConfig,
    scoring_cfg: ScoringConfig,
    cfg: SelectionConfig,
) -> list[Candidate]:
    """Causal Stage-2 candidate legs at the live-equivalent viewport ``anchor_b + k``.

    For every base pivot (a potential ``anchor_b``), truncate the frame at ``anchor_b + k``,
    **re-detect pivots on the truncated frame** (so the universe is only legs confirmable live),
    pair the endpoint with its most-recent ``max_legs_per_point`` opposite pivots, and compute
    features on the truncated frame. Returns one Candidate per (endpoint, prior-opposite) pair.
    """
    index_ns = df.index.values.astype("datetime64[ns]").astype("int64")
    n = len(df)
    full_pivots = detect_pivots(df, pivot_cfg)
    # scale_confluence (k*=12) needs larger-degree pivots; compute them on the truncated frame ONLY
    # when the active whitelist admits it (k>=12) — else it stays the degenerate neutral 0.5 and is
    # whitelisted out anyway. Keeps k<12 cheap and the k=12 cell causally honest.
    need_confluence = "scale_confluence" in live_feature_names(cfg.k)
    out: list[Candidate] = []
    for piv in full_pivots:
        j = piv.index
        end_view = j + cfg.k
        if end_view >= n:  # cannot be confirmed live within the data — skip (no peeking)
            continue
        df_t = df.iloc[: end_view + 1]
        atr_t = atr(df_t, period=cfg.atr_period)
        atr_arr = atr_t.to_numpy()
        piv_t = detect_pivots(df_t, pivot_cfg)
        end_piv = next((q for q in piv_t if q.index == j and q.kind == piv.kind), None)
        if end_piv is None:  # dedupe/edge dropped it on the truncated frame — not live-confirmable
            continue
        multi_t = (
            detect_pivots_multi(df_t, pivot_cfg, scoring_cfg.confluence_degrees)
            if need_confluence
            else None
        )
        prior_opp = [q for q in piv_t if q.kind != end_piv.kind and q.index < end_piv.index]
        atr_at_b = float(atr_arr[j]) if 0 <= j < len(atr_arr) else float("nan")
        for start in prior_opp[-cfg.max_legs_per_point :]:
            swing = Swing(start=start, end=end_piv)
            feats = compute_features(df_t, swing, atr_t, scoring_cfg, piv_t, multi_t)
            h = _matches_human(start, end_piv, human_legs, index_ns, atr_at_b, cfg)
            out.append(
                Candidate(
                    anchor_b_pos=j,
                    start_pos=start.index,
                    features=feats,
                    label=1 if h >= 0 else 0,
                    human_idx=h,
                    prom_max=max(float(start.prominence), float(end_piv.prominence)),
                )
            )
    return out


# --- purged/embargoed split (parameterized by forward reach) ----------------------------------


def window_of(anchor_b_pos: int, split_idx: int, n: int, reach: int) -> str | None:
    """train if the leg is fully confirmed before the split (no peek into test); test if decided
    at/after the split with its forward reach inside the data; else embargoed. ``reach`` = the
    forward viewport (``k`` live, ``W`` retrospective) — parameterized now so the W-model's large
    embargo is designed in, not discovered (advisor)."""
    if anchor_b_pos + reach < split_idx:
        return "train"
    if anchor_b_pos >= split_idx and anchor_b_pos + reach < n:
        return "test"
    return None


# --- interpretable model + metric (numpy, zero new deps) --------------------------------------


def _standardize(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (x - mean) / np.where(std > 0, std, 1.0)


def fit_logreg(x: np.ndarray, y: np.ndarray, cfg: SelectionConfig) -> dict[str, Any]:
    """Deterministic ridge-penalized logistic regression via full-batch gradient descent.
    Interpretable (§10): returns standardization stats + weights — no black box, no test-tuning."""
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    xs = _standardize(x, mean, std)
    n, d = xs.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(cfg.n_iter):
        z = xs @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        err = p - y
        grad_w = xs.T @ err / n + cfg.l2 * w / n
        grad_b = float(err.mean())
        w -= cfg.lr * grad_w
        b -= cfg.lr * grad_b
    return {"mean": mean, "std": std, "w": w, "b": b}


def predict_proba(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xs = _standardize(x, model["mean"], model["std"])
    return 1.0 / (1.0 + np.exp(-(xs @ model["w"] + model["b"])))


def average_precision(y_true: np.ndarray, scores: np.ndarray) -> float | None:
    """Pooled AP = area under the precision–recall curve (rare-positive honest primary, A5.1).
    Ties broken deterministically by stable sort. None if no positives."""
    y = np.asarray(y_true, dtype=float)
    if y.sum() == 0:
        return None
    order = np.argsort(-np.asarray(scores, dtype=float), kind="stable")
    y_sorted = y[order]
    tp = np.cumsum(y_sorted)
    fp = np.cumsum(1.0 - y_sorted)
    precision = tp / (tp + fp)
    total_pos = y.sum()
    recall = tp / total_pos
    # AP = Σ (R_k - R_{k-1}) · P_k
    prev_recall = np.concatenate([[0.0], recall[:-1]])
    return float(np.sum((recall - prev_recall) * precision))


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float | None:
    """ROC-AUC (secondary, A5.1) via the rank-sum (Mann–Whitney) identity. None if degenerate."""
    y = np.asarray(y_true, dtype=float)
    n_pos = int(y.sum())
    n_neg = int(len(y) - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(np.asarray(scores, dtype=float), kind="stable")
    ranks = np.empty(len(scores), dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    # average ranks for ties
    s_sorted = np.asarray(scores, dtype=float)[order]
    i = 0
    while i < len(s_sorted):
        j = i
        while j + 1 < len(s_sorted) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for t in range(i, j + 1):
                ranks[order[t]] = avg
        i = j + 1
    sum_pos = ranks[y == 1].sum()
    return float((sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def decision_point_bootstrap(
    y: np.ndarray,
    scores_model: np.ndarray,
    scores_base: np.ndarray,
    groups: np.ndarray,
    n_boot: int,
    seed: int,
) -> dict[str, Any] | None:
    """Cluster-bootstrap CI + one-sided p for the AP-lift, resampled by **decision point**.

    The candidate rows cluster by ``anchor_b`` decision point (many legs share one endpoint); an
    independent row bootstrap would understate variance. So we resample whole decision-point groups
    with replacement, re-pool their candidates, and recompute ``AP(model) − AP(baseline)`` on the
    held-fixed model scores (no refit — this measures the OOS test-estimate's sampling variability).
    Null = lift ≤ 0; one-sided p = fraction of resamples with lift ≤ 0. None if no positives."""
    if y.sum() == 0:
        return None
    uniq = np.unique(groups)
    rows_by_group = {int(g): np.flatnonzero(groups == g) for g in uniq}
    rng = np.random.default_rng(seed)
    lifts: list[float] = []
    for _ in range(n_boot):
        sampled = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([rows_by_group[int(g)] for g in sampled])
        ap_m = average_precision(y[idx], scores_model[idx])
        ap_b = average_precision(y[idx], scores_base[idx])
        if ap_m is None or ap_b is None:
            continue
        lifts.append(ap_m - ap_b)
    if not lifts:
        return None
    arr = np.array(lifts)
    return {
        "method": "decision_point_cluster_bootstrap",
        "n_boot": n_boot,
        "n_boot_effective": int(arr.size),
        "n_groups": int(uniq.size),
        "lift_mean": float(arr.mean()),
        "ci95_low": float(np.percentile(arr, 2.5)),
        "ci95_high": float(np.percentile(arr, 97.5)),
        "p_one_sided_lift_le_0": float(np.mean(arr <= 0.0)),
    }


def prominence_survival_verdict(
    inf_sum: dict[str, Any] | None, inf_max: dict[str, Any] | None
) -> str:
    """Pre-committed §6 prominence-family verdict (locked before the run, not chosen after).

    A bootstrap CI "survives" if its lower bound > 0 (lift robustly positive). Survival vs BOTH the
    summed (A) and max (B) prominence baselines → robust; only one → baseline-dependent; neither →
    the earlier lift reduces to a magnitude-baseline-only lead."""

    def _survives(inf: dict[str, Any] | None) -> bool:
        return inf is not None and inf["ci95_low"] > 0.0

    surv_sum, surv_max = _survives(inf_sum), _survives(inf_max)
    if surv_sum and surv_max:
        return "survives_prominence_family"
    if surv_sum or surv_max:
        return "baseline_dependent_inconclusive"
    return "reduced_to_magnitude_baseline_only"


# --- per-timeframe driver ---------------------------------------------------------------------


def run_timeframe(timeframe: str, cfg: SelectionConfig, settings: Any) -> dict[str, Any]:
    """Headline cell for one TF: Stage 2, live-equivalent k, AP(model) vs AP(baseline) OOS."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {timeframe!r} not allowed (1H rejected fail-closed)")
    data_cfg = settings.data.model_copy(update={"timeframe": timeframe})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    human_legs = load_human_legs(timeframe)
    cands = build_candidates(df, human_legs, settings.pivots, settings.scoring, cfg)

    feat_names = live_feature_names(cfg.k)
    split_idx = int(len(df) * cfg.train_frac)
    reach = cfg.k

    train, test = [], []
    for c in cands:
        win = window_of(c.anchor_b_pos, split_idx, len(df), reach)
        if win == "train":
            train.append(c)
        elif win == "test":
            test.append(c)

    def _xy(rows: list[Candidate]) -> tuple[np.ndarray, np.ndarray]:
        if not rows:
            return np.zeros((0, len(feat_names))), np.zeros(0)
        x = np.array([[c.features[f] for f in feat_names] for c in rows], dtype=float)
        y = np.array([c.label for c in rows], dtype=float)
        return x, y

    x_tr, y_tr = _xy(train)
    x_te, y_te = _xy(test)

    # coverage ceiling: fraction of human legs reachable by ANY candidate (model + baseline capped)
    matched_humans = {c.human_idx for c in cands if c.human_idx >= 0}
    reachable_fraction = len(matched_humans) / len(human_legs) if human_legs else None

    ap_model = ap_base = auc_model = lift = None
    p_model = mag = None
    model_weights = None
    if len(train) and len(test) and y_tr.sum() > 0 and y_te.sum() > 0:
        model = fit_logreg(x_tr, y_tr, cfg)
        # §10 interpretability: standardized weights are directly comparable across features
        model_weights = {f: float(w) for f, w in zip(feat_names, model["w"], strict=True)}
        p_model = predict_proba(model, x_te)
        ap_model = average_precision(y_te, p_model)
        auc_model = roc_auc(y_te, p_model)
        # §6 baseline parity: identical test set/viewport, rank by magnitude only
        mag = x_te[:, feat_names.index("magnitude")]
        ap_base = average_precision(y_te, mag)
        if ap_model is not None and ap_base is not None:
            lift = ap_model - ap_base

    n_test_pos = int(y_te.sum())
    powered = n_test_pos >= cfg.min_test_positives
    # NOT an inferential verdict — just a point-estimate flag (lift>0 on a powered cell).
    lift_pos_powered = bool(powered and lift is not None and lift > 0)

    # AP-lift inference (decision-point cluster bootstrap), powered cells only.
    inference = None
    # §6 prominence-baseline sensitivity (locked pre-run): A = summed endpoint prominence
    # (= the `prominence` feature column, rank-equivalent to raw sum), B = max endpoint prominence.
    ap_base_prom_sum = ap_base_prom_max = None
    lift_vs_prom_sum = lift_vs_prom_max = None
    inf_prom_sum = inf_prom_max = None
    prominence_verdict = None
    groups = np.array([c.anchor_b_pos for c in test])  # decision-point ids for cluster bootstrap
    if powered and ap_model is not None and p_model is not None and mag is not None:
        inference = decision_point_bootstrap(y_te, p_model, mag, groups, cfg.n_boot, cfg.seed)
    # §6 prominence baselines: only where prominence is causally whitelisted at this k (k*=3).
    # k<3 → N/A (not failure): prominence is not live-available, so the family check skips it.
    if powered and p_model is not None and "prominence" in feat_names:
        prom_sum = x_te[:, feat_names.index("prominence")]  # A (parallel to magnitude column)
        prom_max = np.array([c.prom_max for c in test])  # B
        ap_base_prom_sum = average_precision(y_te, prom_sum)
        ap_base_prom_max = average_precision(y_te, prom_max)
        if ap_base_prom_sum is not None:
            lift_vs_prom_sum = ap_model - ap_base_prom_sum
        if ap_base_prom_max is not None:
            lift_vs_prom_max = ap_model - ap_base_prom_max
        nb, sd = cfg.n_boot, cfg.seed
        inf_prom_sum = decision_point_bootstrap(y_te, p_model, prom_sum, groups, nb, sd)
        inf_prom_max = decision_point_bootstrap(y_te, p_model, prom_max, groups, nb, sd)
        prominence_verdict = prominence_survival_verdict(inf_prom_sum, inf_prom_max)

    return {
        "timeframe": timeframe,
        "n_bars": len(df),
        "n_human_legs": len(human_legs),
        "reachable_fraction": reachable_fraction,
        "features": feat_names,
        "k": cfg.k,
        "n_candidates": len(cands),
        "n_train": len(train),
        "n_test": len(test),
        "n_test_positives": n_test_pos,
        "ap_model": ap_model,
        "ap_baseline_magnitude": ap_base,
        "ap_baseline_prominence_sum": ap_base_prom_sum,  # §6 baseline A
        "ap_baseline_prominence_max": ap_base_prom_max,  # §6 baseline B
        "ap_lift_vs_magnitude": lift,
        "ap_lift_vs_prominence_sum": lift_vs_prom_sum,
        "ap_lift_vs_prominence_max": lift_vs_prom_max,
        "auc_model_secondary": auc_model,
        "model_weights_standardized": model_weights,  # §10 interpretability (read before claiming)
        "powered": powered,
        "lift_pos_powered": lift_pos_powered,  # point-estimate flag, NOT an inferential verdict
        "ap_lift_inference_vs_magnitude": inference,
        "ap_lift_inference_vs_prominence_sum": inf_prom_sum,
        "ap_lift_inference_vs_prominence_max": inf_prom_max,
        "prominence_survival_verdict": prominence_verdict,  # pre-committed §6-family rule
        "retro_W_bars": _TF_W_BARS[timeframe],
    }


def _k_survives_magnitude(r: dict[str, Any]) -> bool:
    """Transparency flag: powered AND the model-vs-magnitude bootstrap CI excludes 0 (the weaker
    bar). Reported alongside the family criterion; never the verdict driver."""
    inf = r.get("ap_lift_inference_vs_magnitude")
    return bool(r.get("powered") and inf is not None and inf["ci95_low"] > 0.0)


def _k_survives_family(r: dict[str, Any]) -> bool:
    """LOCKED survival criterion (user 2026-06-18): a k-cell survives iff it is powered AND the
    model AP-lift CI excludes 0 vs EVERY causally-allowed §6 baseline at that k — magnitude always,
    plus prominence A/B where prominence is whitelisted (k>=3). The stronger, more valid bar; it is
    the same family the k=3 headline already had to beat (validity over convenience)."""
    if not r.get("powered"):
        return False
    infs = [
        r.get("ap_lift_inference_vs_magnitude"),
        r.get("ap_lift_inference_vs_prominence_sum"),
        r.get("ap_lift_inference_vs_prominence_max"),
    ]
    present = [i for i in infs if i is not None]
    # require magnitude present (always allowed) and ALL present baselines' CI exclude 0
    if r.get("ap_lift_inference_vs_magnitude") is None:
        return False
    return all(i["ci95_low"] > 0.0 for i in present)


def k_sweep_verdict(per_k: list[dict[str, Any]]) -> str:
    """Cross-k verdict (locked rule). Survival = the prominence-FAMILY criterion.

    ≥2 k survive → k-stable; only k=3 → narrow buffer dependency; none → primary-k3-only."""
    survivors = {int(r["k"]) for r in per_k if _k_survives_family(r)}
    if len(survivors) >= 2:
        return "k_stable_live_selection_signal"
    if survivors == {3}:
        return "k_sensitive_narrow_confirmation_buffer_dependency"
    return "previous_result_valid_only_for_primary_k3_not_robust_across_k"


def run_k_sweep(
    timeframe: str, ks: list[int], config_path: str | None, cfg: SelectionConfig
) -> dict:
    """4H live-only k-sweep sensitivity (addendum A5 k-sweep). Re-runs the headline cell per k —
    each k rebuilds the candidate universe on its own truncated viewport and applies the frozen
    k*-whitelist. Reports per-k cells + the locked cross-k verdict. No W/gap, no Stage 1."""
    settings = load_settings(config_path) if config_path else load_settings()
    per_k: list[dict[str, Any]] = []
    for k in ks:
        res = run_timeframe(timeframe, replace(cfg, k=k), settings)
        res["active_features"] = live_feature_names(k)
        res["survives_vs_magnitude"] = _k_survives_magnitude(res)  # transparency (weaker bar)
        res["survives_prominence_family"] = _k_survives_family(res)  # LOCKED verdict driver
        per_k.append(res)
    return {
        "generated_by": "fib_selection_learning_k_sweep",
        "timeframe": timeframe,
        "metric": "pooled_test_average_precision",
        "k_values": ks,
        "seed": cfg.seed,
        "k_sweep_verdict": k_sweep_verdict(per_k),
        "results_by_k": per_k,
    }


def run_study(timeframes: list[str], config_path: str | None, cfg: SelectionConfig) -> dict:
    settings = load_settings(config_path) if config_path else load_settings()
    results = [run_timeframe(tf, cfg, settings) for tf in timeframes]
    any_lift_pos_powered = any(r["lift_pos_powered"] for r in results)
    return {
        "generated_by": "fib_selection_learning",
        "stage": "stage2_headline_live_k3",
        "metric": "pooled_test_average_precision",
        "inference": "AP-lift: decision-point cluster bootstrap (powered cells only)",
        "seed": cfg.seed,
        "timeframes": timeframes,
        "any_lift_pos_powered": any_lift_pos_powered,
        "results": results,
    }


# --- CLI --------------------------------------------------------------------------------------


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _print_k_sweep(report: dict, path: Path) -> None:
    for r in report["results_by_k"]:
        print(
            f"[k={r['k']}] active={r['active_features']} "
            f"n_test={r['n_test']} test_pos={r['n_test_positives']} powered={r['powered']} "
            f"ap_model={r['ap_model']} ap_mag={r['ap_baseline_magnitude']} "
            f"lift_vs_mag={r['ap_lift_vs_magnitude']} "
            f"survives_family={r['survives_prominence_family']} "
            f"(mag_only={r['survives_vs_magnitude']})"
        )
        print(
            f"    lift_vs_prom_sum={r['ap_lift_vs_prominence_sum']} "
            f"lift_vs_prom_max={r['ap_lift_vs_prominence_max']}"
        )
        print(f"    inf_vs_mag={r['ap_lift_inference_vs_magnitude']}")
        print(f"    inf_vs_prom_sum={r['ap_lift_inference_vs_prominence_sum']}")
        print(f"    inf_vs_prom_max={r['ap_lift_inference_vs_prominence_max']}")
        print(f"    weights={r['model_weights_standardized']}")
    print(f"k_sweep_verdict={report['k_sweep_verdict']}  summary={path}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="BTC Fib selection-learning (Stage 2 headline)")
    ap.add_argument("--timeframes", default="1d,4h")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR))
    ap.add_argument("--k-sweep", action="store_true", help="4H live-only k-sweep {0,3,6,12}")
    args = ap.parse_args(argv)
    if args.k_sweep:
        report = run_k_sweep("4h", list(K_SWEEP), args.config, SelectionConfig())
        path = _write_summary(report, Path(args.out) / "k_sweep")
        _print_k_sweep(report, path)
        return 0
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    bad = [t for t in tfs if t not in ALLOWED_TIMEFRAMES]
    if bad:
        raise SystemExit(f"disallowed timeframe(s) {bad} (1H rejected fail-closed)")
    report = run_study(tfs, args.config, SelectionConfig())
    path = _write_summary(report, Path(args.out))
    for r in report["results"]:
        print(
            f"[{r['timeframe']}] ap_model={r['ap_model']} "
            f"ap_mag={r['ap_baseline_magnitude']} ap_prom_sum={r['ap_baseline_prominence_sum']} "
            f"ap_prom_max={r['ap_baseline_prominence_max']} "
            f"lift_vs_mag={r['ap_lift_vs_magnitude']} "
            f"lift_vs_prom_sum={r['ap_lift_vs_prominence_sum']} "
            f"lift_vs_prom_max={r['ap_lift_vs_prominence_max']} "
            f"test_pos={r['n_test_positives']} powered={r['powered']} "
            f"verdict={r['prominence_survival_verdict']}"
        )
        print(f"    inf_prom_sum={r['ap_lift_inference_vs_prominence_sum']}")
        print(f"    inf_prom_max={r['ap_lift_inference_vs_prominence_max']}")
    print(f"any_lift_pos_powered={report['any_lift_pos_powered']}  summary={path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
