"""Write human review packages (CSV, JSONL, index, charts)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from fibengine.core.config import Settings, load_settings
from fibengine.research.human_review_charts import render_chart
from fibengine.research.human_review_constants import (
    _LABEL_HELP,
    HUMAN_CONFIDENCE,
    HUMAN_LABELS,
    REVIEW_COLUMNS,
    HumanReviewConfig,
)
from fibengine.research.human_review_rows import (
    collect_candidates,
    collect_human_fib_event_candidates,
    sample_candidates,
)
from fibengine.research.level_events import LevelEventConfig


def write_review_sheets(rows: list[dict], out_dir: Path) -> tuple[Path, Path]:
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
    import fibengine.research.human_review_level_events as hr

    settings = settings or load_settings()
    cfg = cfg or HumanReviewConfig()
    df = hr.load_candles(settings.data)
    candidates = collect_candidates(df, settings, level_cfg, mode=mode, dedupe=dedupe)
    sampled = sample_candidates(candidates, cfg)

    run_id = datetime.now(UTC).strftime("review_%Y%m%dT%H%M%SZ")
    run_dir = hr.REVIEW_ROOT / run_id
    charts_dir = run_dir / "charts"
    for r in sampled:
        render_chart(df, r, charts_dir / f"{r['review_id']}.png", cfg)
    write_review_sheets(sampled, run_dir)
    summary = _summary(len(candidates), sampled, run_dir)
    write_index(sampled, summary, run_dir)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "mode": mode,
        "dedupe": dedupe,
        **summary,
    }


def run_human_fib_review(
    event_paths: list[Path],
    settings: Settings | None = None,
    cfg: HumanReviewConfig | None = None,
) -> dict:
    import fibengine.research.human_review_level_events as hr

    settings = settings or load_settings()
    cfg = cfg or HumanReviewConfig()
    candidates, _ = collect_human_fib_event_candidates(event_paths, settings)
    sampled = sample_candidates(candidates, cfg)

    run_id = datetime.now(UTC).strftime("human_fib_review_%Y%m%dT%H%M%SZ")
    run_dir = hr.REVIEW_ROOT / run_id
    charts_dir = run_dir / "charts"
    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    for r in sampled:
        key = (r.get("exchange", settings.data.exchange), r["symbol"], r["timeframe"])
        if key not in df_cache:
            data_cfg = settings.data.model_copy(
                update={"exchange": key[0], "symbol": key[1], "timeframe": key[2]}
            )
            df_cache[key] = hr.load_candles(data_cfg, fetch_if_missing=False)
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
