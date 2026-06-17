"""4H source-fib zoom — per-fib windowed visual confirmation for scoped groups.

Renders a pair of per-fib 4H zoom charts (clean + levels) for the groups where the
Tier-1 annual map (`fourh_source_fib_map.py`) showed per-fib zoom is necessary:

- **2017_h2** — the Sep–Dec 2017 parabolic run has 103 fibs in 4 months; the annual
  map is globally unreadable. Every fib in H2 2017 gets its own windowed chart.
- **2021_dec2020_mar2021** — the initial 2020/2021 bull-leg creates a dense cluster in
  the 2021 map between Jan–Mar 2021. Only those ~37 fibs need per-fib zoom; the rest
  of the 2021 group is map-OK.

All other groups (2017_h1, 2018, 2019, 2020, 2022, 2023, 2024, 2025, 2026) are
map-OK and do **not** have a scope defined here.

Output::

    experiments/review/fourh_source_fib_zoom/
        2017_h2/
            fib_BTC-USD_4h_20170801T040000/
                4h_clean.png
                4h_levels.png
            ...
        2021_dec2020_mar2021/
            fib_BTC-USD_4h_20210105T040000/
                4h_clean.png
                4h_levels.png
            ...

Strict separation (same constraints as ``fourh_source_fib_map``):

- Only true 4H human source fibs; timeframe guard is fail-closed.
- No auto-fib, no anchor inference, no forward projection, no review-window scope,
  no event markers, no ``source_fib_projection_review``, no ``review_sample.csv``.
- Source-quality review only: "Is this anchor on the right 4H structural swing?"

Reuses ``_draw_map``, ``_load_fibs``, ``_nearest_pos``, ``_short_id`` from
``monthly_fib_map`` unchanged (same visual style as Tier 1 maps).

Usage::

    python -m fibengine.research.fourh_source_fib_zoom \\
        --scope 2017_h2 \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/4h \\
        --config config/settings.expansion.yaml

    python -m fibengine.research.fourh_source_fib_zoom \\
        --scope 2021_dec2020_mar2021 \\
        --fib-id fib_BTC-USD_4h_20210108T040000 \\
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

FOURH_SOURCE_FIB_ZOOM_ROOT = REPO_ROOT / "experiments" / "review" / "fourh_source_fib_zoom"

SOURCE_TF = "4h"

# Context before anchor_a and after anchor_b in a per-fib zoom window.
# 40 four-hour bars ≈ 1 week — same as fourh_source_fib_map for visual consistency.
_CONTEXT_PAD_BARS = 40

# Guards — identical to fourh_source_fib_map.
_REQUIRED_PROFILE = "tradingview_log_chamoun"
_REQUIRED_SCALE = "log"
_FORBIDDEN_RATIO = 0.236
_RATIO_TOL = 1e-6
_FORBIDDEN_TOKENS = ("candidate", "auto", "inferred")

# Tier 1 review (2026-06-15) identified exactly these two scopes as needing per-fib
# zoom. All other annual groups are map-OK and must not be added here without a new
# review decision.
SCOPE_2017_H2 = "2017_h2"
SCOPE_2021_DEC2020_MAR2021 = "2021_dec2020_mar2021"
_VALID_SCOPES = (SCOPE_2017_H2, SCOPE_2021_DEC2020_MAR2021)


@dataclass
class ZoomArtifacts:
    """Artifacts rendered for one fib in a zoom scope."""

    fib_id: str
    scope: str
    clean: Path | None = None
    levels: Path | None = None
    skipped: bool = False
    skip_reason: str | None = None


@dataclass
class FourhSourceFibZoom:
    """Result of a zoom render run for one scope."""

    scope: str
    artifacts: list[ZoomArtifacts]
    fib_count: int
    rendered: int
    skipped: list[str] = field(default_factory=list)


def _validate_source_fibs(fibs: list[HumanFibAnnotation]) -> None:
    """Fail-closed guard: every fib must be a true, human, 4H log source fib.

    Raises ``ValueError`` listing every violation. Mirror of the guard in
    ``fourh_source_fib_map`` — kept local so this module has no import dependency on it.
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
            "fourh_source_fib_zoom refuses non-4H-source fibs:\n  - " + "\n  - ".join(violations)
        )


def _select_scope(
    fibs: list[HumanFibAnnotation],
    scope: str,
    fib_id: str | None = None,
) -> list[HumanFibAnnotation]:
    """Return fibs matching ``scope``, optionally narrowed to a single ``fib_id``.

    Scope definitions (from Tier 1 review 2026-06-15):

    ``2017_h2``
        anchor_a year=2017, month ≥ 7. Mirrors the half-year split used by
        ``fourh_source_fib_map._group_by_year`` at the ``_DENSE_YEAR_THRESHOLD``.

    ``2021_dec2020_mar2021``
        anchor_a in [2021-01-01, 2021-04-01). The "Dec 2020 → Mar 2021" name
        describes the price-action period (initial 2020/2021 bull leg); the
        anchor_a filter starts at 2021-01-01 because Dec 2020 fibs (anchor_a
        year=2020) belong to the 2020 annual group, which is map-OK.

    Raises ``ValueError`` for unknown scope or a ``fib_id`` that does not match any
    fib in the resolved scope.
    """
    if scope not in _VALID_SCOPES:
        raise ValueError(f"Unknown scope {scope!r}; valid scopes: {_VALID_SCOPES}")

    if scope == SCOPE_2017_H2:
        selected = [
            ann
            for ann in fibs
            if (t := pd.to_datetime(ann.anchor_a.time, utc=True)).year == 2017 and t.month >= 7
        ]
    else:  # SCOPE_2021_DEC2020_MAR2021
        _win_start = pd.Timestamp("2021-01-01", tz="UTC")
        _win_end = pd.Timestamp("2021-04-01", tz="UTC")
        selected = [
            ann
            for ann in fibs
            if _win_start <= pd.to_datetime(ann.anchor_a.time, utc=True) < _win_end
        ]

    if fib_id is not None:
        selected = [ann for ann in selected if ann.fib_id == fib_id]
        if not selected:
            raise ValueError(
                f"fib_id {fib_id!r} not found in scope {scope!r} "
                f"(check the full fib_id, e.g. fib_BTC-USD_4h_YYYYMMDDTHHMMSS)"
            )

    return selected


def _render_fib_zoom(
    ann: HumanFibAnnotation,
    df_full: pd.DataFrame,
    scope: str,
    out_dir: Path,
) -> ZoomArtifacts:
    """Render clean + levels zoom charts for one fib, windowed to its A→B span.

    The window is ``[min(pos_a, pos_b) − pad, max(pos_a, pos_b) + pad]`` in bar
    indices, clamped to the candle range. A fib whose anchors fall outside the cache
    is surfaced as skipped (never silently dropped).
    """
    fib_id = ann.fib_id or _short_id(ann)
    ta = pd.to_datetime(ann.anchor_a.time, utc=True)
    tb = pd.to_datetime(ann.anchor_b.time, utc=True)

    pa_full = _nearest_pos(df_full, ta)
    pb_full = _nearest_pos(df_full, tb)

    if pa_full is None or pb_full is None:
        edge = "anchor_a" if pa_full is None else "anchor_b"
        return ZoomArtifacts(
            fib_id=fib_id,
            scope=scope,
            skipped=True,
            skip_reason=f"{fib_id}: {edge} beyond 4h candle range",
        )

    lo = max(0, min(pa_full, pb_full) - _CONTEXT_PAD_BARS)
    hi = min(len(df_full) - 1, max(pa_full, pb_full) + _CONTEXT_PAD_BARS)
    df = df_full.iloc[lo : hi + 1]

    pa = _nearest_pos(df, ta)
    pb = _nearest_pos(df, tb)
    if pa is None or pb is None:
        return ZoomArtifacts(
            fib_id=fib_id,
            scope=scope,
            skipped=True,
            skip_reason=f"{fib_id}: anchor not resolvable in sliced window",
        )

    fib_out = out_dir / scope / fib_id
    fib_out.mkdir(parents=True, exist_ok=True)

    sid = _short_id(ann)
    a_str = ta.strftime("%Y-%m-%d")
    b_str = tb.strftime("%Y-%m-%d")
    title = f"{ann.symbol} 4H zoom  {sid}  |  {ann.direction}  {a_str} → {b_str}  (log)"

    n = len(df)
    fig_w = max(12, min(n // 2, 30))
    clean_path = fib_out / "4h_clean.png"
    levels_path = fib_out / "4h_levels.png"
    drawn = [(ann, sid, pa, pb)]

    _draw_map(df, drawn, clean_path, show_levels=False, title=f"{title}  |  CLEAN", fig_w=fig_w)
    _draw_map(df, drawn, levels_path, show_levels=True, title=f"{title}  |  LEVELS", fig_w=fig_w)

    return ZoomArtifacts(fib_id=fib_id, scope=scope, clean=clean_path, levels=levels_path)


def render_fourh_source_fib_zoom(
    fib_dir: Path | str,
    scope: str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    fib_id: str | None = None,
) -> FourhSourceFibZoom:
    """Render per-fib 4H zoom charts for all fibs in the given scope.

    Parameters
    ----------
    fib_dir:
        Directory holding the ``fib_*.json`` **4H** annotations.
    scope:
        One of ``"2017_h2"`` or ``"2021_dec2020_mar2021"``.
    settings:
        Loaded ``Settings``; falls back to ``load_settings()``.
    out_root:
        Output directory. Defaults to ``FOURH_SOURCE_FIB_ZOOM_ROOT``.
    fib_id:
        If set, render only this specific fib (full fib_id string, e.g.
        ``fib_BTC-USD_4h_20210108T040000``). Must be present in the resolved scope.
    """
    if settings is None:
        settings = load_settings()

    fib_dir = Path(fib_dir)
    fibs = _load_fibs(fib_dir)
    if not fibs:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")
    _validate_source_fibs(fibs)

    selected = _select_scope(fibs, scope, fib_id=fib_id)
    if not selected:
        raise ValueError(
            f"Scope {scope!r} selected 0 fibs from {fib_dir} — verify scope definition and fib_dir"
        )

    ref = fibs[0]
    out_dir = Path(out_root) if out_root else FOURH_SOURCE_FIB_ZOOM_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)

    data_cfg = settings.data.model_copy(
        update={"symbol": ref.symbol, "timeframe": SOURCE_TF, "exchange": ref.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)

    artifacts = [_render_fib_zoom(ann, df_full, scope, out_dir) for ann in selected]

    rendered = sum(1 for a in artifacts if not a.skipped)
    skipped_reasons = [a.skip_reason for a in artifacts if a.skipped and a.skip_reason]
    for reason in skipped_reasons:
        print(f"WARNING: {reason}")

    return FourhSourceFibZoom(
        scope=scope,
        artifacts=artifacts,
        fib_count=len(selected),
        rendered=rendered,
        skipped=skipped_reasons,
    )


def _default_fib_dir(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    exch = settings.data.exchange.lower()
    return REPO_ROOT / "data" / "labels" / "human_fib" / exch / sym / SOURCE_TF


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Render per-fib 4H zoom charts for scoped groups identified by Tier 1 map review."
        )
    )
    p.add_argument(
        "--scope",
        required=True,
        choices=list(_VALID_SCOPES),
        help="Zoom scope: '2017_h2' (full, 103 fibs) or '2021_dec2020_mar2021' (partial, ~37 fibs)",
    )
    p.add_argument(
        "--fib-dir",
        default=None,
        help="Directory of fib_*.json 4H annotations (default: BTC/USD 4H label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    p.add_argument(
        "--fib-id",
        default=None,
        help="Full fib_id to render (e.g. fib_BTC-USD_4h_20210108T040000); renders all if omitted",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_dir = Path(args.fib_dir) if args.fib_dir else _default_fib_dir(settings)
    result = render_fourh_source_fib_zoom(
        fib_dir=fib_dir,
        scope=args.scope,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        fib_id=args.fib_id,
    )
    print(
        f"4H source fib zoom [{result.scope}]: "
        f"{result.rendered}/{result.fib_count} rendered"
        + (f", {len(result.skipped)} skipped" if result.skipped else "")
    )
    for art in result.artifacts:
        if art.skipped:
            print(f"  SKIP  {art.fib_id}: {art.skip_reason}")
        else:
            assert art.clean and art.levels
            print(f"  OK    {art.fib_id}")
            print(f"          {art.clean}")
            print(f"          {art.levels}")
