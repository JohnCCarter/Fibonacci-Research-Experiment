"""Weekly source-fib zoom — per-fib windowed confirmation of the human **1W** fibs.

Renders **one chart per 1W source fib**, windowed to that fib's own
``anchor_a→anchor_b`` span plus bounded context before/after, on a finer chart
timeframe (default **4H**). This solves the problem the combined
``weekly_source_fib_map`` cannot: a single 4H chart over the full fib era is too
compressed for candle-level confirmation, so each fib gets its own readable window.

    experiments/review/weekly_source_fib_zoom/
        <fib_id>/
            4h_clean.png             # candles + A→B leg + id
            4h_levels.png            # + fib levels confined to the A→B segment
            4h_levels_labeled.png    # (only with --label-levels)
        weekly_source_fib_zoom_index.md

Strict separation (source confirmation only):

- Input is the **1W** human-fib dir; every fib must pass the same fail-closed guard
  as ``weekly_source_fib_map`` (``timeframe == "1w"``, log scale, the
  ``tradingview_log_chamoun`` profile, no 0.236, human/manual only).
- The window is **visual only**: candles + the source fib leg + the fib's own
  levels. No event markers, no reaction/relation classification, no review windows,
  and **no dependency on ``review_sample.csv``**. This is deliberately NOT the
  reaction-review flow in ``source_fib_projection_chart`` — none of that module is
  imported here (its constants are copied locally to avoid pulling in the
  review/event import graph).
- No auto-fib, no anchor inference, no forward projection beyond the context pad.

Usage::

    python -m fibengine.research.weekly_source_fib_zoom \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/1w \\
        --chart-tfs 4h \\
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
    _short_id,
)
from fibengine.research.weekly_source_fib_map import (
    _SNAP_WINDOW,
    SOURCE_TF,
    _resolve_anchor_pos,
    _validate_source_fibs,
)

WEEKLY_SOURCE_FIB_ZOOM_ROOT = REPO_ROOT / "experiments" / "review" / "weekly_source_fib_zoom"

# Chart timeframes the per-fib window is rendered on (default: 4H only — the
# combined 1D map is already usable, so per-fib 1D is opt-in via --chart-tfs).
_DEFAULT_CHART_TFS = ("4h",)

# Per-TF context pad (bars BEFORE anchor_a). Copied locally from the positional
# values in source_fib_projection_chart (NOT imported — that module pulls in the
# reaction-review graph). ~120 four-hour bars ≈ 20 days of pre-context.
_PRE_PAD: dict[str, int] = {"1w": 8, "1d": 30, "4h": 120}
_PRE_PAD_DEFAULT = 30

# Context pad AFTER anchor_b so the levels' immediate forward candle context is
# visible. Purely visual — no events, no review_end scoping.
_POST_PAD_DEFAULT = 120


@dataclass
class TfZoom:
    """One chart-timeframe window for a single fib (or a skip reason)."""

    timeframe: str
    bars: int = 0
    clean: Path | None = None
    levels: Path | None = None
    levels_labeled: Path | None = None
    window_start: str | None = None
    window_end: str | None = None
    skipped: str | None = None


@dataclass
class FibZoom:
    """All chart-timeframe windows rendered for a single fib."""

    fib_id: str
    short_id: str
    per_tf: dict[str, TfZoom] = field(default_factory=dict)


@dataclass
class WeeklySourceFibZoom:
    """Result of rendering per-fib windowed confirmation charts."""

    fibs: list[FibZoom]
    index: Path
    fib_count: int
    chart_tfs: tuple[str, ...]


def _zoom_width(n_bars: int) -> int:
    """Figure width (inches) for a windowed per-fib chart.

    Copied local equivalent of source_fib_projection_chart._zoom_width (positional,
    no reaction-review coupling).
    """
    return max(16, min(n_bars // 6, 48))


def _select_fibs(fibs: list[HumanFibAnnotation], fib_id: str | None) -> list[HumanFibAnnotation]:
    """Filter to a single fib by fib_id or short id; raise if no match."""
    if fib_id is None:
        return fibs
    chosen = [a for a in fibs if a.fib_id == fib_id or _short_id(a) == fib_id]
    if not chosen:
        raise ValueError(f"--fib-id {fib_id!r} matched no fib in the loaded 1W source fibs")
    return chosen


def render_weekly_source_fib_zoom(
    fib_dir: Path | str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    chart_tfs: tuple[str, ...] = _DEFAULT_CHART_TFS,
    fib_id: str | None = None,
    context_bars: int | None = None,
    post_bars: int | None = None,
    label_levels: bool = False,
) -> WeeklySourceFibZoom:
    """Render a windowed per-fib confirmation chart per fib per chart timeframe.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` **1W** annotations.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``WEEKLY_SOURCE_FIB_ZOOM_ROOT``.
    chart_tfs:
        Candle timeframes to window onto (default ``("4h",)``).
    fib_id:
        When given, render only the fib whose ``fib_id`` or short id matches.
    context_bars:
        Override the pre-anchor_a context pad (bars) for all timeframes.
    post_bars:
        Override the post-anchor_b context pad (bars). Defaults to
        ``_POST_PAD_DEFAULT``.
    label_levels:
        When True, also write ``<tf>_levels_labeled.png`` per fib.
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")
    _validate_source_fibs(fibs)  # fail-closed over the whole dir, before any --fib-id filter
    fibs = _select_fibs(fibs, fib_id)

    out_dir = Path(out_root) if out_root else WEEKLY_SOURCE_FIB_ZOOM_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)

    # Cache candle frames per timeframe so we load each TF once, not once per fib.
    ref = fibs[0]
    df_by_tf: dict[str, pd.DataFrame] = {}
    for tf in chart_tfs:
        data_cfg = settings.data.model_copy(
            update={"symbol": ref.symbol, "timeframe": tf, "exchange": ref.exchange}
        )
        df_by_tf[tf] = load_candles(data_cfg, fetch_if_missing=False)  # never auto-fetch

    results: list[FibZoom] = []
    for ann in fibs:
        sid = _short_id(ann)
        fib_out = out_dir / ann.fib_id
        per_tf: dict[str, TfZoom] = {}
        for tf in chart_tfs:
            per_tf[tf] = _render_fib_tf(
                ann, sid, tf, df_by_tf[tf], fib_out, context_bars, post_bars, label_levels
            )
        results.append(FibZoom(fib_id=ann.fib_id, short_id=sid, per_tf=per_tf))

    index_path = out_dir / "weekly_source_fib_zoom_index.md"
    _write_index(index_path, ref, results, chart_tfs)

    return WeeklySourceFibZoom(
        fibs=results, index=index_path, fib_count=len(fibs), chart_tfs=tuple(chart_tfs)
    )


def _render_fib_tf(
    ann: HumanFibAnnotation,
    sid: str,
    tf: str,
    df_full: pd.DataFrame,
    fib_out: Path,
    context_bars: int | None,
    post_bars: int | None,
    label_levels: bool,
) -> TfZoom:
    """Window one fib on one chart TF and render clean + levels (or record a skip)."""
    window = _SNAP_WINDOW.get(tf, 7)
    ta = pd.to_datetime(ann.anchor_a.time, utc=True)
    tb = pd.to_datetime(ann.anchor_b.time, utc=True)
    pa = _resolve_anchor_pos(df_full, ta, float(ann.anchor_a.price), window)
    pb = _resolve_anchor_pos(df_full, tb, float(ann.anchor_b.price), window)
    if pa is None or pb is None:
        edge = "anchor_a" if pa is None else "anchor_b"
        t = ann.anchor_a.time if pa is None else ann.anchor_b.time
        return TfZoom(timeframe=tf, skipped=f"{edge} {t} beyond {tf} candle range")

    pre = context_bars if context_bars is not None else _PRE_PAD.get(tf, _PRE_PAD_DEFAULT)
    post = post_bars if post_bars is not None else _POST_PAD_DEFAULT
    lo = max(0, min(pa, pb) - pre)
    hi = min(len(df_full) - 1, max(pa, pb) + post)
    df = df_full.iloc[lo : hi + 1]

    # Positions relative to the sliced window (lo <= min(pa, pb), so both are >= 0).
    drawn = [(ann, sid, pa - lo, pb - lo)]

    fib_out.mkdir(parents=True, exist_ok=True)
    clean_path = fib_out / f"{tf}_clean.png"
    levels_path = fib_out / f"{tf}_levels.png"
    fig_w = _zoom_width(len(df))
    win = f"{df.index[0]:%Y-%m-%d}→{df.index[-1]:%Y-%m-%d}"
    base_title = f"{ann.fib_id}  |  {tf}  |  1W source fib → {tf} candles  |  {win}"
    _draw_map(
        df, drawn, clean_path, show_levels=False, title=f"{base_title}  |  CLEAN", fig_w=fig_w
    )
    _draw_map(
        df, drawn, levels_path, show_levels=True, title=f"{base_title}  |  LEVELS", fig_w=fig_w
    )

    levels_labeled: Path | None = None
    if label_levels:
        labeled_path = fib_out / f"{tf}_levels_labeled.png"
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

    return TfZoom(
        timeframe=tf,
        bars=len(df),
        clean=clean_path,
        levels=levels_path,
        levels_labeled=levels_labeled,
        window_start=f"{df.index[0]:%Y-%m-%d}",
        window_end=f"{df.index[-1]:%Y-%m-%d}",
    )


def _write_index(
    path: Path,
    ref: HumanFibAnnotation,
    results: list[FibZoom],
    chart_tfs: tuple[str, ...],
) -> None:
    """Write the combined per-fib zoom index (one row per fib × timeframe)."""
    rendered = sum(
        1 for f in results for z in f.per_tf.values() if z.skipped is None
    )
    skips = [
        (f.short_id, tf, z.skipped)
        for f in results
        for tf, z in f.per_tf.items()
        if z.skipped is not None
    ]
    lines: list[str] = [
        f"# Weekly source fib zoom — {ref.symbol} 1W per-fib windows",
        "",
        "Per-fib windowed confirmation of the human-drawn **1W source fibs** on finer",
        "candles. Each chart is one fib over its own anchor-A→anchor-B span plus bounded",
        "context. Visual only: candles + source fib leg + confined levels. No events, no",
        "reaction classification, no review windows; not the 1M→1W projection map.",
        "",
        f"- Fibs: {len(results)}",
        f"- Chart timeframes: {', '.join(chart_tfs)}",
        f"- Charts rendered: {rendered}",
        "",
        "| Id | Dir | Anchor A | Anchor B | "
        + " | ".join(f"{tf} window (bars)" for tf in chart_tfs)
        + " |",
        "|----|-----|----------|----------|" + "|".join("---" for _ in chart_tfs) + "|",
    ]
    for f in results:
        # Anchor metadata comes from the fib's annotation via the first rendered TF
        # (the annotation itself is identical across TFs).
        cells = []
        for tf in chart_tfs:
            z = f.per_tf[tf]
            if z.skipped is not None:
                cells.append("⚠ skipped")
            else:
                cells.append(f"{z.window_start}→{z.window_end} ({z.bars})")
        lines.append(f"| {f.short_id} | — | — | — | " + " | ".join(cells) + " |")

    if skips:
        lines += ["", "## ⚠ Skipped (anchor outside candle range)", ""]
        lines += [f"- {sid} [{tf}]: {reason}" for sid, tf, reason in skips]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    exch = settings.data.exchange.lower()
    return REPO_ROOT / "data" / "labels" / "human_fib" / exch / sym / SOURCE_TF


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render per-fib windowed confirmation charts for BTC/USD 1W source fibs."
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
        help='Comma-separated chart timeframes (default: "4h")',
    )
    p.add_argument(
        "--context-bars",
        type=int,
        default=None,
        help="Override pre-anchor_a context pad (bars) for all timeframes",
    )
    p.add_argument(
        "--post-bars",
        type=int,
        default=None,
        help=f"Override post-anchor_b context pad (bars; default {_POST_PAD_DEFAULT})",
    )
    p.add_argument("--fib-id", default=None, help="Render only this fib (fib_id or short id)")
    p.add_argument(
        "--label-levels",
        action="store_true",
        help="Also write <tf>_levels_labeled.png per fib with ratio+price labels",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    chart_tfs = tuple(tf.strip() for tf in args.chart_tfs.split(",") if tf.strip())
    result = render_weekly_source_fib_zoom(
        fib_dir=fib_dir,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        chart_tfs=chart_tfs,
        fib_id=args.fib_id,
        context_bars=args.context_bars,
        post_bars=args.post_bars,
        label_levels=args.label_levels,
    )
    rendered = sum(1 for f in result.fibs for z in f.per_tf.values() if z.skipped is None)
    skipped = sum(1 for f in result.fibs for z in f.per_tf.values() if z.skipped is not None)
    print(f"Weekly source fib zoom: {result.fib_count} fibs, {rendered} charts, {skipped} skipped")
    for f in result.fibs:
        for tf, z in f.per_tf.items():
            status = z.skipped if z.skipped else f"{z.bars} bars -> {z.clean.name}, {z.levels.name}"
            print(f"  [{f.short_id}] {tf}: {status}")
    print(f"  index: {result.index}")
