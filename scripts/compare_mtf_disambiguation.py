"""MTF Disambiguation Layer: OFF vs ON research measurement (no tuning).

Run:
    uv run python scripts/compare_mtf_disambiguation.py
    uv run python scripts/compare_mtf_disambiguation.py --summary
    uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USDT --timeframe 1w
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from statistics import mean

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.compare import compare_label
from fibengine.labeling.mtf_disambiguation import (
    MTF_RESOLVED,
    MTF_UNRESOLVED,
    disambiguate_label_endpoints,
)
from fibengine.labeling.store import SwingLabel, list_labels

RESULTS_DIR = REPO_ROOT / "experiments" / "results"


def _with_mtf_flag(base: Settings, enabled: bool) -> Settings:
    labeling = base.labeling.model_copy(update={"mtf_disambiguation": enabled})
    return base.model_copy(update={"labeling": labeling})


def _classify_labels(settings: Settings, labels: list[SwingLabel]) -> list[dict]:
    rows = []
    for label in labels:
        data_cfg = settings.data.model_copy(
            update={
                "exchange": label.exchange,
                "symbol": label.symbol,
                "timeframe": label.timeframe,
            }
        )
        df = load_candles(data_cfg)
        end_off = disambiguate_label_endpoints(label, df, _with_mtf_flag(settings, False))
        end_on = disambiguate_label_endpoints(label, df, _with_mtf_flag(settings, True))
        rows.append(
            {
                "label": f"{label.exchange}_{label.symbol.replace('/', '-')}_{label.timeframe}",
                "timeframe": label.timeframe,
                "same_htf_candle": end_off.same_htf_candle,
                "has_mtf_metadata": label.same_candle_mtf_resolution is not None,
                "off_status": end_off.mtf_status,
                "on_status": end_on.mtf_status,
                "on_resolution_kind": end_on.resolution_kind,
                "on_skip": end_on.skip_evaluation,
                "on_skip_reason": end_on.skip_reason,
                "order": end_on.order,
            }
        )
    return rows


def _run_mode(settings: Settings, labels: list[SwingLabel]) -> list[dict]:
    rows = []
    for label in labels:
        row = compare_label(settings, label)
        metrics = row.get("metrics") or {}
        rows.append(
            {
                "label": row["label"],
                "error": row.get("error"),
                "mtf_status": metrics.get("mtf_status"),
                "skipped_mtf": metrics.get("skipped_mtf"),
                "same_htf_candle": metrics.get("same_htf_candle"),
                "agreement": metrics.get("agreement"),
                "mean_fib_err_frac": metrics.get("mean_fib_err_frac"),
                "fib_agree": metrics.get("fib_agree"),
                "price_agree": metrics.get("price_agree"),
                "time_agree": metrics.get("time_agree"),
                "mtf_order": metrics.get("mtf_order"),
                "mtf_resolution_kind": metrics.get("mtf_resolution_kind"),
                "out_of_window": metrics.get("out_of_window"),
            }
        )
    return rows


def _mean_optional(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    return round(mean(nums), 4) if nums else None


def _summarize(
    classification: list[dict],
    off: list[dict],
    on: list[dict],
) -> dict:
    n = len(classification)
    same_candle = [c for c in classification if c["same_htf_candle"]]
    resolved_on = [c for c in classification if c["on_status"] == MTF_RESOLVED]
    fractal_on = [c for c in classification if c.get("on_resolution_kind") == "fractal_endpoints"]
    unresolved_on = [
        c for c in classification if c["same_htf_candle"] and c["on_status"] == MTF_UNRESOLVED
    ]

    off_scored = [r for r in off if not r.get("skipped_mtf") and not r.get("out_of_window")]
    on_scored = [r for r in on if not r.get("skipped_mtf") and not r.get("out_of_window")]

    # Paired comparison where both modes produced metrics
    paired = []
    off_by = {r["label"]: r for r in off}
    on_by = {r["label"]: r for r in on}
    for label_id in off_by:
        o, n_row = off_by[label_id], on_by.get(label_id)
        if (
            o.get("skipped_mtf")
            or o.get("out_of_window")
            or n_row is None
            or n_row.get("skipped_mtf")
            or n_row.get("out_of_window")
        ):
            continue
        if o.get("mean_fib_err_frac") is None or n_row.get("mean_fib_err_frac") is None:
            continue
        paired.append(
            {
                "label": label_id,
                "fib_err_off": o["mean_fib_err_frac"],
                "fib_err_on": n_row["mean_fib_err_frac"],
                "fib_delta": round(n_row["mean_fib_err_frac"] - o["mean_fib_err_frac"], 4),
                "agreement_off": o.get("agreement"),
                "agreement_on": n_row.get("agreement"),
                "same_htf_candle": o.get("same_htf_candle"),
            }
        )

    same_candle_paired = [p for p in paired if p["same_htf_candle"]]

    return {
        "n_human_labels": n,
        "n_same_htf_candle": len(same_candle),
        "same_htf_candle_labels": [c["label"] for c in same_candle],
        "n_with_mtf_metadata": sum(1 for c in classification if c["has_mtf_metadata"]),
        "n_resolved_on": len(resolved_on),
        "n_fractal_endpoints_on": len(fractal_on),
        "fractal_endpoint_labels": [c["label"] for c in fractal_on],
        "n_unresolved_on_same_candle": len(unresolved_on),
        "n_scored_off": len(off_scored),
        "n_scored_on": len(on_scored),
        "mean_fib_err_off": _mean_optional([r["mean_fib_err_frac"] for r in off_scored]),
        "mean_fib_err_on": _mean_optional([r["mean_fib_err_frac"] for r in on_scored]),
        "mean_agreement_off": _mean_optional([r["agreement"] for r in off_scored]),
        "mean_agreement_on": _mean_optional([r["agreement"] for r in on_scored]),
        "paired_comparisons": paired,
        "same_candle_paired": same_candle_paired,
        "classification": classification,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MTF disambiguation OFF vs ON comparison.")
    parser.add_argument("--symbol", default="")
    parser.add_argument("--timeframe", default="")
    parser.add_argument("--config", default="")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate research summary and write JSON under experiments/results/.",
    )
    args = parser.parse_args()

    base = load_settings(args.config or None)
    labels = list_labels(source="human")
    if args.symbol:
        labels = [lbl for lbl in labels if lbl.symbol == args.symbol]
    if args.timeframe:
        labels = [lbl for lbl in labels if lbl.timeframe == args.timeframe]

    classification = _classify_labels(base, labels)
    off = _run_mode(_with_mtf_flag(base, False), labels)
    on = _run_mode(_with_mtf_flag(base, True), labels)

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "mtf_disambiguation_default": base.labeling.mtf_disambiguation,
        "baseline_off": off,
        "mtf_disambiguation_on": on,
    }

    if args.summary:
        summary = _summarize(classification, off, on)
        payload["summary"] = summary
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        out = RESULTS_DIR / f"mtf_disambiguation_compare_{stamp}.json"
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2))
        print(f"Wrote {out}\n")
        _print_summary(summary)
    else:
        print(json.dumps(payload, indent=2))


def _print_summary(summary: dict) -> None:
    print("=== MTF Disambiguation research (OFF vs ON) ===\n")
    print(f"Human labels:              {summary['n_human_labels']}")
    print(f"Same HTF candle:           {summary['n_same_htf_candle']}")
    if summary["same_htf_candle_labels"]:
        print(f"  -> {', '.join(summary['same_htf_candle_labels'])}")
    print(f"With MTF metadata saved:   {summary['n_with_mtf_metadata']}")
    print(f"Resolved (ON):             {summary['n_resolved_on']}")
    print(f"Fractal endpoints (ON):    {summary.get('n_fractal_endpoints_on', 0)}")
    if summary.get("fractal_endpoint_labels"):
        print(f"  -> {', '.join(summary['fractal_endpoint_labels'])}")
    print(f"Unresolved same-candle:    {summary['n_unresolved_on_same_candle']}")
    print()
    print(f"Scored OFF (not skipped):  {summary['n_scored_off']}")
    print(f"Scored ON (not skipped):   {summary['n_scored_on']}")
    print(f"Mean fib_err OFF:          {summary['mean_fib_err_off']}")
    print(f"Mean fib_err ON:           {summary['mean_fib_err_on']}")
    print(f"Mean agreement OFF:        {summary['mean_agreement_off']}")
    print(f"Mean agreement ON:         {summary['mean_agreement_on']}")
    print()
    if summary["paired_comparisons"]:
        print("Per-label fib_err (ON - OFF); negative = ON closer to facit fib:")
        for row in summary["paired_comparisons"]:
            tag = " [same HTF]" if row["same_htf_candle"] else ""
            print(
                f"  {row['label']}: off={row['fib_err_off']} on={row['fib_err_on']} "
                f"delta={row['fib_delta']:+}{tag}"
            )
    if summary["same_candle_paired"]:
        print("\nSame-candle subset only:")
        for row in summary["same_candle_paired"]:
            print(f"  {row['label']}: delta={row['fib_delta']:+}")


if __name__ == "__main__":
    main()
