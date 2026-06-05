"""Reference-backtest via backtesting.py for comparison with the custom runner."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy

from fibengine.backtest.stability import walk_forward_selection
from fibengine.core.config import Settings, load_settings
from fibengine.core.fib import fib_levels


@dataclass(frozen=True)
class ReferenceTradePlan:
    signal_bar: int
    entry_bar: int
    direction: str
    entry: float
    stop: float
    target: float


def build_reference_trade_plans(
    df: pd.DataFrame, settings: Settings, records: list[dict]
) -> list[ReferenceTradePlan]:
    """Map confirmed Layer A swings to concrete reference trades."""
    plans: list[ReferenceTradePlan] = []
    seen: set[tuple[int, int, str]] = set()
    entry_level = settings.sizing.entry_levels[-1]
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()

    for record in records:
        swing = record["swing"]
        if swing is None or swing.status != "confirmed":
            continue

        key = (swing.start.index, swing.end.index, swing.direction)
        if key in seen:
            continue
        seen.add(key)

        entry = fib_levels(swing, [entry_level])[entry_level]
        stop = swing.start.price
        target = swing.end.price
        entry_bar = None

        for bar in range(record["t"] + 1, len(df)):
            if lows[bar] <= entry <= highs[bar]:
                entry_bar = bar
                break

        if entry_bar is None:
            continue
        plans.append(
            ReferenceTradePlan(
                signal_bar=record["t"],
                entry_bar=entry_bar,
                direction=swing.direction,
                entry=entry,
                stop=stop,
                target=target,
            )
        )

    return plans


def _backtesting_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )
    return frame[["Open", "High", "Low", "Close", "Volume"]]


class ReferenceFibStrategy(Strategy):
    plans: tuple[ReferenceTradePlan, ...] = ()

    def init(self) -> None:
        self._plans_by_bar: dict[int, list[ReferenceTradePlan]] = {}
        for plan in self.plans:
            self._plans_by_bar.setdefault(plan.entry_bar, []).append(plan)

    def next(self) -> None:
        bar = len(self.data) - 1
        if self.position:
            return

        for plan in self._plans_by_bar.get(bar, []):
            if plan.direction == "up":
                self.buy(size=1, sl=plan.stop, tp=plan.target)
            else:
                self.sell(size=1, sl=plan.stop, tp=plan.target)
            break


def run_reference_backtest(
    df: pd.DataFrame,
    trade_plans: list[ReferenceTradePlan],
    cash: float = 10_000.0,
) -> dict:
    """Execute the mapped trades in backtesting.py for cross-checking."""
    stats = Backtest(
        _backtesting_frame(df),
        ReferenceFibStrategy,
        cash=cash,
        commission=0.0,
        exclusive_orders=True,
        trade_on_close=True,
    ).run(plans=tuple(trade_plans))
    profit_factor = float(stats["Profit Factor"])
    return {
        "trades": int(stats["# Trades"]),
        "win_rate": round(float(stats["Win Rate [%]"]), 4),
        "return_pct": round(float(stats["Return [%]"]), 4),
        "equity_final": round(float(stats["Equity Final [$]"]), 2),
        "profit_factor": None if not np.isfinite(profit_factor) else round(profit_factor, 4),
    }


def run_reference_backtest_from_settings(settings: Settings | None = None) -> dict:
    settings = settings or load_settings()
    from fibengine.data.loader import load_candles

    df = load_candles(settings.data)
    records = walk_forward_selection(
        df, settings, settings.backtest.warmup_bars, settings.backtest.step
    )
    plans = build_reference_trade_plans(df, settings, records)
    return {
        "config_hash": settings.config_hash(),
        "exchange": settings.data.exchange,
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "plans": len(plans),
        **run_reference_backtest(df, plans),
    }


if __name__ == "__main__":
    print(json.dumps(run_reference_backtest_from_settings(), indent=2))
