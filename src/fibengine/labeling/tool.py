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
- f: toggle fib levels (includes read-only HTF overlays on lower TFs: parent fib
     level lines + parent swing H/L anchor markers in time+price, for nesting)
- HTF overlays default to fibs drawn THIS session only (clean nesting view): draw on
  1M, save (w), drop to 1w/1d and your 1M/1w lines follow down — the frozen corpus stays hidden
- b: toggle frozen-corpus overlays (off = session fibs only, on = all saved fibs)
- c: nesting focus — cycle through parent fibs overlapping the current view; shows
     only that parent's H/L and fits the view to it (press again to step / clear)
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
import json
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from fibengine.core.config import DataConfig, Settings, load_settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.labeling.hover import HoverReadout
from fibengine.labeling.htf_fib_overlay import (
    cycle_focus_id,
    draw_htf_overlays,
    filter_to_session,
    load_htf_overlays,
    overlays_in_view,
    select_focused,
)
from fibengine.labeling.human_fib import (
    HumanFibAnnotation,
    anchors_from_picks,
    annotation_path,
    find_annotation,
    load_annotation,
    make_annotation,
    save_annotation,
)
from fibengine.labeling.same_candle_mtf_resolution import (
    attempt_same_candle_mtf_resolution,
    mtf_resolution_enabled,
    resolution_timeframe_for,
)
from fibengine.labeling.selection_capture import (
    build_window,
    make_candidate,
    save_window,
    time_ordered,
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
from fibengine.research.selection_annotation import OPTIONAL_TAGS, Anchor, Candidate

SELECTION_ANNOTATIONS_DIR = "data/labels/selection_annotations"
# Contrastive-mode label → colour (green accept / red reject / grey ambiguous).
SELECTION_LABEL_COLORS = {
    "accepted": "#6be675",
    "rejected": "#ff6b6b",
    "ambiguous": "#b0b6c4",
}
SELECTION_LABEL_KEYS = {"1": "accepted", "2": "rejected", "3": "ambiguous"}

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
    parser.add_argument(
        "--review-candidate",
        dest="review_candidate",
        default=None,
        help=(
            "Promote a screenshot-transcription candidate JSON: preload its anchors for "
            "visual review against the chart; press 'w' to save to human_fib as facit "
            "(created_by=human, source=manual_screenshot_transcription_reviewed). The "
            "candidate's market + scale are read from the file. Mutually exclusive with "
            "--edit-fib-id. Refuses non-candidate files. Nothing saved unless you press 'w'."
        ),
    )
    parser.add_argument(
        "--annotate-selection",
        dest="annotate_selection",
        action="store_true",
        help=(
            "Contrastive selection-annotation mode (Issue #42): draw candidate legs on real "
            "candles and label each 1=accepted / 2=rejected / 3=ambiguous, cycle a tag (t), "
            "add a reason via terminal prompt (e), press 'v' to save the window to "
            "data/labels/selection_annotations/ (created_by=human, exact prices — no snap)."
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


def _load_candidate_for_review(path: Path) -> tuple[HumanFibAnnotation, dict]:
    """Load a transcription candidate for review-and-promote (read-only).

    Returns the facit-shaped annotation plus its ``_transcription`` audit block so the
    caller can surface guessed/near anchors for scrutiny. Fail-closed: refuses anything
    that is not a candidate, so this mode can never silently re-save existing facit.
    """
    if not path.exists():
        raise SystemExit(f"--review-candidate: file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"--review-candidate: cannot read {path}: {exc}") from exc
    if not raw.get("_candidate"):
        raise SystemExit(
            f"--review-candidate: {path} is not a candidate (missing _candidate flag). "
            "Use --edit-fib-id to edit saved facit."
        )
    ann = load_annotation(path)  # tolerates the extra _candidate / _transcription keys
    return ann, raw.get("_transcription", {})


def _print_review_candidate_banner(ann: HumanFibAnnotation, audit: dict) -> None:
    """Tell the reviewer what to scrutinise before promoting (press 'w').

    The transcription recovers the *bar* heuristically when an anchor price repeats on
    several candles (``n_within_near > 1``) or only matches *near* a candle extreme — those
    are exactly the bars a human must confirm before the candidate becomes facit.
    """
    conf = audit.get("confidence", "?")
    print(
        f"Review-candidate mode: {ann.fib_id} ({ann.direction}) — anchors preloaded "
        f"(transcription confidence: {conf}).\n"
        "  Verify against the screenshot, nudge a bar if wrong, then 'w' to PROMOTE to "
        "human_fib (facit; source=manual_screenshot_transcription_reviewed).\n"
        "  Nothing is saved unless you press 'w'."
    )
    for m in audit.get("matches", []):
        if m.get("n_within_near", 1) > 1:
            print(
                f"  ! {m.get('role')} {m.get('price')}: price repeats on "
                f"{m.get('n_within_near')} bars — BAR WAS GUESSED, verify x-position."
            )
        elif m.get("confidence") != "exact":
            print(
                f"  ! {m.get('role')} {m.get('price')}: {m.get('confidence')} match "
                f"(delta={m.get('rel_delta')}) — verify the price/bar."
            )


def _view_time_range(df: pd.DataFrame, x0: float, x1: float) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Map positional x-axis limits to the df timestamps they bracket (clamped)."""
    n = len(df)
    i0 = max(0, min(n - 1, int(x0)))
    i1 = max(0, min(n - 1, int(x1)))
    lo, hi = sorted((i0, i1))
    return df.index[lo], df.index[hi]


def _focus_view_for_parent(df: pd.DataFrame, ann: HumanFibAnnotation) -> tuple:
    """View limits ``(xlim, ylim)`` framing a parent fib's A→B span on the child chart.

    Positional x-bar limits with context padding + log-aware price limits, so focusing
    a parent swing zooms to it. Touches neither df nor picks (view-only, index-based).
    """
    ia = _nearest_timestamp_bar(df, ann.anchor_a.time)
    ib = _nearest_timestamp_bar(df, ann.anchor_b.time)
    lo_i, hi_i = sorted((ia, ib))
    xpad = max(3, (hi_i - lo_i) // 4)
    prices = [float(ann.anchor_a.price), float(ann.anchor_b.price)]
    pmin, pmax = min(prices), max(prices)
    return ((lo_i - xpad, hi_i + xpad), (pmin * 0.85, pmax * 1.15))


def _window_fit_view(df: pd.DataFrame, *, pad: float = 0.03) -> tuple:
    """Initial ``(xlim, ylim)`` framing the (already windowed) candles.

    Without this a date-windowed view autoscales the log price axis to the *full* price
    history, squishing a narrow recent band against the top (unreadable for review). Fit
    Y to the window's low/high with a small multiplicative pad (log-friendly). Pure helper.
    """
    n = len(df)
    lo = float(df["low"].min())
    hi = float(df["high"].max())
    return ((-0.5, n - 0.5), (lo / (1 + pad), hi * (1 + pad)))


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
    # Legs loaded from facit but hidden by a display window. Kept in memory so a
    # windowed save merges them back instead of silently dropping them (facit-safety).
    hidden_legs: list[LegLabel] = field(default_factory=list)
    active_leg_index: int = 0
    show_fib: bool = True
    show_range: bool = False
    window_start: pd.Timestamp | None = None
    window_end: pd.Timestamp | None = None
    single_fib_mode: bool = False
    # Nesting focus: fib_id of the one parent fib whose H/L to show (None = show all).
    focus_parent_id: str | None = None
    # HTF overlays show only fibs drawn this session by default (clean nesting view);
    # session_fib_ids persists across TF switches so a 1M draw stays visible on 1w/1d.
    session_fib_ids: set[str] = field(default_factory=set)
    show_frozen_overlays: bool = False
    # Review-candidate promote mode: when set, 'w' saves with this source (provenance: the
    # fib was transcribed from a screenshot then human-reviewed) instead of the default
    # manual_labeling_tool, and overwriting an existing facit needs a second 'w' to confirm.
    promote_source: str | None = None
    # Contrastive selection-annotation mode (Issue #42): a separate candidate list, NOT the facit
    # `legs` — rejected candidates are deliberately "bad" legs that would trip the swing warnings.
    annotate_selection: bool = False
    selection_candidates: list[dict] = field(default_factory=list)
    _htf_overlays: list | None = field(default=None, init=False, repr=False)
    _pending_overwrite: bool = field(default=False, init=False, repr=False)

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

    def parent_overlays(self) -> list:
        """HTF overlays scoped to this nesting session (or the whole corpus if frozen shown)."""
        return filter_to_session(
            self.get_htf_overlays(), self.session_fib_ids, self.show_frozen_overlays
        )

    def focused_overlays(self) -> list:
        """Session-scoped overlays, narrowed to the focused parent fib if one is set."""
        return select_focused(self.parent_overlays(), self.focus_parent_id)

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
        self.focus_parent_id = None
        self.picks.clear()
        self.history.clear()
        self.legs.clear()
        self.selection_candidates.clear()
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
        self.hidden_legs = []
        existing = find_label(self.data.exchange, self.data.symbol, self.data.timeframe)
        if existing is None:
            return
        all_legs = list(existing.all_legs())
        if self.window_start is not None or self.window_end is not None:
            in_window: list[LegLabel] = []
            hidden: list[LegLabel] = []
            for leg in all_legs:
                visible = self._in_display_window(leg.high.timestamp) and self._in_display_window(
                    leg.low.timestamp
                )
                (in_window if visible else hidden).append(leg)
            self.hidden_legs = hidden
            all_legs = in_window
            if hidden:
                print(
                    f"{len(hidden)} saved leg(s) outside the display window are hidden but "
                    "will be preserved on save."
                )
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

    # --- Contrastive selection-annotation mode (Issue #42) -----------------------------------
    def commit_selection_candidate(self, label: str) -> bool:
        """Store the current high/low picks as a labelled candidate (no swing-warning gate)."""
        if not self._picks_complete():
            print("Set both high and low before labelling a candidate.")
            return False
        self.selection_candidates.append(
            {
                "high": self.picks["high"],
                "low": self.picks["low"],
                "label": label,
                "reason": "",
                "tags": [],
            }
        )
        self.picks.clear()
        self.history.clear()
        self.active_kind = "high"
        print(
            f"Candidate {len(self.selection_candidates)} = {label}. "
            "Draw the next; 't' cycles a tag, 'e' adds a reason, 'v' saves the window."
        )
        return True

    def cycle_selection_tag(self, delta: int = 1) -> None:
        """Cycle a single structured tag on the most-recent candidate (None → tag → ... → None)."""
        if not self.selection_candidates:
            print("No candidate yet to tag (label one with 1/2/3 first).")
            return
        cand = self.selection_candidates[-1]
        options = [None, *sorted(OPTIONAL_TAGS)]
        current = cand["tags"][0] if cand["tags"] else None
        idx = options.index(current) if current in options else 0
        nxt = options[(idx + delta) % len(options)]
        cand["tags"] = [nxt] if nxt else []
        print(f"Candidate {len(self.selection_candidates)} tag = {nxt or '(none)'}")

    def prompt_selection_reason(self) -> None:
        """Ask for the most-recent candidate's reason in the TERMINAL (no GUI key-focus leakage)."""
        if not self.selection_candidates:
            print("No candidate yet — label one with 1/2/3 before adding a reason.")
            return
        n = len(self.selection_candidates)
        try:
            text = input(f"reason for candidate {n} (blank = keep): ")
        except (EOFError, KeyboardInterrupt):
            print("(reason unchanged)")
            return
        if text.strip():
            self.selection_candidates[-1]["reason"] = text.strip()
            print(f"Reason on candidate {n}: {text.strip()!r}")

    def undo_selection_candidate(self) -> None:
        if not self.selection_candidates:
            print("No candidates to remove.")
            return
        removed = self.selection_candidates.pop()
        print(f"Removed candidate ({removed['label']}). {len(self.selection_candidates)} left.")

    def _candidate_to_schema(self, cand: dict, existing: list[Candidate]) -> Candidate:
        hi_idx, hi_price = cand["high"]
        lo_idx, lo_price = cand["low"]
        origin, endpoint = time_ordered(
            Anchor(self.df.index[hi_idx].isoformat(), hi_price),
            Anchor(self.df.index[lo_idx].isoformat(), lo_price),
        )
        return make_candidate(
            origin,
            endpoint,
            cand["label"],
            existing=existing,
            reason=cand["reason"],
            tags=tuple(cand["tags"]),
        )

    def save_selection_window(self) -> None:
        """Write all committed candidates as one AnnotationWindow (exact cache prices, no snap)."""
        if not self.selection_candidates:
            print("No candidates to save — label at least one with 1/2/3.")
            return
        schema: list[Candidate] = []
        for cand in self.selection_candidates:
            schema.append(self._candidate_to_schema(cand, schema))
        # Window bounds come from the drawn legs (not the loaded chart), so you can open ONE chart,
        # pan/zoom to each structure and save without restarting — bounds stay tight + correct.
        times = [t for c in schema for t in (c.anchor_a.time, c.anchor_b.time)]
        window = build_window(
            symbol=self.data.symbol,
            timeframe=self.data.timeframe,
            exchange=self.data.exchange,
            window_start=min(times),
            window_end=max(times),
            candidates=schema,
            created_by="human",
        )
        path = save_window(window, SELECTION_ANNOTATIONS_DIR)
        n_acc = len(window.accepted_ids)
        self.selection_candidates.clear()  # auto-clear → next structure starts fresh, no restart
        print(
            f"Saved {len(schema)} candidate(s) ({n_acc} accepted) → {path}. "
            "Candidates cleared; pan/zoom to the next structure and draw."
        )

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

        visible = [leg for leg in self.legs if leg.high.price and leg.low.price]
        hidden = [leg for leg in self.hidden_legs if leg.high.price and leg.low.price]
        # Merge back legs hidden by a display window so a windowed save is non-destructive.
        legs_to_save = visible + hidden
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
        if self.promote_source:
            # Promoting a reviewed transcription: the selection (prices) is human, so
            # created_by stays "human"; record the real method in source instead of plain
            # manual labeling so the guessed-bar provenance is not erased (validity).
            annotation.source = self.promote_source
            target = annotation_path(annotation)
            if target.exists() and not self._pending_overwrite:
                self._pending_overwrite = True
                print(
                    f"WARNING: facit already exists at {target}.\n"
                    "  Press 'w' again to overwrite it, or move on to leave it untouched."
                )
                return
            self._pending_overwrite = False
        path = save_annotation(annotation)
        # Track as a session fib so it shows as an HTF overlay on lower TFs (nesting).
        self.session_fib_ids.add(annotation.fib_id)
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
        review_candidate=None,
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

    review_candidate = getattr(cli, "review_candidate", None)
    review_audit: dict = {}
    if review_candidate:
        if edit_fib_id:
            raise SystemExit("--edit-fib-id and --review-candidate are mutually exclusive")
        selected_fib, review_audit = _load_candidate_for_review(Path(review_candidate))
        # Use the candidate's own market + geometry so promotion is correct regardless of
        # which --config was passed (the candidate carries scale_mode / levels_profile).
        settings.data = settings.data.model_copy(
            update={
                "exchange": selected_fib.exchange,
                "symbol": selected_fib.symbol,
                "timeframe": selected_fib.timeframe,
            }
        )
        settings.fib = settings.fib.model_copy(
            update={
                "scale_mode": selected_fib.scale_mode,
                "levels_profile": selected_fib.levels_profile,
            }
        )
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
        annotate_selection=getattr(cli, "annotate_selection", False),
    )
    if selected_fib is not None:
        _preload_fib_picks(workspace, selected_fib)
        if review_candidate:
            workspace.promote_source = "manual_screenshot_transcription_reviewed"
            _print_review_candidate_banner(selected_fib, review_audit)
        else:
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
        nest = (
            f"| nest={workspace.focus_parent_id.split('_')[-1]} "
            if workspace.focus_parent_id
            else ""
        )
        overlay_scope = "all" if workspace.show_frozen_overlays else "session"
        ax.set_title(
            f"{workspace.data.symbol} {workspace.data.timeframe} "
            f"| active={workspace.active_kind.upper()} "
            f"| fib={'on' if workspace.show_fib else 'off'} "
            f"range={'on' if workspace.show_range else 'off'} "
            f"| overlays={overlay_scope} "
            f"{nest}"
            f"| {queue_labeled_count()}/{len(queue)} labeled "
            f"| {queue_index() + 1}/{len(queue)} "
            f"| legs={len(workspace.legs)} "
            f"| {'unsaved' if is_dirty else 'saved'} "
            "| h/l p push-leg j/k leg fib b frozen c focus g w fib-annot s save d delete q quit",
            color="#d6d9e0",
        )

    def redraw(
        *, reset_view: bool = False, set_view: tuple | None = None, lightweight: bool = False
    ) -> None:
        nonlocal view_limits, chart_drawn
        if reset_view:
            view_limits = None
        elif set_view is not None:
            view_limits = set_view
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

        draw_htf_overlays(ax, df, workspace.focused_overlays(), show=workspace.show_fib)

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

        if workspace.annotate_selection:
            for ci, cand in enumerate(workspace.selection_candidates, start=1):
                hi_idx, hi_price = cand["high"]
                lo_idx, lo_price = cand["low"]
                color = SELECTION_LABEL_COLORS.get(cand["label"], "#ffffff")
                ax.plot([hi_idx, lo_idx], [hi_price, lo_price], color=color, lw=1.8, zorder=6)
                ax.scatter([hi_idx, lo_idx], [hi_price, lo_price], color=color, s=55, zorder=7)
                tag = cand["tags"][0] if cand["tags"] else ""
                lbl = f"{ci}:{cand['label'][:3]}" + (f" {tag}" if tag else "")
                ax.text(
                    (hi_idx + lo_idx) / 2,
                    (hi_price + lo_price) / 2,
                    lbl,
                    color=color,
                    fontsize=8,
                    zorder=8,
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
        if workspace.annotate_selection:
            if key in SELECTION_LABEL_KEYS:
                workspace.commit_selection_candidate(SELECTION_LABEL_KEYS[key])
                redraw()
                return
            if key == "t":
                workspace.cycle_selection_tag(1)
                redraw()
                return
            if key == "e":
                workspace.prompt_selection_reason()
                redraw()
                return
            if key == "x":
                workspace.undo_selection_candidate()
                redraw()
                return
            if key == "v":
                workspace.save_selection_window()
                redraw()
                return
            if key in {"s", "w", "a", "p", "d"}:
                print("Contrastive mode: facit keys disabled. Use 1/2/3, t, e, x, 'v' to save.")
                return
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
        elif key == "b":
            workspace.show_frozen_overlays = not workspace.show_frozen_overlays
            workspace.focus_parent_id = None
            print(
                "Frozen-corpus overlays "
                f"{'ON (all fibs)' if workspace.show_frozen_overlays else 'OFF (session only)'}."
            )
        elif key == "c":
            overlays = workspace.parent_overlays()
            if not overlays:
                print("No parent overlays to focus (top timeframe, or none drawn this session).")
                return
            t0, t1 = _view_time_range(workspace.df, *ax.get_xlim())
            candidates = overlays_in_view(overlays, t0, t1)
            cand_ids = [ann.fib_id for _, ann in candidates]
            workspace.focus_parent_id = cycle_focus_id(workspace.focus_parent_id, cand_ids)
            if workspace.focus_parent_id is None:
                print(f"Nesting focus: OFF ({len(cand_ids)} parent fib(s) in view).")
                redraw()
            else:
                ann = next(a for _, a in candidates if a.fib_id == workspace.focus_parent_id)
                print(f"Nesting focus: {ann.fib_id} — H/L only, view fitted.")
                redraw(set_view=_focus_view_for_parent(workspace.df, ann))
            return
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

    if workspace.annotate_selection:
        print(
            "Contrastive mode ON: draw a leg (h/l + click), then 1=accept 2=reject 3=ambiguous; "
            "'t' cycles a tag on the last candidate; 'e' types a reason in THIS terminal; "
            "'v' saves the window; 'x' removes the last candidate. Facit keys are disabled here."
        )

    # A date-windowed view (review/edit single-fib, or --label-year) must fit Y to the
    # window, else the log axis autoscales to full history and squishes the band (unreadable).
    initial_view = (
        _window_fit_view(workspace.df)
        if (window_start is not None or window_end is not None) and len(workspace.df)
        else None
    )
    redraw(set_view=initial_view)
    plt.show()


if __name__ == "__main__":
    run_label_tool(_parse_args())
