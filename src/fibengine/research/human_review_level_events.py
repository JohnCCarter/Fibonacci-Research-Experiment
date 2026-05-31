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
from fibengine.core.models import Swing  # noqa: E402
from fibengine.core.scoring import select_swing  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
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
    "fib_level",
    "fib_price",
    "event_bar",
    "event_time",
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
    symbol: str, timeframe: str, level: str, swing_end_bar: int, event_bar: int, candidate: str
) -> str:
    """Deterministiskt, filsystemssäkert id. Unikt per (leg, nivå, bar)."""
    sym = symbol.replace("/", "-").replace(":", "-")
    tf = timeframe.replace("/", "-")
    lvl = level.replace(".", "p").replace("/", "-")
    short = _CANDIDATE_SHORT.get(candidate, candidate.replace("_candidate", ""))
    return f"{sym}_{tf}_L{lvl}_e{swing_end_bar}_b{event_bar}_{short}"


def _row_for_event(
    df: pd.DataFrame, swing: Swing, meta: dict, level: str, price: float, ev
) -> dict:
    """Bygg en review-rad genom att slå ihop event + swing- + symbol-kontext."""
    review_id = make_review_id(
        meta["symbol"], meta["timeframe"], level, swing.end.index, ev.bar_index, ev.auto_candidate
    )
    return {
        "review_id": review_id,
        "symbol": meta["symbol"],
        "timeframe": meta["timeframe"],
        "exchange": meta["exchange"],
        "fib_level": level,
        "fib_price": round(float(price), 6),
        "event_bar": int(ev.bar_index),
        "event_time": ev.event_bar,
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
        for stream in streams:
            for ev in stream.events:
                if lo <= ev.bar_index < hi:
                    rows.append(_row_for_event(df, swing, meta, stream.level, stream.price, ev))
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


def _mark_swing_point(ax, df, bar_idx, lo, hi, *, marker, color, label) -> None:
    """Markera en swing-punkt. Ligger den i fönstret ritas en markör vid dess pris;
    annars ritas en kant-annotering med pil som pekar mot punkten utanför vyn."""
    if lo <= bar_idx <= hi:
        ax.scatter(
            [bar_idx],
            [df["close"].iloc[bar_idx]],
            color=color,
            marker=marker,
            s=130,
            edgecolors="black",
            linewidths=0.6,
            zorder=7,
            label=label,
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

    # Fib-nivån, med ratio-etikett vid höger kant.
    fib_price = row["fib_price"]
    ax.axhline(
        fib_price,
        color="tab:blue",
        ls="--",
        lw=1.2,
        zorder=4,
        label=f"fib {row['fib_level']} @ {fib_price:g}",
    )
    ax.text(hi, fib_price, f" {row['fib_level']}", color="tab:blue", va="center", fontsize=8)

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
        label=f"event bar ({row['touch_type']})",
    )

    # Swing start/end (markör i vyn, annars kant-annotering).
    _mark_swing_point(
        ax, df, row["swing_start_bar"], lo, hi, marker="^", color="tab:purple", label="swing start"
    )
    _mark_swing_point(
        ax, df, row["swing_end_bar"], lo, hi, marker="v", color="tab:purple", label="swing end"
    )

    span = f"±{max(cfg.context_before, cfg.context_after)} bars"
    ax.set_title(
        f"{row['symbol']} {row['timeframe']} | fib {row['fib_level']} | "
        f"{row['auto_candidate']} | {span}\n{row['event_time']}",
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
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in REVIEW_COLUMNS})
    with jsonl_path.open("w") as f:
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
    lines.append("- **Dashed blue line** = the fib level price.")
    lines.append("- **Orange marker / vertical line** = the event bar (the touch being judged).")
    lines.append(
        "- **Purple ▲ / ▼** = swing start / end (the leg the fib is drawn from), when in view."
    )
    lines.append("- The title shows symbol, timeframe, fib level, auto_candidate and event time.")
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
            f"@ {r['fib_price']}"
        )
        lines.append(
            f"- auto_candidate: **{r['auto_candidate']}** | touch_type: {r['touch_type']} | "
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
            f"- swing: {r['swing_direction']} | start {r['swing_start_time']} "
            f"→ end {r['swing_end_time']}"
        )
        lines.append("- **human_label:** ____  **human_confidence:** ____  **human_note:** ____")
        lines.append("")
    index_path.write_text("\n".join(lines))
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
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    before = args.context if args.context is not None else args.context_before
    after = args.context if args.context is not None else args.context_after
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
    result = run_human_review(cfg=cfg, mode=args.mode, dedupe=args.dedupe)
    print(json.dumps(result, indent=2))
