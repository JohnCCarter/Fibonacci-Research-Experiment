"""Row building and sampling for human Fibonacci level-event review."""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict, deque
from pathlib import Path

import pandas as pd

from fibengine.backtest.stability import walk_forward_selection
from fibengine.core.config import Settings, load_settings
from fibengine.core.fib import fib_levels
from fibengine.core.models import Swing
from fibengine.labeling.human_fib import classify_candle
from fibengine.research.human_review_constants import (
    _CANDIDATE_SHORT,
    CANDIDATE_TYPES,
    HumanReviewConfig,
)
from fibengine.research.level_events import (
    LevelEventConfig,
    _unique_confirmed_legs,
    detect_level_events,
)


def make_review_id(
    symbol: str,
    timeframe: str,
    level: str,
    swing_start_bar: int,
    swing_end_bar: int,
    event_bar: int,
    candidate: str,
) -> str:
    sym = symbol.replace("/", "-").replace(":", "-")
    tf = timeframe.replace("/", "-")
    lvl = level.replace(".", "p").replace("/", "-")
    short = _CANDIDATE_SHORT.get(candidate, candidate.replace("_candidate", ""))
    return f"{sym}_{tf}_L{lvl}_s{swing_start_bar}_e{swing_end_bar}_b{event_bar}_{short}"


def _bar_index(df: pd.DataFrame, time_str: str) -> int:
    idx = _bar_index_optional(df, time_str)
    if idx is None:
        start, end = df.index[0], df.index[-1]
        raise ValueError(
            f"Timestamp {time_str} is outside loaded candles "
            f"({start.date()} .. {end.date()}, {len(df)} bars). "
            "Fetch/refresh candles: "
            "python -m fibengine.data.fetch --symbols <SYM> --timeframes 1d --refresh "
            "(see config data.history_start and data.timeframe_limits)."
        )
    return idx


def _bar_index_optional(df: pd.DataFrame, time_str: str) -> int | None:
    ts = pd.to_datetime(time_str, utc=True)
    start, end = df.index[0], df.index[-1]
    if ts < start or ts > end:
        return None
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


def encode_levels(levels: list[dict]) -> str:
    return json.dumps(levels, sort_keys=True, separators=(",", ":"))


def decode_levels(row: dict) -> list[dict]:
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
        "fib_levels": encode_levels(levels),
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
        "human_label": "",
        "human_confidence": "",
        "human_note": "",
    }


def _legs_for_mode(df: pd.DataFrame, settings: Settings, mode: str) -> list[tuple[int, Swing]]:
    import fibengine.research.human_review_level_events as hr

    if mode == "single":
        swing = hr.select_swing(df, settings.pivots, settings.scoring)
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


def _anchor_fields_from_payload_optional(df: pd.DataFrame, payload: dict) -> dict | None:
    a = payload["anchor_a"]
    b = payload["anchor_b"]
    a_bar = _bar_index_optional(df, a["time"])
    b_bar = _bar_index_optional(df, b["time"])
    if a_bar is None or b_bar is None:
        return None
    return {
        "anchor_a_time": a["time"],
        "anchor_a_price": round(float(a["price"]), 6),
        "anchor_a_bar": a_bar,
        "anchor_b_time": b["time"],
        "anchor_b_price": round(float(b["price"]), 6),
        "anchor_b_bar": b_bar,
    }


def _rows_from_human_fib_events_payload(
    df: pd.DataFrame,
    payload: dict,
    *,
    event_path: str = "",
    skip_out_of_range: bool = False,
    load_skips: list[dict] | None = None,
) -> list[dict]:
    levels = _level_rows_from_payload(payload)
    if skip_out_of_range:
        anchors = _anchor_fields_from_payload_optional(df, payload)
        if anchors is None:
            if load_skips is not None:
                load_skips.append(
                    {
                        "event_file": event_path,
                        "fib_id": payload.get("fib_id", ""),
                        "symbol": payload.get("symbol", ""),
                        "timeframe": payload.get("timeframe", ""),
                        "reason": "anchors_outside_candle_cache",
                        "detail": (
                            f"anchor_a={payload['anchor_a']['time']} "
                            f"anchor_b={payload['anchor_b']['time']} "
                            f"cache={df.index[0].date()}..{df.index[-1].date()}"
                        ),
                    }
                )
            return []
    else:
        anchors = _anchor_fields_from_payload(df, payload)
    rows: list[dict] = []
    for stream in payload.get("levels", []):
        level = str(stream["level"])
        price = float(stream["price"])
        for ev in stream.get("events", []):
            if skip_out_of_range:
                event_bar = _bar_index_optional(df, str(ev["event_bar"]))
                if event_bar is None:
                    if load_skips is not None:
                        load_skips.append(
                            {
                                "event_file": event_path,
                                "fib_id": payload.get("fib_id", ""),
                                "symbol": payload.get("symbol", ""),
                                "timeframe": payload.get("timeframe", ""),
                                "fib_level": level,
                                "reason": "event_outside_candle_cache",
                                "detail": str(ev["event_bar"]),
                            }
                        )
                    continue
            else:
                event_bar = _bar_index(df, str(ev["event_bar"]))
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
                    "fib_levels": encode_levels(levels),
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
    event_paths: list[Path],
    settings: Settings | None = None,
    *,
    skip_out_of_range: bool = False,
) -> tuple[list[dict], list[dict]]:
    import fibengine.research.human_review_level_events as hr

    settings = settings or load_settings()
    rows: list[dict] = []
    load_skips: list[dict] = []
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
            try:
                df_cache[key] = hr.load_candles(data_cfg, fetch_if_missing=False)
            except FileNotFoundError as exc:
                if skip_out_of_range:
                    load_skips.append(
                        {
                            "event_file": str(event_path),
                            "fib_id": payload.get("fib_id", ""),
                            "symbol": payload.get("symbol", ""),
                            "timeframe": payload.get("timeframe", ""),
                            "reason": "missing_candle_cache",
                            "detail": str(exc),
                        }
                    )
                    continue
                raise
        rows.extend(
            _rows_from_human_fib_events_payload(
                df_cache[key],
                payload,
                event_path=str(event_path),
                skip_out_of_range=skip_out_of_range,
                load_skips=load_skips if skip_out_of_range else None,
            )
        )
    return rows, load_skips


def _balanced_fill(
    pool: list[dict], limit: int, cfg: HumanReviewConfig, rng: random.Random
) -> list[dict]:
    """Round-robin pick across candidate types, rotating levels within each type."""
    if limit <= 0 or not pool:
        return []
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
    while len(selected) < limit and progress:
        progress = False
        for t in types:
            if len(selected) >= limit:
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
    return selected


def sample_candidates(rows: list[dict], cfg: HumanReviewConfig) -> list[dict]:
    rng = random.Random(cfg.seed)
    pool = [
        r
        for r in rows
        if (not cfg.candidate_types or r["auto_candidate"] in cfg.candidate_types)
        and (not cfg.levels or r["fib_level"] in cfg.levels)
    ]
    if not pool:
        return []

    # All levels are sampled equally (round-robin across candidate × level). No
    # golden-zone / primary-level bias (Addendum 2): the machine treats every level the
    # same; human_highlights affect presentation only, never sampling.
    selected = _balanced_fill(pool, cfg.max_events, cfg, rng)
    selected.sort(key=lambda x: x["review_id"])
    return selected
