"""Measure whether detected pivots cover manually labeled swing endpoints.

This is a Layer A diagnostic: it evaluates candidate pivot recall before scoring
changes are considered.

Run:
    uv run python -m fibengine.evaluation.pivot_recall
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fibengine.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.metrics import _bar_of_timestamp
from fibengine.labeling.store import SwingLabel, list_labels
from fibengine.models import Pivot
from fibengine.pivots.detect import detect_pivots

PIVOT_RECALL_RESULTS = REPO_ROOT / "experiments" / "pivot_recall.jsonl"


def _nearest_pivot(
    pivots: list[Pivot],
    target_bar: int,
    kind: str,
) -> tuple[Pivot | None, int | None]:
    candidates = [p for p in pivots if p.kind == kind]
    if not candidates:
        return None, None
    nearest = min(candidates, key=lambda p: abs(p.index - target_bar))
    return nearest, abs(nearest.index - target_bar)


def evaluate_label_recall(
    settings: Settings,
    label: SwingLabel,
    tol_bars: int | None = None,
) -> dict:
    """Return pivot-recall metrics for one manual swing label."""
    data_cfg = settings.data.model_copy(
        update={
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
        }
    )
    df = load_candles(data_cfg)
    pivots = detect_pivots(df, settings.pivots)
    tol = tol_bars if tol_bars is not None else max(1, settings.pivots.lookback)

    high_bar = _bar_of_timestamp(df, label.high.timestamp)
    low_bar = _bar_of_timestamp(df, label.low.timestamp)
    high_pivot, high_dist = _nearest_pivot(pivots, high_bar, "high")
    low_pivot, low_dist = _nearest_pivot(pivots, low_bar, "low")

    high_hit = high_dist is not None and high_dist <= tol
    low_hit = low_dist is not None and low_dist <= tol

    return {
        "exchange": label.exchange,
        "symbol": label.symbol,
        "timeframe": label.timeframe,
        "tol_bars": tol,
        "n_pivots": len(pivots),
        "high_bar": high_bar,
        "low_bar": low_bar,
        "high_hit": high_hit,
        "low_hit": low_hit,
        "both_hit": high_hit and low_hit,
        "high_dist_bars": high_dist,
        "low_dist_bars": low_dist,
        "nearest_high": high_pivot.to_dict() if high_pivot else None,
        "nearest_low": low_pivot.to_dict() if low_pivot else None,
    }


def run_pivot_recall(settings: Settings | None = None) -> list[dict]:
    settings = settings or load_settings()
    rows: list[dict] = []
    run_id = datetime.now(UTC).strftime("pivot_recall_%Y%m%dT%H%M%SZ")
    labels = list_labels()

    for label in labels:
        row = {
            "run_id": run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "config_hash": settings.config_hash(),
            **evaluate_label_recall(settings, label),
        }
        rows.append(row)

    if rows:
        PIVOT_RECALL_RESULTS.parent.mkdir(parents=True, exist_ok=True)
        with PIVOT_RECALL_RESULTS.open("a") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    return rows


if __name__ == "__main__":
    result_rows = run_pivot_recall()
    print(json.dumps({"labels": len(result_rows), "rows": result_rows}, indent=2))
