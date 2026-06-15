"""Interactive Fibonacci labeling workspace.

Run:
    uv run python -m fibengine.labeling.tool
    uv run python -m fibengine.labeling.tool --symbols BTC/USD,ETH/USD --timeframes 1h,1w
    # single-fib declutter mode (open one saved human fib, HTF overlays hidden):
    uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 4h \
        --edit-fib-id fib_BTC-USD_4h_20171228T200000 --config config/settings.expansion.yaml

Controls:
- Click sets the active point. It snaps to the nearest bar high/low.
- Drag an existing high/low marker to reposition it (snaps to candle high/low).
- Shift + drag a marker moves the whole leg (high+low) together.
- h / l: next click sets high / low
- u/backspace: undo latest high/low edit
- r: clear current picks
- f: toggle fib levels (includes read-only HTF human-fib overlays on lower TFs)
- g: toggle high-low range shading
- w: write active fib as a human ground-truth annotation (data/labels/human_fib/...)
- s: save label (all legs) for the active symbol/timeframe
- p or a: push current high/low as a new leg (keeps prior legs; clears picks)
- j / k: previous / next leg when multiple legs exist
- s: saves all legs; if picks differ from active leg, auto-adds a new leg
- d: delete saved label for the active symbol/timeframe
- left/right or [ ] or , . : previous/next symbol
- down/up or ; ' : previous/next timeframe
- n: jump to next unlabeled symbol/timeframe
- z: reset chart view
- q: quit

Tips:
- Matplotlib toolbar: pan/zoom; view persists across redraw until z (reset) or market change.

Hover: crosshair price (mouse Y) + bar OHLC readout. See docs/labeling/LABELING_TOOL.md
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd

from fibengine.core.config import DataConfig, Settings, load_settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.labeling.hover import HoverReadout
from fibengine.labeling.htf_fib_overlay import draw_htf_overlays, load_htf_overlays
from fibengine.labeling.human_fib import (
    HumanFibAnnotation,
    anchors_from_picks,
    find_annotation,
    make_annotation,
    save_annotation,
)
from fibengine.labeling.same_candle_mtf_resolution import (
    attempt_same_candle_mtf_resolution,
    mtf_resolution_enabled,
    resolution_timeframe_for,
)
from fibengine.labeling.store import (
    LegLabel,
    Point,
    SwingLabel,
    delete_label,
    find_label,
    save_label,
    set_labels_dir,
)
from fibengine.research.human_review_candles import draw_review_candles

DEFAULT_FIB_LEVELS = [0.0, 0.382, 0.5, 0.618, 0.786, 1.0]
LEG_FIB_COLORS = ["#6ea8ff", "#ffb86b", "#bd93f9", "#8be9fd", "#ff79c6"]
LEG_MARKER_ALPHA_INACTIVE = 0.45
DEFAULT_LABEL_TIMEFRAMES = ["15m", "30m", "1h", "4h", "daily", "weekly", "monthly"]
DEFAULT_CYCLE_SYMBOLS = ["BTC/USD", "ETH/USD", "SOL/USD"]
KEY_PREV_SYMBOL = frozenset({"left", "[", ","})
KEY_NEXT_SYMBOL = frozenset({"right", "]", "."})
KEY_PREV_TIMEFRAME = frozenset({"down", ";"})
KEY_NEXT_TIMEFRAME = frozenset({"up", "'"})
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
    "keymap.pan",
]


def _normalize_key(key: str | None) -> str:
    if not key:
        return ""
    aliases = {
        "leftarrow": "left",
        "rightarrow": "right",
        "arrowleft": "left",
        "arrowright": "right",
        "uparrow": "up",
        "downarrow": "down",
    }
    return aliases.get(key.lower().strip(), key.lower().strip())


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
        defer_same_bar = (
            mtf_resolution_enabled(settings)
            and resolution_timeframe_for(settings.data.timeframe) is not None
        )
        if not defer_same_bar:
            warnings.append(
                "High and low are on the same candle. Pick a leg with distinct endpoints."
            )

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
    scale_mode: str = "log",
) -> dict[float, float]:
    if "high" not in picks or "low" not in picks:
        return {}
    high_idx, high_price = picks["high"]
    low_idx, low_price = picks["low"]
    if low_idx <= high_idx:
        return fib_from_prices(low_price, high_price, levels, scale_mode=scale_mode)
    return fib_from_prices(high_price, low_price, levels, scale_mode=scale_mode)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Fibonacci label workspace.")
    parser.add_argument("--exchange", help="CCXT exchange id, e.g. bitfinex")
    parser.add_argument("--symbol", help="Initial market symbol, e.g. BTC/USD")
    parser.add_argument("--timeframe", help="Initial candle timeframe, e.g. 1h or 1w")
    parser.add_argument("--limit", type=int, help="Number of candles to load/fetch")
    parser.add_argument(
        "--symbols",
        help="Comma-separated symbols to cycle, e.g. BTC/USD,ETH/USD,SOL/USD",
    )
    parser.add_argument(
        "--timeframes",
        help="Comma-separated timeframes to cycle, e.g. 15m,1h,4h,1w",
    )
    parser.add_argument(
        "--labels-dir",
        default="",
        help="Label JSON root (default data/labels). Use data/labels/tmp for a clean sandbox.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="",
        help="Settings file (default: config/settings.yaml).",
    )
    parser.add_argument(
        "--window-start",
        default=None,
        help=(
            "ISO date to restrict displayed candles from (e.g. 2019-01-01). "
            "Windowing is display-only; save paths are unchanged. "
            "Mutually exclusive with --label-year."
        ),
    )
    parser.add_argument(
        "--window-end",
        default=None,
        help=(
            "ISO date to restrict displayed candles to (e.g. 2019-12-31). "
            "Mutually exclusive with --label-year."
        ),
    )
    parser.add_argument(
        "--label-year",
        type=int,
        default=None,
        help=(
            "Display only candles for YEAR (±--buffer-months context on each side). "
            "Convenience wrapper for --window-start/--window-end. "
            "Buffer zone is context only — label swings whose anchors lie within the year. "
            "Mutually exclusive with --window-start/--window-end."
        ),
    )
    parser.add_argument(
        "--buffer-months",
        type=int,
        default=3,
        help="Context months prepended/appended when using --label-year (default: 3).",
    )
    parser.add_argument(
        "--edit-fib-id",
        dest="edit_fib_id",
        default=None,
        help=(
            "Single-fib declutter mode: open exactly one saved human source fib by id "
            "(e.g. fib_BTC-USD_4h_20171228T200000). HTF overlays are hidden, the window "
            "auto-fits the fib's A→B span, and its anchors are preloaded for assessment. "
            "Read-only on load — nothing is saved unless you press 'w'."
        ),
    )
    return parser.parse_args()


def _window_from_anchors(
    ann: HumanFibAnnotation, min_pad_days: int = 2
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Display window bracketing a fib's A→B span with symmetric context padding.

    Pad each side by the larger of the leg span or ``min_pad_days`` so a one-bar leg
    still gets readable context. Pure helper — no I/O.
    """
    ta = pd.to_datetime(ann.anchor_a.time, utc=True)
    tb = pd.to_datetime(ann.anchor_b.time, utc=True)
    lo, hi = min(ta, tb), max(ta, tb)
    pad = max(hi - lo, pd.Timedelta(days=min_pad_days))
    return lo - pad, hi + pad


def _preload_fib_picks(workspace: LabelWorkspace, ann: HumanFibAnnotation) -> None:
    """Load a fib's exact anchors as the active high/low picks (in-memory only).

    Maps anchors to high/low by price so the existing redraw shows the selected fib's
    markers and its level ladder. Mutates no label file.
    """
    points = [
        (ann.anchor_a.time, float(ann.anchor_a.price)),
        (ann.anchor_b.time, float(ann.anchor_b.price)),
    ]
    hi = max(points, key=lambda p: p[1])
    lo = min(points, key=lambda p: p[1])
    workspace.picks = {
        "high": (_nearest_timestamp_bar(workspace.df, hi[0]), hi[1]),
        "low": (_nearest_timestamp_bar(workspace.df, lo[0]), lo[1]),
    }
    workspace.active_kind = "high"


def _resolve_window(
    args: argparse.Namespace,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    """Return (window_start, window_end) from CLI args.

    --label-year and --window-start/--window-end are mutually exclusive.
    Returns (None, None) when no window args are given — no filtering applied.
    """
    has_explicit = bool(getattr(args, "window_start", None) or getattr(args, "window_end", None))
    has_year = getattr(args, "label_year", None) is not None
    if has_explicit and has_year:
        raise SystemExit(
            "Error: --label-year and --window-start/--window-end are mutually exclusive. "
            "Use one or the other."
        )
    if has_year:
        buf: int = getattr(args, "buffer_months", 3)
        year: int = args.label_year
        start = pd.Timestamp(f"{year}-01-01", tz="UTC") - pd.DateOffset(months=buf)
        end = pd.Timestamp(f"{year + 1}-01-01", tz="UTC") + pd.DateOffset(months=buf)
        return pd.Timestamp(start), pd.Timestamp(end)
    ws = (
        pd.to_datetime(getattr(args, "window_start", None), utc=True)
        if getattr(args, "window_start", None)
        else None
    )
    we = (
        pd.to_datetime(getattr(args, "window_end", None), utc=True)
        if getattr(args, "window_end", None)
        else None
    )
    return ws, we


@dataclass
class LabelWorkspace:
    settings: Settings
    symbols: list[str]
    timeframes: list[str]
    active_kind: str = "high"
    picks: dict[str, tuple[int, float]] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    legs: list[LegLabel] = field(default_factory=list)
    active_leg_index: int = 0
    show_fib: bool = True
    show_range: bool = False
    window_start: pd.Timestamp | None = None
    window_end: pd.Timestamp | None = None
    single_fib_mode: bool = False
    _htf_overlays: list | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.df = self._load_chart_candles()

    @property
    def data(self) -> DataConfig:
        return self.settings.data

    def _load_chart_candles(self) -> pd.DataFrame:
        """Load candles from local cache only (no exchange fetch on TF switch)."""
        try:
            df = load_candles(self.settings.data, fetch_if_missing=False)
        except FileNotFoundError as exc:
            raise SystemExit(
                f"{exc}\n"
                "Labeling tool does not auto-fetch. Run preflight first:\n"
                "  uv run python -m fibengine.labeling.preflight "
                f"--symbol {self.data.symbol} --config <settings.yaml>"
            ) from exc
        df = self._apply_window(df)
        if df.empty and (self.window_start is not None or self.window_end is not None):
            raise SystemExit(
                f"Window filter produced an empty chart for "
                f"{self.data.symbol} {self.data.timeframe}. "
                "Check --window-start/--window-end or --label-year vs available cache range."
            )
        return df

    def _apply_window(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a date-filtered slice of df. Timestamps preserved; save semantics unchanged."""
        if self.window_start is None and self.window_end is None:
            return df
        mask = pd.Series(True, index=df.index)
        if self.window_start is not None:
            mask &= df.index >= self.window_start
        if self.window_end is not None:
            mask &= df.index <= self.window_end
        return df[mask]

    def _in_display_window(self, ts_str: str) -> bool:
        ts = pd.to_datetime(ts_str, utc=True)
        if self.window_start is not None and ts < self.window_start:
            return False
        if self.window_end is not None and ts > self.window_end:
            return False
        return True

    def get_htf_overlays(self) -> list:
        """Return HTF fib overlays; loaded once per market, cached until market switch.

        In single-fib declutter mode the HTF overlays are suppressed (this is the main
        source of chart clutter on lower timeframes), so only the selected fib shows.
        """
        if self.single_fib_mode:
            return []
        if self._htf_overlays is None:
            self._htf_overlays = load_htf_overlays(
                self.data.exchange,
                self.data.symbol,
                self.data.timeframe,
            )
        return self._htf_overlays

    def set_market(self, symbol: str | None = None, timeframe: str | None = None) -> None:
        next_data = self.settings.data.model_copy(
            update={
                key: value
                for key, value in {"symbol": symbol, "timeframe": timeframe}.items()
                if value is not None
            }
        )
        try:
            df = load_candles(next_data, fetch_if_missing=False)
        except FileNotFoundError as exc:
            print(
                f"Cannot switch to {next_data.symbol} {next_data.timeframe}: {exc}\n"
                "Prefetch cache (tool does not auto-fetch). Example:\n"
                "  uv run python -m fibengine.labeling.preflight "
                f"--symbol {next_data.symbol} --timeframes {next_data.timeframe}"
            )
            return
        display_df = self._apply_window(df)
        if display_df.empty and (self.window_start is not None or self.window_end is not None):
            print(
                f"Window filter returned empty chart for {next_data.symbol} {next_data.timeframe}. "
                "Cache may not cover this window range."
            )
            return
        self.settings.data = next_data
        self.df = display_df
        self._htf_overlays = None
        self.picks.clear()
        self.history.clear()
        self.legs.clear()
        self.active_leg_index = 0
        self.active_kind = "high"
        self.load_existing_label()

    def _picks_from_leg(self, leg: LegLabel) -> dict[str, tuple[int, float]]:
        return {
            "high": (_nearest_timestamp_bar(self.df, leg.high.timestamp), leg.high.price),
            "low": (_nearest_timestamp_bar(self.df, leg.low.timestamp), leg.low.price),
        }

    def _load_picks_from_active_leg(self) -> None:
        self.picks.clear()
        self.history.clear()
        if not self.legs:
            return
        self.picks.update(self._picks_from_leg(self.legs[self.active_leg_index]))

    def load_existing_label(self) -> None:
        existing = find_label(self.data.exchange, self.data.symbol, self.data.timeframe)
        if existing is None:
            return
        all_legs = list(existing.all_legs())
        if self.window_start is not None or self.window_end is not None:
            before = len(all_legs)
            all_legs = [
                leg
                for leg in all_legs
                if self._in_display_window(leg.high.timestamp)
                and self._in_display_window(leg.low.timestamp)
            ]
            dropped = before - len(all_legs)
            if dropped:
                print(f"Skipped {dropped} saved leg(s) outside display window.")
        if not all_legs:
            return
        self.legs = all_legs
        self.active_leg_index = 0
        self._load_picks_from_active_leg()
        n = len(self.legs)
        if n > 1:
            print(f"Loaded {n} legs. Active: {self.legs[0].id}. j/k leg, a add, s save all.")
        else:
            print("Loaded existing label. Edit high/low and press 's' to save.")
        leg0 = self.legs[0]
        if leg0.same_candle_mtf_resolution:
            mtf = leg0.same_candle_mtf_resolution
            print(
                "  MTF-resolved (research): "
                f"high daily {mtf.get('high_daily_timestamp')}, "
                f"low daily {mtf.get('low_daily_timestamp')}"
            )

    def _picks_complete(self) -> bool:
        return "high" in self.picks and "low" in self.picks

    def _picks_match_active_leg(self) -> bool:
        if not self.legs or not self._picks_complete():
            return False
        ref = self._picks_from_leg(self.legs[self.active_leg_index])
        return self.picks["high"][0] == ref["high"][0] and self.picks["low"][0] == ref["low"][0]

    def _leg_from_picks(self, leg_id: str = "") -> LegLabel | None:
        if not self._picks_complete():
            return None
        hi_idx, hi_price = self.picks["high"]
        lo_idx, lo_price = self.picks["low"]
        return LegLabel(
            id=leg_id or f"leg_{len(self.legs) + 1}",
            high=Point(self.df.index[hi_idx].isoformat(), hi_price),
            low=Point(self.df.index[lo_idx].isoformat(), lo_price),
        )

    def flush_picks_to_active_leg(self) -> bool:
        leg = self._leg_from_picks(self.legs[self.active_leg_index].id if self.legs else "leg_1")
        if leg is None:
            return False
        if self.legs and self.active_leg_index < len(self.legs):
            leg.id = self.legs[self.active_leg_index].id
            leg.note = self.legs[self.active_leg_index].note
            leg.role = self.legs[self.active_leg_index].role
            leg.same_candle_mtf_resolution = self.legs[
                self.active_leg_index
            ].same_candle_mtf_resolution
            self.legs[self.active_leg_index] = leg
        elif self.legs:
            self.legs.append(leg)
            self.active_leg_index = len(self.legs) - 1
        else:
            self.legs.append(leg)
            self.active_leg_index = 0
        return True

    def _push_picks_as_new_leg(self) -> bool:
        if not self._picks_complete():
            return False
        hi_idx, lo_idx = self.picks["high"][0], self.picks["low"][0]
        warnings = _label_warnings(self.df, hi_idx, lo_idx, self.settings)
        if warnings:
            print("Leg not added:")
            for warning in warnings:
                print(f"- {warning}")
            return False
        leg = self._leg_from_picks(f"leg_{len(self.legs) + 1}")
        assert leg is not None
        self.legs.append(leg)
        self.active_leg_index = len(self.legs) - 1
        self.picks.clear()
        self.history.clear()
        self.active_kind = "high"
        print(
            f"Stored {leg.id} ({len(self.legs)} leg(s) in session). "
            "Set high/low for next fib, then 'p' or 's'."
        )
        return True

    def append_leg(self) -> None:
        if not self._picks_complete():
            print("Set both high and low before push-leg (p or a).")
            return
        self._push_picks_as_new_leg()

    def cycle_leg(self, delta: int) -> None:
        if not self.legs:
            print("No legs yet. Set high/low and press 'p' to push first leg.")
            return
        if self._picks_complete():
            self.flush_picks_to_active_leg()
        self.active_leg_index = (self.active_leg_index + delta) % len(self.legs)
        self._load_picks_from_active_leg()
        leg = self.legs[self.active_leg_index]
        print(f"Active leg {self.active_leg_index + 1}/{len(self.legs)}: {leg.id}")

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
        self.legs.clear()
        self.active_leg_index = 0
        self.active_kind = "high"
        print("Reset current picks and all legs in session.")

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
        if self._picks_complete():
            hi_idx, lo_idx = self.picks["high"][0], self.picks["low"][0]
            warnings = _label_warnings(self.df, hi_idx, lo_idx, self.settings)
            if warnings:
                print("Label not saved:")
                for warning in warnings:
                    print(f"- {warning}")
                return
            if hi_idx == lo_idx:
                mtf_meta, mtf_err = attempt_same_candle_mtf_resolution(
                    self.settings, self.df, hi_idx
                )
                if mtf_err:
                    print("Label not saved:")
                    print(f"- {mtf_err}")
                    return
                self.flush_picks_to_active_leg()
                if self.legs:
                    self.legs[self.active_leg_index].same_candle_mtf_resolution = mtf_meta
                print(
                    "same_candle_mtf_resolution (research): "
                    f"high daily {mtf_meta['high_daily_timestamp']}, "
                    f"low daily {mtf_meta['low_daily_timestamp']} "
                    f"({mtf_meta['order']})"
                )
            elif self.legs and not self._picks_match_active_leg():
                if not self._push_picks_as_new_leg():
                    return
            else:
                self.flush_picks_to_active_leg()
        elif not self.legs:
            print("Choose both high and low before saving.")
            return

        legs_to_save = [leg for leg in self.legs if leg.high.price and leg.low.price]
        if not legs_to_save:
            print("No legs to save.")
            return

        primary = legs_to_save[0]
        label = SwingLabel(
            exchange=self.data.exchange,
            symbol=self.data.symbol,
            timeframe=self.data.timeframe,
            high=primary.high,
            low=primary.low,
            legs=legs_to_save if len(legs_to_save) > 1 else None,
            same_candle_mtf_resolution=primary.same_candle_mtf_resolution,
        )
        path = save_label(label)
        if len(legs_to_save) > 1:
            print(f"Saved {len(legs_to_save)} legs -> {path}")
        else:
            print(f"Saved label -> {path}")

    def save_human_fib_annotation(self) -> None:
        """Persist the active drawn fib as a human ground-truth annotation.

        The human-drawn anchors are the source of truth; this only stores them
        and the derived fib levels (no auto-fib, no behaviour classification)."""
        if not self._picks_complete():
            print("Set both high and low before writing a fib annotation (w).")
            return
        hi_idx, hi_price = self.picks["high"]
        lo_idx, lo_price = self.picks["low"]
        anchor_a, anchor_b = anchors_from_picks(self.df, hi_idx, hi_price, lo_idx, lo_price)
        annotation = make_annotation(
            symbol=self.data.symbol,
            timeframe=self.data.timeframe,
            exchange=self.data.exchange,
            anchor_a=anchor_a,
            anchor_b=anchor_b,
            scale_mode=self.settings.fib.scale_mode,
            levels_profile=self.settings.fib.levels_profile,
        )
        path = save_annotation(annotation)
        print(f"Saved human fib annotation ({annotation.direction}) -> {path}")


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
    if args and getattr(args, "labels_dir", ""):
        set_labels_dir(args.labels_dir)
        print(f"Labels dir: {args.labels_dir}")
    cli = args or argparse.Namespace(
        exchange=None,
        symbol=None,
        timeframe=None,
        limit=None,
        symbols=None,
        timeframes=None,
        config="",
        window_start=None,
        window_end=None,
        label_year=None,
        buffer_months=3,
        edit_fib_id=None,
    )
    settings = _apply_cli_overrides(load_settings(cli.config or None), cli)
    window_start, window_end = _resolve_window(cli)

    edit_fib_id = getattr(cli, "edit_fib_id", None)
    selected_fib: HumanFibAnnotation | None = None
    if edit_fib_id:
        try:
            selected_fib = find_annotation(
                edit_fib_id,
                exchange=settings.data.exchange,
                symbol=settings.data.symbol,
                timeframe=settings.data.timeframe,
            )
        except (FileNotFoundError, ValueError) as exc:
            raise SystemExit(f"--edit-fib-id: {exc}") from exc
        if window_start is None and window_end is None:
            window_start, window_end = _window_from_anchors(selected_fib)
    args = args or argparse.Namespace(symbols=None, timeframes=None)
    symbols = _csv_values(args.symbols, DEFAULT_CYCLE_SYMBOLS)
    timeframes = _csv_values(args.timeframes, _default_timeframes(settings.data.timeframe))
    if settings.data.symbol not in symbols:
        symbols.insert(0, settings.data.symbol)
    if settings.data.timeframe not in timeframes:
        timeframes.insert(0, settings.data.timeframe)

    queue = [(sym, tf) for sym in symbols for tf in timeframes]

    workspace = LabelWorkspace(
        settings,
        symbols,
        timeframes,
        window_start=window_start,
        window_end=window_end,
        single_fib_mode=selected_fib is not None,
    )
    if selected_fib is not None:
        _preload_fib_picks(workspace, selected_fib)
        print(
            f"Single-fib edit mode: {selected_fib.fib_id} ({selected_fib.direction}) "
            "— HTF overlays hidden, anchors preloaded. Nothing saved unless you press 'w'."
        )
    else:
        workspace.load_existing_label()

    if window_start is not None or window_end is not None:
        if getattr(cli, "label_year", None) is not None:
            print(
                f"Year window: {cli.label_year} ±{cli.buffer_months}m  "
                f"({window_start.strftime('%Y-%m-%d')} -> {window_end.strftime('%Y-%m-%d')})"
                "  [save paths unchanged]"
            )
        else:
            ws_str = window_start.strftime("%Y-%m-%d") if window_start else "start"
            we_str = window_end.strftime("%Y-%m-%d") if window_end else "end"
            print(f"Display window: {ws_str} -> {we_str}  [save paths unchanged]")

    print(
        f"Symbol cycle ({len(symbols)}): {', '.join(symbols)}  "
        f"| timeframe cycle: {', '.join(timeframes)}"
    )
    print("Market: [ ] or , . = symbol   ; ' or arrows = timeframe (click chart first)")
    print(
        "Multi-leg fib: set H+L, then 'p' (or 'a') to push another leg without losing the first. "
        "'s' saves all legs (auto-pushes if endpoints differ from active leg)."
    )

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    drag_kind: str | None = None
    view_limits: tuple[tuple[float, float], tuple[float, float]] | None = None
    chart_drawn = False
    click_moved = False
    is_dirty = False
    leg_drag_start_x: float | None = None
    leg_drag_base: dict[str, int] | None = None
    leg_drag_active = False
    hover = HoverReadout()

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
        nonlocal view_limits, chart_drawn
        workspace.set_market(symbol=symbol, timeframe=timeframe)
        view_limits = None
        chart_drawn = False
        mark_dirty(False)
        print(f"Market: {symbol} {timeframe}")

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
            f"| legs={len(workspace.legs)} "
            f"| {'unsaved' if is_dirty else 'saved'} "
            "| h/l p push-leg j/k leg fib g w fib-annot s save d delete q quit",
            color="#d6d9e0",
        )

    def redraw(*, reset_view: bool = False, lightweight: bool = False) -> None:
        nonlocal view_limits, chart_drawn
        if reset_view:
            view_limits = None
        elif chart_drawn:
            view_limits = (ax.get_xlim(), ax.get_ylim())

        ax.clear()
        ax.set_facecolor("#0f1117")
        # Log price axis so log-scale fib levels render evenly spaced (TradingView-style).
        ax.set_yscale("log" if workspace.settings.fib.scale_mode == "log" else "linear")
        df = workspace.df
        x = range(len(df))
        lows = df["low"].to_numpy()
        highs = df["high"].to_numpy()

        draw_review_candles(ax, df, candlestick=True, dark_theme=True)

        draw_htf_overlays(ax, df, workspace.get_htf_overlays(), show=workspace.show_fib)

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

        def _draw_leg_picks(
            picks: dict[str, tuple[int, float]],
            *,
            leg_index: int,
            active: bool,
            label_suffix: str = "",
        ) -> None:
            alpha = 1.0 if active else LEG_MARKER_ALPHA_INACTIVE
            fib_color = LEG_FIB_COLORS[leg_index % len(LEG_FIB_COLORS)]
            for kind, (idx, price) in picks.items():
                color = "#ff6b6b" if kind == "high" else "#6be675"
                marker = "^" if kind == "high" else "v"
                ax.scatter(
                    [idx],
                    [price],
                    color=color,
                    marker=marker,
                    s=100 if active else 70,
                    alpha=alpha,
                    zorder=5 if active else 4,
                )
                tag = f" {kind}{label_suffix}"
                ax.text(idx, price, tag, color=color, fontsize=9, alpha=alpha)

            draw_fib = workspace.show_fib and picks and (active or len(workspace.legs) <= 1)
            if draw_fib:
                for level, price in _fib_prices_from_picks(
                    picks,
                    workspace.settings.fib.levels or DEFAULT_FIB_LEVELS,
                    scale_mode=workspace.settings.fib.scale_mode,
                ).items():
                    ax.axhline(
                        price,
                        color=fib_color,
                        ls="--",
                        lw=0.9 if active else 0.6,
                        alpha=0.75 if active else 0.35,
                    )
                    if active:
                        ax.text(
                            len(df) - 1,
                            price,
                            f" {level}",
                            color=fib_color,
                            fontsize=8,
                        )

        for i, leg in enumerate(workspace.legs):
            if i == workspace.active_leg_index and workspace._picks_complete():
                continue
            leg_picks = workspace._picks_from_leg(leg)
            _draw_leg_picks(
                leg_picks,
                leg_index=i,
                active=i == workspace.active_leg_index,
                label_suffix=f" L{i + 1}",
            )

        if workspace.picks:
            _draw_leg_picks(
                workspace.picks,
                leg_index=workspace.active_leg_index,
                active=True,
                label_suffix=" *",
            )

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
        if not lightweight:
            fig.tight_layout()
        hover.reattach(ax, fig)
        chart_drawn = True
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
        if leg_drag_active and leg_drag_start_x is not None and leg_drag_base is not None:
            hover.hide()
            delta = int(round(event.xdata - leg_drag_start_x))
            n = len(workspace.df) - 1
            for kind in ("high", "low"):
                base_idx = leg_drag_base[kind]
                workspace.move_pick(kind, min(max(base_idx + delta, 0), n))
            mark_dirty(True)
            click_moved = True
            redraw(lightweight=True)
            return

        if drag_kind is not None:
            if event.inaxes != ax or event.xdata is None:
                return
            hover.hide()
            idx = _nearest_bar(workspace.df, event.xdata)
            workspace.move_pick(drag_kind, idx)
            mark_dirty(True)
            click_moved = True
            redraw(lightweight=True)
            return

        hover.update(event, workspace.df)

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
        key = _normalize_key(event.key)
        if key == "r":
            workspace.reset()
            mark_dirty(True)
        elif key == "h":
            workspace.active_kind = "high"
            print("Next click sets HIGH.")
        elif key == "l":
            workspace.active_kind = "low"
            print("Next click sets LOW.")
        elif key in {"u", "backspace"}:
            workspace.undo()
            mark_dirty(True)
        elif key == "d":
            workspace.delete_current_label()
            mark_dirty(False)
        elif key == "s":
            workspace.save_current_label()
            mark_dirty(False)
        elif key in {"a", "p"}:
            workspace.append_leg()
            mark_dirty(True)
        elif key == "j":
            workspace.cycle_leg(-1)
            mark_dirty(False)
        elif key == "k":
            workspace.cycle_leg(1)
            mark_dirty(False)
        elif key == "f":
            workspace.show_fib = not workspace.show_fib
            print(f"Fib levels {'ON' if workspace.show_fib else 'OFF'}.")
        elif key == "g":
            workspace.show_range = not workspace.show_range
            print(f"High-low range {'ON' if workspace.show_range else 'OFF'}.")
        elif key == "w":
            workspace.save_human_fib_annotation()
        elif key in KEY_NEXT_SYMBOL:
            goto_market(_cycle(symbols, workspace.data.symbol, 1), workspace.data.timeframe)
        elif key in KEY_PREV_SYMBOL:
            goto_market(_cycle(symbols, workspace.data.symbol, -1), workspace.data.timeframe)
        elif key in KEY_NEXT_TIMEFRAME:
            goto_market(workspace.data.symbol, _cycle(timeframes, workspace.data.timeframe, 1))
        elif key in KEY_PREV_TIMEFRAME:
            goto_market(workspace.data.symbol, _cycle(timeframes, workspace.data.timeframe, -1))
        elif key == "n":
            goto_next_unlabeled()
        elif key == "z":
            redraw(reset_view=True)
            return
        elif key == "q":
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
