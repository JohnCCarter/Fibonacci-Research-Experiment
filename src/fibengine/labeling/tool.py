"""Interactive Fibonacci labeling workspace.

Run:
    uv run python -m fibengine.labeling.tool
    uv run python -m fibengine.labeling.tool --symbols BTC/USDT,ETH/USDT --timeframes 1h,1w

Controls:
- Click sets the active point. It snaps to the nearest bar high/low.
- Drag an existing high/low marker to reposition it (snaps to candle high/low).
- Shift + drag a marker moves the whole leg (high+low) together.
- h / l: next click sets high / low
- u/backspace: undo latest high/low edit
- r: clear current picks
- f: toggle fib levels
- g: toggle high-low range shading
- s: save or overwrite label for the active symbol/timeframe
- d: delete saved label for the active symbol/timeframe
- left/right: previous/next symbol
- down/up: previous/next timeframe
- n: jump to next unlabeled symbol/timeframe
- z: reset chart view
- q: quit

Tips:
- Use Matplotlib toolbar for pan/zoom/home to avoid interaction conflicts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from fibengine.core.config import DataConfig, Settings, load_settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.labeling.store import (
    Point,
    SwingLabel,
    delete_label,
    find_label,
    save_label,
)

DEFAULT_FIB_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
DEFAULT_LABEL_TIMEFRAMES = ["15m", "30m", "1h", "4h", "daily", "weekly", "monthly"]
TIMEFRAME_ALIASES = {
    "daily": "1d",
    "day": "1d",
    "weekly": "1w",
    "week": "1w",
    "monthly": "1M",
    "month": "1M",
}
CONFLICTING_MATPLOTLIB_KEYMAPS = [
    "keymap.back",
    "keymap.forward",
    "keymap.fullscreen",
    "keymap.grid",
    "keymap.grid_minor",
    "keymap.home",
    "keymap.quit",
    "keymap.save",
    "keymap.xscale",
    "keymap.yscale",
]


def _disable_matplotlib_keymap_conflicts() -> None:
    """Reserve labeling shortcuts for the tool instead of Matplotlib's toolbar."""
    for key in CONFLICTING_MATPLOTLIB_KEYMAPS:
        plt.rcParams[key] = []


def _csv_values(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    values: list[str] = []
    for item in value.split(","):
        token = item.strip()
        if not token:
            continue
        values.append(TIMEFRAME_ALIASES.get(token.lower(), token))
    return values


def _default_timeframes(primary: str) -> list[str]:
    normalized_primary = TIMEFRAME_ALIASES.get(primary.lower(), primary)
    values = [TIMEFRAME_ALIASES.get(item.lower(), item) for item in DEFAULT_LABEL_TIMEFRAMES]
    if normalized_primary not in values:
        values.insert(0, normalized_primary)
    return values


def _nearest_bar(df: pd.DataFrame, x: float) -> int:
    return int(min(max(round(x), 0), len(df) - 1))


def _nearest_timestamp_bar(df: pd.DataFrame, timestamp: str) -> int:
    target = pd.to_datetime(timestamp, utc=True)
    return int(df.index.get_indexer([target], method="nearest")[0])


def _edge_margin(settings: Settings) -> int:
    return max(settings.pivots.lookback, settings.pivots.fractal_n, 1)


def _label_warnings(
    df: pd.DataFrame,
    high_idx: int,
    low_idx: int,
    settings: Settings,
) -> list[str]:
    warnings = []
    if high_idx == low_idx:
        warnings.append("High and low are on the same candle. Pick a leg with distinct endpoints.")

    margin = _edge_margin(settings)
    last_idx = len(df) - 1
    for kind, idx in {"high": high_idx, "low": low_idx}.items():
        if idx < margin:
            warnings.append(
                f"{kind} is too close to the left edge ({idx} < {margin}); "
                "load more history or pick a later swing."
            )
        elif last_idx - idx < margin:
            warnings.append(
                f"{kind} is too close to the right edge ({last_idx - idx} < {margin}); "
                "use only if you want a provisional edge case."
            )
    return warnings


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
    show_fib: bool = True
    show_range: bool = False

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

    def move_pick(self, kind: str, idx: int) -> None:
        """Move an existing pick without changing active mode/history."""
        price = float(self.df["high"].iloc[idx] if kind == "high" else self.df["low"].iloc[idx])
        self.picks[kind] = (idx, price)

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
        warnings = _label_warnings(self.df, hi_idx, lo_idx, self.settings)
        if warnings:
            print("Label not saved:")
            for warning in warnings:
                print(f"- {warning}")
            return
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
    _disable_matplotlib_keymap_conflicts()
    settings = _apply_cli_overrides(
        load_settings(),
        args
        or argparse.Namespace(
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
    timeframes = _csv_values(args.timeframes, _default_timeframes(settings.data.timeframe))
    if settings.data.symbol not in symbols:
        symbols.insert(0, settings.data.symbol)
    if settings.data.timeframe not in timeframes:
        timeframes.insert(0, settings.data.timeframe)

    queue = [(sym, tf) for sym in symbols for tf in timeframes]

    workspace = LabelWorkspace(settings, symbols, timeframes)
    workspace.load_existing_label()

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    drag_kind: str | None = None
    view_limits: tuple[tuple[float, float], tuple[float, float]] | None = None
    click_moved = False
    is_dirty = False
    leg_drag_start_x: float | None = None
    leg_drag_base: dict[str, int] | None = None
    leg_drag_active = False

    def queue_index() -> int:
        try:
            return queue.index((workspace.data.symbol, workspace.data.timeframe))
        except ValueError:
            return 0

    def queue_labeled_count() -> int:
        return sum(
            1 for sym, tf in queue if find_label(workspace.data.exchange, sym, tf) is not None
        )

    def goto_market(symbol: str, timeframe: str) -> None:
        nonlocal view_limits
        workspace.set_market(symbol=symbol, timeframe=timeframe)
        view_limits = None
        mark_dirty(False)

    def goto_next_unlabeled() -> None:
        start = queue_index()
        total = len(queue)
        for offset in range(1, total + 1):
            idx = (start + offset) % total
            symbol, timeframe = queue[idx]
            if find_label(workspace.data.exchange, symbol, timeframe) is None:
                goto_market(symbol, timeframe)
                print(f"Jumped to next unlabeled: {symbol} {timeframe}")
                return
        print("All symbol/timeframe combinations in the queue are labeled.")

    def mark_dirty(flag: bool = True) -> None:
        nonlocal is_dirty
        is_dirty = flag

    def update_title():
        ax.set_title(
            f"{workspace.data.symbol} {workspace.data.timeframe} "
            f"| active={workspace.active_kind.upper()} "
            f"| fib={'on' if workspace.show_fib else 'off'} "
            f"range={'on' if workspace.show_range else 'off'} "
            f"| {queue_labeled_count()}/{len(queue)} labeled "
            f"| {queue_index() + 1}/{len(queue)} "
            f"| {'unsaved' if is_dirty else 'saved'} "
            "| h/l fib g range n next z reset arrows market/tf s save d delete q quit",
            color="#d6d9e0",
        )

    def redraw():
        ax.clear()
        ax.set_facecolor("#0f1117")
        df = workspace.df
        x = range(len(df))
        opens = df["open"].to_numpy()
        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        closes = df["close"].to_numpy()

        up_color = "#26a69a"
        down_color = "#ef5350"
        wick_color = "#c7cedb"
        candle_width = 0.62

        # Candlesticks for a more standard trading-chart look.
        for i, (o, h, low, c) in enumerate(zip(opens, highs, lows, closes, strict=False)):
            color = up_color if c >= o else down_color
            ax.vlines(i, low, h, color=wick_color, linewidth=0.8, alpha=0.9, zorder=2)
            body_bottom = min(o, c)
            body_height = abs(c - o)
            if body_height <= 1e-12:
                ax.hlines(
                    c,
                    i - candle_width / 2,
                    i + candle_width / 2,
                    color=color,
                    linewidth=1.2,
                    zorder=3,
                )
            else:
                ax.add_patch(
                    Rectangle(
                        (i - candle_width / 2, body_bottom),
                        candle_width,
                        body_height,
                        facecolor=color,
                        edgecolor=color,
                        linewidth=0.8,
                        zorder=3,
                    )
                )

        if workspace.show_range:
            ax.fill_between(
                x,
                lows,
                highs,
                color="#7f8799",
                alpha=0.08,
                label="high-low range",
                zorder=1,
            )

        for kind, (idx, price) in workspace.picks.items():
            color = "#ff6b6b" if kind == "high" else "#6be675"
            marker = "^" if kind == "high" else "v"
            ax.scatter([idx], [price], color=color, marker=marker, s=100, zorder=5)
            ax.text(idx, price, f" {kind}", color=color, fontsize=9)

        if workspace.show_fib:
            for level, price in _fib_prices_from_picks(
                workspace.picks, workspace.settings.fib.levels or DEFAULT_FIB_LEVELS
            ).items():
                ax.axhline(price, color="#6ea8ff", ls="--", lw=0.8, alpha=0.7)
                ax.text(len(df) - 1, price, f" {level}", color="#86b8ff", fontsize=8)

        step = max(1, len(df) // 10)
        ticks = list(range(0, len(df), step))
        ax.set_xticks(ticks)
        ax.set_xticklabels(
            [df.index[i].strftime("%Y-%m-%d") for i in ticks],
            rotation=35,
            ha="right",
            color="#c6ccda",
        )
        ax.tick_params(axis="y", colors="#c6ccda")
        ax.grid(True, color="#2a3040", alpha=0.35, linewidth=0.7)
        ax.yaxis.set_ticks_position("right")
        ax.yaxis.set_label_position("right")
        if view_limits is not None:
            ax.set_xlim(*view_limits[0])
            ax.set_ylim(*view_limits[1])

        update_title()
        fig.tight_layout()
        fig.canvas.draw_idle()

    def on_press(event):
        nonlocal drag_kind, click_moved, leg_drag_start_x, leg_drag_base, leg_drag_active
        if event.inaxes != ax or event.x is None or event.y is None:
            return
        click_moved = False
        if event.button != 1:
            return
        if not workspace.picks:
            return
        closest_kind = None
        closest_dist = None
        for kind, (idx, price) in workspace.picks.items():
            sx, sy = ax.transData.transform((idx, price))
            dist = ((sx - event.x) ** 2 + (sy - event.y) ** 2) ** 0.5
            if closest_dist is None or dist < closest_dist:
                closest_dist = dist
                closest_kind = kind
        if closest_kind is not None and closest_dist is not None and closest_dist <= 18:
            if event.key == "shift" and "high" in workspace.picks and "low" in workspace.picks:
                leg_drag_active = True
                leg_drag_start_x = event.xdata
                leg_drag_base = {
                    "high": workspace.picks["high"][0],
                    "low": workspace.picks["low"][0],
                }
            else:
                drag_kind = closest_kind

    def on_motion(event):
        nonlocal click_moved
        if event.inaxes != ax or event.xdata is None or event.ydata is None:
            return

        if leg_drag_active and leg_drag_start_x is not None and leg_drag_base is not None:
            delta = int(round(event.xdata - leg_drag_start_x))
            n = len(workspace.df) - 1
            for kind in ("high", "low"):
                base_idx = leg_drag_base[kind]
                workspace.move_pick(kind, min(max(base_idx + delta, 0), n))
            mark_dirty(True)
            click_moved = True
            redraw()
            return

        if drag_kind is None:
            return
        idx = _nearest_bar(workspace.df, event.xdata)
        workspace.move_pick(drag_kind, idx)
        mark_dirty(True)
        click_moved = True
        redraw()

    def on_release(event):
        nonlocal drag_kind, click_moved, leg_drag_start_x, leg_drag_base, leg_drag_active
        if (
            not click_moved
            and drag_kind is None
            and event.inaxes == ax
            and event.xdata is not None
            and event.button == 1
        ):
            workspace.set_pick(workspace.active_kind, _nearest_bar(workspace.df, event.xdata))
            mark_dirty(True)
            redraw()
        drag_kind = None
        leg_drag_active = False
        leg_drag_start_x = None
        leg_drag_base = None
        click_moved = False

    def on_key(event):
        nonlocal view_limits
        if event.key == "r":
            workspace.reset()
            mark_dirty(True)
        elif event.key == "h":
            workspace.active_kind = "high"
            print("Next click sets HIGH.")
        elif event.key == "l":
            workspace.active_kind = "low"
            print("Next click sets LOW.")
        elif event.key in {"u", "backspace"}:
            workspace.undo()
            mark_dirty(True)
        elif event.key == "d":
            workspace.delete_current_label()
            mark_dirty(False)
        elif event.key == "s":
            workspace.save_current_label()
            mark_dirty(False)
        elif event.key == "f":
            workspace.show_fib = not workspace.show_fib
            print(f"Fib levels {'ON' if workspace.show_fib else 'OFF'}.")
        elif event.key == "g":
            workspace.show_range = not workspace.show_range
            print(f"High-low range {'ON' if workspace.show_range else 'OFF'}.")
        elif event.key == "right":
            goto_market(_cycle(symbols, workspace.data.symbol, 1), workspace.data.timeframe)
        elif event.key == "left":
            goto_market(_cycle(symbols, workspace.data.symbol, -1), workspace.data.timeframe)
        elif event.key == "up":
            goto_market(workspace.data.symbol, _cycle(timeframes, workspace.data.timeframe, 1))
        elif event.key == "down":
            goto_market(workspace.data.symbol, _cycle(timeframes, workspace.data.timeframe, -1))
        elif event.key == "n":
            goto_next_unlabeled()
        elif event.key == "z":
            view_limits = None
        elif event.key == "q":
            plt.close(fig)
            return
        redraw()

    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)
    fig.canvas.mpl_connect("key_press_event", on_key)
    redraw()
    plt.show()


if __name__ == "__main__":
    run_label_tool(_parse_args())
