"""Research: full MTF leg â€” HTF facit + daily Fib touches (in/out structure).

Run (forces mtf_disambiguation ON for analysis):
    uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USD --timeframe 1w
    uv run python scripts/mtf_leg_daily_fib.py --all-1w
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.mtf_leg_research import analyze_mtf_leg_daily_fib
from fibengine.labeling.store import list_labels

RESULTS_DIR = REPO_ROOT / "experiments" / "results"


def _print_report(report) -> None:
    print(f"\n=== {report.label_id} ===")
    if report.skip_reason and report.mtf_status != "resolved":
        print(f"SKIP: {report.skip_reason}")
        return
    print(f"MTF: {report.resolution_kind} | order={report.order}")
    print(f"HTF range: {report.htf_high_price} -> {report.htf_low_price}")
    print(
        f"LTF anchors: high {report.ltf_high_timestamp[:10]} | low {report.ltf_low_timestamp[:10]}"
    )
    print("Fib (HTF facit grid):")
    for lvl in sorted(report.fib_levels, key=float):
        print(f"  {lvl}: {report.fib_levels[lvl]}")
    for phase in (report.impulse, report.retrace):
        if phase is None:
            continue
        print(
            f"\n{phase.name} ({phase.bar_count} daily bars, {phase.start[:10]} .. {phase.end[:10]})"
        )
        if not phase.events:
            print("  (no level events)")
        for ev in phase.events:
            print(f"  {ev.level}: {ev.event} @ {ev.timestamp[:10]} ({ev.price})")


def main() -> None:
    parser = argparse.ArgumentParser(description="MTF leg daily Fib research report.")
    parser.add_argument("--symbol", default="")
    parser.add_argument("--timeframe", default="1w")
    parser.add_argument("--all-1w", action="store_true", help="All human 1w labels")
    parser.add_argument("--config", default="")
    args = parser.parse_args()

    settings = load_settings(args.config or None)
    labels = [lbl for lbl in list_labels(source="human") if lbl.timeframe == "1w"]
    if args.symbol:
        labels = [lbl for lbl in labels if lbl.symbol == args.symbol]
    if args.timeframe and not args.all_1w:
        labels = [lbl for lbl in labels if lbl.timeframe == args.timeframe]
    if not labels:
        print("No matching labels.")
        return

    reports = []
    for label in labels:
        cfg = settings.data.model_copy(
            update={
                "exchange": label.exchange,
                "symbol": label.symbol,
                "timeframe": label.timeframe,
            }
        )
        htf_df = load_candles(cfg)
        report = analyze_mtf_leg_daily_fib(label, htf_df, settings)
        reports.append(report.to_dict())
        _print_report(report)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = RESULTS_DIR / f"mtf_leg_daily_fib_{stamp}.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"reports": reports}, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
