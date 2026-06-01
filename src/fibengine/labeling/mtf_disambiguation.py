"""MTF Disambiguation Layer (research): LTF order and time alignment for HTF facit.

HTF prices = range/facit (weekly OHLC snap). LTF = which **day** within each week
for high/low and temporal order — never overrides HTF prices.

Modes when ``mtf_disambiguation`` is ON (1w → 1d today):
- **same_candle:** saved metadata or derive max-high / min-low days in one week.
- **fractal_endpoints:** high/low on different weeks — each endpoint → daily extreme
  in its own week (weekly fib placed on daily structure).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from fibengine.core.config import Settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.labeling.same_candle_mtf_resolution import (
    build_same_candle_mtf_metadata,
    daily_candles_in_week,
    resolution_timeframe_for,
)
from fibengine.labeling.store import SwingLabel

VALID_ORDERS = frozenset({"high_then_low", "low_then_high"})
MTF_NOT_APPLICABLE = "not_applicable"
MTF_RESOLVED = "resolved"
MTF_UNRESOLVED = "unresolved"
RESOLUTION_SAME_CANDLE_SAVED = "same_candle_saved"
RESOLUTION_SAME_CANDLE_DERIVED = "same_candle_derived"
RESOLUTION_FRACTAL_ENDPOINTS = "fractal_endpoints"


@dataclass(frozen=True)
class DisambiguatedEndpoints:
    """Endpoints for evaluation after optional MTF disambiguation."""

    high_price: float
    low_price: float
    high_timestamp: str
    low_timestamp: str
    mtf_status: str
    same_htf_candle: bool
    order: str | None
    fib_start_price: float
    fib_end_price: float
    time_df_timeframe: str
    resolution_kind: str | None = None
    skip_evaluation: bool = False
    skip_reason: str = ""


def _same_htf_candle(label: SwingLabel, htf_df: pd.DataFrame) -> bool:
    hi_bar, hi_ok = bar_of_timestamp(htf_df, label.high.timestamp)
    lo_bar, lo_ok = bar_of_timestamp(htf_df, label.low.timestamp)
    if not (hi_ok and lo_ok):
        return False
    return hi_bar == lo_bar


def _order_from_timestamps(hi_ts: pd.Timestamp, lo_ts: pd.Timestamp) -> str:
    return "high_then_low" if hi_ts <= lo_ts else "low_then_high"


def _fib_leg_from_order(order: str, high_price: float, low_price: float) -> tuple[float, float]:
    if order == "high_then_low":
        return high_price, low_price
    return low_price, high_price


def _daily_extreme_in_week(
    weekly_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    week_idx: int,
    kind: str,
) -> tuple[pd.Timestamp | None, str]:
    week_days = daily_candles_in_week(weekly_df, daily_df, week_idx)
    if week_days.empty:
        return None, f"no {kind} LTF bars in week index {week_idx}"
    if kind == "high":
        return week_days["high"].idxmax(), ""
    return week_days["low"].idxmin(), ""


def _derive_same_week_daily(
    weekly_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    week_idx: int,
) -> tuple[dict[str, str] | None, str]:
    week_days = daily_candles_in_week(weekly_df, daily_df, week_idx)
    if week_days.empty:
        return None, "no LTF bars in HTF week window"
    hi_ts = week_days["high"].idxmax()
    lo_ts = week_days["low"].idxmin()
    if hi_ts == lo_ts:
        return None, "LTF high and low collapse to one daily bar"
    meta = build_same_candle_mtf_metadata("1w", "1d", hi_ts, lo_ts)
    return meta, ""


def _verify_mtf_metadata(
    label: SwingLabel,
    htf_df: pd.DataFrame,
    daily_df: pd.DataFrame,
) -> tuple[bool, str]:
    meta = label.same_candle_mtf_resolution
    if not meta:
        return False, "missing same_candle_mtf_resolution"
    if meta.get("resolved_by") != "lower_timeframe":
        return False, "resolved_by is not lower_timeframe"
    resolution_tf = meta.get("resolution_timeframe")
    expected = resolution_timeframe_for(label.timeframe)
    if not resolution_tf or resolution_tf != expected:
        return False, f"unexpected resolution_timeframe {resolution_tf!r}"
    order = meta.get("order")
    if order not in VALID_ORDERS:
        return False, f"invalid order {order!r}"
    hi_ts_raw = meta.get("high_daily_timestamp")
    lo_ts_raw = meta.get("low_daily_timestamp")
    if not hi_ts_raw or not lo_ts_raw:
        return False, "missing LTF timestamps"
    hi_ts = pd.to_datetime(hi_ts_raw, utc=True)
    lo_ts = pd.to_datetime(lo_ts_raw, utc=True)
    if hi_ts == lo_ts:
        return False, "LTF high and low collapse to one bar"
    if order == "high_then_low" and hi_ts > lo_ts:
        return False, "order high_then_low but high daily is after low daily"
    if order == "low_then_high" and lo_ts > hi_ts:
        return False, "order low_then_high but low daily is after high daily"

    hi_bar, _ = bar_of_timestamp(htf_df, label.high.timestamp)
    week_days = daily_candles_in_week(htf_df, daily_df, hi_bar)
    if week_days.empty:
        return False, "no LTF bars in HTF week window"
    if hi_ts not in week_days.index:
        return False, "high_daily_timestamp outside HTF week"
    if lo_ts not in week_days.index:
        return False, "low_daily_timestamp outside HTF week"
    if week_days["high"].idxmax() != hi_ts:
        return False, "high_daily_timestamp is not max daily high in week"
    if week_days["low"].idxmin() != lo_ts:
        return False, "low_daily_timestamp is not min daily low in week"
    return True, ""


def _resolved(
    *,
    high_p: float,
    low_p: float,
    hi_ts: str,
    lo_ts: str,
    order: str,
    resolution_tf: str,
    same_bar: bool,
    resolution_kind: str,
) -> DisambiguatedEndpoints:
    fib_start, fib_end = _fib_leg_from_order(order, high_p, low_p)
    return DisambiguatedEndpoints(
        high_price=high_p,
        low_price=low_p,
        high_timestamp=hi_ts,
        low_timestamp=lo_ts,
        mtf_status=MTF_RESOLVED,
        same_htf_candle=same_bar,
        order=order,
        fib_start_price=fib_start,
        fib_end_price=fib_end,
        time_df_timeframe=resolution_tf,
        resolution_kind=resolution_kind,
    )


def _unresolved(
    *,
    high_p: float,
    low_p: float,
    label: SwingLabel,
    same_bar: bool,
    reason: str,
) -> DisambiguatedEndpoints:
    return DisambiguatedEndpoints(
        high_price=high_p,
        low_price=low_p,
        high_timestamp=label.high.timestamp,
        low_timestamp=label.low.timestamp,
        mtf_status=MTF_UNRESOLVED,
        same_htf_candle=same_bar,
        order=None,
        fib_start_price=low_p,
        fib_end_price=high_p,
        time_df_timeframe=label.timeframe,
        skip_evaluation=True,
        skip_reason=reason,
    )


def disambiguate_label_endpoints(
    label: SwingLabel,
    htf_df: pd.DataFrame,
    settings: Settings,
) -> DisambiguatedEndpoints:
    """Resolve evaluation endpoints; never override HTF prices."""
    same_bar = _same_htf_candle(label, htf_df)
    high_p, low_p = label.high.price, label.low.price
    resolution_tf = resolution_timeframe_for(label.timeframe)
    use_mtf = settings.labeling.mtf_disambiguation and resolution_tf is not None

    if not use_mtf:
        if same_bar:
            return _unresolved(
                high_p=high_p,
                low_p=low_p,
                label=label,
                same_bar=True,
                reason="same HTF candle; mtf_disambiguation OFF",
            )
        lo_ts = pd.to_datetime(label.low.timestamp, utc=True)
        hi_ts = pd.to_datetime(label.high.timestamp, utc=True)
        if lo_ts <= hi_ts:
            fib_start, fib_end = low_p, high_p
        else:
            fib_start, fib_end = high_p, low_p
        return DisambiguatedEndpoints(
            high_price=high_p,
            low_price=low_p,
            high_timestamp=label.high.timestamp,
            low_timestamp=label.low.timestamp,
            mtf_status=MTF_NOT_APPLICABLE,
            same_htf_candle=False,
            order=_order_from_timestamps(hi_ts, lo_ts),
            fib_start_price=fib_start,
            fib_end_price=fib_end,
            time_df_timeframe=label.timeframe,
        )

    daily_cfg = settings.data.model_copy(
        update={
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": resolution_tf,
        }
    )
    try:
        daily_df = load_candles(daily_cfg)
    except FileNotFoundError:
        return _unresolved(
            high_p=high_p,
            low_p=low_p,
            label=label,
            same_bar=same_bar,
            reason=f"missing {resolution_tf} cache",
        )

    if same_bar:
        ok, reason = _verify_mtf_metadata(label, htf_df, daily_df)
        if ok:
            meta = label.same_candle_mtf_resolution
            assert meta is not None
            order = meta["order"]
            return _resolved(
                high_p=high_p,
                low_p=low_p,
                hi_ts=meta["high_daily_timestamp"],
                lo_ts=meta["low_daily_timestamp"],
                order=order,
                resolution_tf=resolution_tf,
                same_bar=True,
                resolution_kind=RESOLUTION_SAME_CANDLE_SAVED,
            )
        hi_bar, _ = bar_of_timestamp(htf_df, label.high.timestamp)
        derived, derive_reason = _derive_same_week_daily(htf_df, daily_df, hi_bar)
        if derived is None:
            return _unresolved(
                high_p=high_p,
                low_p=low_p,
                label=label,
                same_bar=True,
                reason=derive_reason or reason,
            )
        order = derived["order"]
        return _resolved(
            high_p=high_p,
            low_p=low_p,
            hi_ts=derived["high_daily_timestamp"],
            lo_ts=derived["low_daily_timestamp"],
            order=order,
            resolution_tf=resolution_tf,
            same_bar=True,
            resolution_kind=RESOLUTION_SAME_CANDLE_DERIVED,
        )

    hi_bar, hi_ok = bar_of_timestamp(htf_df, label.high.timestamp)
    lo_bar, lo_ok = bar_of_timestamp(htf_df, label.low.timestamp)
    if not (hi_ok and lo_ok):
        return _unresolved(
            high_p=high_p,
            low_p=low_p,
            label=label,
            same_bar=False,
            reason="HTF endpoint out of window for fractal LTF map",
        )

    hi_daily, hi_err = _daily_extreme_in_week(htf_df, daily_df, hi_bar, "high")
    lo_daily, lo_err = _daily_extreme_in_week(htf_df, daily_df, lo_bar, "low")
    if hi_daily is None:
        return _unresolved(
            high_p=high_p,
            low_p=low_p,
            label=label,
            same_bar=False,
            reason=hi_err,
        )
    if lo_daily is None:
        return _unresolved(
            high_p=high_p,
            low_p=low_p,
            label=label,
            same_bar=False,
            reason=lo_err,
        )
    if hi_daily == lo_daily:
        return _unresolved(
            high_p=high_p,
            low_p=low_p,
            label=label,
            same_bar=False,
            reason="fractal endpoints collapsed to one LTF bar",
        )

    order = _order_from_timestamps(hi_daily, lo_daily)
    return _resolved(
        high_p=high_p,
        low_p=low_p,
        hi_ts=hi_daily.isoformat(),
        lo_ts=lo_daily.isoformat(),
        order=order,
        resolution_tf=resolution_tf,
        same_bar=False,
        resolution_kind=RESOLUTION_FRACTAL_ENDPOINTS,
    )
