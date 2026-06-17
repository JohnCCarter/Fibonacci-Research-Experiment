"""Weekly source-fib map — visual confirmation of the human **1W** source fibs.

Renders every human-drawn BTC/USD **1W** source fib on 1W / 1D / 4H candles, each
fib confined to its own ``anchor_a→anchor_b`` source segment. This answers one
question per timeframe: *"Do my true 1W source fibs still make structural sense as
I drop to finer candles?"*

    experiments/review/weekly_source_fib_map/
        weekly_source_fib_map_1w_clean.png    weekly_source_fib_map_1w_levels.png
        weekly_source_fib_map_1d_clean.png    weekly_source_fib_map_1d_levels.png
        weekly_source_fib_map_4h_clean.png    weekly_source_fib_map_4h_levels.png
        weekly_source_fib_map_index.md

Strict separation (this module is **only** for true 1W source fibs):

- Input is the **1W** human-fib dir; every loaded fib must have ``timeframe == "1w"``
  (fail-closed — pointing ``--fib-dir`` at the 1M folder is refused).
- Does **not** consume 1M fibs, and is **not** the 1M→1W projection map
  (``weekly_projection_map``). The fib *math* is untouched — level prices come
  straight from the annotation.
- No auto-fib, no anchor inference, no forward projection, no review-window scope,
  no event markers, no trading logic.

Snap behaviour: on the source timeframe (1W) anchors are pinned to the nearest bar
(faithful reproduction, like ``monthly_fib_map``). On finer candles (1D/4H) a weekly
extreme falls somewhere inside the week, so each anchor is snapped to the
price-matching candle within a bounded, TF-aware window.

The rendering primitives (``_draw_map``) and loaders (``_load_fibs``,
``_nearest_pos``, ``_short_id``) are reused unchanged from ``monthly_fib_map`` so the
visual style is identical. Importing them also installs the Agg backend.

Usage::

    python -m fibengine.research.weekly_source_fib_map \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/1w \\
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

WEEKLY_SOURCE_FIB_MAP_ROOT = REPO_ROOT / "experiments" / "review" / "weekly_source_fib_map"

# The fib timeframe this module is allowed to consume. Anything else is refused.
SOURCE_TF = "1w"

# Chart timeframes the source fibs are projected onto, coarse → fine.
_DEFAULT_CHART_TFS = ("1w", "1d", "4h")

# Half-width (in chart-TF bars) of the anchor swing-snap search. 0 = exact nearest
# bar (no snap) on the source TF; on finer TFs the weekly extreme sits inside the
# week, so the window spans ~one week either side of the time-nearest bar
# (1D: ~7 days; 4H: ~42 four-hour bars ≈ 7 days).
_SNAP_WINDOW: dict[str, int] = {"1w": 0, "1d": 7, "4h": 42}
_SNAP_WINDOW_DEFAULT = 7

# Per-TF context pad (bars before the earliest anchor_a) so the fib era isn't pinned
# to the left edge. Only the left edge is trimmed; candles run to the last bar.
_CONTEXT_PAD_BARS: dict[str, int] = {"1w": 8, "1d": 30, "4h": 120}
_CONTEXT_PAD_DEFAULT = 20

# Profile / scale the 1W source fibs must carry (BTC monthly-first protocol).
_REQUIRED_PROFILE = "tradingview_log_chamoun"
_REQUIRED_SCALE = "log"
_FORBIDDEN_RATIO = 0.236
_RATIO_TOL = 1e-6
# Substrings that mark a non-human / inferred fib (must never reach a source map).
_FORBIDDEN_TOKENS = ("candidate", "auto", "inferred")


@dataclass
class TfArtifacts:
    """Artifacts rendered for one chart timeframe."""

    timeframe: str
    clean: Path
    levels: Path
    drawn: int
    skipped: list[str] = field(default_factory=list)
    levels_labeled: Path | None = None


@dataclass
class WeeklySourceFibMap:
    """Result of rendering the weekly source-fib map across chart timeframes."""

    per_tf: dict[str, TfArtifacts]
    index: Path
    fib_count: int


def _validate_source_fibs(fibs: list[HumanFibAnnotation]) -> None:
    """Fail-closed guard: every fib must be a true, human, 1W log source fib.

    Raises ``ValueError`` listing every violation. The ``timeframe == "1w"`` check
    is the structural guarantee that this module cannot consume 1M fibs even if
    ``--fib-dir`` is pointed at the 1M folder.
    """
    violations: list[str] = []
    for ann in fibs:
        sid = ann.fib_id or _short_id(ann)
        if ann.timeframe != SOURCE_TF:
            violations.append(f"{sid}: timeframe {ann.timeframe!r} != {SOURCE_TF!r} (not a 1W fib)")
        if ann.levels_profile != _REQUIRED_PROFILE:
            violations.append(
                f"{sid}: levels_profile {ann.levels_profile!r} != {_REQUIRED_PROFILE!r}"
            )
        if ann.scale_mode != _REQUIRED_SCALE:
            violations.append(f"{sid}: scale_mode {ann.scale_mode!r} != {_REQUIRED_SCALE!r}")
        if any(abs(lv.ratio - _FORBIDDEN_RATIO) < _RATIO_TOL for lv in ann.levels):
            violations.append(f"{sid}: contains forbidden ratio {_FORBIDDEN_RATIO}")
        if ann.created_by != "human" or "manual" not in ann.source.lower():
            violations.append(
                f"{sid}: non-manual origin (created_by={ann.created_by!r}, source={ann.source!r})"
            )
        token = next(
            (t for t in _FORBIDDEN_TOKENS if t in sid.lower() or t in ann.source.lower()), None
        )
        if token is not None:
            violations.append(f"{sid}: looks {token} (no candidate/auto/inferred fibs)")
    if violations:
        raise ValueError(
            "weekly_source_fib_map refuses non-1W-source fibs:\n  - " + "\n  - ".join(violations)
        )


def _resolve_anchor_pos(df: pd.DataFrame, t, price: float, window: int) -> int | None:
    """Bar position for an anchor at time ``t`` / price ``price``.

    ``window <= 0`` → exact nearest bar by time (source-TF reproduction). Otherwise
    the bar within ``±window`` of the time-nearest bar whose ``[low, high]`` contains
    ``price`` — or, failing that, is closest to it — so the leg endpoint lands on the
    real candle the weekly extreme corresponds to. Ties break toward the nearest bar
    in time. Returns ``None`` only when ``t`` is outside the candle range.
    """
    base = _nearest_pos(df, t)
    if base is None or window <= 0:
        return base
    lo = max(0, base - window)
    hi = min(len(df) - 1, base + window)
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


def render_weekly_source_fib_map(
    fib_dir: Path | str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    chart_tfs: tuple[str, ...] = _DEFAULT_CHART_TFS,
    label_levels: bool = False,
) -> WeeklySourceFibMap:
    """Render clean + levels maps of the 1W source fibs on each chart timeframe.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` **1W** annotations.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``WEEKLY_SOURCE_FIB_MAP_ROOT``.
    chart_tfs:
        Candle timeframes to project onto (default ``("1w", "1d", "4h")``).
    label_levels:
        When True, also write a ``..._{tf}_levels_labeled.png`` per timeframe with
        ratio + rounded price on each level segment.
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")
    _validate_source_fibs(fibs)  # fail-closed before any rendering

    ref = fibs[0]  # all fibs share symbol/exchange (BTC/USD bitfinex protocol)
    out_dir = Path(out_root) if out_root else WEEKLY_SOURCE_FIB_MAP_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)

    per_tf: dict[str, TfArtifacts] = {}
    for tf in chart_tfs:
        per_tf[tf] = _render_one_tf(fibs, ref, tf, out_dir, settings, label_levels)

    index_path = out_dir / "weekly_source_fib_map_index.md"
    _write_index(index_path, ref, fibs, per_tf, chart_tfs)

    return WeeklySourceFibMap(per_tf=per_tf, index=index_path, fib_count=len(fibs))


def _render_one_tf(
    fibs: list[HumanFibAnnotation],
    ref: HumanFibAnnotation,
    tf: str,
    out_dir: Path,
    settings: Settings,
    label_levels: bool,
) -> TfArtifacts:
    """Load ``tf`` candles, resolve each fib's A→B span, render clean + levels."""
    data_cfg = settings.data.model_copy(
        update={"symbol": ref.symbol, "timeframe": tf, "exchange": ref.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)  # never auto-fetch

    window = _SNAP_WINDOW.get(tf, _SNAP_WINDOW_DEFAULT)
    pad = _CONTEXT_PAD_BARS.get(tf, _CONTEXT_PAD_DEFAULT)

    # Trim the left edge to the fib era so early-history candles don't compress the map.
    anchor_a_positions = [
        pos
        for ann in fibs
        if (pos := _nearest_pos(df_full, pd.to_datetime(ann.anchor_a.time, utc=True))) is not None
    ]
    lo = max(0, (min(anchor_a_positions) if anchor_a_positions else 0) - pad)
    df = df_full.iloc[lo:]
    if df.empty:
        raise ValueError(f"No {tf} candles for {ref.symbol} after trim")

    # Resolve each fib's A→B positions. A fib whose anchor falls outside the candle
    # range cannot be drawn — surface it, never skip silently.
    drawn: list[tuple[HumanFibAnnotation, str, int, int]] = []
    skipped: list[str] = []
    for ann in fibs:
        sid = _short_id(ann)
        ta = pd.to_datetime(ann.anchor_a.time, utc=True)
        tb = pd.to_datetime(ann.anchor_b.time, utc=True)
        pa = _resolve_anchor_pos(df, ta, float(ann.anchor_a.price), window)
        pb = _resolve_anchor_pos(df, tb, float(ann.anchor_b.price), window)
        if pa is None or pb is None:
            edge = "anchor_a" if pa is None else "anchor_b"
            t = ann.anchor_a.time if pa is None else ann.anchor_b.time
            skipped.append(f"{sid} ({edge} {t} beyond {tf} candle range)")
            continue
        drawn.append((ann, sid, pa, pb))

    clean_path = out_dir / f"weekly_source_fib_map_{tf}_clean.png"
    levels_path = out_dir / f"weekly_source_fib_map_{tf}_levels.png"
    n = len(df)
    fig_w = max(20, min(n // 2, 50))
    base_title = f"{ref.symbol} 1W source fib map → {tf} candles  |  {len(drawn)} fibs (log)"
    _draw_map(
        df, drawn, clean_path, show_levels=False, title=f"{base_title}  |  CLEAN", fig_w=fig_w
    )
    _draw_map(
        df, drawn, levels_path, show_levels=True, title=f"{base_title}  |  LEVELS", fig_w=fig_w
    )

    levels_labeled: Path | None = None
    if label_levels:
        labeled_path = out_dir / f"weekly_source_fib_map_{tf}_levels_labeled.png"
        _draw_map(
            df,
            drawn,
            labeled_path,
            show_levels=True,
            title=f"{base_title}  |  LEVELS (labeled)",
            fig_w=fig_w,
            label_levels=True,
        )
        levels_labeled = labeled_path

    if skipped:
        print(f"WARNING [{tf}]: {len(skipped)} fib(s) not drawn (outside candle range):")
        for s in skipped:
            print(f"  - {s}")

    return TfArtifacts(
        timeframe=tf,
        clean=clean_path,
        levels=levels_path,
        drawn=len(drawn),
        skipped=skipped,
        levels_labeled=levels_labeled,
    )


def _write_index(
    path: Path,
    ref: HumanFibAnnotation,
    fibs: list[HumanFibAnnotation],
    per_tf: dict[str, TfArtifacts],
    chart_tfs: tuple[str, ...],
) -> None:
    """Write the combined human-readable index (one document, a section per TF)."""
    lines: list[str] = [
        f"# Weekly source fib map — {ref.symbol} 1W → {'/'.join(chart_tfs)}",
        "",
        "Visual confirmation of the human-drawn **1W source fibs** on each chart",
        "timeframe. Each fib's levels are drawn only across its own anchor-A→anchor-B",
        "segment. Not the 1M→1W projection map; no 1M fibs, no forward projection, no",
        "review-window scoping, no events, no auto-fib.",
        "",
        f"- Fibs loaded: {len(fibs)}",
        f"- Chart timeframes: {', '.join(chart_tfs)}",
        "",
        "| Id | Dir | Anchor A | Anchor B |",
        "|----|-----|----------|----------|",
    ]
    for ann in fibs:
        sid = _short_id(ann)
        a_t = pd.to_datetime(ann.anchor_a.time, utc=True).strftime("%Y-%m-%d")
        b_t = pd.to_datetime(ann.anchor_b.time, utc=True).strftime("%Y-%m-%d")
        lines.append(
            f"| {sid} | {ann.direction} | {a_t} @ ${ann.anchor_a.price:,.0f} "
            f"| {b_t} @ ${ann.anchor_b.price:,.0f} |"
        )

    # Per-fib level table — the artifact records its own exact level set (rounded;
    # full-precision values live in the source fib_*.json).
    ratios = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)
    lines += [
        "",
        "## Levels (rounded; exact values in source fib_*.json)",
        "",
        "| Id | " + " | ".join(f"{r:g}" for r in ratios) + " |",
        "|----|" + "|".join("---" for _ in ratios) + "|",
    ]
    for ann in fibs:
        sid = _short_id(ann)
        by_ratio = {lv.ratio: lv.price for lv in ann.levels}
        cells = " | ".join(f"{by_ratio[r]:,.0f}" if r in by_ratio else "—" for r in ratios)
        lines.append(f"| {sid} | {cells} |")

    lines += ["", "## Per-timeframe", ""]
    for tf in chart_tfs:
        art = per_tf[tf]
        lines += [
            f"### {tf}",
            "",
            f"- Charts: `{art.clean.name}`, `{art.levels.name}`",
            f"- Fibs drawn: {art.drawn}/{len(fibs)}",
        ]
        if art.skipped:
            lines.append("- ⚠ Not drawn (anchor outside candle range):")
            lines += [f"  - {s}" for s in art.skipped]
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    exch = settings.data.exchange.lower()
    return REPO_ROOT / "data" / "labels" / "human_fib" / exch / sym / SOURCE_TF


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the BTC/USD 1W source-fib map on 1W/1D/4H candles (clean + levels)."
    )
    p.add_argument(
        "--fib-dir",
        default=None,
        help="Directory of fib_*.json 1W annotations (default: BTC/USD 1W label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    p.add_argument(
        "--chart-tfs",
        default=",".join(_DEFAULT_CHART_TFS),
        help='Comma-separated chart timeframes (default: "1w,1d,4h")',
    )
    p.add_argument(
        "--label-levels",
        action="store_true",
        help="Also write a ..._{tf}_levels_labeled.png per timeframe with ratio+price labels",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    chart_tfs = tuple(tf.strip() for tf in args.chart_tfs.split(",") if tf.strip())
    result = render_weekly_source_fib_map(
        fib_dir=fib_dir,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        chart_tfs=chart_tfs,
        label_levels=args.label_levels,
    )
    print(f"Weekly source fib map: {result.fib_count} fibs")
    for tf, art in result.per_tf.items():
        extra = f", labeled={art.levels_labeled.name}" if art.levels_labeled else ""
        print(
            f"  [{tf}] drawn {art.drawn}/{result.fib_count}  -> "
            f"{art.clean.name}, {art.levels.name}{extra}"
        )
        if art.skipped:
            print(f"        skipped: {len(art.skipped)}")
    print(f"  index: {result.index}")
