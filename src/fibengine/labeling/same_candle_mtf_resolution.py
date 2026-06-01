"""Research: resolve same weekly bar H/L via lower timeframe (1w → 1d).

Not used by pivot_recall, experiment, or scoring — labeling-tool save path only.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from fibengine.core.config import DataConfig, Settings
from fibengine.data.loader import load_candles

# Chart TF → resolution TF (research scope).
RESOLUTION_TIMEFRAME: dict[str, str] = {"1w": "1d"}


def mtf_resolution_enabled(settings: Settings) -> bool:
    return settings.labeling.enable_same_candle_mtf_resolution


def resolution_timeframe_for(chart_timeframe: str) -> str | None:
    return RESOLUTION_TIMEFRAME.get(chart_timeframe)


def daily_candles_in_week(
    weekly_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    week_idx: int,
) -> pd.DataFrame:
    week_start = weekly_df.index[week_idx]
    if week_idx + 1 < len(weekly_df):
        week_end = weekly_df.index[week_idx + 1]
    else:
        week_end = week_start + pd.Timedelta(days=7)
    return daily_df[(daily_df.index >= week_start) & (daily_df.index < week_end)]


def build_same_candle_mtf_metadata(
    chart_timeframe: str,
    resolution_tf: str,
    high_daily_ts: pd.Timestamp,
    low_daily_ts: pd.Timestamp,
) -> dict[str, str]:
    order = "high_then_low" if high_daily_ts <= low_daily_ts else "low_then_high"
    return {
        "timeframe": chart_timeframe,
        "resolved_by": "lower_timeframe",
        "resolution_timeframe": resolution_tf,
        "high_daily_timestamp": high_daily_ts.isoformat(),
        "low_daily_timestamp": low_daily_ts.isoformat(),
        "order": order,
    }


def attempt_same_candle_mtf_resolution(
    settings: Settings,
    weekly_df: pd.DataFrame,
    week_idx: int,
    *,
    load_candles_fn: Callable[[DataConfig], pd.DataFrame] = load_candles,
) -> tuple[dict | None, str | None]:
    """Return (same_candle_mtf_resolution dict, error message)."""
    chart_tf = settings.data.timeframe
    resolution_tf = resolution_timeframe_for(chart_tf)
    if resolution_tf is None:
        return None, (
            f"same_candle_mtf_resolution: no resolution TF for chart timeframe {chart_tf!r}."
        )
    if not mtf_resolution_enabled(settings):
        return None, (
            "High and low are on the same candle. Enable "
            "labeling.enable_same_candle_mtf_resolution in config (research) "
            "or pick distinct weekly bars."
        )

    daily_cfg = settings.data.model_copy(update={"timeframe": resolution_tf})
    try:
        daily_df = load_candles_fn(daily_cfg)
    except FileNotFoundError as exc:
        return None, f"Could not load {resolution_tf} candles for MTF resolution: {exc}"

    week_days = daily_candles_in_week(weekly_df, daily_df, week_idx)
    if week_days.empty:
        return None, (
            f"No {resolution_tf} candles in week starting {weekly_df.index[week_idx].isoformat()}. "
            f"Fetch more daily history (data.raw .../{resolution_tf}/)."
        )

    high_daily_ts = week_days["high"].idxmax()
    low_daily_ts = week_days["low"].idxmin()
    if high_daily_ts == low_daily_ts:
        return None, (
            f"Same weekly candle collapses to one {resolution_tf} bar "
            f"({high_daily_ts.isoformat()}). Pick distinct weeks on 1W or label on {resolution_tf}."
        )

    meta = build_same_candle_mtf_metadata(chart_tf, resolution_tf, high_daily_ts, low_daily_ts)
    return meta, None
