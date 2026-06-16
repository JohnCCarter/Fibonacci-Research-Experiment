"""Context-conditioned BTC/Fib study (research-only, Lean Fib Research).

Follows the no-signal behaviour event study. New pre-registered question: do fib levels react
differently than matched placebo/swing levels **only within causal market contexts** (trend
regime; deep retracement)? Primary metric is continuous (`reaction_asym_atr = MFE - MAE`), tested
with a rank permutation test, Holm-corrected across the two confirmatory contexts.

**Behaviour only — no trading/edge claim, no Genesis touch, no 1H, no auto-fib, no label
mutation.** A positive result is a CANDIDATE for future fresh-data testing, never a confirmation.

Pre-registration (frozen): docs/research_wiki/reviews/
btc-fib-context-conditioned-study-prereg-20260616.md

Run:
    uv run python -m fibengine.research.fib_context_conditioned_study \\
        --timeframes 4h,1d --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.research.fib_behaviour_event_study import (
    _TF_PARAMS,
    ALLOWED_TIMEFRAMES,
    EventStudyConfig,
    _window_of,
    detect_swing_levels,
    event_reject,
    find_events,
    load_fib_levels,
    make_placebo_levels,
)

RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "fib_context_conditioned_study"
DEEP_RATIOS = (0.618, 0.786)  # golden-ratio prior (frozen)
SHALLOW_RATIOS = (0.382, 0.5)
CONFIRMATORY = ("trend", "deep")  # K = 2 (frozen)


@dataclass(frozen=True)
class ContextConfig:
    """Frozen context-definition parameters (prereg §3-§4)."""

    trend_lookback: int = 50  # L: log-return averaging window
    trend_median_window: int = 500  # W: causal trailing median window
    vol_window: int = 100  # exploratory ATR-percentile window
    holm_alpha: float = 0.05  # family-wise alpha across K confirmatory tests
    min_events: int = 30


# --- causal context flags ---------------------------------------------------------------------


def trend_flags(df: pd.DataFrame, ctx: ContextConfig) -> np.ndarray:
    """Causal in-trend mask: |rolling-mean log-return (L)| above its trailing rolling median (W)."""
    logc = np.log(df["close"].to_numpy())
    ret = pd.Series(np.diff(logc, prepend=logc[0]), index=df.index)
    absroll = ret.rolling(ctx.trend_lookback, min_periods=ctx.trend_lookback).mean().abs()
    thresh = absroll.rolling(ctx.trend_median_window, min_periods=ctx.trend_lookback).median()
    flags = np.array((absroll > thresh).to_numpy(), dtype=bool, copy=True)
    flags[~np.isfinite(absroll.to_numpy())] = False  # warmup → not in trend (fail-closed)
    return flags


def vol_high_flags(df: pd.DataFrame, atr_s: np.ndarray, ctx: ContextConfig) -> np.ndarray:
    """Exploratory: high-volatility mask = ATR above its trailing rolling median (causal)."""
    a = pd.Series(atr_s, index=df.index)
    med = a.rolling(ctx.vol_window, min_periods=ctx.trend_lookback).median()
    flags = np.array((a > med).to_numpy(), dtype=bool, copy=True)
    flags[~np.isfinite(med.to_numpy())] = False
    return flags


# --- event tables -----------------------------------------------------------------------------


def _event_rows(
    df: pd.DataFrame,
    atr_s: np.ndarray,
    levels: list,
    cfg: EventStudyConfig,
    tf: str,
    split_idx: int,
    primary_h: int,
    max_h: int,
    trend: np.ndarray,
    vol: np.ndarray,
) -> list[dict[str, Any]]:
    """Per-event rows tagged with window + causal context flags + the continuous primary metric."""
    n = len(df)
    rows: list[dict[str, Any]] = []
    seen: set[float] = set()
    for ev in find_events(df, atr_s, levels, cfg, tf):
        win = _window_of(ev.pos, split_idx, n, max_h)
        if win is None:
            continue
        res = event_reject(df, atr_s, ev, primary_h, cfg.react_eps)
        if res is None:
            continue
        first = ev.level not in seen
        seen.add(ev.level)
        rows.append(
            {
                "window": win,
                "asym": res["mfe_atr"] - res["mae_atr"],
                "reject": res["reject"],
                "trend": bool(trend[ev.pos]),
                "vol_high": bool(vol[ev.pos]),
                "first_touch": first,
                "pos": ev.pos,
            }
        )
    return rows


# --- statistics -------------------------------------------------------------------------------


def rank_perm_p(
    a: list[float], b: list[float], rng: np.random.Generator, n_perm: int
) -> float | None:
    """Rank-based two-sided permutation p for the difference in mean rank between A and B."""
    if len(a) < 2 or len(b) < 2:
        return None
    pooled = np.concatenate([np.asarray(a, float), np.asarray(b, float)])
    ranks = np.argsort(np.argsort(pooled)).astype(float)  # 0-based ranks (ties arbitrary)
    na = len(a)
    obs = abs(ranks[:na].mean() - ranks[na:].mean())
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(ranks)
        if abs(perm[:na].mean() - perm[na:].mean()) >= obs - 1e-9:
            count += 1
    return (count + 1) / (n_perm + 1)


def _cell(rows: list[dict], window: str, *, trend=None, deep_rows=None) -> list[float]:
    """asym values for a window, optionally filtered by trend flag."""
    src = rows if deep_rows is None else deep_rows
    return [
        r["asym"] for r in src if r["window"] == window and (trend is None or r["trend"] == trend)
    ]


def _stats(vals: list[float]) -> dict[str, Any]:
    if not vals:
        return {"n": 0, "mean": None, "median": None}
    arr = np.asarray(vals, float)
    return {"n": len(arr), "mean": float(arr.mean()), "median": float(np.median(arr))}


def _mde(vals_a: list[float], vals_b: list[float], alpha: float) -> float | None:
    """Pre-registered MDE in ATR units (Cohen-style) for the achieved cell sizes."""
    if len(vals_a) < 2 or len(vals_b) < 2:
        return None
    pooled = np.concatenate([np.asarray(vals_a, float), np.asarray(vals_b, float)])
    sd = float(np.std(pooled, ddof=1))
    z = 2.24 if abs(alpha - 0.025) < 1e-6 else 1.96
    nmin = min(len(vals_a), len(vals_b))
    return (z + 0.84) * sd * np.sqrt(2.0 / nmin)


def _holm(pvals: dict[str, float | None], alpha: float) -> dict[str, bool]:
    """Holm-Bonferroni: returns {context: significant_bool} for the FIB-vs-PLACEBO family."""
    items = [(k, v) for k, v in pvals.items() if v is not None]
    items.sort(key=lambda kv: kv[1])
    m = len(items)
    out: dict[str, bool] = {k: False for k in pvals}
    for rank, (k, p) in enumerate(items):
        if p <= alpha / (m - rank):
            out[k] = True
        else:
            break  # Holm stops at first failure
    return out


# --- per-timeframe driver ---------------------------------------------------------------------


def run_timeframe_context(
    tf: str, cfg: EventStudyConfig, ctx: ContextConfig, settings: Any
) -> dict[str, Any]:
    if tf not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {tf!r} not allowed (1H is rejected fail-closed)")
    horizons, primary_h, _, _ = _TF_PARAMS[tf]
    max_h = max(horizons)
    data_cfg = settings.data.model_copy(update={"timeframe": tf})
    df = load_candles(data_cfg, fetch_if_missing=False, strict=False)
    if df.empty:
        raise ValueError(f"empty candle frame for {tf} — fail-closed")
    atr_s = atr(df, period=cfg.atr_period).to_numpy()
    rng = np.random.default_rng(cfg.seed)
    trend = trend_flags(df, ctx)
    vol = vol_high_flags(df, atr_s, ctx)
    split_idx = int(len(df) * cfg.train_frac)

    fib = load_fib_levels(tf, cfg)
    deep = load_fib_levels(tf, cfg, ratios=DEEP_RATIOS)
    shallow = load_fib_levels(tf, cfg, ratios=SHALLOW_RATIOS)
    placebo = make_placebo_levels(fib, df, rng)
    swing = detect_swing_levels(df, cfg)

    def tbl(levels):
        return _event_rows(df, atr_s, levels, cfg, tf, split_idx, primary_h, max_h, trend, vol)

    fib_r, deep_r, shal_r = tbl(fib), tbl(deep), tbl(shallow)
    plc_r, swg_r = tbl(placebo), tbl(swing)

    # confirmatory cells (predicted cell vs comparison arm)
    cells = {
        "trend": {
            "fib": _cell(fib_r, "test", trend=True),
            "placebo": _cell(plc_r, "test", trend=True),
            "swing": _cell(swg_r, "test", trend=True),
            "fib_train": _cell(fib_r, "train", trend=True),
            "placebo_train": _cell(plc_r, "train", trend=True),
        },
        "deep": {
            "fib": _cell(None, "test", deep_rows=deep_r),
            "placebo": _cell(plc_r, "test"),
            "swing": _cell(swg_r, "test"),
            "fib_train": _cell(None, "train", deep_rows=deep_r),
            "placebo_train": _cell(plc_r, "train"),
        },
    }

    contexts: dict[str, Any] = {}
    fib_vs_plc_p: dict[str, float | None] = {}
    for name in CONFIRMATORY:
        c = cells[name]
        rng_c = np.random.default_rng(cfg.seed + (1 if name == "deep" else 0))
        p_plc = rank_perm_p(c["fib"], c["placebo"], rng_c, cfg.n_perm)
        p_swg = rank_perm_p(c["fib"], c["swing"], rng_c, cfg.n_perm)
        fib_vs_plc_p[name] = p_plc
        contexts[name] = {
            "fib": _stats(c["fib"]),
            "placebo": _stats(c["placebo"]),
            "swing": _stats(c["swing"]),
            "fib_train": _stats(c["fib_train"]),
            "placebo_train": _stats(c["placebo_train"]),
            "p_vs_placebo_test": p_plc,
            "p_vs_swing_test": p_swg,
            "mde_vs_placebo_atr": _mde(c["fib"], c["placebo"], ctx.holm_alpha / 2),
        }
    holm = _holm(fib_vs_plc_p, ctx.holm_alpha)

    gate = {name: _gate_one(contexts[name], holm[name], ctx.min_events) for name in CONFIRMATORY}
    any_candidate = any(gate[name]["candidate"] for name in CONFIRMATORY)

    # exploratory (descriptive only)
    exploratory = {
        "first_touch_test_n": {
            "fib": sum(1 for r in fib_r if r["window"] == "test" and r["first_touch"]),
            "placebo": sum(1 for r in plc_r if r["window"] == "test" and r["first_touch"]),
        },
        "range_fib_test": _stats(_cell(fib_r, "test", trend=False)),
        "shallow_fib_test": _stats(_cell(shal_r, "test")),
    }
    return {
        "timeframe": tf,
        "n_bars": len(df),
        "primary_horizon": primary_h,
        "contexts": contexts,
        "holm_significant": holm,
        "gate": gate,
        "any_candidate": any_candidate,
        "exploratory": exploratory,
    }


def _gate_one(ctx_stats: dict, holm_sig: bool, min_events: int) -> dict[str, Any]:
    f, p, s = ctx_stats["fib"], ctx_stats["placebo"], ctx_stats["swing"]
    ft, pt = ctx_stats["fib_train"], ctx_stats["placebo_train"]
    n_ok = f["n"] >= min_events and p["n"] >= min_events
    beats = (
        f["mean"] is not None
        and p["mean"] is not None
        and s["mean"] is not None
        and f["mean"] > p["mean"]
        and f["mean"] > s["mean"]
    )
    train_sign = ft["mean"] is not None and pt["mean"] is not None and (ft["mean"] - pt["mean"]) > 0
    candidate = bool(n_ok and beats and holm_sig and train_sign)
    return {
        "n_ge_min": n_ok,
        "fib_beats_both_test": beats,
        "holm_significant": holm_sig,
        "train_same_sign": train_sign,
        "candidate": candidate,
    }


def run_study(
    timeframes: list[str], config_path: str | None, cfg: EventStudyConfig, ctx: ContextConfig
) -> dict:
    settings = load_settings(config_path) if config_path else load_settings()
    results = [run_timeframe_context(tf, cfg, ctx, settings) for tf in timeframes]
    confirmatory = [r for r in results if r["timeframe"] == "4h"]
    any_candidate = any(r["any_candidate"] for r in confirmatory)  # verdict: 4h only
    return {
        "generated_by": "fib_context_conditioned_study",
        "seed": cfg.seed,
        "confirmatory_tf": "4h",
        "timeframes": timeframes,
        "any_candidate_confirmatory": any_candidate,
        "results": results,
    }


# --- CLI --------------------------------------------------------------------------------------


def _write_summary(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Context-conditioned BTC/Fib study")
    ap.add_argument("--timeframes", default="4h,1d")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR))
    args = ap.parse_args(argv)
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    bad = [t for t in tfs if t not in ALLOWED_TIMEFRAMES]
    if bad:
        raise SystemExit(f"disallowed timeframe(s) {bad} (1H is rejected fail-closed)")
    report = run_study(tfs, args.config, EventStudyConfig(), ContextConfig())
    path = _write_summary(report, Path(args.out))
    for r in report["results"]:
        for name in CONFIRMATORY:
            c, g = r["contexts"][name], r["gate"][name]
            print(
                f"[{r['timeframe']}/{name}] fib={c['fib']['mean']} (N={c['fib']['n']}) "
                f"plc={c['placebo']['mean']} (N={c['placebo']['n']}) "
                f"p={c['p_vs_placebo_test']} mde={c['mde_vs_placebo_atr']} "
                f"candidate={g['candidate']}"
            )
    print(f"any_candidate_confirmatory={report['any_candidate_confirmatory']}  summary={path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
