"""Körningsmotor: kör pipelinen, logga allt, skriv en immutabel audit-mapp.

Kör: uv run python -m fibengine.experiment
"""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from fibengine.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.evaluation.metrics import evaluate
from fibengine.labeling.store import SwingLabel, list_labels
from fibengine.logging_conf import setup_logging
from fibengine.models import Swing
from fibengine.scoring import select_swing
from fibengine.sizing.solros import build_sizing_plan, simulate_plan
from fibengine.viz.plot import plot_prediction

RUNS_DIR = REPO_ROOT / "experiments" / "runs"
LEADERBOARD = REPO_ROOT / "experiments" / "leaderboard.jsonl"


def _new_run_id() -> str:
    return datetime.now(UTC).strftime("run_%Y%m%dT%H%M%SZ")


def _maybe_emit_sizing(settings: Settings, df, swing: Swing, run_dir: Path, name: str, log):
    """Lager B: skriv en sizing-plan endast om aktiverad. Påverkar inte urvalet."""
    if not settings.sizing.enabled:
        return
    plan = simulate_plan(df, swing, build_sizing_plan(swing, settings.sizing))
    (run_dir / f"sizing_plan_{name}.json").write_text(
        json.dumps([e.to_dict() for e in plan], indent=2)
    )
    log.info("Sizing-plan ({}) skriven: {} entries", name, len(plan))


def _run_one(settings: Settings, label: SwingLabel, run_dir: Path, log) -> dict | None:
    data_cfg = settings.data.model_copy(
        update={
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
        }
    )
    df = load_candles(data_cfg)
    swing = select_swing(df, settings.pivots, settings.scoring)
    if swing is None:
        log.warning("Ingen swing detekterad för {}", label.symbol)
        return None

    atr_series = atr(df, settings.pivots.atr_period)
    atr_value = float(atr_series.iloc[swing.end.index])
    if not np.isfinite(atr_value) or atr_value <= 0:
        atr_value = float(np.nanmedian(atr_series.to_numpy()))

    metrics = evaluate(df, swing, label, atr_value, settings.evaluation)
    label_id = f"{label.exchange}_{label.symbol.replace('/', '-')}_{label.timeframe}"
    plot_path = run_dir / f"{label_id}.png"
    plot_prediction(
        df, swing, settings.fib.levels, plot_path, label=label, title=label_id
    )
    _maybe_emit_sizing(settings, df, swing, run_dir, label_id, log)
    log.info(
        "{} | status={} agreement={} fib_err={}",
        label_id, swing.status, metrics["agreement"], metrics["mean_fib_err_frac"],
    )
    return {"label": label_id, "metrics": metrics, "predicted_swing": swing.to_dict()}


def _aggregate(results: list[dict]) -> dict:
    if not results:
        return {}
    m = [r["metrics"] for r in results]
    return {
        "n": len(m),
        "mean_agreement": round(float(np.mean([x["agreement"] for x in m])), 4),
        "mean_fib_err_frac": round(float(np.mean([x["mean_fib_err_frac"] for x in m])), 4),
        "mean_high_price_err_atr": round(float(np.mean([x["high_price_err_atr"] for x in m])), 4),
        "mean_low_price_err_atr": round(float(np.mean([x["low_price_err_atr"] for x in m])), 4),
    }


def run_experiment(settings: Settings | None = None) -> Path:
    settings = settings or load_settings()
    random.seed(settings.seed)
    np.random.seed(settings.seed)

    run_id = _new_run_id()
    config_hash = settings.config_hash()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log = setup_logging(run_id, config_hash, log_file=run_dir / "run.log")

    # Immutabel config-snapshot för auditen.
    (run_dir / "config.json").write_text(json.dumps(settings.model_dump(), indent=2))
    log.info("Startar experiment {} (cfg {})", run_id, config_hash)

    labels = list_labels()
    results: list[dict] = []
    if not labels:
        log.warning("Inga labels i data/labels/ — kör enbart prediktion på konfig-symbolen.")
        df = load_candles(settings.data)
        swing = select_swing(df, settings.pivots, settings.scoring)
        if swing is not None:
            plot_prediction(
                df, swing, settings.fib.levels,
                run_dir / "prediction.png",
                title=f"{settings.data.symbol} {settings.data.timeframe}",
            )
            _maybe_emit_sizing(settings, df, swing, run_dir, "demo", log)
            log.info("Predikterad leg: {}", swing.to_dict())
    else:
        for label in labels:
            r = _run_one(settings, label, run_dir, log)
            if r is not None:
                results.append(r)

    aggregate = _aggregate(results)
    (run_dir / "metrics.json").write_text(
        json.dumps({"aggregate": aggregate, "results": results}, indent=2)
    )

    leaderboard_row = {
        "run_id": run_id,
        "config_hash": config_hash,
        "timestamp": datetime.now(UTC).isoformat(),
        "weights": settings.scoring.weights,
        **aggregate,
    }
    with LEADERBOARD.open("a") as f:
        f.write(json.dumps(leaderboard_row) + "\n")

    log.info("Klart. Audit-mapp: {} | aggregate: {}", run_dir, aggregate)
    return run_dir


if __name__ == "__main__":
    run_experiment()
