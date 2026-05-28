"""Run Layer A stability backtests over a real-market symbol/timeframe matrix.

Run:
    uv run python -m fibengine.backtest.matrix
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np

from fibengine.backtest.stability import stability_metrics, walk_forward_selection
from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.logging_conf import setup_logging
from fibengine.data.loader import load_candles

MATRIX_RESULTS = REPO_ROOT / "experiments" / "results" / "backtest_matrix.jsonl"
DEFAULT_SYMBOLS = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
DEFAULT_TIMEFRAMES = ("15m", "1h", "4h")


@dataclass(frozen=True)
class MatrixCase:
    symbol: str
    timeframe: str


def default_matrix() -> list[MatrixCase]:
    return [
        MatrixCase(symbol=symbol, timeframe=timeframe)
        for symbol in DEFAULT_SYMBOLS
        for timeframe in DEFAULT_TIMEFRAMES
    ]


def _append_jsonl(path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def _case_settings(settings: Settings, case: MatrixCase) -> Settings:
    return settings.model_copy(
        deep=True,
        update={
            "data": settings.data.model_copy(
                update={"symbol": case.symbol, "timeframe": case.timeframe}
            )
        },
    )


def run_matrix(
    settings: Settings | None = None,
    cases: Iterable[MatrixCase] | None = None,
) -> list[dict]:
    """Run stability backtests for each matrix case and persist JSONL rows."""
    settings = settings or load_settings()
    cases = list(cases or default_matrix())
    run_id = datetime.now(UTC).strftime("matrix_%Y%m%dT%H%M%SZ")
    log = setup_logging(run_id, settings.config_hash())
    rows: list[dict] = []

    random.seed(settings.seed)
    np.random.seed(settings.seed)

    for case in cases:
        case_settings = _case_settings(settings, case)
        config_hash = case_settings.config_hash()
        started_at = datetime.now(UTC).isoformat()
        base_row = {
            "run_id": run_id,
            "timestamp": started_at,
            "exchange": case_settings.data.exchange,
            "symbol": case.symbol,
            "timeframe": case.timeframe,
            "limit": case_settings.data.limit,
            "config_hash": config_hash,
        }
        try:
            df = load_candles(case_settings.data)
            records = walk_forward_selection(
                df,
                case_settings,
                case_settings.backtest.warmup_bars,
                case_settings.backtest.step,
            )
            metrics = stability_metrics(records, case_settings.backtest.extension_tol_bars)
            row = {
                **base_row,
                "status": "ok",
                "candles": len(df),
                **metrics,
            }
            log.info(
                "Matrix {} {} klart: flip={} confirmed={}",
                case.symbol,
                case.timeframe,
                metrics["flip_rate"],
                metrics["confirmed_rate"],
            )
        except Exception as exc:  # noqa: BLE001 - record failures per case.
            row = {
                **base_row,
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            log.error("Matrix {} {} fel: {}", case.symbol, case.timeframe, exc)

        _append_jsonl(MATRIX_RESULTS, row)
        rows.append(row)

    return rows


if __name__ == "__main__":
    run_matrix()
