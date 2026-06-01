"""Heuristic auto-candidates for fib-level behavior (research only — never human facit)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from fibengine.core.fib import fib_from_prices
from fibengine.labeling.store import LegLabel

DEFAULT_LEVELS = ("0.382", "0.5", "0.618", "0.786")


def leg_direction(leg: LegLabel) -> str:
    hi = pd.to_datetime(leg.high.timestamp, utc=True)
    lo = pd.to_datetime(leg.low.timestamp, utc=True)
    return "up" if lo < hi else "down"


def derive_level_prices(
    leg: LegLabel, ratios: tuple[str, ...] = DEFAULT_LEVELS
) -> dict[str, float]:
    direction = leg_direction(leg)
    floats = [float(r) for r in ratios]
    if direction == "up":
        prices = fib_from_prices(leg.low.price, leg.high.price, floats)
    else:
        prices = fib_from_prices(leg.high.price, leg.low.price, floats)
    return {str(r): prices[float(r)] for r in ratios}


AUTO_CANDIDATES = frozenset(
    {
        "reaction_candidate",
        "rejection_candidate",
        "continuation_candidate",
        "failure_candidate",
        "not_reached_candidate",
        "unknown_candidate",
    }
)

CANDIDATE_SUFFIX = "_candidate"


def candidate_to_behavior(candidate: str | None) -> str | None:
    """Map auto_candidate to behavior enum (for display only — not for saving facit)."""
    if not candidate:
        return None
    if candidate.endswith(CANDIDATE_SUFFIX):
        return candidate[: -len(CANDIDATE_SUFFIX)]
    return candidate


@dataclass(frozen=True)
class LevelCandidate:
    level: str
    price: float
    auto_candidate: str
    event_bar: str = ""
    note: str = ""


def leg_time_window(leg: LegLabel) -> tuple[pd.Timestamp, pd.Timestamp]:
    hi = pd.to_datetime(leg.high.timestamp, utc=True)
    lo = pd.to_datetime(leg.low.timestamp, utc=True)
    return min(hi, lo), max(hi, lo)


def slice_leg_bars(candles: pd.DataFrame, leg: LegLabel) -> pd.DataFrame:
    start, end = leg_time_window(leg)
    return candles[(candles.index >= start) & (candles.index <= end)].sort_index()


def _band(level_price: float, frac: float = 0.0005) -> float:
    return level_price * frac


def _first_touch_down(bars: pd.DataFrame, level_price: float) -> int | None:
    for i, (_, row) in enumerate(bars.iterrows()):
        if float(row["low"]) <= level_price:
            return i
    return None


def _first_touch_up(bars: pd.DataFrame, level_price: float) -> int | None:
    for i, (_, row) in enumerate(bars.iterrows()):
        if float(row["high"]) >= level_price:
            return i
    return None


def _classify_after_touch_down(bars: pd.DataFrame, idx: int, level_price: float) -> tuple[str, int]:
    band = _band(level_price)
    row = bars.iloc[idx]
    close = float(row["close"])
    low = float(row["low"])

    if low <= level_price + band and close > level_price + band:
        return "rejection_candidate", idx

    if close < level_price - band:
        return "continuation_candidate", idx

    if idx + 1 < len(bars):
        nxt = bars.iloc[idx + 1]
        nclose = float(nxt["close"])
        if nclose < level_price - band:
            return "continuation_candidate", idx + 1
        if nclose > level_price + band:
            return "rejection_candidate", idx + 1

    return "reaction_candidate", idx


def _classify_after_touch_up(bars: pd.DataFrame, idx: int, level_price: float) -> tuple[str, int]:
    band = _band(level_price)
    row = bars.iloc[idx]
    close = float(row["close"])
    high = float(row["high"])

    if high >= level_price - band and close < level_price - band:
        return "rejection_candidate", idx

    if close > level_price + band:
        return "continuation_candidate", idx

    if idx + 1 < len(bars):
        nxt = bars.iloc[idx + 1]
        nclose = float(nxt["close"])
        if nclose > level_price + band:
            return "continuation_candidate", idx + 1
        if nclose < level_price - band:
            return "rejection_candidate", idx + 1

    return "reaction_candidate", idx


def classify_level(
    candles: pd.DataFrame,
    leg: LegLabel,
    ratio: str,
    level_price: float,
) -> LevelCandidate:
    """Return heuristic candidate for one fib level within the leg's bar window."""
    bars = slice_leg_bars(candles, leg)
    direction = leg_direction(leg)

    if bars.empty:
        return LevelCandidate(
            level=ratio,
            price=level_price,
            auto_candidate="not_reached_candidate",
            note="No bars in leg window",
        )

    if direction == "down":
        touch_idx = _first_touch_down(bars, level_price)
        if touch_idx is None:
            return LevelCandidate(
                level=ratio,
                price=level_price,
                auto_candidate="not_reached_candidate",
                note="Price did not reach level in leg window",
            )
        kind, bar_idx = _classify_after_touch_down(bars, touch_idx, level_price)
    else:
        touch_idx = _first_touch_up(bars, level_price)
        if touch_idx is None:
            return LevelCandidate(
                level=ratio,
                price=level_price,
                auto_candidate="not_reached_candidate",
                note="Price did not reach level in leg window",
            )
        kind, bar_idx = _classify_after_touch_up(bars, touch_idx, level_price)

    event_ts = bars.index[bar_idx]
    return LevelCandidate(
        level=ratio,
        price=level_price,
        auto_candidate=kind,
        event_bar=event_ts.isoformat(),
        note="Auto heuristic — confirm or override human_label",
    )


def annotate_leg_levels(
    candles: pd.DataFrame,
    leg: LegLabel,
    ratios: tuple[str, ...] = DEFAULT_LEVELS,
) -> dict[str, LevelCandidate]:
    prices = derive_level_prices(leg, ratios)
    return {ratio: classify_level(candles, leg, ratio, prices[ratio]) for ratio in ratios}
