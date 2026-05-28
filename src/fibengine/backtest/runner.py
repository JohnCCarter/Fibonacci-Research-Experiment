"""Kör stabilitets-backtestet och skriv en audit-mapp + tidslinje-plot.

Kör: uv run python -m fibengine.backtest.runner
"""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-säkert
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from fibengine.backtest.stability import stability_metrics, walk_forward_selection  # noqa: E402
from fibengine.config import REPO_ROOT, Settings, load_settings  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.logging_conf import setup_logging  # noqa: E402

RUNS_DIR = REPO_ROOT / "experiments" / "runs"
BACKTESTS = REPO_ROOT / "experiments" / "backtests.jsonl"


def _plot_timeline(df, records: list[dict], out_path: Path):
    """Visa hur den valda legens endpunkter rör sig medan cursorn stegar framåt."""
    fig, (ax_p, ax_s) = plt.subplots(
        2, 1, figsize=(14, 8), sharex=True, height_ratios=[2, 1]
    )
    ax_p.plot(range(len(df)), df["close"].to_numpy(), color="black", lw=0.7)
    ax_p.set_title("Pris + vald legs endpunkter (kausalt walk-forward)")

    ts = [r["t"] for r in records]
    starts = [r["swing"].start.index if r["swing"] else np.nan for r in records]
    ends = [r["swing"].end.index if r["swing"] else np.nan for r in records]
    ax_s.plot(ts, starts, color="tab:green", lw=1.2, label="vald start-bar")
    ax_s.plot(ts, ends, color="tab:blue", lw=1.2, label="vald end-bar")
    ax_s.plot(ts, ts, color="gray", lw=0.5, ls="--", label="cursor (nu)")
    ax_s.set_xlabel("cursor-position t (bar)")
    ax_s.set_ylabel("vald endpunkt (bar)")
    ax_s.legend(loc="upper left", fontsize=8)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def run_backtest(settings: Settings | None = None) -> Path:
    settings = settings or load_settings()
    random.seed(settings.seed)
    np.random.seed(settings.seed)

    run_id = datetime.now(UTC).strftime("bt_%Y%m%dT%H%M%SZ")
    config_hash = settings.config_hash()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log = setup_logging(run_id, config_hash, log_file=run_dir / "run.log")

    (run_dir / "config.json").write_text(json.dumps(settings.model_dump(), indent=2))
    df = load_candles(settings.data)
    log.info("Backtest {} på {} barer (warmup {})", run_id, len(df), settings.backtest.warmup_bars)

    records = walk_forward_selection(
        df, settings, settings.backtest.warmup_bars, settings.backtest.step
    )
    metrics = stability_metrics(records, settings.backtest.extension_tol_bars)
    _plot_timeline(df, records, run_dir / "stability_timeline.png")
    (run_dir / "stability.json").write_text(json.dumps(metrics, indent=2))

    row = {
        "run_id": run_id,
        "config_hash": config_hash,
        "timestamp": datetime.now(UTC).isoformat(),
        **metrics,
    }
    with BACKTESTS.open("a") as f:
        f.write(json.dumps(row) + "\n")

    log.info("Klart. Stabilitet: {}", metrics)
    return run_dir


if __name__ == "__main__":
    run_backtest()
