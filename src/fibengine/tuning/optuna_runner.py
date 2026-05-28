"""Optuna-based tuning for Layer A scoring weights.

Run:
    uv run python -m fibengine.tuning.optuna_runner --trials 30
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import optuna

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.scoring import select_swing
from fibengine.data.loader import atr, load_candles
from fibengine.evaluation.metrics import evaluate
from fibengine.labeling.store import SwingLabel, list_labels

RESULTS_DIR = REPO_ROOT / "experiments" / "results"
TRIALS_JSONL = RESULTS_DIR / "optuna_trials.jsonl"
BEST_JSON = RESULTS_DIR / "optuna_best.json"
RUNS_DIR = REPO_ROOT / "experiments" / "runs"


def _run_id() -> str:
    return datetime.now(UTC).strftime("optuna_%Y%m%dT%H%M%SZ")


def _run_dir(run_id: str) -> Path:
    stamp = run_id.split("_", 1)[1]
    run_date = f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}"
    return RUNS_DIR / "optuna" / run_date / run_id


def _csv_set(value: str | None) -> set[str]:
    if not value:
        return set()
    return {x.strip() for x in value.split(",") if x.strip()}


def _filter_labels(
    labels: list[SwingLabel], symbols: set[str], timeframes: set[str]
) -> list[SwingLabel]:
    out = labels
    if symbols:
        out = [lbl for lbl in out if lbl.symbol in symbols]
    if timeframes:
        out = [lbl for lbl in out if lbl.timeframe in timeframes]
    return out


def _cached_frames(
    labels: list[SwingLabel], settings: Settings
) -> dict[tuple[str, str, str], object]:
    frames = {}
    for label in labels:
        key = (label.exchange, label.symbol, label.timeframe)
        if key in frames:
            continue
        cfg = settings.data.model_copy(
            update={
                "exchange": label.exchange,
                "symbol": label.symbol,
                "timeframe": label.timeframe,
            }
        )
        frames[key] = load_candles(cfg)
    return frames


def tune(
    settings: Settings,
    labels: list[SwingLabel],
    trials: int,
    timeout_s: int | None,
    seed: int,
    fib_penalty: float,
) -> Path:
    if not labels:
        raise ValueError("Inga labels hittades för tuning.")

    run_id = _run_id()
    run_dir = _run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(
        json.dumps(settings.model_dump(), indent=2), encoding="utf-8"
    )

    frames = _cached_frames(labels, settings)
    base_weights = settings.scoring.weights
    keys = sorted(base_weights.keys())

    sampler = optuna.samplers.TPESampler(seed=seed)
    study = optuna.create_study(direction="maximize", sampler=sampler)

    def objective(trial: optuna.Trial) -> float:
        trial_weights = {}
        for key in keys:
            base = base_weights[key]
            lo = min(-2.0, base - 1.5)
            hi = max(2.0, base + 1.5)
            trial_weights[key] = trial.suggest_float(key, lo, hi)

        scoring_cfg = settings.scoring.model_copy(update={"weights": trial_weights})

        metrics_all = []
        for label in labels:
            df = frames[(label.exchange, label.symbol, label.timeframe)]
            swing = select_swing(df, settings.pivots, scoring_cfg)
            if swing is None:
                continue
            atr_series = atr(df, settings.pivots.atr_period)
            atr_value = float(atr_series.iloc[swing.end.index])
            if not np.isfinite(atr_value) or atr_value <= 0:
                atr_value = float(np.nanmedian(atr_series.to_numpy()))
            metrics_all.append(evaluate(df, swing, label, atr_value, settings.evaluation))

        if not metrics_all:
            return -1e9

        mean_agreement = float(np.mean([m["agreement"] for m in metrics_all]))
        mean_fib_err = float(np.mean([m["mean_fib_err_frac"] for m in metrics_all]))
        objective_value = mean_agreement - fib_penalty * mean_fib_err

        trial.set_user_attr("n", len(metrics_all))
        trial.set_user_attr("mean_agreement", round(mean_agreement, 6))
        trial.set_user_attr("mean_fib_err_frac", round(mean_fib_err, 6))
        trial.set_user_attr("objective", round(objective_value, 6))

        row = {
            "run_id": run_id,
            "trial": trial.number,
            "timestamp": datetime.now(UTC).isoformat(),
            "objective": round(objective_value, 6),
            "mean_agreement": round(mean_agreement, 6),
            "mean_fib_err_frac": round(mean_fib_err, 6),
            "n": len(metrics_all),
            "weights": trial_weights,
        }
        with TRIALS_JSONL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        return objective_value

    study.optimize(objective, n_trials=trials, timeout=timeout_s)

    best = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "trials": trials,
        "seed": seed,
        "fib_penalty": fib_penalty,
        "best_value": study.best_value,
        "best_trial": study.best_trial.number,
        "best_params": study.best_trial.params,
        "best_attrs": study.best_trial.user_attrs,
    }
    BEST_JSON.write_text(json.dumps(best, indent=2), encoding="utf-8")
    (run_dir / "best.json").write_text(json.dumps(best, indent=2), encoding="utf-8")
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "label_count": len(labels),
                "trials": len(study.trials),
                "best_value": study.best_value,
                "best_trial": study.best_trial.number,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_dir


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tune scoring weights with Optuna (Layer A).")
    p.add_argument(
        "--config",
        type=str,
        default="",
        help="Optional settings file path (default: config/settings.yaml).",
    )
    p.add_argument("--trials", type=int, default=30, help="Number of Optuna trials.")
    p.add_argument("--timeout-sec", type=int, default=None, help="Optional timeout in seconds.")
    p.add_argument("--seed", type=int, default=42, help="Seed for Optuna sampler.")
    p.add_argument(
        "--fib-penalty", type=float, default=0.15, help="Penalty multiplier for mean_fib_err_frac."
    )
    p.add_argument("--symbols", type=str, default="", help="CSV filter, e.g. BTC/USDT,ETH/USDT")
    p.add_argument("--timeframes", type=str, default="", help="CSV filter, e.g. 15m,1h,4h")
    return p.parse_args()


def main():
    args = _parse_args()
    settings = load_settings(args.config or None)
    labels = list_labels()
    labels = _filter_labels(labels, _csv_set(args.symbols), _csv_set(args.timeframes))
    run_dir = tune(
        settings=settings,
        labels=labels,
        trials=args.trials,
        timeout_s=args.timeout_sec,
        seed=args.seed,
        fib_penalty=args.fib_penalty,
    )
    print(run_dir)


if __name__ == "__main__":
    main()
