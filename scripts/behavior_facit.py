"""Fas 3 behavior facit â€” scaffold, annotate candidates, validate, print (research only).

auto_candidate is never facit. Only human_label counts after you approve.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fibengine.core.config import REPO_ROOT
from fibengine.labeling.behavior_facit import (
    DEFAULT_GOLDEN_LEG_IDS,
    annotate_behavior_file,
    default_behavior_path,
    load_behavior_facit,
    resolve_parent_path,
    save_behavior_facit,
    scaffold_from_parent,
    validate_behavior_facit,
)
from fibengine.labeling.store import load_label


def _parent_path(exchange: str, symbol: str, timeframe: str, labels_subdir: str = "") -> Path:
    sym = symbol.replace("/", "-")
    root = REPO_ROOT / "data" / "labels"
    if labels_subdir:
        root = root / labels_subdir.strip("/\\")
    return root / exchange.lower() / sym / f"{timeframe}.json"


def _behavior_path(exchange: str, symbol: str, timeframe: str, research_subdir: str = "") -> Path:
    return default_behavior_path(exchange, symbol, timeframe, research_subdir=research_subdir)


def cmd_scaffold(args: argparse.Namespace) -> None:
    parent = (
        Path(args.parent)
        if args.parent
        else _parent_path(args.exchange, args.symbol, args.timeframe, args.labels_subdir)
    )
    leg_ids = tuple(args.legs.split(",")) if args.legs else DEFAULT_GOLDEN_LEG_IDS
    facit = scaffold_from_parent(
        parent,
        leg_ids=leg_ids,
        all_legs=args.all_legs,
        notes=args.notes,
    )
    out = (
        Path(args.out)
        if args.out
        else _behavior_path(args.exchange, args.symbol, args.timeframe, args.research_subdir)
    )
    save_behavior_facit(facit, out)
    print(f"Scaffolded {len(facit.legs)} legs -> {out}")
    print("Next: annotate (auto suggestions) then set human_label per level.")
    for leg in facit.legs:
        print(f"  {leg.leg_id} {leg.leg_direction} 0.618={leg.derived_prices.get('0.618', 0):,.0f}")


def cmd_annotate(args: argparse.Namespace) -> None:
    path = (
        Path(args.path)
        if args.path
        else _behavior_path(args.exchange, args.symbol, args.timeframe, args.research_subdir)
    )
    facit, count = annotate_behavior_file(
        path,
        fetch_if_missing=not args.no_fetch,
        overwrite_auto=not args.keep_auto,
    )
    print(f"{path}: wrote auto_candidate on {count} level slot(s)")
    print("human_label on events was NOT modified. Add events manually or edit human_label.")
    pending = 0
    for lb in facit.legs:
        for _ratio, lv in lb.levels.items():
            lv._ensure_legacy_migrated()
            if not lv.events:
                pending += 1
            else:
                for ev in lv.events:
                    if ev.human_label is None:
                        pending += 1
    print(f"  {pending} event slot(s) awaiting human_label")


def cmd_validate(args: argparse.Namespace) -> None:
    path = (
        Path(args.path)
        if args.path
        else _behavior_path(args.exchange, args.symbol, args.timeframe, args.research_subdir)
    )
    facit = load_behavior_facit(path)
    issues = validate_behavior_facit(
        facit,
        require_human=not args.allow_auto_only,
    )
    if issues:
        print(f"{path}: {len(issues)} issue(s)")
        for item in issues:
            print(f"  - {item}")
        raise SystemExit(1)
    mode = "human facit complete" if not args.allow_auto_only else "structure OK"
    print(f"{path}: OK â€” {mode} ({len(facit.legs)} legs)")


def cmd_print(args: argparse.Namespace) -> None:
    path = (
        Path(args.path)
        if args.path
        else _behavior_path(args.exchange, args.symbol, args.timeframe, args.research_subdir)
    )
    facit = load_behavior_facit(path)
    parent = resolve_parent_path(facit.parent_label_path)
    label = load_label(parent)
    by_id = {leg.id: leg for leg in label.all_legs()}

    print(f"Behavior facit: {path.name} (schema {facit.schema_version})")
    print(f"Parent: {facit.parent_label_path}")
    print("Grid = derived_prices | Facit = events[].human_label | auto = suggestion.\n")

    for lb in facit.legs:
        leg = by_id.get(lb.leg_id)
        if not leg:
            print(f"{lb.leg_id}: MISSING in parent")
            continue
        print(
            f"{lb.leg_id} ({lb.leg_direction})  "
            f"H {leg.high.timestamp[:10]} {leg.high.price:,.0f}  "
            f"L {leg.low.timestamp[:10]} {leg.low.price:,.0f}"
        )
        for ratio in ("0.382", "0.5", "0.618", "0.786"):
            lv = lb.levels.get(ratio)
            if not lv:
                continue
            price = lv.price or lb.derived_prices.get(ratio, 0)
            lv._ensure_legacy_migrated()
            if not lv.events:
                print(f"    {ratio:>5} {price:>10,.0f}  (no events)")
                continue
            for ev in lv.events:
                human = ev.human_label or "â€”"
                auto = ev.auto_candidate or "â€”"
                bar = f" @ {ev.event_bar[:10]}" if ev.event_bar else ""
                print(f"    {ratio:>5} {price:>10,.0f}  human={human}  auto={auto}{bar}")
        print()


def _add_shared_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--exchange", default="Bitfinex")
    p.add_argument("--symbol", default="BTC/USD")
    p.add_argument("--timeframe", default="1d")
    p.add_argument("--path", default="", help="behavior JSON path")
    p.add_argument(
        "--labels-subdir",
        default="",
        help="Under data/labels/, e.g. tmp (parent 1d.json for scaffold)",
    )
    p.add_argument(
        "--research-subdir",
        default="",
        help="Under data/labels/research/, e.g. tmp (1d-behavior.json)",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fas 3 behavior facit (research).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scaffold = sub.add_parser("scaffold", help="Create template from parent multi-leg label")
    _add_shared_args(p_scaffold)
    p_scaffold.add_argument("--parent", default="")
    p_scaffold.add_argument("--out", default="")
    p_scaffold.add_argument("--legs", default="", help="Comma-separated leg_ids")
    p_scaffold.add_argument("--notes", default="Golden subset â€” Fas 3 pilot")
    p_scaffold.add_argument(
        "--all-legs",
        action="store_true",
        help="Scaffold every leg_id from parent (e.g. after tmp labeling)",
    )
    p_scaffold.set_defaults(func=cmd_scaffold)

    p_ann = sub.add_parser(
        "annotate",
        help="Fill auto_candidate from OHLC heuristics (never sets human_label)",
    )
    _add_shared_args(p_ann)
    p_ann.add_argument(
        "--no-fetch",
        action="store_true",
        help="Do not fetch candles if cache missing",
    )
    p_ann.add_argument(
        "--keep-auto",
        action="store_true",
        help="Do not overwrite existing auto_candidate values",
    )
    p_ann.set_defaults(func=cmd_annotate)

    p_val = sub.add_parser("validate", help="Check schema; default requires human_label set")
    _add_shared_args(p_val)
    p_val.add_argument(
        "--allow-auto-only",
        action="store_true",
        help="Pass even if only auto_candidate is set (not valid facit for Fas 5)",
    )
    p_val.set_defaults(func=cmd_validate)

    p_print = sub.add_parser("print", help="Human vs auto summary for review")
    _add_shared_args(p_print)
    p_print.set_defaults(func=cmd_print)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
