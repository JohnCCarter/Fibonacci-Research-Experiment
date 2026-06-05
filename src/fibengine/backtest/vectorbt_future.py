"""Future-facing vectorbt scaffolding without requiring vectorbt today."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from fibengine.backtest.reference import ReferenceTradePlan


@dataclass(frozen=True)
class VectorbtSignalFrame:
    close: pd.Series
    entries: pd.Series
    exits: pd.Series
    short_entries: pd.Series
    short_exits: pd.Series
    sl_stop: pd.Series
    tp_stop: pd.Series

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "close": self.close,
                "entries": self.entries,
                "exits": self.exits,
                "short_entries": self.short_entries,
                "short_exits": self.short_exits,
                "sl_stop": self.sl_stop,
                "tp_stop": self.tp_stop,
            }
        )

    def to_portfolio_kwargs(self) -> dict[str, pd.Series]:
        return {
            "close": self.close,
            "entries": self.entries,
            "exits": self.exits,
            "short_entries": self.short_entries,
            "short_exits": self.short_exits,
            "sl_stop": self.sl_stop,
            "tp_stop": self.tp_stop,
        }


def build_vectorbt_signal_frame(
    df: pd.DataFrame, trade_plans: list[ReferenceTradePlan]
) -> VectorbtSignalFrame:
    """Prepare the arrays vectorbt.Portfolio.from_signals would need later."""
    index = df.index
    entries = pd.Series(False, index=index)
    exits = pd.Series(False, index=index)
    short_entries = pd.Series(False, index=index)
    short_exits = pd.Series(False, index=index)
    sl_stop = pd.Series(np.nan, index=index, dtype=float)
    tp_stop = pd.Series(np.nan, index=index, dtype=float)
    close = df["close"].astype(float).copy()

    for plan in trade_plans:
        risk = abs(plan.entry - plan.stop)
        reward = abs(plan.target - plan.entry)
        if plan.entry <= 0 or risk <= 0 or reward <= 0:
            continue

        if plan.direction == "up":
            entries.iloc[plan.entry_bar] = True
        else:
            short_entries.iloc[plan.entry_bar] = True

        sl_stop.iloc[plan.entry_bar] = risk / plan.entry
        tp_stop.iloc[plan.entry_bar] = reward / plan.entry

    return VectorbtSignalFrame(
        close=close,
        entries=entries,
        exits=exits,
        short_entries=short_entries,
        short_exits=short_exits,
        sl_stop=sl_stop,
        tp_stop=tp_stop,
    )
