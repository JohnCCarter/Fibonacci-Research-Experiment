"""Interactive Fibonacci labeling workspace.

Run:
    uv run python -m fibengine.labeling.tool
    uv run python -m fibengine.labeling.tool --symbols BTC/USDT,ETH/USDT --timeframes 1h,1w

Controls:
- Click sets the active point. It snaps to the nearest bar high/low.
- h / l: next click sets high / low
- u/backspace: undo latest high/low edit
- r: clear current picks
- s: save or overwrite label for the active symbol/timeframe
- d: delete saved label for the active symbol/timeframe
- left/right: previous/next symbol
- down/up: previous/next timeframe
- q: quit
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd

from fibengine.config import DataConfig, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.fib import fib_from_prices
from fibengine.labeling.store import (
    Point,
    SwingLabel,
    delete_label,
    find_label,
    save_label,
)

DEFAULT_FIB_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]


def _csv_values(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    return [item.strip() for item in value.split(",") if item.strip()]


def _nearest_bar(df: pd.DataFrame, x: float) -> int:
    return int(min(max(round(x), 0), len(df) - 1))


def _nearest_timestamp_bar(df: pd.DataFrame, timestamp: str) -> int:
    target = pd.to_datetime(timestamp, utc=True)
    return int(df.index.get_indexer([target], method="nearest")[0])


def _cycle(values: list[str], current: str, delta: int) -> str:
    idx = values.index(current)
    return values[(idx + delta) % len(values)]


def _fib_prices_from_picks(
    picks: dict[str, tuple[int, float]],
    levels: list[float],
) -> dict[float, float]:
    if "high" not in picks or "low" not in picks:
        return {}
    high_idx, high_price = picks["high"]
    low_idx, low_price = picks["low"]
    if low_idx <= high_idx:
        return fib_from_prices(low_price, high_price, levels)
    return fib_from_prices(high_price, low_price, levels)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Fibonacci label workspace.")
    parser.add_argument("--exchange", help="CCXT exchange id, e.g. binance")
    parser.add_argument("--symbol", help="Initial market symbol, e.g. BTC/USDT")
    parser.add_argument("--timeframe", help="Initial candle timeframe, e.g. 1h or 1w")
    parser.add_argument("--limit", type=int, help="Number of candles to load/fetch")
    parser.add_argument(
        "--symbols",
        help="Comma-separated symbols to cycle, e.g. BTC/USDT,ETH/USDT,SOL/USDT",
    )
    parser.add_argument(
        "--timeframes",
        help="Comma-separated timeframes to cycle, e.g. 15m,1h,4h,1w",
    )
    return parser.parse_args()


@dataclass
class LabelWorkspace:
    settings: Settings
    symbols: list[str]
    timeframes: list[str]
    active_kind: str = "high"
    picks: dict[str, tuple[int, float]] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.df = load_candles(self.settings.data)

    @property
    def data(self) -> DataConfig:
        return self.settings.data

    def set_market(self, symbol: str | None = None, timeframe: str | None = None) -> None:
        self.settings.data = self.settings.data.model_copy(
            update={
                key: value
                for key, value in {"symbol": symbol, "timeframe": timeframe}.items()
                if value is not None
            }
        )
        self.df = load_candles(self.settings.data)
        self.picks.clear()
        self.history.clear()
        self.active_kind = "high"
        self.load_existing_label()

    def load_existing_label(self) -> None:
        existing = find_label(self.data.exchange, self.data.symbol, self.data.timeframe)
        if existing is None:
            return
        self.picks["high"] = (
            _nearest_timestamp_bar(self.df, existing.high.timestamp),
            existing.high.price,
        )
        self.picks["low"] = (
            _nearest_timestamp_bar(self.df, existing.low.timestamp),
            existing.low.price,
        )
        print("Loaded existing label. Edit high/low and press 's' to overwrite.")

    def cycle_symbol(self, delta: int) -> None:
        self.set_market(symbol=_cycle(self.symbols, self.data.symbol, delta))

    def cycle_timeframe(self, delta: int) -> None:
        self.set_market(timeframe=_cycle(self.timeframes, self.data.timeframe, delta))

    def set_pick(self, kind: str, idx: int) -> None:
        price = float(self.df["high"].iloc[idx] if kind == "high" else self.df["low"].iloc[idx])
        self.picks[kind] = (idx, price)
        self.history.append(kind)
        print(f"{kind.upper()} @ bar {idx}, {self.df.index[idx].isoformat()}, price {price}")
        self.active_kind = "low" if kind == "high" else "high"

    def undo(self) -> None:
        if not self.history:
            return
        removed = self.history.pop()
        self.picks.pop(removed, None)
        self.active_kind = removed
        print(f"Undid {removed.upper()}.")

    def reset(self) -> None:
        self.picks.clear()
        self.history.clear()
        self.active_kind = "high"
        print("Reset current picks.")

    def delete_current_label(self) -> None:
        label = SwingLabel(
            exchange=self.data.exchange,
            symbol=self.data.symbol,
            timeframe=self.data.timeframe,
            high=Point("", 0.0),
            low=Point("", 0.0),
        )
        deleted = delete_label(label)
        print("Deleted saved label." if deleted else "No saved label to delete.")

    def save_current_label(self) -> None:
        if "high" not in self.picks or "low" not in self.picks:
            print("Choose both high and low before saving.")
            return
        hi_idx, hi_price = self.picks["high"]
        lo_idx, lo_price = self.picks["low"]
        label = SwingLabel(
            exchange=self.data.exchange,
            symbol=self.data.symbol,
            timeframe=self.data.timeframe,
            high=Point(self.df.index[hi_idx].isoformat(), hi_price),
            low=Point(self.df.index[lo_idx].isoformat(), lo_price),
        )
        path = save_label(label)
        print(f"Saved/overwrote label -> {path}")


def _apply_cli_overrides(settings: Settings, args: argparse.Namespace) -> Settings:
    settings.data = settings.data.model_copy(
        update={
            key: value
            for key, value in {
                "exchange": args.exchange,
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "limit": args.limit,
            }.items()
            if value is not None
        }
    )
    return settings


def run_label_tool(args: argparse.Namespace | None = None):
    settings = _apply_cli_overrides(
        load_settings(),
        args or argparse.Namespace(
            exchange=None,
            symbol=None,
            timeframe=None,
            limit=None,
            symbols=None,
            timeframes=None,
        ),
    )
    args = args or argparse.Namespace(symbols=None, timeframes=None)
    symbols = _csv_values(args.symbols, [settings.data.symbol])
    timeframes = _csv_values(args.timeframes, [settings.data.timeframe])
    if settings.data.symbol not in symbols:
        symbols.insert(0, settings.data.symbol)
    if settings.data.timeframe not in timeframes:
        timeframes.insert(0, settings.data.timeframe)

    workspace = LabelWorkspace(settings, symbols, timeframes)
    workspace.load_existing_label()

    fig, ax = plt.subplots(figsize=(15, 8))

    def update_title():
        ax.set_title(
            f"{workspace.data.symbol} {workspace.data.timeframe} "
            f"| active={workspace.active_kind.upper()} "
            "| h/l set, arrows market/timeframe, s save, d delete, q quit"
        )

    def redraw():
        ax.clear()
        df = workspace.df
        x = range(len(df))
        ax.plot(x, df["close"].to_numpy(), color="black", lw=0.9, label="close")
        ax.fill_between(
            x,
            df["low"].to_numpy(),
            df["high"].to_numpy(),
            color="gray",
            alpha=0.16,
            label="high-low range",
        )

        for kind, (idx, price) in workspace.picks.items():
            color = "red" if kind == "high" else "green"
            marker = "^" if kind == "high" else "v"
            ax.scatter([idx], [price], color=color, marker=marker, s=100, zorder=5)
            ax.text(idx, price, f" {kind}", color=color, fontsize=9)

        for level, price in _fib_prices_from_picks(
            workspace.picks, workspace.settings.fib.levels or DEFAULT_FIB_LEVELS
        ).items():
            ax.axhline(price, color="tab:blue", ls="--", lw=0.8, alpha=0.65)
            ax.text(len(df) - 1, price, f" {level}", color="tab:blue", fontsize=8)

        step = max(1, len(df) // 10)
        ticks = list(range(0, len(df), step))
        ax.set_xticks(ticks)
        ax.set_xticklabels(
            [df.index[i].strftime("%Y-%m-%d") for i in ticks],
            rotation=35,
            ha="right",
        )
        ax.grid(True, alpha=0.22)
        ax.legend(loc="best", fontsize=8)
        update_title()
        fig.tight_layout()
        fig.canvas.draw_idle()

    def on_click(event):
        if event.inaxes != ax or event.xdata is None:
            return
        workspace.set_pick(workspace.active_kind, _nearest_bar(workspace.df, event.xdata))
        redraw()

    def on_key(event):
        if event.key == "r":
            workspace.reset()
        elif event.key == "h":
            workspace.active_kind = "high"
            print("Next click sets HIGH.")
        elif event.key == "l":
            workspace.active_kind = "low"
            print("Next click sets LOW.")
        elif event.key in {"u", "backspace"}:
            workspace.undo()
        elif event.key == "d":
            workspace.delete_current_label()
        elif event.key == "s":
            workspace.save_current_label()
        elif event.key == "right":
            workspace.cycle_symbol(1)
        elif event.key == "left":
            workspace.cycle_symbol(-1)
        elif event.key == "up":
            workspace.cycle_timeframe(1)
        elif event.key == "down":
            workspace.cycle_timeframe(-1)
        elif event.key == "q":
            plt.close(fig)
            return
        redraw()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    redraw()
    plt.show()


if __name__ == "__main__":
    run_label_tool(_parse_args())
