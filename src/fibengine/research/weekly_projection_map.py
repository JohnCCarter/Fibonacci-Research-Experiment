"""Weekly projection map (source_segment_map) — all 1M fibs on 1W candles.

Renders every human-drawn BTC/USD **1M** fib on the **1W** candle chart, each fib
confined to its own ``anchor_a→anchor_b`` source segment (snapped to weekly bars).
This is the macro recognition step *between* the monthly fib map and selecting a
single fib for lower-TF projection — it answers: *"Do my 1M fibs still make
structural sense one timeframe lower?"*

    experiments/review/weekly_projection_map/
        weekly_projection_map_clean.png    # 1W candles + A→B legs + fib ids
        weekly_projection_map_levels.png   # + levels confined to each fib's A→B segment
        weekly_projection_map_index.md

Deliberately the **source_segment_map**, not a reaction map: levels are drawn only
across each fib's own A→B span, never extended forward to review_end, nothing
rendered "active until now", no event markers. (A future reaction_review_map will
use anchor_b→review_end scope.)

The rendering primitives are reused unchanged from ``monthly_fib_map`` so the visual
style is identical (same candles styling, log axis, leg/dot/id presentation). The
fib *math* is untouched — level prices come straight from the annotation.

Usage::

    python -m fibengine.research.weekly_projection_map \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/1M \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.human_fib import HumanFibAnnotation
from fibengine.research.monthly_fib_map import (
    _draw_map,
    _load_fibs,
    _nearest_pos,
    _short_id,
)

WEEKLY_PROJECTION_MAP_ROOT = REPO_ROOT / "experiments" / "review" / "weekly_projection_map"

# Weekly context before the earliest anchor_a (~6 months) so the fib era isn't
# pinned to the left edge. Only the left edge is trimmed; candles run to the last bar.
_CONTEXT_PAD_BARS_WK = 26

# Half-width (weekly bars) of the swing-snap search around the time-nearest bar.
# A 1M anchor is a *monthly* extreme; the week that hit it is often 1-3 weeks off
# the first-of-month timestamp, so legs drawn at the time-nearest week float above/
# below the weekly candles. ~5 weeks covers a calendar month either side.
_SWING_SNAP_WINDOW_WK = 5


def _swing_snap_pos(df: pd.DataFrame, t, price: float) -> int | None:
    """Weekly bar whose high/low best matches ``price`` near time ``t``.

    Returns the position (within ``±_SWING_SNAP_WINDOW_WK`` of the time-nearest bar)
    whose ``[low, high]`` contains ``price`` — or, failing that, is closest to it —
    so the A→B leg endpoint lands on the real weekly swing the monthly extreme
    corresponds to. Ties are broken toward the bar closest in time. Returns None
    only when ``t`` is outside the candle range (same as ``_nearest_pos``).
    """
    base = _nearest_pos(df, t)
    if base is None:
        return None
    lo = max(0, base - _SWING_SNAP_WINDOW_WK)
    hi = min(len(df) - 1, base + _SWING_SNAP_WINDOW_WK)
    best = base
    best_key = (float("inf"), float("inf"))
    for j in range(lo, hi + 1):
        bar = df.iloc[j]
        low, high = float(bar["low"]), float(bar["high"])
        if low <= price <= high:
            dist = 0.0
        elif price > high:
            dist = (price - high) / high
        else:
            dist = (low - price) / low
        key = (dist, abs(j - base))  # nearest in price, then nearest in time
        if key < best_key:
            best_key = key
            best = j
    return best


@dataclass
class WeeklyProjectionMap:
    """Result of rendering the weekly projection (source-segment) map."""

    clean: Path
    levels: Path
    index: Path
    fib_count: int
    drawn: int
    skipped: list[str] = field(default_factory=list)


def render_weekly_projection_map(
    fib_dir: Path | str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    chart_tf: str = "1w",
) -> WeeklyProjectionMap:
    """Render the clean + levels 1W source-segment map and an index.

    Each 1M fib is drawn only over its own anchor_a→anchor_b span on the weekly
    candles. No review-window scope, no forward projection, no event markers.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` 1M annotations.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``WEEKLY_PROJECTION_MAP_ROOT``.
    chart_tf:
        Candle timeframe to project onto (default ``1w``).
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")

    ref = fibs[0]  # all fibs share symbol/exchange (BTC/USD bitfinex protocol)
    data_cfg = settings.data.model_copy(
        update={"symbol": ref.symbol, "timeframe": chart_tf, "exchange": ref.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)

    # Trim the left edge to the fib era so early-history candles don't compress the map.
    anchor_a_positions = [
        pos
        for ann in fibs
        if (pos := _nearest_pos(df_full, pd.to_datetime(ann.anchor_a.time, utc=True))) is not None
    ]
    lo = max(0, (min(anchor_a_positions) if anchor_a_positions else 0) - _CONTEXT_PAD_BARS_WK)
    df = df_full.iloc[lo:]
    if df.empty:
        raise ValueError(f"No {chart_tf} candles for {ref.symbol} after trim")

    # Resolve each fib's A→B positions on the trimmed df. A fib whose anchor falls
    # outside the candle range cannot be drawn — surface it, never skip silently.
    drawn: list[tuple[HumanFibAnnotation, str, int, int]] = []
    skipped: list[str] = []
    for ann in fibs:
        sid = _short_id(ann)
        ta = pd.to_datetime(ann.anchor_a.time, utc=True)
        tb = pd.to_datetime(ann.anchor_b.time, utc=True)
        pa = _swing_snap_pos(df, ta, float(ann.anchor_a.price))
        pb = _swing_snap_pos(df, tb, float(ann.anchor_b.price))
        if pa is None or pb is None:
            edge = "anchor_a" if pa is None else "anchor_b"
            t = ann.anchor_a.time if pa is None else ann.anchor_b.time
            skipped.append(f"{sid} ({edge} {t} beyond candle range)")
            continue
        drawn.append((ann, sid, pa, pb))

    out_dir = Path(out_root) if out_root else WEEKLY_PROJECTION_MAP_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_path = out_dir / "weekly_projection_map_clean.png"
    levels_path = out_dir / "weekly_projection_map_levels.png"
    index_path = out_dir / "weekly_projection_map_index.md"

    n = len(df)
    fig_w = max(20, min(n // 2, 50))
    base_title = f"{ref.symbol} 1M→1W source-segment map  |  {len(drawn)} fibs (log)"
    _draw_map(
        df, drawn, clean_path, show_levels=False, title=f"{base_title}  |  CLEAN", fig_w=fig_w
    )
    _draw_map(
        df, drawn, levels_path, show_levels=True, title=f"{base_title}  |  LEVELS", fig_w=fig_w
    )
    _write_index(index_path, ref, df, drawn, skipped)

    if skipped:
        print(f"WARNING: {len(skipped)} fib(s) not drawn (outside candle range):")
        for s in skipped:
            print(f"  - {s}")

    return WeeklyProjectionMap(
        clean=clean_path,
        levels=levels_path,
        index=index_path,
        fib_count=len(fibs),
        drawn=len(drawn),
        skipped=skipped,
    )


def _write_index(
    path: Path,
    ref: HumanFibAnnotation,
    df: pd.DataFrame,
    drawn: list[tuple[HumanFibAnnotation, str, int, int]],
    skipped: list[str],
) -> None:
    """Write the human-readable weekly source-segment map index."""
    lines: list[str] = [
        f"# Weekly projection map (source_segment) — {ref.symbol} 1M→1W",
        "",
        "Every human-drawn 1M fib projected onto 1W candles, each confined to its own",
        "anchor-A→anchor-B source segment (snapped to weekly bars). No review-window",
        "scope, no forward projection to review_end, no 'active until now', no events.",
        "",
        f"- Charts: `{path.with_name('weekly_projection_map_clean.png').name}`, "
        f"`{path.with_name('weekly_projection_map_levels.png').name}`",
        f"- Candles: {ref.symbol} 1W (log scale), {df.index[0]:%Y-%m-%d} → {df.index[-1]:%Y-%m-%d}",
        f"- Fibs drawn: {len(drawn)}",
        "",
        "| Id | Dir | Anchor A | Anchor B |",
        "|----|-----|----------|----------|",
    ]
    for ann, sid, _pa, _pb in drawn:
        a_t = pd.to_datetime(ann.anchor_a.time, utc=True).strftime("%Y-%m-%d")
        b_t = pd.to_datetime(ann.anchor_b.time, utc=True).strftime("%Y-%m-%d")
        lines.append(
            f"| {sid} | {ann.direction} | {a_t} @ ${ann.anchor_a.price:,.0f} "
            f"| {b_t} @ ${ann.anchor_b.price:,.0f} |"
        )

    # Per-fib level table so the artifact records the exact level set itself
    # (rounded for scanning; full-precision values live in the source fib_*.json).
    ratios = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)
    lines += [
        "",
        "## Levels (rounded; exact values in source fib_*.json)",
        "",
        "| Id | " + " | ".join(f"{r:g}" for r in ratios) + " |",
        "|----|" + "|".join("---" for _ in ratios) + "|",
    ]
    for ann, sid, _pa, _pb in drawn:
        by_ratio = {lv.ratio: lv.price for lv in ann.levels}
        cells = " | ".join(f"{by_ratio[r]:,.0f}" if r in by_ratio else "—" for r in ratios)
        lines.append(f"| {sid} | {cells} |")

    if skipped:
        lines += ["", "## ⚠ Not drawn (anchor outside candle range)", ""]
        lines += [f"- {s}" for s in skipped]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    return REPO_ROOT / "data" / "labels" / "human_fib" / settings.data.exchange.lower() / sym / "1M"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the BTC/USD 1M→1W source-segment projection map (clean + levels)."
    )
    p.add_argument(
        "--fib-dir",
        default=None,
        help="Directory of fib_*.json 1M annotations (default: BTC/USD 1M label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    result = render_weekly_projection_map(
        fib_dir=fib_dir,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
    )
    print(f"Weekly projection map: {result.drawn}/{result.fib_count} fibs drawn")
    print(f"  clean:  {result.clean}")
    print(f"  levels: {result.levels}")
    print(f"  index:  {result.index}")
