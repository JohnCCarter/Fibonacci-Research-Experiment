"""Measure whether detected pivots cover manually labeled swing endpoints.

This is a Layer A diagnostic: it evaluates candidate pivot recall before scoring
changes are considered.

Run:
    uv run python -m fibengine.evaluation.pivot_recall
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime

import pandas as pd

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.logging_conf import setup_logging
from fibengine.core.models import Pivot
from fibengine.data.loader import load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.labeling.mtf_disambiguation import disambiguate_label_endpoints
from fibengine.labeling.store import SwingLabel, list_labels
from fibengine.pivots.detect import detect_pivots

PIVOT_RECALL_RESULTS = REPO_ROOT / "experiments" / "results" / "pivot_recall.jsonl"


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
    pivot_producer: Callable[[pd.DataFrame], list[Pivot]] | None = None,
) -> dict:
    """Return pivot-recall metrics for one manual swing label.

    ``pivot_producer`` injicerar kandidat-pivots (t.ex. en alternativ detektor som
    trunkerar ramen kausalt). None → default ``detect_pivots`` (alla befintliga
    anropare oförändrade).
    """
    data_cfg = settings.data.model_copy(
        update={
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
        }
    )
    df = load_candles(data_cfg)
    endpoints = disambiguate_label_endpoints(label, df, settings)
    pivot_df = df
    if endpoints.time_df_timeframe != label.timeframe:
        pivot_df = load_candles(
            data_cfg.model_copy(update={"timeframe": endpoints.time_df_timeframe})
        )
    pivots = (
        pivot_producer(pivot_df)
        if pivot_producer is not None
        else detect_pivots(pivot_df, settings.pivots)
    )
    tol = tol_bars if tol_bars is not None else max(1, settings.pivots.lookback)

    if endpoints.skip_evaluation:
        return {
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
            "tol_bars": tol,
            "n_pivots": len(pivots),
            "high_bar": None,
            "low_bar": None,
            "high_hit": False,
            "low_hit": False,
            "both_hit": False,
            "out_of_window": False,
            "high_dist_bars": None,
            "low_dist_bars": None,
            "nearest_high": None,
            "nearest_low": None,
            "mtf_status": endpoints.mtf_status,
            "skipped_mtf": True,
            "mtf_skip_reason": endpoints.skip_reason,
        }

    high_bar, high_in_window = bar_of_timestamp(pivot_df, endpoints.high_timestamp)
    low_bar, low_in_window = bar_of_timestamp(pivot_df, endpoints.low_timestamp)
    high_pivot, high_dist = _nearest_pivot(pivots, high_bar, "high")
    low_pivot, low_dist = _nearest_pivot(pivots, low_bar, "low")

    out_of_window = not (high_in_window and low_in_window)
    # En out-of-window-label snäpps till en kant-bar; räkna inte det som en
    # träff (skulle annars skriva falska recall-hits till ledger).
    if out_of_window:
        high_hit = low_hit = False
        high_dist = low_dist = None
        high_pivot = low_pivot = None
    else:
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
        "out_of_window": out_of_window,
        "high_dist_bars": high_dist,
        "low_dist_bars": low_dist,
        "nearest_high": high_pivot.to_dict() if high_pivot else None,
        "nearest_low": low_pivot.to_dict() if low_pivot else None,
        "mtf_status": endpoints.mtf_status,
        "skipped_mtf": False,
    }


def summarize_recall(rows: list[dict]) -> dict:
    """Aggregera recall och gör exkluderingen EXPLICIT (inte tyst).

    Out-of-window-labels exkluderas korrekt från recall, men om många faller bort
    beräknas måtten på allt färre punkter och ser bättre ut än verkligheten. Här
    räknas och flaggas de så att ett krympande sampel syns.
    """
    n = len(rows)
    in_window = [r for r in rows if not r["out_of_window"] and not r.get("skipped_mtf")]
    n_in = len(in_window)
    n_excluded_oow = sum(1 for r in rows if r["out_of_window"] and not r.get("skipped_mtf"))
    n_excluded_mtf = sum(1 for r in rows if r.get("skipped_mtf"))
    n_excluded = n_excluded_oow + n_excluded_mtf
    summary = {
        "n_labels": n,
        "n_in_window": n_in,
        "n_excluded_out_of_window": n_excluded_oow,
        "n_excluded_mtf_unresolved": n_excluded_mtf,
        "excluded_frac": round(n_excluded / n, 4) if n else 0.0,
    }
    if in_window:
        summary["both_hit_rate"] = round(sum(1 for r in in_window if r["both_hit"]) / n_in, 4)
        summary["high_hit_rate"] = round(sum(1 for r in in_window if r["high_hit"]) / n_in, 4)
        summary["low_hit_rate"] = round(sum(1 for r in in_window if r["low_hit"]) / n_in, 4)
    else:
        summary["both_hit_rate"] = summary["high_hit_rate"] = summary["low_hit_rate"] = None
    return summary


def run_pivot_recall(settings: Settings | None = None) -> list[dict]:
    settings = settings or load_settings()
    rows: list[dict] = []
    run_id = datetime.now(UTC).strftime("pivot_recall_%Y%m%dT%H%M%SZ")
    log = setup_logging(run_id, settings.config_hash())
    # Endast mänskligt facit får vara ground truth. Maskin-labels är kandidater
    # och EXKLUDERAS — annars mäter vi motorn mot sig själv (cirkulärt).
    labels = list_labels(source="human")
    n_machine = len(list_labels(source="machine"))
    if n_machine:
        log.info("Hoppar över {} maskin-labels (ej ground truth för recall)", n_machine)

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

    summary = summarize_recall(rows)
    if summary["n_excluded_out_of_window"]:
        log.warning(
            "Pivot-recall: {}/{} labels exkluderade som out-of-window "
            "(ladda mer historik för dessa timeframes; recall mäts på {} kvar)",
            summary["n_excluded_out_of_window"],
            summary["n_labels"],
            summary["n_in_window"],
        )
    log.info("Pivot-recall sammanfattning: {}", summary)
    return rows


if __name__ == "__main__":
    result_rows = run_pivot_recall()
    print(
        json.dumps(
            {"summary": summarize_recall(result_rows), "rows": result_rows},
            indent=2,
        )
    )
