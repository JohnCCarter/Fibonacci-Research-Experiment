"""Source-fib projection review (issue #30 Phase 2).

Load one human-drawn HTF fib, project its exact level prices onto one or more
lower-TF candle caches, and write a structured review artifact:

    experiments/review/source_fib_projection/<run_id>/
        REVIEW_INDEX.md
        review_sample.csv
        review_sample.jsonl
        summary.json

Usage::

    python -m fibengine.research.source_fib_projection_review \\
        --source-fib data/labels/human_fib/bitfinex/BTC-USD/1M/<fib>.json \\
        --chart-timeframes 1w,1d,4h \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
from pathlib import Path
from typing import Any

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.human_fib import load_annotation
from fibengine.research.level_events import LevelEventConfig
from fibengine.research.mtf_fib_level_projection import detect_ltf_level_interactions

PROJECTION_ROOT = REPO_ROOT / "experiments" / "review" / "source_fib_projection"

PROJECTION_COLUMNS = [
    "event_id",
    "source_tf",
    "chart_tf",
    "fib_id",
    "symbol",
    "exchange",
    "fib_level",
    "fib_price",
    "level_role",
    "event_bar",
    "event_time",
    "relation",
    "auto_candidate",
    "touch_type",
    "approach_side",
    "event_label",
]

_VERB: dict[str, str] = {
    "touch": "touched",
    "cross": "crossed",
    "above": "held above",
    "below": "held below",
}


def _level_role(ratio_str: str) -> str:
    try:
        r = float(ratio_str)
    except ValueError:
        return "retracement"
    return "boundary" if r in (0.0, 1.0) else "retracement"


def _event_label(source_tf: str, fib_level: str, relation: str, chart_tf: str) -> str:
    verb = _VERB.get(relation, relation)
    return f"{source_tf} {fib_level} {verb} by {chart_tf} candle"


def _run_id() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_projection_sheets(rows: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path]:
    csv_path = out_dir / "review_sample.csv"
    jsonl_path = out_dir / "review_sample.jsonl"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PROJECTION_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps({k: row.get(k) for k in PROJECTION_COLUMNS}) + "\n")
    return csv_path, jsonl_path


def _write_projection_index(
    ann_meta: dict[str, Any],
    rows_by_tf: dict[str, list[dict[str, Any]]],
    out_dir: Path,
) -> Path:
    lines: list[str] = []
    fib_id = ann_meta["fib_id"]
    lines.append(f"# Source-fib projection review — {fib_id}\n")

    lines.append("## SOURCE FIB")
    lines.append(
        f"- Timeframe: {ann_meta['timeframe']} | Direction: {ann_meta['direction']}"
        f" | Symbol: {ann_meta['symbol']}"
    )
    lines.append(
        f"- Anchor A: {ann_meta['anchor_a_time']} @ {ann_meta['anchor_a_price']}  (ratio 1.0)"
    )
    lines.append(
        f"- Anchor B: {ann_meta['anchor_b_time']} @ {ann_meta['anchor_b_price']}  (ratio 0.0)"
    )
    lines.append(f"- Profile: {ann_meta['levels_profile']} | Scale: {ann_meta['scale_mode']}")
    level_ratios = " · ".join(str(lv["ratio"]) for lv in ann_meta["levels"])
    lines.append(f"- Levels: {level_ratios}")

    highlights = ann_meta.get("human_highlights", [])
    if highlights:
        lines.append("- Highlights (presentation only):")
        for h in highlights:
            note = h.get("note", "")
            lines.append(
                f"  - {h.get('kind', '')} {h.get('from', '')}–{h.get('to', '')}"
                + (f" ({note})" if note else "")
            )
    lines.append("")

    for chart_tf, tf_rows in rows_by_tf.items():
        lines.append(f"## CURRENT CHART: {chart_tf}")
        lines.append("")
        lines.append("### PROJECTED LEVELS")
        lines.append("| Ratio | Price | Role |")
        lines.append("|-------|-------|------|")
        seen: dict[str, float] = {}
        for lv in ann_meta["levels"]:
            r = str(lv["ratio"])
            seen[r] = lv["price"]
        for ratio_str, price in sorted(seen.items(), key=lambda x: float(x[0])):
            role = _level_role(ratio_str)
            lines.append(f"| {ratio_str} | {price:.2f} | {role} |")
        lines.append("")

        if tf_rows:
            lines.append(f"### Events ({len(tf_rows)} interactions)")
            for row in tf_rows:
                label = row.get("event_label", "")
                t = row.get("event_time", "")
                rel = row.get("relation", "")
                cand = row.get("auto_candidate", "")
                lines.append(f"- `{label}` — {t} | {rel} | {cand}")
        else:
            lines.append("### Events (0 interactions)")
            lines.append("No candle interactions detected for this timeframe.")
        lines.append("")

    idx_path = out_dir / "REVIEW_INDEX.md"
    idx_path.write_text("\n".join(lines), encoding="utf-8")
    return idx_path


def run_source_fib_projection_review(
    source_fib_path: Path | str,
    chart_timeframes: list[str],
    settings: Settings | None = None,
    level_cfg: LevelEventConfig | None = None,
    out_root: Path | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Project one HTF human fib onto LTF candles and write a review artifact.

    Parameters
    ----------
    source_fib_path:
        Path to a ``fib_*.json`` annotation file.
    chart_timeframes:
        LTF timeframes to project onto, e.g. ``["1w", "1d", "4h"]``.
    settings:
        Loaded ``Settings`` (supply symbol/exchange/limit defaults). Falls back to
        ``load_settings()`` if not provided.
    level_cfg:
        Controls debounce and touch-tolerance. Defaults to ``LevelEventConfig()``.
    out_root:
        Override output directory. Defaults to ``PROJECTION_ROOT / run_id``.
    seed:
        Unused — kept for API parity; projection is deterministic.
    """
    if settings is None:
        settings = load_settings()

    ann = load_annotation(source_fib_path)
    run_id = _run_id()
    out_dir = Path(out_root) if out_root else PROJECTION_ROOT / ann.fib_id
    out_dir.mkdir(parents=True, exist_ok=True)

    ann_meta: dict[str, Any] = {
        "fib_id": ann.fib_id,
        "symbol": ann.symbol,
        "timeframe": ann.timeframe,
        "exchange": ann.exchange,
        "direction": ann.direction,
        "anchor_a_time": ann.anchor_a.time,
        "anchor_a_price": ann.anchor_a.price,
        "anchor_b_time": ann.anchor_b.time,
        "anchor_b_price": ann.anchor_b.price,
        "scale_mode": ann.scale_mode,
        "levels_profile": ann.levels_profile,
        "levels": [{"ratio": lv.ratio, "price": lv.price} for lv in ann.levels],
        "human_highlights": ann.human_highlights,
    }
    levels_dicts = [{"ratio": lv.ratio, "price": lv.price} for lv in ann.levels]

    all_rows: list[dict[str, Any]] = []
    rows_by_tf: dict[str, list[dict[str, Any]]] = {}
    skipped: dict[str, str] = {}

    for chart_tf in chart_timeframes:
        data_cfg = settings.data.model_copy(
            update={"symbol": ann.symbol, "timeframe": chart_tf, "exchange": ann.exchange}
        )
        df = load_candles(data_cfg, fetch_if_missing=False)

        raw_rows, skip_reason = detect_ltf_level_interactions(
            df,
            levels_dicts,
            start_time=ann.anchor_b.time,
            fib_id=ann.fib_id,
            symbol=ann.symbol,
            timeframe=chart_tf,
            exchange=ann.exchange,
            direction=ann.direction,
            projected_from_timeframe=ann.timeframe,
            level_cfg=level_cfg,
        )

        if skip_reason:
            skipped[chart_tf] = skip_reason
            rows_by_tf[chart_tf] = []
            continue

        tf_rows: list[dict[str, Any]] = []
        for row in raw_rows:
            decorated = dict(row)
            decorated["source_tf"] = ann.timeframe
            decorated["chart_tf"] = chart_tf
            decorated["level_role"] = _level_role(str(row["fib_level"]))
            decorated["event_label"] = _event_label(
                ann.timeframe, str(row["fib_level"]), row["relation"], chart_tf
            )
            tf_rows.append(decorated)

        rows_by_tf[chart_tf] = tf_rows
        all_rows.extend(tf_rows)

    _write_projection_sheets(all_rows, out_dir)
    _write_projection_index(ann_meta, rows_by_tf, out_dir)

    interactions_by_tf = {tf: len(r) for tf, r in rows_by_tf.items()}
    summary: dict[str, Any] = {
        "run_id": run_id,
        "output_dir": str(out_dir),
        "source_fib": str(source_fib_path),
        "fib_id": ann.fib_id,
        "source_tf": ann.timeframe,
        "chart_timeframes": chart_timeframes,
        "total_interactions": len(all_rows),
        "interactions_by_tf": interactions_by_tf,
        "skipped": skipped,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Project a human HTF fib onto LTF candles and write a review artifact."
    )
    p.add_argument("--source-fib", required=True, help="Path to fib_*.json annotation")
    p.add_argument(
        "--chart-timeframes",
        default="1w,1d,4h",
        help="Comma-separated LTF timeframes (default: 1w,1d,4h)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    tfs = [t.strip() for t in args.chart_timeframes.split(",") if t.strip()]
    summary = run_source_fib_projection_review(
        source_fib_path=args.source_fib,
        chart_timeframes=tfs,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
    )
    print(f"run_id: {summary['run_id']}")
    print(f"output: {summary['output_dir']}")
    print(f"total interactions: {summary['total_interactions']}")
    for tf, n in summary["interactions_by_tf"].items():
        print(f"  {tf}: {n}")
    if summary["skipped"]:
        for tf, reason in summary["skipped"].items():
            print(f"  {tf}: SKIPPED ({reason})")
