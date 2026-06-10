"""Auto-detect Fibonacci level interaction events (research-only — issue #8).

For a selected swing this scans the bars *after* the leg's end and emits an
**event stream per Fibonacci level**: each touch is classified as a
continuation / rejection / reaction / failure *candidate* with a timestamp and
supporting evidence. Candidates are never facts — they are meant for human
review, and this module does not feed back into swing selection, fib prices,
evaluation, recall or promotion.

NOTE on look-ahead: classification inspects a forward window of bars after the
touch, so it is strictly post-hoc annotation — never a live trading signal.

Run:
    uv run python -m fibengine.research.level_events
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pandas as pd
from pydantic import BaseModel, Field

from fibengine.backtest.stability import walk_forward_selection
from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.fib import fib_levels
from fibengine.core.models import Swing
from fibengine.core.scoring import select_swing
from fibengine.data.loader import atr, load_candles

LEVEL_EVENTS_RESULTS = REPO_ROOT / "experiments" / "results" / "level_events.jsonl"
LEVEL_EVENTS_WF_RESULTS = REPO_ROOT / "experiments" / "results" / "level_events_walkforward.jsonl"


class LevelEventConfig(BaseModel):
    """Research-only config. Medvetet INTE en del av canonical ``Settings`` —
    det skulle lägga forskningsfunktionen på Promotion-ytan och ändra
    ``Settings.config_hash()`` för alla körningar. Konstrueras med defaults eller
    skickas in vid anrop; rör inte swing-urval/fib-priser/evaluation/promotion."""

    levels: list[float] = Field(default_factory=list)  # tom → ärver fib.levels
    touch_tolerance_atr: float = Field(default=0.10, gt=0.0)  # bandhalvbredd = detta × ATR[bar]
    forward_window: int = Field(default=5, ge=1)  # barer efter en touch som klassificeringen ser
    acceptance_closes: int = Field(default=2, ge=1)  # stängningar bortom nivån → "accepterad"
    immediate_rejection_bars: int = Field(default=2, ge=1)  # fönster för snabb retur (rejection)
    debounce_bars: int = Field(default=3, ge=0)  # barer priset måste lämna bandet före ny händelse


@dataclass
class LevelEvent:
    event_bar: str  # ISO-8601 timestamp för baren där händelsen börjar
    bar_index: int
    touch_type: str  # wick_below | wick_above | close_above | close_below
    approach_side: str  # "above" | "below" — vilken sida priset kom ifrån
    auto_candidate: str  # *_candidate (aldrig facit)
    note: str
    evidence: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_bar": self.event_bar,
            "bar_index": self.bar_index,
            "touch_type": self.touch_type,
            "approach_side": self.approach_side,
            "auto_candidate": self.auto_candidate,
            "note": self.note,
            "evidence": self.evidence,
        }


@dataclass
class LevelInteractionStream:
    level: str  # fib-ratio som sträng, t.ex. "0.382"
    price: float
    events: list[LevelEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "price": round(self.price, 4),
            "events": [e.to_dict() for e in self.events],
        }


_NOTES = {
    "continuation_candidate": "Broke through level and continued",
    "rejection_candidate": "Touched level and rejected back to the approach side",
    "failure_candidate": "Accepted beyond level then reversed back across it",
    "reaction_candidate": "Reacted at level without a clear breakout or rejection",
}


def _classify(
    closes,
    b: int,
    last: int,
    price: float,
    band,
    break_side: int,
    cfg: LevelEventConfig,
) -> tuple[str, dict[str, float]]:
    """Klassificera händelsen vid bar ``b`` med hjälp av framåtfönstret b..last."""
    approach = -break_side

    def side(k: int) -> int:
        if closes[k] > price + band[k]:
            return 1
        if closes[k] < price - band[k]:
            return -1
        return 0

    beyond = sum(1 for k in range(b, last + 1) if side(k) == break_side)
    back = sum(1 for k in range(b, last + 1) if side(k) == approach)
    accepted = beyond >= cfg.acceptance_closes
    side_b = side(b)
    side_last = side(last)
    quick_back = any(
        side(k) == approach
        for k in range(b + 1, min(b + 1 + cfg.immediate_rejection_bars, last + 1))
    )
    moved_away = abs(closes[last] - price) > abs(closes[b] - price)

    if accepted:
        if side_last == approach:
            candidate = "failure_candidate"
        elif side_last == break_side:
            candidate = "continuation_candidate"
        else:
            candidate = "reaction_candidate"
    elif side_b == break_side:
        if side_last == break_side:
            candidate = "continuation_candidate"
        elif side_last == approach:
            candidate = "failure_candidate"
        else:
            candidate = "reaction_candidate"
    elif quick_back and side_last == approach and moved_away:
        candidate = "rejection_candidate"
    else:
        candidate = "reaction_candidate"

    atr_b = band[b] / cfg.touch_tolerance_atr if cfg.touch_tolerance_atr else 0.0
    max_pen = max((break_side * (closes[k] - price) for k in range(b, last + 1)), default=0.0)
    max_pen = max(max_pen, 0.0)
    evidence = {
        "forward_bars": last - b,
        "closes_beyond": beyond,
        "closes_back": back,
        "max_penetration_atr": round(max_pen / atr_b, 4) if atr_b > 0 else 0.0,
    }
    return candidate, evidence


def detect_level_events(
    df: pd.DataFrame,
    swing: Swing,
    cfg: LevelEventConfig,
    fib_ratios: list[float],
    atr_period: int = 14,
    scale_mode: str = "linear",
) -> list[LevelInteractionStream]:
    """Detektera interaktioner mellan pris och fib-nivåer som en ström per nivå."""
    ratios = cfg.levels or fib_ratios
    prices = fib_levels(swing, ratios, scale_mode=scale_mode)
    n = len(df)
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    closes = df["close"].to_numpy()
    band = (cfg.touch_tolerance_atr * atr(df, atr_period)).to_numpy()
    timestamps = df.index

    # Skanna ENBART barer efter legens slut. Endpoint-baren är själva fib-ankaret
    # (dess intrabar-touch kan ligga före pivoten), så den exkluderas.
    start_bar = swing.end.index + 1
    streams: list[LevelInteractionStream] = []

    for ratio in ratios:
        price = prices[ratio]
        stream = LevelInteractionStream(level=f"{ratio:g}", price=float(price))
        gap_count = cfg.debounce_bars  # börja "eligible" för första touchen

        for bar in range(start_bar, n):
            touched = lows[bar] - band[bar] <= price <= highs[bar] + band[bar]
            if not touched:
                gap_count += 1
                continue
            if gap_count < cfg.debounce_bars:
                gap_count = 0
                continue
            gap_count = 0

            prev = bar - 1  # föregående bar finns alltid (start_bar = end.index + 1)
            from_above = closes[prev] > price
            approach_side = "above" if from_above else "below"
            break_side = -1 if from_above else 1

            if closes[bar] >= price:
                touch_type = "wick_below" if lows[bar] < price - band[bar] else "close_above"
            else:
                touch_type = "wick_above" if highs[bar] > price + band[bar] else "close_below"

            last = min(bar + cfg.forward_window, n - 1)
            candidate, evidence = _classify(closes, bar, last, price, band, break_side, cfg)
            stream.events.append(
                LevelEvent(
                    event_bar=timestamps[bar].isoformat(),
                    bar_index=int(bar),
                    touch_type=touch_type,
                    approach_side=approach_side,
                    auto_candidate=candidate,
                    note=_NOTES[candidate],
                    evidence=evidence,
                )
            )
        streams.append(stream)

    return streams


def run_level_events(
    settings: Settings | None = None, level_cfg: LevelEventConfig | None = None
) -> dict:
    """Kör detektorn på konfig-symbolen och skriv en additiv JSONL-rad."""
    settings = settings or load_settings()
    level_cfg = level_cfg or LevelEventConfig()
    run_id = datetime.now(UTC).strftime("levelev_%Y%m%dT%H%M%SZ")
    df = load_candles(settings.data)
    swing = select_swing(df, settings.pivots, settings.scoring)
    streams: list[LevelInteractionStream] = []
    if swing is not None:
        streams = detect_level_events(
            df, swing, level_cfg, settings.fib.levels, settings.pivots.atr_period
        )

    record = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "config_hash": settings.config_hash(),
        "exchange": settings.data.exchange,
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "swing": swing.to_dict() if swing is not None else None,
        "levels": [s.to_dict() for s in streams],
        "n_events": sum(len(s.events) for s in streams),
    }
    LEVEL_EVENTS_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with LEVEL_EVENTS_RESULTS.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def _unique_confirmed_legs(records: list[dict]) -> list[tuple[int, Swing]]:
    """Plocka varje distinkt *bekräftad* leg som walk-forward låste, kausalt vald.

    Legen väljs kausalt (ingen framtid i urvalet). Dess interaktioner observeras
    sedan på barerna efter legens slut — post-hoc annotering, aldrig live-signal.
    """
    seen: set[tuple[int, int, str]] = set()
    legs: list[tuple[int, Swing]] = []
    for r in records:
        swing = r["swing"]
        if swing is None or swing.status != "confirmed":
            continue
        # Nyckel inkl. riktning — samma konvention som backtest/trade.py.
        key = (swing.start.index, swing.end.index, swing.direction)
        if key in seen:
            continue
        seen.add(key)
        legs.append((r["t"], swing))
    return legs


def walk_forward_level_events(
    df: pd.DataFrame,
    settings: Settings,
    non_overlapping: bool = False,
    level_cfg: LevelEventConfig | None = None,
) -> dict:
    """Aggregera nivå-interaktioner över alla bekräftade legs i en walk-forward.

    Detta svarar på issue #8:s forskningsfråga 4 ("hur många händelser per nivå")
    genom att följa varje leg över dess liv istället för ett enskilt nu-val.

    Attribution:
      * ``non_overlapping=False`` (default): varje leg räknar alla sina events från
        legens slut framåt. Enkelt, men överlappande legs dubbelräknar samma
        prisrörelse → absoluta totaler beror på ``step``.
      * ``non_overlapping=True``: varje bar tillskrivs exakt EN leg — den som var
        den live bekräftade selektionen då. En legs fönster är [bekräftelse-cursor
        ``t``, nästa legs ``t``). Inga events dubbelräknas.
    """
    bt = settings.backtest
    level_cfg = level_cfg or LevelEventConfig()
    records = walk_forward_selection(df, settings, bt.warmup_bars, bt.step)
    legs = _unique_confirmed_legs(records)
    return _aggregate_leg_events(df, legs, settings, non_overlapping, level_cfg)


def _aggregate_leg_events(
    df: pd.DataFrame,
    legs: list[tuple[int, Swing]],
    settings: Settings,
    non_overlapping: bool,
    level_cfg: LevelEventConfig | None = None,
) -> dict:
    """Aggregera events över en lista av (bekräftelse-cursor, leg), med valbar
    icke-överlappande attribution. Utbruten för att kunna testas deterministiskt."""
    n = len(df)
    level_cfg = level_cfg or LevelEventConfig()
    ratios = level_cfg.levels or settings.fib.levels
    agg: dict[str, Counter] = {f"{r:g}": Counter() for r in ratios}
    leg_summaries: list[dict] = []
    total_events = 0

    for i, (t, swing) in enumerate(legs):
        # Attributionsfönster [lo, hi) för denna leg.
        lo = t if non_overlapping else swing.end.index
        hi = legs[i + 1][0] if (non_overlapping and i + 1 < len(legs)) else n
        streams = detect_level_events(df, swing, level_cfg, ratios, settings.pivots.atr_period)
        leg_events = 0
        for stream in streams:
            kept = [e for e in stream.events if lo <= e.bar_index < hi]
            agg[stream.level] += Counter(e.auto_candidate for e in kept)
            leg_events += len(kept)
        total_events += leg_events
        leg_summaries.append(
            {
                "first_confirmed_t": t,
                "start_bar": swing.start.index,
                "end_bar": swing.end.index,
                "end_time": df.index[swing.end.index].isoformat(),
                "direction": swing.direction,
                "n_events": leg_events,
            }
        )

    per_level = [
        {
            "level": lvl,
            "events": sum(counts.values()),
            "by_candidate": {k.replace("_candidate", ""): v for k, v in sorted(counts.items())},
        }
        for lvl, counts in agg.items()
    ]
    n_legs = len(legs)
    return {
        "attribution": "non_overlapping" if non_overlapping else "forward",
        "n_legs": n_legs,
        "n_events": total_events,
        "events_per_leg": round(total_events / n_legs, 4) if n_legs else 0.0,
        "per_level": per_level,
        "legs": leg_summaries,
    }


def run_walk_forward_level_events(
    settings: Settings | None = None,
    non_overlapping: bool = False,
    level_cfg: LevelEventConfig | None = None,
) -> dict:
    """Kör walk-forward-aggregeringen och skriv en additiv JSONL-rad."""
    settings = settings or load_settings()
    run_id = datetime.now(UTC).strftime("levelwf_%Y%m%dT%H%M%SZ")
    df = load_candles(settings.data)
    result = walk_forward_level_events(
        df, settings, non_overlapping=non_overlapping, level_cfg=level_cfg
    )

    record = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "config_hash": settings.config_hash(),
        "exchange": settings.data.exchange,
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "warmup_bars": settings.backtest.warmup_bars,
        "step": settings.backtest.step,
        **result,
    }
    LEVEL_EVENTS_WF_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with LEVEL_EVENTS_WF_RESULTS.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detect Fibonacci level interaction events (research).")
    p.add_argument(
        "--mode",
        choices=["single", "walk-forward"],
        default="single",
        help="single: en nu-ögonblicksbild. walk-forward: aggregera över alla bekräftade legs.",
    )
    p.add_argument(
        "--dedupe",
        action="store_true",
        help="Walk-forward: icke-överlappande attribution (varje bar räknas under en leg).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.mode == "walk-forward":
        print(json.dumps(run_walk_forward_level_events(non_overlapping=args.dedupe), indent=2))
    else:
        print(json.dumps(run_level_events(), indent=2))
