"""Drawing helpers and MTF context views for ``level_event_review_tool``."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fibengine.research.human_review_level_events import (
    HumanReviewConfig,
    ReviewViewMode,
    _draw_active_fib_badge,
    _draw_anchor_labels,
    _draw_event_label,
    _draw_fib_leg_overlay,
    _draw_fib_levels,
    _draw_fib_review_panel,
    _draw_view_mode_badge,
    window_for_view,
)

# BTC top-down timeframe hierarchy (highest → lowest)
TF_HIERARCHY: list[str] = ["1M", "1w", "1d", "4h", "1h"]
_TF_COLORS: dict[str, str] = {
    "1M": "#ffd700",  # gold
    "1w": "#69f0ae",  # green
    "1d": "#40c4ff",  # light blue
    "4h": "#ff80ab",  # pink
    "1h": "#ce93d8",  # lavender
}


def _tf_rank(tf: str) -> int:
    """Position of tf in TF_HIERARCHY (lower index = higher timeframe)."""
    tfl = tf.lower()
    for i, t in enumerate(TF_HIERARCHY):
        if t.lower() == tfl:
            return i
    return len(TF_HIERARCHY)


def _load_human_fibs_by_tf(
    label_root: Path | None = None,
) -> dict[str, list[dict]]:
    """Load all fib_*.json annotation files grouped by timeframe directory name."""
    if label_root is None:
        label_root = Path("data/labels/human_fib/bitfinex/BTC-USD")
    out: dict[str, list[dict]] = {}
    if not label_root.exists():
        return out
    for tf_dir in sorted(label_root.iterdir()):
        if not tf_dir.is_dir():
            continue
        fibs: list[dict] = []
        for f in sorted(tf_dir.glob("fib_*.json")):
            if "_events" in f.stem:
                continue
            try:
                fibs.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
        if fibs:
            out[tf_dir.name] = fibs
    return out


def _active_fibs_at(fibs: list[dict], event_ts: pd.Timestamp) -> list[dict]:
    """Return fibs where both anchors predate event_ts (leg is complete at event time)."""
    result = []
    for f in fibs:
        try:
            ta = pd.to_datetime(f["anchor_a"]["time"], utc=True)
            tb = pd.to_datetime(f["anchor_b"]["time"], utc=True)
        except (KeyError, ValueError):
            continue
        if event_ts >= max(ta, tb):
            result.append(f)
    return result


def _context_xlim(
    df: pd.DataFrame,
    fibs: list[dict],
    event_time: str,
    pad: int = 6,
) -> tuple[float, float]:
    """X-limits for a context chart: covers active fib anchors and the event time."""
    event_ts = pd.to_datetime(event_time, utc=True)
    active = _active_fibs_at(fibs, event_ts)
    bars: list[int] = []

    def _try_bar(ts: pd.Timestamp) -> None:
        if df.index[0] <= ts <= df.index[-1]:
            bars.append(int(df.index.get_indexer([ts], method="nearest")[0]))

    _try_bar(event_ts)
    for fib in active:
        for ak in ("anchor_a", "anchor_b"):
            t_str = (fib.get(ak) or {}).get("time")
            if t_str:
                _try_bar(pd.to_datetime(t_str, utc=True))

    if not bars:
        n = len(df)
        return float(max(0, n - 80)), float(n - 1)
    return float(max(0, min(bars) - pad)), float(min(len(df) - 1, max(bars) + pad))


def _draw_context_view(
    ax,
    df: pd.DataFrame,
    fibs: list[dict],
    event_time: str,
    ctx_tf: str,
) -> None:
    """Draw a higher-TF context chart: active fib levels, anchor markers, event marker."""
    event_ts = pd.to_datetime(event_time, utc=True)
    active = _active_fibs_at(fibs, event_ts)
    color = _TF_COLORS.get(ctx_tf, "#aaaaaa")

    for fib in active:
        for lvl in fib.get("levels", []):
            ax.axhline(float(lvl["price"]), color=color, ls="--", lw=0.9, alpha=0.55, zorder=2)
        for ak, is_a in (("anchor_a", True), ("anchor_b", False)):
            anchor = fib.get(ak) or {}
            t_str, price = anchor.get("time"), anchor.get("price")
            if not t_str or price is None:
                continue
            ts = pd.to_datetime(t_str, utc=True)
            if not (df.index[0] <= ts <= df.index[-1]):
                continue
            bar_i = int(df.index.get_indexer([ts], method="nearest")[0])
            direction = fib.get("direction", "down")
            marker = ("^" if is_a else "v") if direction == "down" else ("v" if is_a else "^")
            ax.scatter(
                [bar_i],
                [float(price)],
                color=color,
                marker=marker,
                s=110,
                alpha=0.88,
                zorder=6,
            )

    if not active:
        ax.text(
            0.50,
            0.50,
            f"no active {ctx_tf} fibs at this date",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color="#555e70",
            style="italic",
        )

    if df.index[0] <= event_ts <= df.index[-1]:
        eb = int(df.index.get_indexer([event_ts], method="nearest")[0])
        ax.axvline(eb, color="#ff9f43", lw=1.8, ls="--", alpha=0.80, zorder=5)
        ax.text(
            eb,
            1.0,
            "▼ event",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            color="#ff9f43",
            fontsize=8,
            zorder=7,
        )
    elif event_ts > df.index[-1]:
        ax.text(
            0.98,
            0.04,
            "event ▶",
            transform=ax.transAxes,
            color="#ff9f43",
            fontsize=8.5,
            ha="right",
            va="bottom",
        )
    else:
        ax.text(
            0.02,
            0.04,
            "◀ event",
            transform=ax.transAxes,
            color="#ff9f43",
            fontsize=8.5,
            ha="left",
            va="bottom",
        )

    ax.text(
        0.02,
        0.98,
        f"CONTEXT: {ctx_tf}   d=drill-down  u=up  e=event",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        fontweight="bold",
        color=color,
        bbox={"boxstyle": "round,pad=0.35", "fc": "#1a1d26", "ec": color, "alpha": 0.94},
        zorder=20,
    )


def _draw_htf_overlays(
    ax,
    event_time: str,
    all_fibs: dict[str, list[dict]],
    current_tf: str,
) -> None:
    """Draw faint dotted lines for all active fib levels from TFs above current_tf."""
    event_ts = pd.to_datetime(event_time, utc=True)
    current_rank = _tf_rank(current_tf)
    labeled_tfs: set[str] = set()

    for tf, fibs in all_fibs.items():
        if _tf_rank(tf) >= current_rank:
            continue
        color = _TF_COLORS.get(tf, "#aaaaaa")
        active = _active_fibs_at(fibs, event_ts)
        for fib in active:
            levels = fib.get("levels", [])
            for lvl in levels:
                ax.axhline(float(lvl["price"]), color=color, ls=":", lw=0.9, alpha=0.38, zorder=2)
            if tf not in labeled_tfs and levels:
                mid_price = float(levels[len(levels) // 2]["price"])
                ax.text(
                    1.0,
                    mid_price,
                    f" {tf}",
                    transform=ax.get_yaxis_transform(),
                    color=color,
                    fontsize=7,
                    alpha=0.72,
                    va="center",
                    clip_on=False,
                )
                labeled_tfs.add(tf)


def _tf_path_str(event_tf: str, ctx_tf: str) -> str:
    """Format TF hierarchy display, e.g. '[1M] → 1w → 1d → 4h'."""
    event_rank = _tf_rank(event_tf)
    ctx_rank = _tf_rank(ctx_tf)
    parts: list[str] = []
    for t in TF_HIERARCHY:
        r = _tf_rank(t)
        if r > event_rank:
            break
        label = f"[{t}]" if r == ctx_rank else t
        parts.append(label)
    return " -> ".join(parts) if parts else ctx_tf


def _override_key(row: dict) -> str:
    """Stable composite key for anchor override lookup."""
    return f"{row.get('fib_id', '')}|{row.get('event_time', '')}"


def _load_anchor_overrides(run_dir: Path) -> dict[str, dict]:
    """Load review_anchor_overrides.jsonl; keyed by _override_key."""
    path = run_dir / "review_anchor_overrides.jsonl"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            key = f"{obj.get('fib_id', '')}|{obj.get('event_time', '')}"
            out[key] = obj
        except Exception:
            pass
    return out


def _save_anchor_overrides(overrides: dict[str, dict], run_dir: Path) -> None:
    """Write all anchor overrides to review_anchor_overrides.jsonl."""
    path = run_dir / "review_anchor_overrides.jsonl"
    lines = [json.dumps(v, ensure_ascii=False) for v in overrides.values()]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"Saved {len(lines)} anchor override(s) -> {path.name}")


def _draw_anchor_corrections(ax, df: pd.DataFrame, override: dict) -> None:
    """Draw H/L correction markers, visually distinct from original anchors."""
    color = "#ff4081"
    for anchor_key, marker, va_pos, label in (
        ("high_anchor", "^", "bottom", "H corr"),
        ("low_anchor", "v", "top", "L corr"),
    ):
        a = override.get(anchor_key)
        if not a:
            continue
        try:
            ts = pd.to_datetime(a["time"], utc=True)
        except (KeyError, ValueError):
            continue
        if not (df.index[0] <= ts <= df.index[-1]):
            continue
        bar_i = int(df.index.get_indexer([ts], method="nearest")[0])
        price = float(a["price"])
        ax.scatter(
            [bar_i],
            [price],
            color=color,
            marker=marker,
            s=200,
            zorder=10,
            edgecolors="white",
            linewidths=0.8,
        )
        ax.text(
            bar_i, price, f" {label}", color=color, fontsize=8, va=va_pos, zorder=11, clip_on=True
        )


def _draw_edit_mode_badge(ax, mode: str) -> None:
    """Overlay badge shown while waiting for the user's anchor click."""
    ax.text(
        0.50,
        0.97,
        f"ANCHOR EDIT: click to place {mode} anchor  (Esc=cancel)",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=10,
        fontweight="bold",
        color="#ff4081",
        bbox={"boxstyle": "round,pad=0.38", "fc": "#1a1d26", "ec": "#ff4081", "alpha": 0.97},
        zorder=25,
    )


_CANDIDATE_COLORS: dict[str, str] = {
    "rejection_candidate": "#69f0ae",
    "reaction_candidate": "#69f0ae",
    "failure_candidate": "#ff5252",
    "continuation_candidate": "#40c4ff",
}


def _candidate_color(candidate: str) -> str:
    return _CANDIDATE_COLORS.get(candidate, "#9aa3b2")


def _build_fib_siblings(rows: list[dict]) -> dict[str, list[dict]]:
    """Group review rows by fib_id for multi-level sequence context."""
    out: dict[str, list[dict]] = {}
    for row in rows:
        fid = row.get("fib_id", "")
        out.setdefault(fid, []).append(row)
    return out


def _draw_sibling_markers(
    ax,
    df: pd.DataFrame,
    current_row: dict,
    siblings: list[dict],
) -> None:
    """Subtle diamond markers for other detected interactions on the same fib leg."""
    for row in siblings:
        if row is current_row:
            continue
        fib_price = row.get("fib_price")
        if fib_price is None:
            continue
        fib_price = float(fib_price)
        event_time = row.get("event_time", "")
        eb: int = -1
        if event_time:
            try:
                ts = pd.to_datetime(event_time, utc=True)
                if df.index[0] <= ts <= df.index[-1]:
                    eb = int(df.index.get_indexer([ts], method="nearest")[0])
            except Exception:
                eb = int(row.get("event_bar", -1))
        else:
            eb = int(row.get("event_bar", -1))
        if not (0 <= eb < len(df)):
            continue
        candidate = row.get("auto_candidate", "")
        color = _candidate_color(candidate)
        level = str(row.get("fib_level", ""))
        ax.scatter(
            [eb],
            [fib_price],
            color=color,
            marker="D",
            s=55,
            alpha=0.42,
            zorder=6,
            edgecolors="none",
        )
        ax.text(
            eb + 0.4,
            fib_price,
            f" {level}",
            color=color,
            fontsize=7,
            alpha=0.70,
            va="center",
            zorder=7,
            clip_on=True,
        )


def _draw_sequence_panel(
    ax,
    current_row: dict,
    siblings: list[dict],
) -> None:
    """MULTI-LEVEL SEQUENCE summary — lower-right corner of chart."""
    others = [r for r in siblings if r is not current_row]
    if not others:
        return

    def _ratio_sort(r: dict) -> float:
        try:
            return float(r.get("fib_level", 0))
        except (ValueError, TypeError):
            return 0.0

    sorted_sibs = sorted(siblings, key=_ratio_sort)
    lines = ["─ SEQUENCE (same fib) ─"]
    for row in sorted_sibs:
        level = str(row.get("fib_level", "?"))
        rel = (row.get("relation") or row.get("touch_type") or "?")[:6]
        cand = (row.get("auto_candidate") or "?").replace("_candidate", "")[:11]
        hlabel = row.get("human_label") or ""
        tag = f"[{hlabel[:5]}]" if hlabel else "       "
        focused = " ◄" if row is current_row else ""
        lines.append(f"  {level:<5}  {rel:<6}  {cand:<11}  {tag}{focused}")

    ax.text(
        0.98,
        0.02,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#d6d9e0",
        family="monospace",
        linespacing=1.45,
        bbox={
            "boxstyle": "round,pad=0.45",
            "fc": "#1a1d26",
            "ec": "#69f0ae",
            "alpha": 0.90,
            "lw": 1.0,
        },
        zorder=18,
        clip_on=True,
    )


def _overlay_event(
    ax,
    df: pd.DataFrame,
    row: dict,
    cfg: HumanReviewConfig,
    view_mode: ReviewViewMode,
) -> tuple[int, int]:
    lo, hi = window_for_view(row, df, cfg, view_mode)
    _draw_fib_leg_overlay(ax, row, lo, hi, dark_theme=True)
    _draw_fib_levels(ax, row, dark_theme=True)
    _draw_active_fib_badge(ax, row, dark_theme=True)
    _draw_view_mode_badge(ax, view_mode, dark_theme=True)
    eb = int(row["event_bar"])
    ax.axvspan(eb - 0.5, eb + 0.5, color="#ff9f43", alpha=0.22, zorder=1)
    ax.axvline(eb, color="#ff9f43", lw=1.6, zorder=5)
    ax.scatter(
        [eb],
        [df["close"].iloc[eb]],
        color="#ff9f43",
        marker="*",
        s=300,
        edgecolors="black",
        linewidths=0.6,
        zorder=8,
    )
    _draw_event_label(ax, row, dark_theme=True)
    _draw_anchor_labels(ax, df, row, lo, hi, color="#b388ff", dark_theme=True)
    _draw_fib_review_panel(ax, row, dark_theme=True)
    return lo, hi


def _check_candle_coverage(df: pd.DataFrame, rows: list[dict]) -> None:
    """Fail fast when review timestamps predate the loaded candle cache."""
    need: list[str] = []
    for key in ("event_time", "anchor_a_time", "anchor_b_time"):
        need.extend(str(r[key]) for r in rows if r.get(key))
    if not need:
        return
    earliest = min(pd.to_datetime(t, utc=True) for t in need)
    if earliest < df.index[0]:
        raise ValueError(
            f"Review needs candles from {earliest.date()}, but cache starts "
            f"{df.index[0].date()} ({len(df)} bars). "
            "Run: python -m fibengine.data.fetch --symbols ETH/USD --timeframes 1d --refresh "
            "then regenerate the review pack."
        )
