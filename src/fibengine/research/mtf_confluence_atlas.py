"""MTF confluence visual atlas — per-cluster confluence cards (Checkpoint 3, slice 1).

Renders a single *confluence card* for one structurally-resolved MTF cluster from the
locked BTC/USD source-fib corpus. A confluence card is a **horizontal price-band**
phenomenon over a time window — members from several timeframes whose stored fib levels
coincide in log-price — drawn on a candle backdrop. This is *not* the per-fib diagonal
``A→B`` view of ``monthly_fib_map`` / ``fourh_source_fib_map``; the levels are drawn as
horizontal lines **across the whole window**, because that is what a confluence is.

**Slice 1 scope (deliberately minimal):** only the single robust 4-TF cluster (c001,
~29274, 2021 cycle) under the **fixed-band** method at the primary ``epsilon_log = 0.005``,
on a **1d** candle backdrop. This is the CP2-corrected, method-stable confluence — the one
cluster that survives as a tight 4-TF agreement under both clustering definitions.

The target cluster is resolved by **structural signature**, never by a hard-coded
``cluster_id`` (ids are positional and method-dependent — ``order_clusters`` re-numbers).
Resolution is fail-closed: zero or multiple signature matches stop with a clear error.

Strict separation / non-goals (same spirit as the source-fib renderers):

- fixed-band first; no side-by-side, no single-linkage contrast in this slice.
- No 1H (the corpus has none; a 1H member would fail-closed). No reaction-review, no
  events, no projection, no auto-fib, no anchor inference, no trading/signal/edge claim.
- Superseded ``20250506T080000`` must never appear in a member (fail-closed).
- Output is written under ``experiments/review/mtf_confluence_atlas/`` (gitignored); no
  PNG is committed.

Usage::

    python -m fibengine.research.mtf_confluence_atlas \\
        --fib-root data/labels/human_fib/bitfinex/BTC-USD \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import mplfinance as mpf  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.core.config import REPO_ROOT, Settings, load_settings  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.labeling.human_fib import load_annotation  # noqa: E402
from fibengine.research.monthly_fib_map import _nearest_pos  # noqa: E402
from fibengine.research.mtf_confluence import (  # noqa: E402
    ConfluenceCluster,
    LevelRow,
    cluster_confluence_fixed_band,
    flatten_levels,
)

MTF_CONFLUENCE_ATLAS_ROOT = REPO_ROOT / "experiments" / "review" / "mtf_confluence_atlas"

METHOD = "fixed_band"
DEFAULT_EPSILON_LOG = 0.005
DEFAULT_BACKDROP_TF = "1d"

# 1d backdrop pad: candles before/after the cluster time window so the confluence band
# is not pinned to a chart edge. ~30 daily bars ≈ one month of context each side.
_CONTEXT_PAD_BARS = 30

# A superseded fib must never appear in a confluence member (it is deleted on disk, but
# guard anyway so a stale cache or a regression cannot silently reintroduce it).
_SUPERSEDED_TOKENS = ("20250506T080000",)

# Timeframes the atlas is allowed to consume. A member outside this set (e.g. 1h) is a
# fail-closed error — slice 1 is strictly the four active higher timeframes.
_ALLOWED_TIMEFRAMES = ("1M", "1w", "1d", "4h")

# Stable per-timeframe colours for member level lines (fixed, not palette-indexed, so the
# legend reads the same across runs).
_TF_COLORS = {
    "1M": "#8e24aa",  # purple
    "1w": "#1e88e5",  # blue
    "1d": "#43a047",  # green
    "4h": "#fb8c00",  # orange
}


@dataclass(frozen=True)
class ClusterSignature:
    """Structural fingerprint used to resolve a target cluster without an id.

    All criteria must hold for a match. ``timeframes`` is the *exact* set; ``price_approx``
    matches when ``|representative_price - price_approx| <= price_tol``; ``max_span_log``
    bounds ``price_span_log``; ``window_year`` (when set) requires both window endpoints to
    fall in that calendar year.
    """

    tf_count: int
    timeframes: frozenset[str]
    price_approx: float
    price_tol: float
    max_span_log: float
    window_year: int | None = None
    label: str = "cluster"


# Slice 1 target: the robust 4-TF confluence (c001 under both methods), ~29274, 2021 cycle.
C001_SIGNATURE = ClusterSignature(
    tf_count=4,
    timeframes=frozenset({"1M", "1w", "1d", "4h"}),
    price_approx=29274.0,
    price_tol=200.0,
    max_span_log=DEFAULT_EPSILON_LOG,
    window_year=2021,
    label="c001",
)


@dataclass
class ConfluenceCard:
    """Result of rendering one confluence card."""

    cluster_id: str
    signature_label: str
    method: str
    epsilon_log: float
    backdrop_tf: str
    representative_price: float
    min_price: float
    max_price: float
    price_span_log: float
    timeframe_count: int
    timeframes: tuple[str, ...]
    ratios: tuple[float, ...]
    member_fib_ids: tuple[str, ...]
    member_levels: list[dict] = field(default_factory=list)
    window_start: str | None = None
    window_end: str | None = None
    clean: Path | None = None
    levels: Path | None = None


def resolve_cluster(
    clusters: list[ConfluenceCluster], signature: ClusterSignature
) -> ConfluenceCluster:
    """Return the single cluster matching ``signature``; fail-closed otherwise.

    Raises ``ValueError`` if zero or more than one cluster matches — the atlas must never
    guess which cluster a card is about.
    """
    matches = [c for c in clusters if _matches(c, signature)]
    if len(matches) == 0:
        raise ValueError(
            f"No cluster matches signature {signature.label!r} "
            f"(tf_count={signature.tf_count}, timeframes={sorted(signature.timeframes)}, "
            f"price≈{signature.price_approx}±{signature.price_tol}, "
            f"span≤{signature.max_span_log}, year={signature.window_year}). "
            "Corpus or epsilon changed — re-check the signature before rendering."
        )
    if len(matches) > 1:
        ids = ", ".join(f"{c.cluster_id}@{c.representative_price}" for c in matches)
        raise ValueError(
            f"Ambiguous signature {signature.label!r}: {len(matches)} clusters match ({ids}). "
            "Tighten the signature before rendering."
        )
    return matches[0]


def _matches(c: ConfluenceCluster, sig: ClusterSignature) -> bool:
    if c.timeframe_count != sig.tf_count:
        return False
    if frozenset(c.timeframes) != sig.timeframes:
        return False
    if abs(c.representative_price - sig.price_approx) > sig.price_tol:
        return False
    if c.price_span_log > sig.max_span_log:
        return False
    if sig.window_year is not None:
        ws = pd.to_datetime(c.time_window_start, utc=True).year
        we = pd.to_datetime(c.time_window_end, utc=True).year
        if ws != sig.window_year or we != sig.window_year:
            return False
    return True


def band_member_rows(rows: list[LevelRow], cluster: ConfluenceCluster) -> list[LevelRow]:
    """Reconstruct the level rows that form ``cluster`` (deterministic, source-traceable).

    A fixed-band cluster's members are exactly the level rows whose fib is a member and
    whose price lies inside the cluster's ``[min_price, max_price]`` band. Returned sorted
    by (timeframe order, price) for stable rendering and summaries.
    """
    members = set(cluster.member_fib_ids)
    band = [
        r
        for r in rows
        if r.fib_id in members and cluster.min_price <= r.level_price <= cluster.max_price
    ]
    tf_rank = {tf: i for i, tf in enumerate(_ALLOWED_TIMEFRAMES)}
    band.sort(key=lambda r: (tf_rank.get(r.timeframe, len(tf_rank)), r.level_price))
    return band


def _guard_members(band: list[LevelRow]) -> None:
    """Fail-closed checks on the resolved confluence members.

    - No member may be a superseded fib (token match on id/source path).
    - Every member timeframe must be in ``_ALLOWED_TIMEFRAMES`` (no 1H in slice 1).
    """
    violations: list[str] = []
    for r in band:
        for token in _SUPERSEDED_TOKENS:
            if token in r.fib_id or token in r.source_path:
                violations.append(f"{r.fib_id}: superseded fib {token!r} present in a member")
        if r.timeframe not in _ALLOWED_TIMEFRAMES:
            violations.append(
                f"{r.fib_id}: timeframe {r.timeframe!r} not in {_ALLOWED_TIMEFRAMES} "
                "(no 1H / off-protocol timeframe in the atlas)"
            )
    if violations:
        raise ValueError(
            "mtf_confluence_atlas refuses the resolved cluster:\n  - " + "\n  - ".join(violations)
        )


def _ref_symbol_exchange(band: list[LevelRow]) -> tuple[str, str]:
    """Load one member annotation to recover symbol/exchange (source-traceable)."""
    ann = load_annotation(Path(band[0].source_path))
    return ann.symbol, ann.exchange


def _candle_backdrop(df: pd.DataFrame, title: str, fig_w: int):
    """Build the candle backdrop with the shared log-scale style (new fig/ax).

    Reuses the same marketcolors / grid / log-axis treatment as ``monthly_fib_map._draw_map``
    so the visual style matches the source-fib renderers; the confluence overlays are new.
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
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
    ax.tick_params(axis="y", which="minor", labelsize=6)
    return fig, ax


def _annotate_metadata(ax, card_meta: dict) -> None:
    """Bottom-left metadata box: method, epsilon, span, tf_count (CP2-corrected headline)."""
    text = (
        f"method={card_meta['method']}  epsilon_log={card_meta['epsilon_log']}\n"
        f"price_span_log={card_meta['price_span_log']}  tf_count={card_meta['tf_count']}\n"
        f"band {card_meta['min_price']:,.0f}–{card_meta['max_price']:,.0f}  "
        f"repr {card_meta['representative_price']:,.0f}"
    )
    ax.text(
        0.012,
        0.012,
        text,
        transform=ax.transAxes,
        fontsize=8,
        family="monospace",
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#888888", alpha=0.9),
        zorder=7,
    )


def _short_fib(fib_id: str) -> str:
    """Compact member id: drop the ``fib_BTC-USD_<tf>_`` prefix, keep the timestamp tail."""
    return fib_id.split("_")[-1]


def _annotate_member_table(ax, band: list[LevelRow]) -> None:
    """Top-left member table (TF / ratio / price / short fib id) — replaces stacked labels.

    Because the four members sit within ~$36 their per-line labels would overlap and hide
    each other; a compact table keeps every member individually source-traceable while the
    level lines stay clean.
    """
    lines = ["member levels (fixed-band)", "TF  ratio  price    fib"]
    for r in band:
        lines.append(
            f"{r.timeframe:<3} {r.ratio:<5g} {r.level_price:>7,.0f}  {_short_fib(r.fib_id)}"
        )
    ax.text(
        0.012,
        0.985,
        "\n".join(lines),
        transform=ax.transAxes,
        fontsize=8,
        family="monospace",
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#888888", alpha=0.9),
        zorder=7,
    )


def _draw_card(
    df: pd.DataFrame,
    band: list[LevelRow],
    cluster: ConfluenceCluster,
    out_path: Path,
    *,
    title: str,
    show_members: bool,
    fig_w: int,
    card_meta: dict,
) -> None:
    """Render one confluence card.

    ``show_members=False`` (clean): candle backdrop + shaded ``[min,max]`` confluence band
    + representative-price line + metadata box. ``show_members=True`` (levels): adds one
    horizontal line per member level, coloured by timeframe, plus a top-left member table
    (TF / ratio / price / short fib id) so every member stays source-traceable without the
    near-coincident per-line labels overlapping.
    """
    fig, ax = _candle_backdrop(df, title, fig_w)

    # The confluence band: a horizontal price region across the whole window (axhspan spans
    # the full x-range by construction). c001's span ≈ 0.12% renders as a thin band — the
    # metadata box carries the width that the eye cannot resolve.
    ax.axhspan(cluster.min_price, cluster.max_price, color="#3949ab", alpha=0.12, zorder=1)
    ax.axhline(
        cluster.representative_price,
        color="#3949ab",
        lw=1.6,
        ls="-",
        alpha=0.85,
        zorder=3,
    )

    if show_members:
        for r in band:
            ax.axhline(
                r.level_price,
                color=_TF_COLORS.get(r.timeframe, "#555555"),
                lw=1.2,
                ls="--",
                alpha=0.9,
                zorder=4,
            )
        _annotate_member_table(ax, band)

    _annotate_metadata(ax, card_meta)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def render_confluence_card(
    fib_root: Path | str,
    signature: ClusterSignature = C001_SIGNATURE,
    settings: Settings | None = None,
    out_root: Path | None = None,
    epsilon_log: float = DEFAULT_EPSILON_LOG,
    backdrop_tf: str = DEFAULT_BACKDROP_TF,
    pad_bars: int = _CONTEXT_PAD_BARS,
) -> ConfluenceCard:
    """Render the clean + levels confluence card for the signature-resolved cluster.

    Pure read of the source corpus + candle cache; fail-closed on no/ambiguous signature
    match, superseded/off-protocol members, or missing candle cache (never auto-fetches).
    """
    if settings is None:
        settings = load_settings()

    rows = flatten_levels(fib_root)
    if not rows:
        raise FileNotFoundError(f"No source-fib level rows under {fib_root}")

    clusters = cluster_confluence_fixed_band(rows, epsilon_log)
    cluster = resolve_cluster(clusters, signature)
    band = band_member_rows(rows, cluster)
    _guard_members(band)

    symbol, exchange = _ref_symbol_exchange(band)
    data_cfg = settings.data.model_copy(
        update={"symbol": symbol, "timeframe": backdrop_tf, "exchange": exchange}
    )
    # fetch_if_missing=False → raises FileNotFoundError with a clear "run fetch" message.
    df_full = load_candles(data_cfg, fetch_if_missing=False)

    ws = pd.to_datetime(cluster.time_window_start, utc=True)
    we = pd.to_datetime(cluster.time_window_end, utc=True)
    pa = _nearest_pos(df_full, ws)
    pb = _nearest_pos(df_full, we)
    if pa is None or pb is None:
        edge = "window_start" if pa is None else "window_end"
        raise ValueError(
            f"Cluster {cluster.cluster_id} {edge} ({ws if pa is None else we}) is outside the "
            f"{backdrop_tf} candle range {df_full.index[0]} → {df_full.index[-1]}. "
            "Fetch a wider cache before rendering (no auto-fetch)."
        )
    lo = max(0, pa - pad_bars)
    hi = min(len(df_full) - 1, pb + pad_bars)
    df = df_full.iloc[lo : hi + 1]

    atlas_root = Path(out_root) if out_root else MTF_CONFLUENCE_ATLAS_ROOT
    out_dir = atlas_root / METHOD / cluster.cluster_id
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_path = out_dir / "clean.png"
    levels_path = out_dir / "levels.png"

    card_meta = {
        "method": METHOD,
        "epsilon_log": epsilon_log,
        "price_span_log": cluster.price_span_log,
        "tf_count": cluster.timeframe_count,
        "min_price": cluster.min_price,
        "max_price": cluster.max_price,
        "representative_price": cluster.representative_price,
    }
    n = len(df)
    fig_w = max(16, min(n // 2, 36))
    a_str = f"{df.index[0]:%Y-%m-%d}"
    b_str = f"{df.index[-1]:%Y-%m-%d}"
    # Show the cluster id once; only append the resolved id when it differs from the
    # signature label (avoids the "c001 (c001)" duplication when they coincide).
    id_part = (
        signature.label
        if signature.label == cluster.cluster_id
        else f"{signature.label} ({cluster.cluster_id})"
    )
    base_title = (
        f"{symbol} MTF confluence {id_part}  |  "
        f"{','.join(cluster.timeframes)}  {backdrop_tf} backdrop  {a_str} → {b_str}  (log)"
    )
    _draw_card(
        df,
        band,
        cluster,
        clean_path,
        title=f"{base_title}  |  CLEAN",
        show_members=False,
        fig_w=fig_w,
        card_meta=card_meta,
    )
    _draw_card(
        df,
        band,
        cluster,
        levels_path,
        title=f"{base_title}  |  LEVELS",
        show_members=True,
        fig_w=fig_w,
        card_meta=card_meta,
    )

    member_levels = [
        {
            "timeframe": r.timeframe,
            "ratio": r.ratio,
            "level_price": r.level_price,
            "fib_id": r.fib_id,
            "source_path": r.source_path,
        }
        for r in band
    ]

    return ConfluenceCard(
        cluster_id=cluster.cluster_id,
        signature_label=signature.label,
        method=METHOD,
        epsilon_log=epsilon_log,
        backdrop_tf=backdrop_tf,
        representative_price=cluster.representative_price,
        min_price=cluster.min_price,
        max_price=cluster.max_price,
        price_span_log=cluster.price_span_log,
        timeframe_count=cluster.timeframe_count,
        timeframes=cluster.timeframes,
        ratios=cluster.ratios,
        member_fib_ids=cluster.member_fib_ids,
        member_levels=member_levels,
        window_start=cluster.time_window_start,
        window_end=cluster.time_window_end,
        clean=clean_path,
        levels=levels_path,
    )


def _default_fib_root(settings: Settings) -> Path:
    sym = settings.data.symbol.replace("/", "-")
    exch = settings.data.exchange.lower()
    return REPO_ROOT / "data" / "labels" / "human_fib" / exch / sym


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the BTC/USD MTF confluence atlas card (slice 1: c001, fixed-band)."
    )
    p.add_argument(
        "--fib-root",
        default=None,
        help="Symbol dir holding timeframe subdirs of fib_*.json (default: BTC/USD label dir)",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override output root")
    p.add_argument("--epsilon-log", type=float, default=DEFAULT_EPSILON_LOG)
    p.add_argument("--backdrop-tf", default=DEFAULT_BACKDROP_TF)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    fib_root = Path(args.fib_root) if args.fib_root else _default_fib_root(settings)
    card = render_confluence_card(
        fib_root=fib_root,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        epsilon_log=args.epsilon_log,
        backdrop_tf=args.backdrop_tf,
    )
    print(
        f"MTF confluence card [{card.signature_label} -> {card.cluster_id}]: "
        f"{card.method}, epsilon_log={card.epsilon_log}, tf_count={card.timeframe_count}, "
        f"price_span_log={card.price_span_log}, band {card.min_price:,.0f}–{card.max_price:,.0f}"
    )
    print(f"  members ({len(card.member_levels)}):")
    for m in card.member_levels:
        print(f"    {m['timeframe']:3} {m['ratio']:g} @ {m['level_price']:,.0f}  {m['fib_id']}")
    print(f"  clean:  {card.clean}")
    print(f"  levels: {card.levels}")
