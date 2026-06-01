"""Research: daily Fib structure inside an HTF (1w) facit leg.

Half pipeline (mtf_disambiguation): HTF prices + LTF order/timestamps.
Full pipeline (this module): same anchors, then scan **daily** bars for
touches/rejections at Fib levels derived from the HTF range — where
in/out patterns become visible (not scored against TV).

Requires resolved MTF endpoints (enable mtf_disambiguation for the run).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from fibengine.core.config import Settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.labeling.mtf_disambiguation import (
    MTF_RESOLVED,
    disambiguate_label_endpoints,
)
from fibengine.labeling.same_candle_mtf_resolution import resolution_timeframe_for
from fibengine.labeling.store import SwingLabel

DEFAULT_LEVELS = (0.382, 0.5, 0.618, 0.786)


@dataclass(frozen=True)
class LevelEvent:
    level: float
    price: float
    event: str
    timestamp: str


@dataclass(frozen=True)
class LegPhaseReport:
    """Bars between two LTF timestamps (impulse or retrace)."""

    name: str
    start: str
    end: str
    bar_count: int
    events: tuple[LevelEvent, ...]


@dataclass(frozen=True)
class MtfLegResearchReport:
    label_id: str
    htf_timeframe: str
    ltf_timeframe: str
    mtf_status: str
    resolution_kind: str | None
    order: str | None
    htf_high_price: float
    htf_low_price: float
    fib_start_price: float
    fib_end_price: float
    ltf_high_timestamp: str
    ltf_low_timestamp: str
    fib_levels: dict[str, float]
    impulse: LegPhaseReport | None
    retrace: LegPhaseReport | None
    skip_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _settings_with_mtf_on(settings: Settings) -> Settings:
    return settings.model_copy(
        update={"labeling": settings.labeling.model_copy(update={"mtf_disambiguation": True})}
    )


def _first_high_touch(df: pd.DataFrame, level_price: float) -> tuple[str | None, str | None]:
    for ts, row in df.iterrows():
        if float(row["high"]) >= level_price:
            return ts.isoformat(), "high_touch"
    return None, None


def _first_close_cross_up(df: pd.DataFrame, level_price: float) -> tuple[str | None, str | None]:
    for ts, row in df.iterrows():
        if float(row["close"]) >= level_price:
            return ts.isoformat(), "close_cross_up"
    return None, None


def _first_rejection(
    df: pd.DataFrame, level_price: float, tol_frac: float = 0.0005
) -> tuple[str | None, str | None]:
    """Wick at/above level, close back below (resistance-style on retrace up)."""
    band = level_price * tol_frac
    for ts, row in df.iterrows():
        if float(row["high"]) >= level_price - band and float(row["close"]) < level_price - band:
            return ts.isoformat(), "rejection"
    return None, None


def _scan_phase_down(
    daily: pd.DataFrame,
    *,
    name: str,
    levels: dict[float, float],
) -> LegPhaseReport:
    events: list[LevelEvent] = []
    if daily.empty:
        return LegPhaseReport(name=name, start="", end="", bar_count=0, events=())

    for ratio, price in sorted(levels.items(), reverse=True):
        ts, kind = None, None
        for t, row in daily.iterrows():
            if float(row["low"]) <= price:
                ts, kind = t.isoformat(), "low_touch"
                break
        if ts:
            events.append(
                LevelEvent(
                    level=ratio,
                    price=round(price, 2),
                    event=kind or "",
                    timestamp=ts,
                )
            )

    return LegPhaseReport(
        name=name,
        start=daily.index[0].isoformat(),
        end=daily.index[-1].isoformat(),
        bar_count=len(daily),
        events=tuple(events),
    )


def _scan_phase_up(
    daily: pd.DataFrame,
    *,
    name: str,
    levels: dict[float, float],
) -> LegPhaseReport:
    events: list[LevelEvent] = []
    if daily.empty:
        return LegPhaseReport(name=name, start="", end="", bar_count=0, events=())

    for ratio, price in sorted(levels.items()):
        ts, kind = _first_high_touch(daily, price)
        if ts is None:
            ts, kind = _first_close_cross_up(daily, price)
        rej_ts, rej_kind = _first_rejection(daily, price)
        if rej_ts:
            events.append(
                LevelEvent(
                    level=ratio,
                    price=round(price, 2),
                    event=rej_kind or "rejection",
                    timestamp=rej_ts,
                )
            )
        elif ts:
            events.append(
                LevelEvent(
                    level=ratio,
                    price=round(price, 2),
                    event=kind or "",
                    timestamp=ts,
                )
            )

    return LegPhaseReport(
        name=name,
        start=daily.index[0].isoformat(),
        end=daily.index[-1].isoformat(),
        bar_count=len(daily),
        events=tuple(events),
    )


def analyze_mtf_leg_daily_fib(
    label: SwingLabel,
    htf_df: pd.DataFrame,
    settings: Settings,
    *,
    fib_levels: tuple[float, ...] = DEFAULT_LEVELS,
    force_mtf_on: bool = True,
) -> MtfLegResearchReport:
    """Build HTF Fib grid from facit; scan daily impulse + retrace phases."""
    label_id = f"{label.exchange}_{label.symbol.replace('/', '-')}_{label.timeframe}"
    ltf_tf = resolution_timeframe_for(label.timeframe)
    st = _settings_with_mtf_on(settings) if force_mtf_on else settings
    endpoints = disambiguate_label_endpoints(label, htf_df, st)

    empty = MtfLegResearchReport(
        label_id=label_id,
        htf_timeframe=label.timeframe,
        ltf_timeframe=ltf_tf or "",
        mtf_status=endpoints.mtf_status,
        resolution_kind=endpoints.resolution_kind,
        order=endpoints.order,
        htf_high_price=label.high.price,
        htf_low_price=label.low.price,
        fib_start_price=endpoints.fib_start_price,
        fib_end_price=endpoints.fib_end_price,
        ltf_high_timestamp=endpoints.high_timestamp,
        ltf_low_timestamp=endpoints.low_timestamp,
        fib_levels={},
        impulse=None,
        retrace=None,
        skip_reason=endpoints.skip_reason or "unresolved MTF endpoints",
    )

    if endpoints.mtf_status != MTF_RESOLVED or not ltf_tf:
        return empty

    daily_df = load_candles(
        settings.data.model_copy(
            update={
                "exchange": label.exchange,
                "symbol": label.symbol,
                "timeframe": ltf_tf,
            }
        )
    )

    grid = fib_from_prices(
        endpoints.fib_start_price,
        endpoints.fib_end_price,
        list(fib_levels),
    )
    grid_str = {str(k): round(v, 2) for k, v in grid.items()}

    hi_ts = pd.to_datetime(endpoints.high_timestamp, utc=True)
    lo_ts = pd.to_datetime(endpoints.low_timestamp, utc=True)
    if hi_ts <= lo_ts:
        impulse_df = daily_df[(daily_df.index >= hi_ts) & (daily_df.index <= lo_ts)]
        retrace_df = daily_df[daily_df.index >= lo_ts]
    else:
        impulse_df = daily_df[(daily_df.index >= lo_ts) & (daily_df.index <= hi_ts)]
        retrace_df = daily_df[daily_df.index >= hi_ts]

    if endpoints.order == "high_then_low":
        impulse = _scan_phase_down(impulse_df, name="impulse_down", levels=grid)
        retrace = _scan_phase_up(retrace_df, name="retrace_up", levels=grid)
    else:
        impulse = _scan_phase_up(impulse_df, name="impulse_up", levels=grid)
        retrace = _scan_phase_down(retrace_df, name="retrace_down", levels=grid)

    return MtfLegResearchReport(
        label_id=label_id,
        htf_timeframe=label.timeframe,
        ltf_timeframe=ltf_tf,
        mtf_status=endpoints.mtf_status,
        resolution_kind=endpoints.resolution_kind,
        order=endpoints.order,
        htf_high_price=label.high.price,
        htf_low_price=label.low.price,
        fib_start_price=endpoints.fib_start_price,
        fib_end_price=endpoints.fib_end_price,
        ltf_high_timestamp=endpoints.high_timestamp,
        ltf_low_timestamp=endpoints.low_timestamp,
        fib_levels=grid_str,
        impulse=impulse,
        retrace=retrace,
    )
