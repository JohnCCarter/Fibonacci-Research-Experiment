"""4H source-fib map — annual visual confirmation of the human **4H** source fibs.

Renders every human-drawn BTC/USD **4H** source fib on the 4H candle chart, grouped
by ``anchor_a`` year so 366 fibs become ~10 fast-scan maps instead of one unreadable
wall. This answers one question per group: *"Are my anchor pins on the correct
structural swings on the 4H chart?"* — source-quality review, **not** reaction-review.

    experiments/review/fourh_source_fib_map/
        fourh_source_fib_map_2017_h1_4h_clean.png   fourh_source_fib_map_2017_h1_4h_levels.png
        fourh_source_fib_map_2017_h2_4h_clean.png   fourh_source_fib_map_2017_h2_4h_levels.png
        fourh_source_fib_map_2018_4h_clean.png      fourh_source_fib_map_2018_4h_levels.png
        ...
        fourh_source_fib_map_index.md

Each fib's levels are confined to its own ``anchor_a→anchor_b`` 4H segment. 4H is the
lowest active timeframe (1H paused), so there is no cross-TF projection and no snap:
the source TF *is* the chart TF, so anchors pin to the nearest 4H bar exactly (like
``monthly_fib_map``). A dense year (more than ``_DENSE_YEAR_THRESHOLD`` fibs) is split
into half-years so no single map is hopelessly crowded; the residual crowding of a
busy half-year is itself the signal that per-fib zoom (Tier 2) is warranted there.

Strict separation (this module is **only** for true 4H source fibs):

- Input is the **4H** human-fib dir; every loaded fib must have ``timeframe == "4h"``
  (fail-closed — pointing ``--fib-dir`` at the 1D/1W folder is refused).
- No auto-fib, no anchor inference, no forward projection, no review-window scope,
  no event markers, no trading logic. The fib *math* is untouched — level prices come
  straight from the annotation.

The rendering primitives (``_draw_map``) and loaders (``_load_fibs``, ``_nearest_pos``,
``_short_id``) are reused unchanged from ``monthly_fib_map`` so the visual style is
identical. Importing them also installs the Agg backend.

Usage::

    python -m fibengine.research.fourh_source_fib_map \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/4h \\
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

FOURH_SOURCE_FIB_MAP_ROOT = REPO_ROOT / "experiments" / "review" / "fourh_source_fib_map"

# The fib timeframe this module is allowed to consume. Anything else is refused.
SOURCE_TF = "4h"

# 4H context pad (bars before the earliest anchor_a / after the latest anchor_b in a
# group) so the fib era isn't pinned to a chart edge. 40 four-hour bars ≈ 1 week.
_CONTEXT_PAD_BARS = 40

# A year with more than this many fibs is split into half-years (H1 = anchor_a month
# 1–6, H2 = 7–12) so a single map stays scannable. Verified pre-build: 2017 = 116.
_DENSE_YEAR_THRESHOLD = 60

# Profile / scale the 4H source fibs must carry (BTC monthly-first protocol).
_REQUIRED_PROFILE = "tradingview_log_chamoun"
_REQUIRED_SCALE = "log"
_FORBIDDEN_RATIO = 0.236
_RATIO_TOL = 1e-6
# Substrings that mark a non-human / inferred fib (must never reach a source map).
_FORBIDDEN_TOKENS = ("candidate", "auto", "inferred")


@dataclass
class GroupArtifacts:
    """Artifacts rendered for one fib group (a year or a year-half)."""

    label: str
    fib_count: int
    drawn: int
    clean: Path | None = None
    levels: Path | None = None
    levels_labeled: Path | None = None
    window_start: str | None = None
    window_end: str | None = None
    skipped: list[str] = field(default_factory=list)


@dataclass
class FourhSourceFibMap:
    """Result of rendering the annual 4H source-fib maps."""

    per_group: list[GroupArtifacts]
    index: Path
    fib_count: int


def _validate_source_fibs(fibs: list[HumanFibAnnotation]) -> None:
    """Fail-closed guard: every fib must be a true, human, 4H log source fib.

    Raises ``ValueError`` listing every violation. The ``timeframe == "4h"`` check
    is the structural guarantee that this module cannot consume 1D/1W/1M fibs even if
    ``--fib-dir`` is pointed at the wrong folder.
    """
    violations: list[str] = []
    for ann in fibs:
        sid = ann.fib_id or _short_id(ann)
        if ann.timeframe != SOURCE_TF:
            violations.append(f"{sid}: timeframe {ann.timeframe!r} != {SOURCE_TF!r} (not a 4H fib)")
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
            "fourh_source_fib_map refuses non-4H-source fibs:\n  - " + "\n  - ".join(violations)
        )


def _group_by_year(
    fibs: list[HumanFibAnnotation], dense_threshold: int
) -> list[tuple[str, list[HumanFibAnnotation]]]:
    """Group fibs by ``anchor_a`` year, splitting dense years into half-years.

    Returns ``(label, members)`` pairs in chronological order. ``members`` preserve
    the time-sorted order from ``_load_fibs``. A year with more than ``dense_threshold``
    fibs yields ``"<year>_h1"`` / ``"<year>_h2"`` (omitting an empty half); otherwise a
    single ``"<year>"`` group.
    """
    by_year: dict[int, list[HumanFibAnnotation]] = {}
    for ann in fibs:
        year = pd.to_datetime(ann.anchor_a.time, utc=True).year
        by_year.setdefault(year, []).append(ann)

    groups: list[tuple[str, list[HumanFibAnnotation]]] = []
    for year in sorted(by_year):
        members = by_year[year]
        if len(members) > dense_threshold:
            h1 = [a for a in members if pd.to_datetime(a.anchor_a.time, utc=True).month <= 6]
            h2 = [a for a in members if pd.to_datetime(a.anchor_a.time, utc=True).month > 6]
            if h1:
                groups.append((f"{year}_h1", h1))
            if h2:
                groups.append((f"{year}_h2", h2))
        else:
            groups.append((str(year), members))
    return groups


def render_fourh_source_fib_map(
    fib_dir: Path | str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    label_levels: bool = False,
    dense_threshold: int = _DENSE_YEAR_THRESHOLD,
) -> FourhSourceFibMap:
    """Render per-year clean + levels maps of the 4H source fibs + a shared index.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` **4H** annotations.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``FOURH_SOURCE_FIB_MAP_ROOT``.
    label_levels:
        When True, also write a ``..._{label}_4h_levels_labeled.png`` per group with
        ratio + rounded price on each level segment.
    dense_threshold:
        Years with more than this many fibs are split into half-years.
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")
    _validate_source_fibs(fibs)  # fail-closed before any rendering

    ref = fibs[0]  # all fibs share symbol/exchange (BTC/USD bitfinex protocol)
    out_dir = Path(out_root) if out_root else FOURH_SOURCE_FIB_MAP_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load the 4H candles once; every group is a slice of this frame.
    data_cfg = settings.data.model_copy(
        update={"symbol": ref.symbol, "timeframe": SOURCE_TF, "exchange": ref.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)  # never auto-fetch

    groups = _group_by_year(fibs, dense_threshold)
    per_group = [
        _render_group(members, ref, label, df_full, out_dir, label_levels)
        for label, members in groups
    ]

    index_path = out_dir / "fourh_source_fib_map_index.md"
    _write_index(index_path, ref, fibs, per_group, dense_threshold)

    return FourhSourceFibMap(per_group=per_group, index=index_path, fib_count=len(fibs))


def _render_group(
    members: list[HumanFibAnnotation],
    ref: HumanFibAnnotation,
    label: str,
    df_full: pd.DataFrame,
    out_dir: Path,
    label_levels: bool,
) -> GroupArtifacts:
    """Window ``df_full`` to this group's fib span and render clean + levels.

    The window is ``[min(anchor_a) − pad, max(anchor_b) + pad]`` over the group's
    anchors (not calendar boundaries), so a December-anchored fib whose ``anchor_b``
    crosses into the next year still renders its full leg. A fib whose anchor falls
    outside the candle range is surfaced in ``skipped``, never dropped silently.
    """
    anchor_positions: list[int] = []
    for ann in members:
        for t in (ann.anchor_a.time, ann.anchor_b.time):
            pos = _nearest_pos(df_full, pd.to_datetime(t, utc=True))
            if pos is not None:
                anchor_positions.append(pos)

    if not anchor_positions:
        # Whole group beyond the cache — nothing to draw, surface every fib.
        skipped = [f"{_short_id(a)} (anchors beyond 4h candle range)" for a in members]
        return GroupArtifacts(label=label, fib_count=len(members), drawn=0, skipped=skipped)

    lo = max(0, min(anchor_positions) - _CONTEXT_PAD_BARS)
    hi = min(len(df_full) - 1, max(anchor_positions) + _CONTEXT_PAD_BARS)
    df = df_full.iloc[lo : hi + 1]

    drawn: list[tuple[HumanFibAnnotation, str, int, int]] = []
    skipped: list[str] = []
    for ann in members:
        sid = _short_id(ann)
        pa = _nearest_pos(df, pd.to_datetime(ann.anchor_a.time, utc=True))
        pb = _nearest_pos(df, pd.to_datetime(ann.anchor_b.time, utc=True))
        if pa is None or pb is None:
            edge = "anchor_a" if pa is None else "anchor_b"
            t = ann.anchor_a.time if pa is None else ann.anchor_b.time
            skipped.append(f"{sid} ({edge} {t} beyond 4h candle range)")
            continue
        drawn.append((ann, sid, pa, pb))

    clean_path = out_dir / f"fourh_source_fib_map_{label}_4h_clean.png"
    levels_path = out_dir / f"fourh_source_fib_map_{label}_4h_levels.png"
    n = len(df)
    fig_w = max(20, min(n // 2, 50))
    base_title = f"{ref.symbol} 4H source fib map {label}  |  {len(drawn)} fibs (log)"
    _draw_map(
        df, drawn, clean_path, show_levels=False, title=f"{base_title}  |  CLEAN", fig_w=fig_w
    )
    _draw_map(
        df, drawn, levels_path, show_levels=True, title=f"{base_title}  |  LEVELS", fig_w=fig_w
    )

    levels_labeled: Path | None = None
    if label_levels:
        labeled_path = out_dir / f"fourh_source_fib_map_{label}_4h_levels_labeled.png"
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
        print(f"WARNING [{label}]: {len(skipped)} fib(s) not drawn (outside candle range):")
        for s in skipped:
            print(f"  - {s}")

    return GroupArtifacts(
        label=label,
        fib_count=len(members),
        drawn=len(drawn),
        clean=clean_path,
        levels=levels_path,
        levels_labeled=levels_labeled,
        window_start=f"{df.index[0]:%Y-%m-%d}",
        window_end=f"{df.index[-1]:%Y-%m-%d}",
        skipped=skipped,
    )


def _write_index(
    path: Path,
    ref: HumanFibAnnotation,
    fibs: list[HumanFibAnnotation],
    per_group: list[GroupArtifacts],
    dense_threshold: int,
) -> None:
    """Write the combined human-readable index (group summary + per-fib tables)."""
    dense = [art.label for art in per_group if "_h" in art.label]
    lines: list[str] = [
        f"# 4H source fib map — {ref.symbol} (annual)",
        "",
        "Visual confirmation / source-quality review of the human-drawn **4H source",
        "fibs**, grouped by anchor_a year (dense years split into half-years). Each",
        "fib's levels are drawn only across its own anchor-A→anchor-B 4H segment.",
        "Source-quality review, **not** reaction-review: no events, no projection, no",
        "review-window scoping, no auto-fib, no trading logic.",
        "",
        f"- Fibs loaded: {len(fibs)}",
        f"- Groups: {len(per_group)} (dense-year split threshold: {dense_threshold})",
    ]
    if dense:
        lines.append(f"- Half-year splits: {', '.join(dense)}")
    lines += [
        "",
        "## Groups",
        "",
        "| Group | Fibs | Drawn | Window | Charts |",
        "|-------|------|-------|--------|--------|",
    ]
    for art in per_group:
        charts = f"`{art.clean.name}`, `{art.levels.name}`" if art.clean else "—"
        window = f"{art.window_start} → {art.window_end}" if art.window_start else "—"
        lines.append(
            f"| {art.label} | {art.fib_count} | {art.drawn}/{art.fib_count} | {window} | {charts} |"
        )

    # Per-fib anchor table (self-contained record; group via the anchor_a year).
    lines += [
        "",
        "## Fibs (anchor A → anchor B)",
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

    skipped_groups = [art for art in per_group if art.skipped]
    if skipped_groups:
        lines += ["", "## ⚠ Not drawn (anchor outside candle range)", ""]
        for art in skipped_groups:
            lines.append(f"- **{art.label}**:")
            lines += [f"  - {s}" for s in art.skipped]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    exch = settings.data.exchange.lower()
    return REPO_ROOT / "data" / "labels" / "human_fib" / exch / sym / SOURCE_TF


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the BTC/USD 4H source-fib annual maps (clean + levels per year)."
    )
    p.add_argument(
        "--fib-dir",
        default=None,
        help="Directory of fib_*.json 4H annotations (default: BTC/USD 4H label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    p.add_argument(
        "--dense-threshold",
        type=int,
        default=_DENSE_YEAR_THRESHOLD,
        help=f"Split a year into half-years above this fib count (default {_DENSE_YEAR_THRESHOLD})",
    )
    p.add_argument(
        "--label-levels",
        action="store_true",
        help="Also write a ..._{label}_4h_levels_labeled.png per group with ratio+price labels",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    result = render_fourh_source_fib_map(
        fib_dir=fib_dir,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        label_levels=args.label_levels,
        dense_threshold=args.dense_threshold,
    )
    print(f"4H source fib map: {result.fib_count} fibs across {len(result.per_group)} group(s)")
    for art in result.per_group:
        extra = f", labeled={art.levels_labeled.name}" if art.levels_labeled else ""
        charts = f"{art.clean.name}, {art.levels.name}{extra}" if art.clean else "(no chart)"
        print(f"  [{art.label}] drawn {art.drawn}/{art.fib_count}  -> {charts}")
        if art.skipped:
            print(f"        skipped: {len(art.skipped)}")
    print(f"  index: {result.index}")
