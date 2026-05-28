"""Simple Layer B trade simulation from confirmed Layer A Fibonacci swings.

This module consumes selected swings; it does not feed results back into Layer A.

Run:
    uv run python -m fibengine.backtest.trade
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd

from fibengine.backtest.matrix import MatrixCase, _case_settings, default_matrix
from fibengine.backtest.stability import walk_forward_selection
from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.fib import fib_levels
from fibengine.data.loader import load_candles

TRADE_RESULTS = REPO_ROOT / "experiments" / "results" / "trade_backtests.jsonl"
TRADE_MATRIX_RESULTS = REPO_ROOT / "experiments" / "results" / "trade_matrix.jsonl"


@dataclass
class Trade:
    t: int
    direction: str
    entry: float
    stop: float
    target: float
    filled: bool
    outcome: str
    r_multiple: float
    fill_bar: int | None = None
    exit_bar: int | None = None


def _simulate_trade(
    df: pd.DataFrame,
    t: int,
    direction: str,
    entry: float,
    stop: float,
    target: float,
) -> Trade:
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    fill_bar: int | None = None
    risk = abs(entry - stop)
    reward = abs(target - entry)
    target_r = reward / risk if risk > 0 else 0.0

    for bar in range(t + 1, len(df)):
        if lows[bar] <= entry <= highs[bar]:
            fill_bar = bar
            break

    if fill_bar is None:
        return Trade(t, direction, entry, stop, target, False, "unfilled", 0.0)
    if risk <= 0 or reward <= 0:
        return Trade(t, direction, entry, stop, target, True, "invalid", 0.0, fill_bar)

    for bar in range(fill_bar, len(df)):
        if direction == "up":
            stopped = lows[bar] <= stop
            targeted = highs[bar] >= target
        else:
            stopped = highs[bar] >= stop
            targeted = lows[bar] <= target

        if stopped and targeted:
            return Trade(t, direction, entry, stop, target, True, "ambiguous", 0.0, fill_bar, bar)
        if targeted:
            return Trade(t, direction, entry, stop, target, True, "target", target_r, fill_bar, bar)
        if stopped:
            return Trade(t, direction, entry, stop, target, True, "stop", -1.0, fill_bar, bar)

    return Trade(t, direction, entry, stop, target, True, "open", 0.0, fill_bar, None)


def trades_from_records(df: pd.DataFrame, settings: Settings, records: list[dict]) -> list[Trade]:
    """Build one illustrative trade per confirmed selected swing snapshot."""
    trades: list[Trade] = []
    seen: set[tuple[int, int, str]] = set()
    entry_level = settings.sizing.entry_levels[-1]

    for record in records:
        swing = record["swing"]
        if swing is None or swing.status != "confirmed":
            continue

        key = (swing.start.index, swing.end.index, swing.direction)
        if key in seen:
            continue
        seen.add(key)

        levels = fib_levels(swing, [entry_level])
        entry = levels[entry_level]
        stop = swing.start.price
        target = swing.end.price
        trades.append(_simulate_trade(df, record["t"], swing.direction, entry, stop, target))

    return trades


def summarize_trades(trades: list[Trade]) -> dict:
    filled = [t for t in trades if t.filled]
    closed = [t for t in filled if t.outcome in {"target", "stop", "ambiguous", "invalid"}]
    wins = [t for t in closed if t.outcome == "target"]
    losses = [t for t in closed if t.outcome == "stop"]
    ambiguous = [t for t in closed if t.outcome == "ambiguous"]
    return {
        "trades": len(trades),
        "filled": len(filled),
        "closed": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(ambiguous),
        "fill_rate": round(len(filled) / len(trades), 4) if trades else 0.0,
        "win_rate": round(len(wins) / len(closed), 4) if closed else 0.0,
        "avg_r": round(sum(t.r_multiple for t in closed) / len(closed), 4) if closed else 0.0,
    }


def run_trade_backtest(settings: Settings | None = None) -> dict:
    settings = settings or load_settings()
    run_id = datetime.now(UTC).strftime("trade_%Y%m%dT%H%M%SZ")
    df = load_candles(settings.data)
    records = walk_forward_selection(
        df, settings, settings.backtest.warmup_bars, settings.backtest.step
    )
    trades = trades_from_records(df, settings, records)
    summary = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "config_hash": settings.config_hash(),
        "exchange": settings.data.exchange,
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "limit": settings.data.limit,
        **summarize_trades(trades),
    }
    TRADE_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with TRADE_RESULTS.open("a") as f:
        f.write(json.dumps(summary, sort_keys=True) + "\n")
    return summary


def _trade_summary_for_settings(
    settings: Settings,
    run_id: str,
    timestamp: str,
) -> dict:
    df = load_candles(settings.data)
    records = walk_forward_selection(
        df, settings, settings.backtest.warmup_bars, settings.backtest.step
    )
    trades = trades_from_records(df, settings, records)
    return {
        "run_id": run_id,
        "timestamp": timestamp,
        "config_hash": settings.config_hash(),
        "exchange": settings.data.exchange,
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "limit": settings.data.limit,
        "candles": len(df),
        "status": "ok",
        **summarize_trades(trades),
    }


def run_trade_matrix(
    settings: Settings | None = None,
    cases: list[MatrixCase] | None = None,
) -> list[dict]:
    """Run the simple Layer B trade simulation over the standard market matrix."""
    settings = settings or load_settings()
    run_id = datetime.now(UTC).strftime("trade_matrix_%Y%m%dT%H%M%SZ")
    rows: list[dict] = []

    for case in cases or default_matrix():
        case_settings = _case_settings(settings, case)
        timestamp = datetime.now(UTC).isoformat()
        try:
            row = _trade_summary_for_settings(case_settings, run_id, timestamp)
        except Exception as exc:  # noqa: BLE001 - keep batch failures observable.
            row = {
                "run_id": run_id,
                "timestamp": timestamp,
                "config_hash": case_settings.config_hash(),
                "exchange": case_settings.data.exchange,
                "symbol": case.symbol,
                "timeframe": case.timeframe,
                "limit": case_settings.data.limit,
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        TRADE_MATRIX_RESULTS.parent.mkdir(parents=True, exist_ok=True)
        with TRADE_MATRIX_RESULTS.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        rows.append(row)

    return rows


if __name__ == "__main__":
    print(json.dumps(run_trade_backtest(), indent=2))
