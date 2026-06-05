"""Bounded Human Review v1 for Fibonacci level event candidates (research-only).

Issue #8 / PR #9 added a research-only Fibonacci *level event* detector
(:mod:`fibengine.research.level_events`). It emits, per fib level, a stream of
touch events classified as ``continuation`` / ``rejection`` / ``reaction`` /
``failure`` *candidates*. Those candidates are **never facts** — they need human
validation.

This module turns the detector output into a small, **mobile-friendly review
package** so a reviewer (possibly on an iPhone) can visually confirm whether each
auto-detected event matches what they see on the chart, without running
TradingView manually for each event. For a sampled set of candidates it writes:

    experiments/review/fib_level_events/<run_id>/
        review_sample.csv      # one row per sampled candidate (+ blank human_* cols)
        review_sample.jsonl    # same rows, one JSON object per line
        REVIEW_INDEX.md        # instructions + per-event chart links to fill in
        charts/<review_id>.png # one chart per sampled event

Strictly research-only. It imports the detector but never mutates it, and it
does NOT touch swing selection, fib prices, evaluation, recall, promotion, the
canonical ``Settings`` or ``config_hash``. The forward look-ahead the detector
uses means this is *post-hoc annotation*, never a live trading signal.

Run:
    uv run python -m fibengine.research.human_review_level_events --max-events 40 --seed 7
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-säkert (samma mönster som viz/plot.py)
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from fibengine.backtest.stability import walk_forward_selection  # noqa: E402
from fibengine.core.config import REPO_ROOT, Settings, load_settings  # noqa: E402
from fibengine.core.fib import fib_levels  # noqa: E402
from fibengine.core.models import Swing  # noqa: E402
from fibengine.core.scoring import select_swing  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.labeling.human_fib import classify_candle  # noqa: E402
from fibengine.research.level_events import (  # noqa: E402
    LevelEventConfig,
    _unique_confirmed_legs,
    detect_level_events,
)

REVIEW_ROOT = REPO_ROOT / "experiments" / "review" / "fib_level_events"

# Human annotation-scheman (post-hoc; ej trading, ej promotion).
HUMAN_LABELS = ["agree", "wrong_type", "missed_context", "noise", "unclear"]
HUMAN_CONFIDENCE = ["high", "medium", "low"]
CANDIDATE_TYPES = [
    "continuation_candidate",
    "rejection_candidate",
    "reaction_candidate",
    "failure_candidate",
]

_LABEL_HELP = {
    "agree": "The auto_candidate type matches what the chart shows.",
    "wrong_type": "There is an event here, but it is a different candidate type.",
    "missed_context": "Technically a touch, but context (trend/structure) makes it misleading.",
    "noise": "Not a meaningful interaction with the level — noise.",
    "unclear": "Cannot tell from the chart / ambiguous.",
}

_CANDIDATE_SHORT = {
    "continuation_candidate": "cont",
    "rejection_candidate": "rej",
    "reaction_candidate": "react",
    "failure_candidate": "fail",
}

# Stabil kolumnordning för CSV/JSONL och REVIEW_INDEX.
REVIEW_COLUMNS = [
    "review_id",
    "symbol",
    "timeframe",
    "exchange",
    "fib_source",
    "fib_id",
    "fib_level",
    "fib_price",
    "fib_levels",
    "event_bar",
    "event_time",
    "relation",
    "auto_candidate",
    "touch_type",
    "approach_side",
    "note",
    "evidence_forward_bars",
    "evidence_closes_beyond",
    "evidence_closes_back",
    "evidence_max_penetration_atr",
    "swing_start_time",
    "swing_end_time",
    "swing_direction",
    "swing_start_bar",
    "swing_end_bar",
    "anchor_a_time",
    "anchor_a_price",
    "anchor_a_bar",
    "anchor_b_time",
    "anchor_b_price",
    "anchor_b_bar",
    "chart_path",
    "human_label",
    "human_confidence",
    "human_note",
]


class HumanReviewConfig(BaseModel):
    """Research-only config för review-paketet. Medvetet INTE en del av canonical
    ``Settings`` — det skulle lägga forskningsfunktionen på Promotion-ytan och
    ändra ``Settings.config_hash()``. Styr enbart urval och chart-rendering."""

    max_events: int = Field(default=40, ge=1)
    max_per_candidate: int | None = Field(default=None, ge=1)
    max_per_level: int | None = Field(default=None, ge=1)
    candidate_types: list[str] = Field(default_factory=list)  # tom → alla typer
    levels: list[str] = Field(default_factory=list)  # tom → alla nivåer (fib-ratio-strängar)
    seed: int | None = Field(default=None)
    context_before: int = Field(default=25, ge=1)  # barer före event i charten
    context_after: int = Field(default=25, ge=1)  # barer efter event i charten
    candlestick: bool = Field(default=True)  # True → candlesticks; False → close-line-fallback


def make_review_id(
    symbol: str,
    timeframe: str,
    level: str,
    swing_start_bar: int,
    swing_end_bar: int,
    event_bar: int,
    candidate: str,
) -> str:
    """Deterministiskt, filsystemssäkert id. Unikt per (leg, nivå, bar).

    Legen identifieras av BÅDE start- och end-bar: walk-forward kan låsa två skilda
    bekräftade legs som delar samma end-pivot men har olika start (``_unique_confirmed_legs``
    nycklar på start+end+riktning). Utan start-baren skulle de kollidera → överskriven
    chart-PNG och dubbletter av ``review_id`` i CSV/JSONL."""
    sym = symbol.replace("/", "-").replace(":", "-")
    tf = timeframe.replace("/", "-")
    lvl = level.replace(".", "p").replace("/", "-")
    short = _CANDIDATE_SHORT.get(candidate, candidate.replace("_candidate", ""))
    return f"{sym}_{tf}_L{lvl}_s{swing_start_bar}_e{swing_end_bar}_b{event_bar}_{short}"


def _bar_index(df: pd.DataFrame, time_str: str) -> int:
    """Nearest candle index for a saved ISO timestamp."""
    ts = pd.to_datetime(time_str, utc=True)
    return int(df.index.get_indexer([ts], method="nearest")[0])


def _relation_for_bar(df: pd.DataFrame, bar_idx: int, price: float) -> str:
    bar = df.iloc[int(bar_idx)]
    return classify_candle(
        float(bar["open"]),
        float(bar["high"]),
        float(bar["low"]),
        float(bar["close"]),
        float(price),
    )


def _level_rows_from_swing(swing: Swing, ratios: list[float]) -> list[dict]:
    prices = fib_levels(swing, ratios)
    return [
        {"ratio": f"{ratio:g}", "price": round(float(prices[ratio]), 6)} for ratio in sorted(prices)
    ]


def _level_rows_from_payload(payload: dict) -> list[dict]:
    levels = []
    for lvl in payload.get("levels", []):
        ratio = lvl.get("level", lvl.get("ratio"))
        if ratio is None:
            continue
        levels.append({"ratio": f"{float(ratio):g}", "price": round(float(lvl["price"]), 6)})
    return levels


def _encode_levels(levels: list[dict]) -> str:
    return json.dumps(levels, sort_keys=True, separators=(",", ":"))


def _decode_levels(row: dict) -> list[dict]:
    raw = row.get("fib_levels")
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
    return [{"ratio": str(row["fib_level"]), "price": float(row["fib_price"])}]


def _anchor_fields_from_swing(swing: Swing) -> dict:
    return {
        "anchor_a_time": swing.start.timestamp.isoformat(),
        "anchor_a_price": round(float(swing.start.price), 6),
        "anchor_a_bar": int(swing.start.index),
        "anchor_b_time": swing.end.timestamp.isoformat(),
        "anchor_b_price": round(float(swing.end.price), 6),
        "anchor_b_bar": int(swing.end.index),
    }


def _anchor_fields_from_payload(df: pd.DataFrame, payload: dict) -> dict:
    a = payload["anchor_a"]
    b = payload["anchor_b"]
    return {
        "anchor_a_time": a["time"],
        "anchor_a_price": round(float(a["price"]), 6),
        "anchor_a_bar": _bar_index(df, a["time"]),
        "anchor_b_time": b["time"],
        "anchor_b_price": round(float(b["price"]), 6),
        "anchor_b_bar": _bar_index(df, b["time"]),
    }


def _row_for_event(
    df: pd.DataFrame,
    swing: Swing,
    meta: dict,
    level: str,
    price: float,
    ev,
    all_levels: list[dict] | None = None,
) -> dict:
    """Bygg en review-rad genom att slå ihop event + swing- + symbol-kontext."""
    review_id = make_review_id(
        meta["symbol"],
        meta["timeframe"],
        level,
        swing.start.index,
        swing.end.index,
        ev.bar_index,
        ev.auto_candidate,
    )
    levels = all_levels or [{"ratio": level, "price": round(float(price), 6)}]
    return {
        "review_id": review_id,
        "symbol": meta["symbol"],
        "timeframe": meta["timeframe"],
        "exchange": meta["exchange"],
        "fib_source": meta.get("fib_source", "machine_swing"),
        "fib_id": meta.get("fib_id", ""),
        "fib_level": level,
        "fib_price": round(float(price), 6),
        "fib_levels": _encode_levels(levels),
        "event_bar": int(ev.bar_index),
        "event_time": ev.event_bar,
        "relation": _relation_for_bar(df, ev.bar_index, price),
        "auto_candidate": ev.auto_candidate,
        "touch_type": ev.touch_type,
        "approach_side": ev.approach_side,
        "note": ev.note,
        "evidence_forward_bars": ev.evidence.get("forward_bars"),
        "evidence_closes_beyond": ev.evidence.get("closes_beyond"),
        "evidence_closes_back": ev.evidence.get("closes_back"),
        "evidence_max_penetration_atr": ev.evidence.get("max_penetration_atr"),
        "swing_start_time": swing.start.timestamp.isoformat(),
        "swing_end_time": swing.end.timestamp.isoformat(),
        "swing_direction": swing.direction,
        "swing_start_bar": int(swing.start.index),
        "swing_end_bar": int(swing.end.index),
        **_anchor_fields_from_swing(swing),
        "chart_path": f"charts/{review_id}.png",
        # Tomma platshållare som människan fyller i (aldrig auto-ifyllt).
        "human_label": "",
        "human_confidence": "",
        "human_note": "",
    }


def _legs_for_mode(df: pd.DataFrame, settings: Settings, mode: str) -> list[tuple[int, Swing]]:
    """Returnera (t, swing)-legs. single: en nu-vald leg. walk-forward: alla
    bekräftade legs (kausalt valda av befintlig walk-forward-maskin)."""
    if mode == "single":
        swing = select_swing(df, settings.pivots, settings.scoring)
        return [] if swing is None else [(int(swing.end.index), swing)]
    bt = settings.backtest
    records = walk_forward_selection(df, settings, bt.warmup_bars, bt.step)
    return _unique_confirmed_legs(records)


def collect_candidates(
    df: pd.DataFrame,
    settings: Settings,
    level_cfg: LevelEventConfig | None = None,
    mode: str = "walk-forward",
    dedupe: bool = False,
) -> list[dict]:
    """Kör detektorn och platta ut varje event till en review-rad.

    ``dedupe`` (endast walk-forward): icke-överlappande attribution där varje bar
    tillskrivs exakt EN leg — samma ``[lo, hi)``-fönster som detektorns egen
    ``_aggregate_leg_events``. Annars räknar varje leg events från sitt slut framåt.
    """
    level_cfg = level_cfg or LevelEventConfig()
    ratios = level_cfg.levels or settings.fib.levels
    meta = {
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "exchange": settings.data.exchange,
    }
    legs = _legs_for_mode(df, settings, mode)
    n = len(df)
    rows: list[dict] = []
    for i, (t, swing) in enumerate(legs):
        if dedupe and mode != "single":
            lo = t
            hi = legs[i + 1][0] if i + 1 < len(legs) else n
        else:
            lo = swing.end.index
            hi = n
        streams = detect_level_events(df, swing, level_cfg, ratios, settings.pivots.atr_period)
        level_rows = _level_rows_from_swing(swing, ratios)
        for stream in streams:
            for ev in stream.events:
                if lo <= ev.bar_index < hi:
                    rows.append(
                        _row_for_event(df, swing, meta, stream.level, stream.price, ev, level_rows)
                    )
    return rows


def _rows_from_human_fib_events_payload(df: pd.DataFrame, payload: dict) -> list[dict]:
    """Flatten a saved ``<fib_id>_events.json`` payload into review rows."""
    levels = _level_rows_from_payload(payload)
    anchors = _anchor_fields_from_payload(df, payload)
    rows: list[dict] = []
    for stream in payload.get("levels", []):
        level = str(stream["level"])
        price = float(stream["price"])
        for ev in stream.get("events", []):
            event_bar = int(ev["bar_index"])
            review_id = make_review_id(
                payload["symbol"],
                payload["timeframe"],
                level,
                int(anchors["anchor_a_bar"]),
                int(anchors["anchor_b_bar"]),
                event_bar,
                ev["auto_candidate"],
            )
            evidence = ev.get("evidence", {})
            rows.append(
                {
                    "review_id": review_id,
                    "symbol": payload["symbol"],
                    "timeframe": payload["timeframe"],
                    "exchange": payload.get("exchange", "bitfinex"),
                    "fib_source": payload.get("source", "human_fib_events"),
                    "fib_id": payload["fib_id"],
                    "fib_level": level,
                    "fib_price": round(price, 6),
                    "fib_levels": _encode_levels(levels),
                    "event_bar": event_bar,
                    "event_time": ev["event_bar"],
                    "relation": _relation_for_bar(df, event_bar, price),
                    "auto_candidate": ev["auto_candidate"],
                    "touch_type": ev["touch_type"],
                    "approach_side": ev["approach_side"],
                    "note": ev.get("note", ""),
                    "evidence_forward_bars": evidence.get("forward_bars"),
                    "evidence_closes_beyond": evidence.get("closes_beyond"),
                    "evidence_closes_back": evidence.get("closes_back"),
                    "evidence_max_penetration_atr": evidence.get("max_penetration_atr"),
                    "swing_start_time": anchors["anchor_a_time"],
                    "swing_end_time": anchors["anchor_b_time"],
                    "swing_direction": payload["direction"],
                    "swing_start_bar": int(anchors["anchor_a_bar"]),
                    "swing_end_bar": int(anchors["anchor_b_bar"]),
                    **anchors,
                    "chart_path": f"charts/{review_id}.png",
                    "human_label": "",
                    "human_confidence": "",
                    "human_note": "",
                }
            )
    return rows


def collect_human_fib_event_candidates(
    event_paths: list[Path], settings: Settings | None = None
) -> list[dict]:
    """Load saved human-fib event JSON files and build review rows from them."""
    settings = settings or load_settings()
    rows: list[dict] = []
    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    for event_path in event_paths:
        payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
        key = (
            payload.get("exchange", settings.data.exchange),
            payload["symbol"],
            payload["timeframe"],
        )
        if key not in df_cache:
            data_cfg = settings.data.model_copy(
                update={"exchange": key[0], "symbol": key[1], "timeframe": key[2]}
            )
            df_cache[key] = load_candles(data_cfg, fetch_if_missing=False)
        rows.extend(_rows_from_human_fib_events_payload(df_cache[key], payload))
    return rows


def sample_candidates(rows: list[dict], cfg: HumanReviewConfig) -> list[dict]:
    """Deterministiskt balanserat urval.

    Round-robin över candidate-typer och, inom varje typ, över fib-nivåer.
    Respekterar ``max_events``, ``max_per_candidate`` och ``max_per_level``. Med
    samma ``seed`` ger samma rader (identisk uppsättning ``review_id``)."""
    rng = random.Random(cfg.seed)
    pool = [
        r
        for r in rows
        if (not cfg.candidate_types or r["auto_candidate"] in cfg.candidate_types)
        and (not cfg.levels or r["fib_level"] in cfg.levels)
    ]
    if not pool:
        return []
    # Gruppindela; sortera först för determinism före shuffla.
    by_type: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in sorted(pool, key=lambda x: x["review_id"]):
        by_type[r["auto_candidate"]][r["fib_level"]].append(r)
    for type_buckets in by_type.values():
        for bucket in type_buckets.values():
            rng.shuffle(bucket)

    types = [t for t in CANDIDATE_TYPES if t in by_type]
    types += [t for t in sorted(by_type) if t not in CANDIDATE_TYPES]
    level_rotation = {t: deque(sorted(by_type[t].keys())) for t in types}

    selected: list[dict] = []
    per_type: Counter = Counter()
    per_level: Counter = Counter()
    progress = True
    while len(selected) < cfg.max_events and progress:
        progress = False
        for t in types:
            if len(selected) >= cfg.max_events:
                break
            if cfg.max_per_candidate and per_type[t] >= cfg.max_per_candidate:
                continue
            levels_dq = level_rotation[t]
            for _ in range(len(levels_dq)):
                lvl = levels_dq[0]
                levels_dq.rotate(-1)
                bucket = by_type[t].get(lvl)
                if not bucket:
                    continue
                if cfg.max_per_level and per_level[lvl] >= cfg.max_per_level:
                    continue
                selected.append(bucket.pop())
                per_type[t] += 1
                per_level[lvl] += 1
                progress = True
                break
    selected.sort(key=lambda x: x["review_id"])
    return selected


def _draw_candles(ax, sub: pd.DataFrame, lo: int) -> None:
    """Lättviktiga candlesticks med matplotlib-primitiv (inga extra beroenden).

    High-low ritas som tunn wick, open-close som tjockare body. Dojis (open==close)
    får en tunn horisontell markering så baren inte försvinner."""
    for offset, (_, bar) in enumerate(sub.iterrows()):
        x = lo + offset
        o, h, low, c = bar["open"], bar["high"], bar["low"], bar["close"]
        up = c >= o
        color = "#26a69a" if up else "#ef5350"  # grön / röd
        ax.vlines(x, low, h, color=color, lw=0.8, zorder=2)  # wick (high-low)
        body_lo, body_hi = min(o, c), max(o, c)
        if body_hi - body_lo < 1e-9:
            ax.hlines(c, x - 0.3, x + 0.3, color=color, lw=1.4, zorder=3)  # doji
        else:
            ax.vlines(x, body_lo, body_hi, color=color, lw=3.2, zorder=3)  # body (open-close)


def _mark_swing_point(ax, df, bar_idx, lo, hi, *, marker, color, label, price=None) -> None:
    """Markera en swing-/anchor-punkt. Ligger den i fönstret ritas den vid sitt pris;
    annars ritas en kant-annotering med pil som pekar mot punkten utanför vyn."""
    y = float(price) if price is not None else float(df["close"].iloc[bar_idx])
    if lo <= bar_idx <= hi:
        ax.scatter(
            [bar_idx],
            [y],
            color=color,
            marker=marker,
            s=130,
            edgecolors="black",
            linewidths=0.6,
            zorder=7,
            label=label,
        )
        ax.annotate(
            label,
            xy=(bar_idx, y),
            xytext=(6, 8),
            textcoords="offset points",
            fontsize=7,
            color=color,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": color, "alpha": 0.78},
            zorder=9,
        )
        return
    # Utanför vyn: annotera vid närmaste kant.
    edge_x = lo if bar_idx < lo else hi
    arrow = "◀" if bar_idx < lo else "▶"
    ax.annotate(
        f"{arrow} {label} (bar {bar_idx})",
        xy=(edge_x, df["close"].iloc[edge_x]),
        xytext=(0.02 if bar_idx < lo else 0.98, 0.02),
        textcoords="axes fraction",
        ha="left" if bar_idx < lo else "right",
        va="bottom",
        fontsize=7,
        color=color,
        fontweight="bold",
    )


def _price_label(value: float) -> str:
    return f"{float(value):,.2f}"


def _anchor_points(row: dict) -> list[dict]:
    a = {
        "bar": int(row.get("anchor_a_bar", row["swing_start_bar"])),
        "time": row.get("anchor_a_time", row["swing_start_time"]),
        "price": float(row.get("anchor_a_price", row.get("fib_price"))),
    }
    b = {
        "bar": int(row.get("anchor_b_bar", row["swing_end_bar"])),
        "time": row.get("anchor_b_time", row["swing_end_time"]),
        "price": float(row.get("anchor_b_price", row.get("fib_price"))),
    }
    if row.get("swing_direction") == "down":
        h_anchor, l_anchor = a, b
    else:
        h_anchor, l_anchor = b, a
    tf = row["timeframe"]
    return [
        {
            **h_anchor,
            "label": f"H anchor {tf} @ {_price_label(h_anchor['price'])}",
            "marker": "^",
        },
        {
            **l_anchor,
            "label": f"L anchor {tf} @ {_price_label(l_anchor['price'])}",
            "marker": "v",
        },
    ]


def _draw_anchor_labels(ax, df: pd.DataFrame, row: dict, lo: int, hi: int, *, color: str) -> None:
    for anchor in _anchor_points(row):
        _mark_swing_point(
            ax,
            df,
            anchor["bar"],
            lo,
            hi,
            marker=anchor["marker"],
            color=color,
            label=anchor["label"],
            price=anchor["price"],
        )


def _draw_fib_levels(ax, row: dict, hi: int) -> None:
    fib_id = row.get("fib_id") or ""
    active = str(row["fib_level"])
    for lvl in _decode_levels(row):
        ratio = str(lvl["ratio"])
        price = float(lvl["price"])
        is_active = ratio == active
        color = "tab:blue" if is_active else "#6f8fbf"
        ax.axhline(
            price,
            color=color,
            ls="--",
            lw=1.35 if is_active else 0.75,
            alpha=0.95 if is_active else 0.45,
            zorder=4 if is_active else 2,
            label=f"fib {ratio} @ {price:g}" if is_active else None,
        )
        suffix = f" - {fib_id}" if fib_id else ""
        ax.text(
            hi,
            price,
            f" {ratio} - {_price_label(price)}{suffix}",
            color=color,
            va="center",
            fontsize=7,
            zorder=6,
        )


def _draw_event_label(ax, row: dict) -> None:
    eb = int(row["event_bar"])
    price = float(row["fib_price"])
    relation = row.get("relation") or row.get("touch_type") or "event"
    label = f"{row['fib_level']} {relation} -> {row['auto_candidate']}"
    ax.annotate(
        label,
        xy=(eb, price),
        xytext=(8, 16),
        textcoords="offset points",
        fontsize=8,
        color="tab:orange",
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "tab:orange", "alpha": 0.82},
        arrowprops={"arrowstyle": "->", "color": "tab:orange", "lw": 0.8},
        zorder=10,
    )


def render_chart(df: pd.DataFrame, row: dict, out_path: Path, cfg: HumanReviewConfig) -> Path:
    """Rendera en mobilvänlig PNG för ett event (candlesticks default, close-line-fallback).

    Visar ±N barer runt event-baren, fib-nivån, en tydligt markerad event-bar samt
    swing start/end (markör i vyn, annars kant-annotering)."""
    eb = row["event_bar"]
    lo = max(0, eb - cfg.context_before)
    hi = min(len(df) - 1, eb + cfg.context_after)
    sub = df.iloc[lo : hi + 1]
    x = list(range(lo, hi + 1))

    fig, ax = plt.subplots(figsize=(7, 5))
    if cfg.candlestick:
        _draw_candles(ax, sub, lo)
    else:
        ax.plot(x, sub["close"].to_numpy(), color="black", lw=1.0, label="close")

    # Fib-nivåer från samma human/machine fib-kontext. Aktiv event-nivå markeras tydligast.
    _draw_fib_levels(ax, row, hi)

    # Event-baren tydligt markerad: highlight-band, wick i accentfärg + stor stjärna.
    ax.axvspan(eb - 0.5, eb + 0.5, color="tab:orange", alpha=0.18, zorder=1)
    ax.axvline(eb, color="tab:orange", lw=1.2, alpha=0.9, zorder=4)
    ax.vlines(eb, df["low"].iloc[eb], df["high"].iloc[eb], color="tab:orange", lw=1.4, zorder=5)
    ax.scatter(
        [eb],
        [df["close"].iloc[eb]],
        color="tab:orange",
        marker="*",
        s=240,
        edgecolors="black",
        linewidths=0.7,
        zorder=8,
        label=f"event bar ({row.get('relation') or row['touch_type']})",
    )
    _draw_event_label(ax, row)

    # Human-aware H/L anchors (or machine-swing anchors for legacy review rows).
    _draw_anchor_labels(ax, df, row, lo, hi, color="tab:purple")

    span = f"±{max(cfg.context_before, cfg.context_after)} bars"
    source = row.get("fib_id") or row.get("fib_source", "fib")
    ax.set_title(
        f"{row['symbol']} {row['timeframe']} | {source} | fib {row['fib_level']} | "
        f"{row.get('relation') or row['touch_type']} -> {row['auto_candidate']} | {span}\n"
        f"{row['event_time']}",
        fontsize=9,
    )
    ax.set_xlabel("bar index")
    ax.legend(loc="best", fontsize=7)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_review_sheets(rows: list[dict], out_dir: Path) -> tuple[Path, Path]:
    """Skriv review_sample.csv och review_sample.jsonl med stabil kolumnordning."""
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "review_sample.csv"
    jsonl_path = out_dir / "review_sample.jsonl"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in REVIEW_COLUMNS})
    with jsonl_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({k: r.get(k) for k in REVIEW_COLUMNS}, sort_keys=True) + "\n")
    return csv_path, jsonl_path


def _summary(total_available: int, sampled: list[dict], out_dir: Path) -> dict:
    by_candidate = Counter(r["auto_candidate"] for r in sampled)
    by_level = Counter(r["fib_level"] for r in sampled)
    return {
        "total_candidates_available": total_available,
        "total_sampled": len(sampled),
        "sampled_by_candidate": dict(sorted(by_candidate.items())),
        "sampled_by_fib_level": dict(sorted(by_level.items())),
        "output_dir": str(out_dir),
    }


def write_index(rows: list[dict], summary: dict, out_dir: Path) -> Path:
    """Skriv REVIEW_INDEX.md med instruktioner, summering och en bild per event."""
    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / "REVIEW_INDEX.md"
    lines: list[str] = []
    lines.append("# Fibonacci Level Event — Human Review")
    lines.append("")
    lines.append("> **Research-only.** These are auto-detected *candidates*, **not facts** and ")
    lines.append("> **not trading signals**. The detector inspects a forward window after each ")
    lines.append("> touch, so every label is **post-hoc annotation**, never a live signal. Your ")
    lines.append("> job is only to judge whether each auto label matches the chart.")
    lines.append("")
    lines.append("## How to review (mobile-friendly)")
    lines.append("")
    lines.append("For each event below, look at the chart, then fill in three columns in ")
    lines.append("`review_sample.csv` (or `review_sample.jsonl`) for the matching `review_id`:")
    lines.append("")
    lines.append("- **human_label** — one of: " + ", ".join(f"`{x}`" for x in HUMAN_LABELS))
    lines.append(
        "- **human_confidence** — one of: " + ", ".join(f"`{x}`" for x in HUMAN_CONFIDENCE)
    )
    lines.append("- **human_note** — free text (optional)")
    lines.append("")
    lines.append("### What each human_label means")
    lines.append("")
    for lbl in HUMAN_LABELS:
        lines.append(f"- `{lbl}` — {_LABEL_HELP[lbl]}")
    lines.append("")
    lines.append("### How to read the chart")
    lines.append("")
    lines.append("- **Blue dashed lines** = calculated fib levels from the same saved fib context.")
    lines.append("- **Orange marker / vertical line** = the event bar being judged.")
    lines.append("- **Purple H/L anchor labels** = the high/low anchors, with timeframe and price.")
    lines.append(
        "- Event labels keep raw relation and candidate separate: `relation -> candidate`."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total candidates available: **{summary['total_candidates_available']}**")
    lines.append(f"- Total sampled: **{summary['total_sampled']}**")
    lines.append(f"- Sampled by candidate type: `{summary['sampled_by_candidate']}`")
    lines.append(f"- Sampled by fib level: `{summary['sampled_by_fib_level']}`")
    lines.append(f"- Output dir: `{summary['output_dir']}`")
    lines.append("")
    lines.append("## Events")
    lines.append("")
    for r in rows:
        lines.append(f"### `{r['review_id']}`")
        lines.append("")
        lines.append(f"![{r['review_id']}]({r['chart_path']})")
        lines.append("")
        lines.append(
            f"- {r['symbol']} {r['timeframe']} ({r['exchange']}) | fib **{r['fib_level']}** "
            f"@ {r['fib_price']} | fib_id: `{r.get('fib_id') or r.get('fib_source', '')}`"
        )
        lines.append(
            f"- relation: **{r.get('relation', '')}** | "
            f"auto_candidate: **{r['auto_candidate']}** | "
            f"touch_type: {r['touch_type']} | "
            f"approach_side: {r['approach_side']}"
        )
        lines.append(f"- event_time: {r['event_time']} (bar {r['event_bar']})")
        lines.append(
            f"- evidence: forward_bars={r['evidence_forward_bars']}, "
            f"closes_beyond={r['evidence_closes_beyond']}, "
            f"closes_back={r['evidence_closes_back']}, "
            f"max_penetration_atr={r['evidence_max_penetration_atr']}"
        )
        lines.append(
            f"- anchors: H/L shown on chart | direction {r['swing_direction']} | "
            f"anchor_a {r.get('anchor_a_time', r['swing_start_time'])} "
            f"-> anchor_b {r.get('anchor_b_time', r['swing_end_time'])}"
        )
        lines.append("- **human_label:** ____  **human_confidence:** ____  **human_note:** ____")
        lines.append("")
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def run_human_review(
    settings: Settings | None = None,
    cfg: HumanReviewConfig | None = None,
    level_cfg: LevelEventConfig | None = None,
    mode: str = "walk-forward",
    dedupe: bool = False,
) -> dict:
    """Generera ett komplett review-paket och returnera en summering + sökvägar."""
    settings = settings or load_settings()
    cfg = cfg or HumanReviewConfig()
    df = load_candles(settings.data)
    candidates = collect_candidates(df, settings, level_cfg, mode=mode, dedupe=dedupe)
    sampled = sample_candidates(candidates, cfg)

    run_id = datetime.now(UTC).strftime("review_%Y%m%dT%H%M%SZ")
    run_dir = REVIEW_ROOT / run_id
    charts_dir = run_dir / "charts"
    for r in sampled:
        render_chart(df, r, charts_dir / f"{r['review_id']}.png", cfg)
    write_review_sheets(sampled, run_dir)
    summary = _summary(len(candidates), sampled, run_dir)
    write_index(sampled, summary, run_dir)

    return {"run_id": run_id, "run_dir": str(run_dir), "mode": mode, "dedupe": dedupe, **summary}


def run_human_fib_review(
    event_paths: list[Path],
    settings: Settings | None = None,
    cfg: HumanReviewConfig | None = None,
) -> dict:
    """Generate a review package from saved human-fib event JSON files."""
    settings = settings or load_settings()
    cfg = cfg or HumanReviewConfig()
    candidates = collect_human_fib_event_candidates(event_paths, settings)
    sampled = sample_candidates(candidates, cfg)

    run_id = datetime.now(UTC).strftime("human_fib_review_%Y%m%dT%H%M%SZ")
    run_dir = REVIEW_ROOT / run_id
    charts_dir = run_dir / "charts"
    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    for r in sampled:
        key = (r.get("exchange", settings.data.exchange), r["symbol"], r["timeframe"])
        if key not in df_cache:
            data_cfg = settings.data.model_copy(
                update={"exchange": key[0], "symbol": key[1], "timeframe": key[2]}
            )
            df_cache[key] = load_candles(data_cfg, fetch_if_missing=False)
        render_chart(df_cache[key], r, charts_dir / f"{r['review_id']}.png", cfg)
    write_review_sheets(sampled, run_dir)
    summary = _summary(len(candidates), sampled, run_dir)
    write_index(sampled, summary, run_dir)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "mode": "human-fib-events",
        "event_files": [str(p) for p in event_paths],
        **summary,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a mobile-friendly human-review package for Fibonacci level "
        "event candidates (research-only)."
    )
    p.add_argument("--mode", choices=["single", "walk-forward"], default="walk-forward")
    p.add_argument(
        "--dedupe",
        action="store_true",
        help="Walk-forward: non-overlapping attribution (each bar counted under one leg).",
    )
    p.add_argument("--max-events", type=int, default=40, help="Max sampled events total.")
    p.add_argument("--max-per-candidate", type=int, default=None)
    p.add_argument("--max-per-level", type=int, default=None)
    p.add_argument(
        "--candidate-type",
        action="append",
        default=[],
        dest="candidate_types",
        help="Filter to these candidate types (repeatable).",
    )
    p.add_argument(
        "--level",
        action="append",
        default=[],
        dest="levels",
        help="Filter to these fib levels, e.g. 0.5 (repeatable).",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible sampling.")
    p.add_argument(
        "--exchange",
        default=None,
        help="Override settings.data.exchange (default: config/settings.yaml).",
    )
    p.add_argument(
        "--symbol",
        default=None,
        help="Override settings.data.symbol, e.g. BTC/USD.",
    )
    p.add_argument(
        "--timeframe",
        default=None,
        help="Override settings.data.timeframe, e.g. 1d.",
    )
    p.add_argument(
        "--line",
        action="store_true",
        help="Use a close-line instead of candlesticks (lighter). Candlesticks are default.",
    )
    p.add_argument(
        "--context",
        type=int,
        default=None,
        help="Show ±N bars around the event (sets both --context-before and --context-after).",
    )
    p.add_argument("--context-before", type=int, default=25)
    p.add_argument("--context-after", type=int, default=25)
    p.add_argument(
        "--human-fib-events",
        action="append",
        type=Path,
        default=[],
        help="Review saved <fib_id>_events.json files from human_fib_events (repeatable).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    before = args.context if args.context is not None else args.context_before
    after = args.context if args.context is not None else args.context_after
    settings = load_settings()
    if args.exchange:
        settings.data.exchange = args.exchange
    if args.symbol:
        settings.data.symbol = args.symbol
    if args.timeframe:
        settings.data.timeframe = args.timeframe
    cfg = HumanReviewConfig(
        max_events=args.max_events,
        max_per_candidate=args.max_per_candidate,
        max_per_level=args.max_per_level,
        candidate_types=args.candidate_types,
        levels=args.levels,
        seed=args.seed,
        context_before=before,
        context_after=after,
        candlestick=not args.line,
    )
    if args.human_fib_events:
        result = run_human_fib_review(args.human_fib_events, settings=settings, cfg=cfg)
    else:
        result = run_human_review(settings=settings, cfg=cfg, mode=args.mode, dedupe=args.dedupe)
    print(json.dumps(result, indent=2))
