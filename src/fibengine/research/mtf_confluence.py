"""MTF confluence table — stdlib-only, report-only (Checkpoint 1).

Answers a single structural question about the locked BTC/USD source-fib corpus:
**do stored fib level prices from at least two timeframes cluster together in
log-price while their anchor time-windows overlap?**

This is *not* the segment-overlap detector (``overlap_detector.py`` boxes the
``anchor_a → anchor_b`` segment). Here every fib contributes its six stored level
prices (ratios ``0, 0.382, 0.5, 0.618, 0.786, 1``) as horizontal price rows; a
*confluence cluster* is a connected component of level rows that are both near in
log-price (``|Δlog| <= epsilon_log``) and overlapping in anchor time-window, spanning
``>= min_timeframes`` distinct timeframes.

Single-linkage (connected components): a cluster's total ``price_span_log`` can exceed
``epsilon_log`` when rows chain via intermediate members — ``price_span_log`` is reported
so chaining is visible. It never edits labels, renders, or interprets clusters as signals.

Usage::

    python -m fibengine.research.mtf_confluence \\
        --fib-root data/labels/human_fib/bitfinex/BTC-USD \\
        --epsilon-log 0.005 \\
        --out experiments/review/mtf_confluence/btc-mtf-confluence.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

TF_ORDER: tuple[str, ...] = ("1M", "1w", "1d", "4h")
SIDECAR_MARKERS: tuple[str, ...] = ("_events", "_interactions")
DEFAULT_EPSILON_LOG = 0.005

LEVEL_FIELDS: tuple[str, ...] = (
    "fib_id",
    "timeframe",
    "ratio",
    "level_price",
    "log_price",
    "anchor_start_time",
    "anchor_end_time",
    "direction",
    "source_path",
)

CONFLUENCE_FIELDS: tuple[str, ...] = (
    "cluster_id",
    "epsilon_log",
    "representative_price",
    "min_price",
    "max_price",
    "price_span_log",
    "time_window_start",
    "time_window_end",
    "timeframe_count",
    "level_count",
    "timeframes",
    "ratios",
    "member_fib_ids",
)


@dataclass(frozen=True)
class LevelRow:
    """One stored fib level as a row in (log-price, anchor time-window) space."""

    fib_id: str
    timeframe: str
    ratio: float
    level_price: float
    log_price: float
    anchor_start_time: str
    anchor_end_time: str
    direction: str
    source_path: str


@dataclass
class ConfluenceCluster:
    cluster_id: str
    epsilon_log: float
    representative_price: float
    min_price: float
    max_price: float
    price_span_log: float
    time_window_start: str
    time_window_end: str
    timeframe_count: int
    level_count: int
    timeframes: tuple[str, ...]
    ratios: tuple[float, ...]
    member_fib_ids: tuple[str, ...]


def _epoch(iso_time: str) -> float:
    return datetime.fromisoformat(iso_time).timestamp()


def _is_sidecar(name: str) -> bool:
    return any(m in name for m in SIDECAR_MARKERS)


def flatten_levels(
    fib_root: Path | str,
    timeframes: tuple[str, ...] = TF_ORDER,
) -> list[LevelRow]:
    """Load active source fibs from each timeframe subdir and flatten to level rows.

    ``fib_root`` is the symbol dir (e.g. ``data/labels/human_fib/bitfinex/BTC-USD``);
    each timeframe is a subdir. Sidecars (``*_events*`` / ``*_interactions*``) are
    excluded. Superseded/deleted fibs are simply absent on disk. Pure read.
    """
    root = Path(fib_root)
    rows: list[LevelRow] = []
    for tf in timeframes:
        tf_dir = root / tf
        if not tf_dir.is_dir():
            continue
        for f in sorted(tf_dir.glob("fib_*.json")):
            if _is_sidecar(f.name):
                continue
            d = json.loads(f.read_text(encoding="utf-8"))
            a_iso, b_iso = d["anchor_a"]["time"], d["anchor_b"]["time"]
            a_e, b_e = _epoch(a_iso), _epoch(b_iso)
            start_iso, end_iso = (a_iso, b_iso) if a_e <= b_e else (b_iso, a_iso)
            for lv in d["levels"]:
                price = float(lv["price"])
                rows.append(
                    LevelRow(
                        fib_id=d["fib_id"],
                        timeframe=d["timeframe"],
                        ratio=float(lv["ratio"]),
                        level_price=price,
                        log_price=math.log(price),
                        anchor_start_time=start_iso,
                        anchor_end_time=end_iso,
                        direction=d["direction"],
                        source_path=f.as_posix(),
                    )
                )
    return rows


def _time_overlap(a: LevelRow, b: LevelRow) -> bool:
    a_s, a_e = _epoch(a.anchor_start_time), _epoch(a.anchor_end_time)
    b_s, b_e = _epoch(b.anchor_start_time), _epoch(b.anchor_end_time)
    return a_s <= b_e and b_s <= a_e


class _UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def _tf_sort_key(tf: str) -> int:
    return TF_ORDER.index(tf) if tf in TF_ORDER else len(TF_ORDER)


def _finalize_cluster(
    rows: list[LevelRow], members: list[int], epsilon_log: float
) -> ConfluenceCluster:
    """Build a ConfluenceCluster (id assigned later) from member row indices."""
    tfs = {rows[i].timeframe for i in members}
    logs = [rows[i].log_price for i in members]
    prices = [rows[i].level_price for i in members]
    starts = sorted(rows[i].anchor_start_time for i in members)
    ends = sorted(rows[i].anchor_end_time for i in members)
    rep = math.exp(sum(logs) / len(logs))
    return ConfluenceCluster(
        cluster_id="",  # assigned after ordering
        epsilon_log=epsilon_log,
        representative_price=round(rep, 2),
        min_price=round(min(prices), 2),
        max_price=round(max(prices), 2),
        price_span_log=round(max(logs) - min(logs), 6),
        time_window_start=starts[0],
        time_window_end=ends[-1],
        timeframe_count=len(tfs),
        level_count=len(members),
        timeframes=tuple(sorted(tfs, key=_tf_sort_key)),
        ratios=tuple(sorted({rows[i].ratio for i in members})),
        member_fib_ids=tuple(sorted({rows[i].fib_id for i in members})),
    )


def _time_components(rows: list[LevelRow], indices: list[int]) -> list[list[int]]:
    """Single-linkage components of the given rows under time-overlap edges only.

    Deterministic: operates on sorted indices. Used after price proximity is already
    guaranteed (single-linkage sweep edge, or a fixed-width price band).
    """
    idx = sorted(indices)
    m = len(idx)
    uf = _UnionFind(m)
    for a in range(m):
        for b in range(a + 1, m):
            if _time_overlap(rows[idx[a]], rows[idx[b]]):
                uf.union(a, b)
    comps: dict[int, list[int]] = {}
    for k in range(m):
        comps.setdefault(uf.find(k), []).append(idx[k])
    return list(comps.values())


def cluster_confluence(
    rows: list[LevelRow],
    epsilon_log: float = DEFAULT_EPSILON_LOG,
    min_timeframes: int = 2,
) -> list[ConfluenceCluster]:
    """Connected-component clustering: edge iff ``|Δlog| <= epsilon_log`` and time overlap.

    Single-linkage: a cluster's total ``price_span_log`` may exceed ``epsilon_log`` when
    rows chain via intermediate members. Keeps clusters spanning ``>= min_timeframes``
    distinct timeframes. Deterministic.
    """
    n = len(rows)
    uf = _UnionFind(n)
    order = sorted(range(n), key=lambda i: rows[i].log_price)
    for a in range(n):
        i = order[a]
        for b in range(a + 1, n):
            j = order[b]
            if rows[j].log_price - rows[i].log_price > epsilon_log:
                break
            if _time_overlap(rows[i], rows[j]):
                uf.union(i, j)

    comps: dict[int, list[int]] = {}
    for i in range(n):
        comps.setdefault(uf.find(i), []).append(i)

    clusters = [
        _finalize_cluster(rows, members, epsilon_log)
        for members in comps.values()
        if len({rows[i].timeframe for i in members}) >= min_timeframes
    ]
    return order_clusters(clusters)


def cluster_confluence_fixed_band(
    rows: list[LevelRow],
    epsilon_log: float = DEFAULT_EPSILON_LOG,
    min_timeframes: int = 2,
) -> list[ConfluenceCluster]:
    """Fixed-band clustering: complete-linkage in price, single-linkage in time.

    Greedy price banding over log-sorted rows: a band starts at the lowest unassigned
    row and extends while ``log_price - band_min <= epsilon_log``, so every band (and
    therefore every cluster) has ``price_span_log <= epsilon_log`` — i.e. all member
    pairs are within epsilon in price (complete-linkage in price). Within each band, rows
    are split into time-overlap connected components (single-linkage in time). Clusters
    spanning ``>= min_timeframes`` distinct timeframes are kept.

    Every fixed-band cluster is a subset of exactly one single-linkage cluster at the
    same epsilon (the partition is a refinement). Greedy band cut points are
    price-position-dependent (a known fixed-width-binning property); this is a robustness
    probe, not a canonical clustering. Deterministic.
    """
    n = len(rows)
    order = sorted(range(n), key=lambda i: rows[i].log_price)
    clusters: list[ConfluenceCluster] = []
    a = 0
    while a < n:
        band_min = rows[order[a]].log_price
        b = a + 1
        while b < n and rows[order[b]].log_price - band_min <= epsilon_log:
            b += 1
        band = [order[k] for k in range(a, b)]
        for members in _time_components(rows, band):
            if len({rows[i].timeframe for i in members}) >= min_timeframes:
                clusters.append(_finalize_cluster(rows, members, epsilon_log))
        a = b
    return order_clusters(clusters)


def order_clusters(clusters: list[ConfluenceCluster]) -> list[ConfluenceCluster]:
    """Deterministic order + (re)assign sequential cluster ids.

    Sort: timeframe_count desc, level_count desc, price_span_log asc,
    time_window_start asc, representative_price asc.
    """
    ordered = sorted(
        clusters,
        key=lambda c: (
            -c.timeframe_count,
            -c.level_count,
            c.price_span_log,
            c.time_window_start,
            c.representative_price,
        ),
    )
    for n, c in enumerate(ordered, start=1):
        c.cluster_id = f"c{n:03d}"
    return ordered


def _summarize_members(ids: tuple[str, ...], limit: int = 8) -> str:
    if len(ids) <= limit:
        return "|".join(ids)
    return "|".join(ids[:limit]) + f"|...(+{len(ids) - limit})"


def write_confluence_csv(
    path: Path | str,
    clusters: list[ConfluenceCluster],
    member_limit: int = 8,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CONFLUENCE_FIELDS)
        writer.writeheader()
        for c in clusters:
            writer.writerow(
                {
                    "cluster_id": c.cluster_id,
                    "epsilon_log": c.epsilon_log,
                    "representative_price": c.representative_price,
                    "min_price": c.min_price,
                    "max_price": c.max_price,
                    "price_span_log": c.price_span_log,
                    "time_window_start": c.time_window_start,
                    "time_window_end": c.time_window_end,
                    "timeframe_count": c.timeframe_count,
                    "level_count": c.level_count,
                    "timeframes": ",".join(c.timeframes),
                    "ratios": ",".join(str(r) for r in c.ratios),
                    "member_fib_ids": _summarize_members(c.member_fib_ids, member_limit),
                }
            )
    return out


def write_levels_csv(path: Path | str, rows: list[LevelRow]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEVEL_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "fib_id": r.fib_id,
                    "timeframe": r.timeframe,
                    "ratio": r.ratio,
                    "level_price": r.level_price,
                    "log_price": round(r.log_price, 6),
                    "anchor_start_time": r.anchor_start_time,
                    "anchor_end_time": r.anchor_end_time,
                    "direction": r.direction,
                    "source_path": r.source_path,
                }
            )
    return out


def tf_combo_breakdown(clusters: list[ConfluenceCluster]) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    for c in clusters:
        counts[c.timeframes] = counts.get(c.timeframes, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0])))


def tf_count_histogram(clusters: list[ConfluenceCluster]) -> dict[int, int]:
    """Map distinct-timeframe-count -> number of clusters (e.g. {4: 2, 3: 24, 2: 196})."""
    hist: dict[int, int] = {}
    for c in clusters:
        hist[c.timeframe_count] = hist.get(c.timeframe_count, 0) + 1
    return dict(sorted(hist.items(), reverse=True))


def span_partition(clusters: list[ConfluenceCluster], epsilon_log: float) -> tuple[int, int]:
    """Parameter-free chaining probe: (intact, chained) counts where ``chained`` are
    clusters whose ``price_span_log > epsilon_log`` (only possible under single-linkage).
    """
    chained = sum(1 for c in clusters if c.price_span_log > epsilon_log)
    return len(clusters) - chained, chained


SENSITIVITY_FIELDS: tuple[str, ...] = (
    "epsilon_log",
    "method",
    "total_clusters",
    "n_4tf",
    "n_3tf",
    "n_2tf",
    "max_price_span_log",
    "clusters_over_epsilon",
)

DEFAULT_EPSILONS: tuple[float, ...] = (0.0025, 0.005, 0.01)
METHODS: tuple[str, ...] = ("single_linkage", "fixed_band")


def cluster_for_method(
    rows: list[LevelRow], method: str, epsilon_log: float, min_timeframes: int = 2
) -> list[ConfluenceCluster]:
    if method == "single_linkage":
        return cluster_confluence(rows, epsilon_log, min_timeframes)
    if method == "fixed_band":
        return cluster_confluence_fixed_band(rows, epsilon_log, min_timeframes)
    raise ValueError(f"unknown method: {method}")


def run_sensitivity(
    rows: list[LevelRow],
    epsilons: tuple[float, ...] = DEFAULT_EPSILONS,
    methods: tuple[str, ...] = METHODS,
    min_timeframes: int = 2,
) -> list[dict]:
    """Deterministic sensitivity sweep: one summary row per (epsilon, method)."""
    summary: list[dict] = []
    for eps in epsilons:
        for method in methods:
            clusters = cluster_for_method(rows, method, eps, min_timeframes)
            hist = tf_count_histogram(clusters)
            spans = [c.price_span_log for c in clusters]
            summary.append(
                {
                    "epsilon_log": eps,
                    "method": method,
                    "total_clusters": len(clusters),
                    "n_4tf": hist.get(4, 0),
                    "n_3tf": hist.get(3, 0),
                    "n_2tf": hist.get(2, 0),
                    "max_price_span_log": round(max(spans), 6) if spans else 0.0,
                    "clusters_over_epsilon": sum(1 for s in spans if s > eps),
                }
            )
    return summary


def write_sensitivity_csv(path: Path | str, summary: list[dict]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SENSITIVITY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="MTF confluence table (report-only, stdlib): cluster stored fib "
        "levels across timeframes by log-price proximity + anchor time overlap."
    )
    p.add_argument(
        "--fib-root",
        default="data/labels/human_fib/bitfinex/BTC-USD",
        help="Symbol dir holding timeframe subdirs of fib_*.json",
    )
    p.add_argument("--epsilon-log", type=float, default=DEFAULT_EPSILON_LOG)
    p.add_argument("--min-timeframes", type=int, default=2)
    p.add_argument(
        "--method",
        choices=METHODS,
        default="single_linkage",
        help="Clustering method for --out (default single_linkage)",
    )
    p.add_argument("--out", default=None, help="Confluence CSV path (optional)")
    p.add_argument("--levels-out", default=None, help="Flattened level-rows CSV path (optional)")
    p.add_argument(
        "--sensitivity-out",
        default=None,
        help="Sensitivity-summary CSV path; runs predeclared epsilons x both methods",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    rows = flatten_levels(args.fib_root)
    clusters = cluster_for_method(rows, args.method, args.epsilon_log, args.min_timeframes)
    fibs = len({r.fib_id for r in rows})
    print(
        f"mtf confluence [{args.method}]: {len(rows)} level rows from {fibs} fibs; "
        f"epsilon_log={args.epsilon_log}; {len(clusters)} cluster(s) "
        f">= {args.min_timeframes} timeframes"
    )
    for combo, n in tf_combo_breakdown(clusters).items():
        print(f"  {','.join(combo)} -> {n}")
    if args.levels_out:
        print(f"levels written: {write_levels_csv(args.levels_out, rows)}")
    if args.out:
        print(f"report written: {write_confluence_csv(args.out, clusters)}")
    if args.sensitivity_out:
        summary = run_sensitivity(rows, min_timeframes=args.min_timeframes)
        for s in summary:
            print(
                f"  eps={s['epsilon_log']} {s['method']}: total={s['total_clusters']} "
                f"4TF={s['n_4tf']} 3TF={s['n_3tf']} 2TF={s['n_2tf']} "
                f"over_eps={s['clusters_over_epsilon']}"
            )
        print(f"sensitivity written: {write_sensitivity_csv(args.sensitivity_out, summary)}")


if __name__ == "__main__":
    main()
