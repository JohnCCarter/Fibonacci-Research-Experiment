"""Batch reaction-review for all BTC/USD 1D source fibs → 4H.

Projects each of the 67 human 1D source fibs onto 4H candles using
review_windows.yaml (90-day fixed horizon per fib) and the expansion
config (4H history back to 2016-11-05).

Usage::

    uv run --no-sync python scripts/run_btc_1d_reaction_review.py \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fibengine.core.config import load_settings
from fibengine.research.source_fib_projection_review import run_source_fib_projection_review

LABEL_DIR = Path("data/labels/human_fib/bitfinex/BTC-USD/1d")
CHART_TIMEFRAMES = ["4h"]
MANIFEST_PATH = Path("experiments/review/source_fib_projection/btc_1d_batch_manifest.json")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--config",
        default="config/settings.expansion.yaml",
        help="Settings YAML (default: expansion config with full 4H history)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="List fibs without running the review pipeline",
    )
    p.add_argument(
        "--fib",
        default=None,
        help="Run only one fib by ID or partial filename match (for debugging)",
    )
    args = p.parse_args()

    settings = load_settings(args.config)
    fib_files = sorted(LABEL_DIR.glob("fib_*.json"))

    if args.fib:
        fib_files = [f for f in fib_files if args.fib in f.stem]
        if not fib_files:
            print(f"No fib matching '{args.fib}' found in {LABEL_DIR}")
            raise SystemExit(1)

    print(f"BTC/USD 1D reaction-review: {len(fib_files)} fibs -> {CHART_TIMEFRAMES}")
    print(f"Config: {args.config}")
    print(f"Label dir: {LABEL_DIR}")

    if args.dry_run:
        for f in fib_files:
            print(f"  {f.name}")
        return

    results: list[dict] = []
    errors: list[dict] = []

    for i, fib_path in enumerate(fib_files, 1):
        fib_id = fib_path.stem
        print(f"[{i:2d}/{len(fib_files)}] {fib_id}", end=" ... ", flush=True)
        try:
            summary = run_source_fib_projection_review(
                source_fib_path=fib_path,
                chart_timeframes=CHART_TIMEFRAMES,
                settings=settings,
            )
            n = summary["total_interactions"]
            tf_str = "  ".join(
                f"{tf}={v}" for tf, v in summary.get("interactions_by_tf", {}).items()
            )
            skipped = summary.get("skipped", {})
            skip_str = f"  SKIP:{skipped}" if skipped else ""
            print(f"OK  total={n}  {tf_str}{skip_str}")
            results.append(summary)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {exc}")
            errors.append({"fib_id": fib_id, "error": str(exc)})

    total_events = sum(s["total_interactions"] for s in results)
    print(f"\n=== Done: {len(results)} OK / {len(errors)} errors ===")
    print(f"Total 4H interactions: {total_events}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e['fib_id']}: {e['error']}")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "protocol": "BTC/USD 1D reaction-review",
                "config": args.config,
                "chart_timeframes": CHART_TIMEFRAMES,
                "fib_count": len(fib_files),
                "ok": len(results),
                "errors": len(errors),
                "total_4h_interactions": total_events,
                "results": results,
                "error_list": errors,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nManifest -> {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
