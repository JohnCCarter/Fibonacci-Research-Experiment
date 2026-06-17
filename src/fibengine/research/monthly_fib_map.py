"""Monthly fib-map renderer — visual confirmation of the human 1M source fibs.

Renders every human-drawn BTC/USD **1M** fib on the 1M candle chart so the human
can answer one question: *"These are the 1M fibs I drew."* This is the macro
source-fib map that must be confirmed **before** any lower-timeframe projection.

    experiments/review/monthly_fib_map/
        monthly_fib_map_clean.png    # candles + A→B legs + fib ids
        monthly_fib_map_levels.png   # same + each fib's levels (own A→B segment)
        monthly_fib_map_index.md

For each fib we draw anchor A, anchor B, the diagonal A→B leg, a short id
(e.g. ``20201001``), and — in the levels view only — the fib levels confined to
that fib's own monthly A→B segment. The y-axis is log to match the TradingView
log fib (the fib *math* is unchanged — level prices come straight from the
annotation).

Deliberately NOT here (these belong to the lower-TF projection flow):
no lower-TF events, no projection to 1W/1D/4H, no review-window scoping, no
"active until now" extension, no full-history projection, no auto-fib, no nested
fibs, no trading logic, no edge claims.

Usage::

    python -m fibengine.research.monthly_fib_map \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/1M \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import mplfinance as mpf  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.core.config import REPO_ROOT, Settings, load_settings  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.labeling.human_fib import HumanFibAnnotation, load_annotation  # noqa: E402

MONTHLY_FIB_MAP_ROOT = REPO_ROOT / "experiments" / "review" / "monthly_fib_map"

# Candle context before the earliest anchor_a so the fib era isn't pinned to the
# left edge. Only the left edge is trimmed; candles run to the last cached bar.
_CONTEXT_PAD_BARS = 6

# A categorical palette gives each fib its own stable colour (leg + id + levels).
_PALETTE = plt.get_cmap("tab10")


@dataclass
class MonthlyFibMap:
    """Result of rendering the monthly fib map."""

    clean: Path
    levels: Path
    index: Path
    fib_count: int
    drawn: int
    skipped: list[str] = field(default_factory=list)
    levels_labeled: Path | None = None


def _nearest_pos(df: pd.DataFrame, t) -> int | None:
    """Integer position of the bar nearest ``t``, or None if out of range."""
    if t is None or pd.isna(t):
        return None
    if t < df.index[0] or t > df.index[-1]:
        return None
    secs = np.asarray((df.index - t).total_seconds(), dtype=float)
    return int(np.argmin(np.abs(secs)))


def _short_id(ann: HumanFibAnnotation) -> str:
    """Short human-facing fib id from anchor_a, e.g. ``20201001``."""
    return pd.to_datetime(ann.anchor_a.time, utc=True).strftime("%Y%m%d")


def _load_fibs(fib_dir: Path) -> list[HumanFibAnnotation]:
    """Load every base ``fib_*.json`` (skip ``*_events.json`` sidecars), time-sorted."""
    paths = [p for p in sorted(fib_dir.glob("fib_*.json")) if not p.name.endswith("_events.json")]
    fibs = [load_annotation(p) for p in paths]
    fibs.sort(key=lambda a: pd.to_datetime(a.anchor_a.time, utc=True))
    return fibs


def render_monthly_fib_map(
    fib_dir: Path | str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    chart_tf: str = "1M",
    label_levels: bool = False,
) -> MonthlyFibMap:
    """Render the clean + levels 1M fib-map views and an index.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` 1M annotations.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``MONTHLY_FIB_MAP_ROOT``.
    chart_tf:
        Candle timeframe to render the map on (default ``1M``).
    label_levels:
        When True, also write ``monthly_fib_map_levels_labeled.png`` with ratio +
        rounded price on each level segment. The default ``clean`` + ``levels`` PNGs
        are always rendered identically regardless of this flag.
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")

    # All fibs share symbol/exchange (BTC/USD bitfinex protocol); take the first.
    ref = fibs[0]
    data_cfg = settings.data.model_copy(
        update={"symbol": ref.symbol, "timeframe": chart_tf, "exchange": ref.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)

    # Trim the left edge to the fib era so the map isn't dominated by early-history
    # candles that compress every fib into the top-right corner.
    anchor_a_positions = [
        pos
        for ann in fibs
        if (pos := _nearest_pos(df_full, pd.to_datetime(ann.anchor_a.time, utc=True))) is not None
    ]
    lo = max(0, (min(anchor_a_positions) if anchor_a_positions else 0) - _CONTEXT_PAD_BARS)
    df = df_full.iloc[lo:]
    if df.empty:
        raise ValueError(f"No {chart_tf} candles for {ref.symbol} after trim")

    # Resolve each fib's anchor positions on the trimmed df. A fib whose anchor
    # falls outside the candle range cannot be drawn — surface it, never skip
    # silently (the map claims to be complete).
    drawn: list[tuple[HumanFibAnnotation, str, int, int]] = []
    skipped: list[str] = []
    for ann in fibs:
        sid = _short_id(ann)
        pa = _nearest_pos(df, pd.to_datetime(ann.anchor_a.time, utc=True))
        pb = _nearest_pos(df, pd.to_datetime(ann.anchor_b.time, utc=True))
        if pa is None or pb is None:
            edge = "anchor_a" if pa is None else "anchor_b"
            t = ann.anchor_a.time if pa is None else ann.anchor_b.time
            skipped.append(f"{sid} ({edge} {t} beyond candle range)")
            continue
        drawn.append((ann, sid, pa, pb))

    out_dir = Path(out_root) if out_root else MONTHLY_FIB_MAP_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_path = out_dir / "monthly_fib_map_clean.png"
    levels_path = out_dir / "monthly_fib_map_levels.png"
    labeled_path = out_dir / "monthly_fib_map_levels_labeled.png"
    index_path = out_dir / "monthly_fib_map_index.md"

    n = len(df)
    fig_w = max(20, min(n // 2, 50))
    base_title = f"{ref.symbol} 1M fib map  |  {len(drawn)} fibs (log)"
    _draw_map(
        df, drawn, clean_path, show_levels=False, title=f"{base_title}  |  CLEAN", fig_w=fig_w
    )
    _draw_map(
        df, drawn, levels_path, show_levels=True, title=f"{base_title}  |  LEVELS", fig_w=fig_w
    )
    levels_labeled: Path | None = None
    if label_levels:
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
    _write_index(index_path, ref, df, drawn, skipped)

    if skipped:
        print(f"WARNING: {len(skipped)} fib(s) not drawn (outside candle range):")
        for s in skipped:
            print(f"  - {s}")

    return MonthlyFibMap(
        clean=clean_path,
        levels=levels_path,
        index=index_path,
        fib_count=len(fibs),
        drawn=len(drawn),
        skipped=skipped,
        levels_labeled=levels_labeled,
    )


def _draw_map(
    df: pd.DataFrame,
    drawn: list[tuple[HumanFibAnnotation, str, int, int]],
    out_path: Path,
    *,
    show_levels: bool,
    title: str,
    fig_w: int,
    label_levels: bool = False,
) -> None:
    """Render candles + each fib's A→B leg, id, and (optionally) its levels.

    ``label_levels`` (only meaningful with ``show_levels``) writes ratio + rounded
    price at the right end of each level segment.
    """
    mc = mpf.make_marketcolors(up="#26a69a", down="#ef5350", inherit=True)
    style = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle=":",
        gridcolor="#cccccc",
        facecolor="#f5f5f5",
        figcolor="#ffffff",
        y_on_right=True,
    )
    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        title=title,
        figsize=(fig_w, 11),
        returnfig=True,
        warn_too_much_data=100_000,
    )
    ax = axes[0]

    # Log y-axis to match the TradingView log fib (math unchanged — see docstring).
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
    ax.tick_params(axis="y", which="minor", labelsize=6)

    handles: list[mpatches.Patch] = []
    for i, (ann, sid, pos_a, pos_b) in enumerate(drawn):
        color = _PALETTE(i % 10)
        price_a = float(ann.anchor_a.price)
        price_b = float(ann.anchor_b.price)

        # Each fib's levels are confined to its own monthly A→B segment.
        if show_levels:
            x0, x1 = sorted((pos_a, pos_b))
            for lv in ann.levels:
                is_boundary = lv.ratio in (0.0, 1.0)
                ax.plot(
                    [x0, x1],
                    [lv.price, lv.price],
                    color=color,
                    lw=1.4 if is_boundary else 0.8,
                    ls="--",
                    alpha=0.7 if is_boundary else 0.4,
                    zorder=2,
                )
                # Ratio + rounded price at the segment's right end (opt-in). Left
                # end carries the id label, so right keeps the two from colliding.
                if label_levels:
                    ax.annotate(
                        f"{lv.ratio} ({lv.price:,.1f})",
                        xy=(x1, lv.price),
                        xytext=(3, 0),
                        textcoords="offset points",
                        fontsize=6,
                        fontweight="bold" if is_boundary else "normal",
                        color=color,
                        va="center",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
                        zorder=6,
                    )

        # Diagonal A→B leg + anchor dots (direction is implicit in the slope).
        ax.plot([pos_a, pos_b], [price_a, price_b], color=color, lw=2.0, zorder=3)
        ax.scatter(
            [pos_a, pos_b],
            [price_a, price_b],
            color=color,
            s=36,
            zorder=4,
            edgecolors="white",
            linewidths=0.6,
        )

        # Short id near anchor_a — colour-coded text on a white box for contrast
        # across the full palette (white-on-light washes out).
        ax.annotate(
            sid,
            xy=(pos_a, price_a),
            xytext=(5, 10),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold",
            color=color,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, alpha=0.9),
            zorder=6,
        )

        arrow = "↑" if ann.direction == "up" else "↓"
        handles.append(mpatches.Patch(color=color, label=f"{sid} {arrow} {ann.direction}"))

    if handles:
        ax.legend(handles=handles, loc="upper left", fontsize=7, ncol=2, framealpha=0.85)

    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def _write_index(
    path: Path,
    ref: HumanFibAnnotation,
    df: pd.DataFrame,
    drawn: list[tuple[HumanFibAnnotation, str, int, int]],
    skipped: list[str],
) -> None:
    """Write the human-readable map index."""
    lines: list[str] = [
        f"# Monthly fib map — {ref.symbol} 1M",
        "",
        "Visual confirmation of the human-drawn 1M source fibs. Each fib's levels are",
        "drawn only across its own anchor-A→anchor-B monthly segment. No lower-timeframe",
        "events, no projection, no review-window scoping, no auto-fib.",
        "",
        f"- Charts: `{path.with_name('monthly_fib_map_clean.png').name}`, "
        f"`{path.with_name('monthly_fib_map_levels.png').name}`",
        f"- Candles: {ref.symbol} 1M (log scale), {df.index[0]:%Y-%m-%d} → {df.index[-1]:%Y-%m-%d}",
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

    # Per-fib level table so the map artifact records the exact level set itself
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
        lines += [
            "",
            "## ⚠ Not drawn (anchor outside candle range)",
            "",
        ]
        lines += [f"- {s}" for s in skipped]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    return REPO_ROOT / "data" / "labels" / "human_fib" / settings.data.exchange.lower() / sym / "1M"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the BTC/USD 1M monthly fib map (clean + levels views)."
    )
    p.add_argument(
        "--fib-dir",
        default=None,
        help="Directory of fib_*.json 1M annotations (default: BTC/USD 1M label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    p.add_argument(
        "--label-levels",
        action="store_true",
        help="Also write monthly_fib_map_levels_labeled.png with ratio+price on each level",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    result = render_monthly_fib_map(
        fib_dir=fib_dir,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        label_levels=args.label_levels,
    )
    print(f"Monthly fib map: {result.drawn}/{result.fib_count} fibs drawn")
    print(f"  clean:  {result.clean}")
    print(f"  levels: {result.levels}")
    if result.levels_labeled:
        print(f"  labeled: {result.levels_labeled}")
    print(f"  index:  {result.index}")
