"""Research-triage top-list export for fib fingerprint × outcome joins.

Reads a join run dir's ``fingerprint_outcomes.jsonl``, recomputes the candidate
summary (via :func:`summarize_joined`), and writes two **descriptive, low-sample**
triage views into the same run dir:

1. ``toplist.csv`` — candidate summary, sorted per candidate + horizon by
   ``mean_mfe`` desc, ``mean_mae`` asc, ``mean_post_bars_on_break_side`` desc
   (the expected-side proxy), then ``n_events`` desc. Each row carries a
   ``sample_flag`` (``LOW SAMPLE`` when ``n_events`` < threshold).
2. ``TOPLIST_NOTES.md`` — short markdown: sample inventory, a compact top-1
   preview per candidate/horizon, and deterministic fingerprint↔outcome
   covariation hints (Spearman rho per horizon, direction-inferred events only,
   candidates pooled).

This is research triage only. It answers "what is worth more data / what looks
like noise", NOT "what is the edge". No edge claims. No trading signals. No
parameter tuning. No strategy logic. No candidate-logic changes. Deterministic.

Run:
    uv run python -m fibengine.research.fib_toplist            # latest join run
    uv run python -m fibengine.research.fib_toplist --run-dir <path>
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from fibengine.research.fib_fingerprint_outcomes import (
    _FINGERPRINT_SUMMARY_KEYS,
    JOIN_RUNS,
    summarize_joined,
)

# Buckets with fewer events than this are flagged LOW SAMPLE (triage only).
LOW_SAMPLE_N = 5

# Sample-size inventory reporting thresholds (descriptive only).
SAMPLE_THRESHOLDS = (5, 10, 20)

# "post_bars_on_expected_side" is not a single stored field; the expected side
# differs by candidate. We use post-break-side dwell as a documented proxy.
EXPECTED_SIDE_PROXY = "mean_post_bars_on_break_side"

# Arbitrary triage cut-offs for bucketing covariation magnitude. NOT tuned, NOT
# an edge threshold — only used to sort fields into "look closer" vs "noise-like".
WATCH_ABS_RHO = 0.5
WEAK_ABS_RHO = 0.3

# Raw per-event fingerprint fields used for the covariation hints (numeric).
HINT_FIELDS = tuple(_FINGERPRINT_SUMMARY_KEYS)

TOPLIST_COLUMNS = (
    "rank_in_candidate_horizon",
    "sample_flag",
    "auto_candidate",
    "horizon",
    "relation",
    "fib_level",
    "timeframe",
    "n_events",
    "mean_mfe",
    "mean_mae",
    "mean_post_bars_on_break_side",
    "mean_forward_return",
    "rate_close_on_approach_side",
    "rate_crossed_back",
    "mean_post_retest_count",
    "mean_post_remained_near_level_rate",
    "mean_pre_bars_approaching_level",
    "mean_pre_distance_atr_norm",
    "mean_pre_approach_choppiness",
    "mean_at_wick_through_level",
    "mean_at_close_distance_atr_norm",
)

_BIG = 1e18


def read_joined_rows(run_dir: Path) -> list[dict]:
    """Read the joined fingerprint×outcome rows for a run dir."""
    path = run_dir / "fingerprint_outcomes.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"No fingerprint_outcomes.jsonl in {run_dir}")
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _within_group_key(row: dict) -> tuple:
    """Sort key inside a (candidate, horizon) group: mfe↓, mae↑, proxy↓, n↓."""
    mfe = row.get("mean_mfe")
    mae = row.get("mean_mae")
    proxy = row.get(EXPECTED_SIDE_PROXY)
    return (
        -(mfe if mfe is not None else -_BIG),
        (mae if mae is not None else _BIG),
        -(proxy if proxy is not None else -_BIG),
        -int(row.get("n_events", 0)),
        str(row.get("relation", "")),
        str(row.get("fib_level", "")),
    )


def build_candidate_toplist(joined: list[dict], *, low_sample_n: int = LOW_SAMPLE_N) -> list[dict]:
    """Candidate summary with rank-in-group + LOW SAMPLE flag, sorted for scan."""
    summary = summarize_joined(joined)

    groups: dict[tuple, list[dict]] = {}
    for entry in summary:
        groups.setdefault((entry["auto_candidate"], entry["horizon"]), []).append(entry)

    ranked: list[dict] = []
    for _key, entries in groups.items():
        entries.sort(key=_within_group_key)
        for rank, entry in enumerate(entries, start=1):
            n = int(entry.get("n_events", 0))
            out = {col: entry.get(col) for col in TOPLIST_COLUMNS}
            out["rank_in_candidate_horizon"] = rank
            out["sample_flag"] = "LOW SAMPLE" if n < low_sample_n else "ok"
            ranked.append(out)

    ranked.sort(
        key=lambda r: (
            str(r["auto_candidate"]),
            int(r["horizon"]) if r["horizon"] is not None else 0,
            int(r["rank_in_candidate_horizon"]),
        )
    )
    return ranked


def _avg_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 3:
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((a[i] - ma) ** 2 for i in range(n))
    vb = sum((b[i] - mb) ** 2 for i in range(n))
    if va == 0 or vb == 0:
        return None
    return round(cov / (va**0.5 * vb**0.5), 4)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Deterministic, dependency-free Spearman rho (average ranks for ties).

    Returns ``None`` when fewer than 3 pairs or either side has zero variance.
    """
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    return _pearson(_avg_ranks(xs), _avg_ranks(ys))


def fingerprint_hints(joined: list[dict]) -> dict[str, Any]:
    """Descriptive covariation of fingerprint fields with mfe/mae per horizon.

    Direction-inferred events only (mfe/mae are direction-aware there; reaction
    candidates have mfe == mae and are excluded). Candidates are pooled, so this
    is a coarse hint, not a per-candidate or causal statement.
    """
    dir_rows = [r for r in joined if r.get("direction_inferred") is True]
    horizons = sorted({r["horizon"] for r in dir_rows if r.get("horizon") is not None})

    per_field: dict[str, dict[str, Any]] = {}
    for field in HINT_FIELDS:
        rho_mfe: dict[int, float | None] = {}
        rho_mae: dict[int, float | None] = {}
        for h in horizons:
            rows_h = [r for r in dir_rows if r.get("horizon") == h]
            pairs_mfe = [
                (r[field], r["mfe"])
                for r in rows_h
                if r.get(field) is not None and r.get("mfe") is not None
            ]
            pairs_mae = [
                (r[field], r["mae"])
                for r in rows_h
                if r.get(field) is not None and r.get("mae") is not None
            ]
            rho_mfe[h] = spearman([p[0] for p in pairs_mfe], [p[1] for p in pairs_mfe])
            rho_mae[h] = spearman([p[0] for p in pairs_mae], [p[1] for p in pairs_mae])
        per_field[field] = {"rho_mfe": rho_mfe, "rho_mae": rho_mae}

    # Events per horizon (direction-inferred); used for LOW SAMPLE labelling.
    n_by_horizon = {h: len([r for r in dir_rows if r.get("horizon") == h]) for h in horizons}
    return {
        "horizons": horizons,
        "n_direction_inferred_by_horizon": n_by_horizon,
        "per_field": per_field,
    }


def triage_fields(hints: dict[str, Any]) -> dict[str, list[str]]:
    """Bucket fingerprint fields by covariation strength with mfe (descriptive)."""
    watch: list[str] = []
    weak: list[str] = []
    noise: list[str] = []
    for field in HINT_FIELDS:
        vals = [v for v in hints["per_field"][field]["rho_mfe"].values() if v is not None]
        if not vals:
            noise.append(field)
            continue
        max_abs = max(abs(v) for v in vals)
        signs = {1 if v > 0 else -1 for v in vals if v != 0}
        sign_stable = len(signs) <= 1
        if max_abs >= WATCH_ABS_RHO and sign_stable:
            watch.append(field)
        elif max_abs >= WEAK_ABS_RHO:
            weak.append(field)
        else:
            noise.append(field)
    return {"watch": watch, "weak": weak, "noise": noise}


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def write_toplist_csv(path: Path, toplist: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(TOPLIST_COLUMNS))
        writer.writeheader()
        writer.writerows(toplist)


def _notes_lines(
    toplist: list[dict],
    hints: dict[str, Any],
    triage: dict[str, list[str]],
    meta: dict[str, Any],
) -> list[str]:
    low = sum(1 for r in toplist if r["sample_flag"] == "LOW SAMPLE")
    horizons = hints["horizons"]
    lines: list[str] = []
    lines.append("# Toplist notes — fib fingerprint × outcome (research triage)")
    lines.append("")
    lines.append(f"Run: `{meta.get('run_id', '?')}`")
    lines.append("")
    lines.append("> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a")
    lines.append("> signal, and not a strategy. No parameter tuning. Buckets with")
    lines.append(f"> `n_events` < {LOW_SAMPLE_N} are flagged `LOW SAMPLE`. Use this to decide")
    lines.append("> *what to collect more data on*, not *what to trade*.")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    lines.append(f"- Joined events: {meta.get('joined_events', '?')}")
    lines.append(f"- Joined rows (event × horizon): {meta.get('joined_rows', len(toplist))}")
    lines.append(f"- Candidate buckets: {len(toplist)} ({low} flagged LOW SAMPLE)")
    lines.append(f"- Horizons: {', '.join(str(h) for h in horizons) or 'n/a'}")
    n_by_h = hints["n_direction_inferred_by_horizon"]
    n_dir = ", ".join(f"h{h}={n_by_h[h]}" for h in horizons) or "n/a"
    lines.append(f"- Direction-inferred events per horizon (used for hints): {n_dir}")
    lines.append("")
    lines.append("## View 1 — candidate summary (top 1 per candidate × horizon)")
    lines.append("")
    lines.append("Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).")
    lines.append("`mean_post_bars_on_break_side` is the expected-side proxy.")
    lines.append("")
    lines.append("| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in toplist:
        if r["rank_in_candidate_horizon"] != 1:
            continue
        lines.append(
            f"| {r['auto_candidate']} | {r['horizon']} | {r['relation']} | "
            f"{r['fib_level']} | {r['n_events']} | {r['sample_flag']} | "
            f"{_fmt(r['mean_mfe'])} | {_fmt(r['mean_mae'])} | "
            f"{_fmt(r['mean_post_bars_on_break_side'])} |"
        )
    lines.append("")
    lines.append("## View 2 — fingerprint ↔ outcome hints (Spearman rho)")
    lines.append("")
    lines.append("Direction-inferred events only; candidates pooled (coarse). Positive")
    lines.append("rho vs `mfe` = field tends to be higher when favorable excursion is")
    lines.append("higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,")
    lines.append("not prediction.")
    lines.append("")
    head = "| fingerprint field | " + " | ".join(f"mfe h{h}" for h in horizons) + " |"
    sep = "|---|" + "|".join(["---"] * len(horizons)) + "|"
    lines.append(head)
    lines.append(sep)
    for field in HINT_FIELDS:
        rho = hints["per_field"][field]["rho_mfe"]
        cells = " | ".join(_fmt(rho.get(h)) for h in horizons)
        lines.append(f"| {field} | {cells} |")
    lines.append("")
    head_mae = "| fingerprint field | " + " | ".join(f"mae h{h}" for h in horizons) + " |"
    lines.append(head_mae)
    lines.append(sep)
    for field in HINT_FIELDS:
        rho = hints["per_field"][field]["rho_mae"]
        cells = " | ".join(_fmt(rho.get(h)) for h in horizons)
        lines.append(f"| {field} | {cells} |")
    lines.append("")
    lines.append("## Triage buckets (arbitrary cut-offs, not tuned)")
    lines.append("")
    lines.append(
        f"Cut-offs on max |rho vs mfe| across horizons: "
        f"watch ≥ {WATCH_ABS_RHO} & sign-stable, weak ≥ {WEAK_ABS_RHO}, else noise-like."
    )
    lines.append("")
    lines.append(f"- **Worth more data (watch):** {', '.join(triage['watch']) or 'none'}")
    lines.append(f"- **Weak / unstable:** {', '.join(triage['weak']) or 'none'}")
    lines.append(f"- **Low covariation (noise-like):** {', '.join(triage['noise']) or 'none'}")
    lines.append("")
    lines.append("## What to look at next (triage, not conclusions)")
    lines.append("")
    lines.append("- Candidates whose buckets are all LOW SAMPLE need more events before")
    lines.append("  any pattern is worth reading.")
    lines.append("- `watch` fields are only candidates for *more data collection*, not")
    lines.append("  evidence of edge.")
    lines.append("- Recent (2026) fibs may have truncated long horizons (`bars_available`),")
    lines.append("  so h20/h50 fill in as post-2022-10-31 history grows.")
    lines.append("")
    return lines


def write_notes_md(
    path: Path,
    toplist: list[dict],
    hints: dict[str, Any],
    triage: dict[str, list[str]],
    meta: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(_notes_lines(toplist, hints, triage, meta))
    path.write_text(text, encoding="utf-8")


def _read_meta(run_dir: Path, joined: list[dict], toplist: list[dict]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "run_id": run_dir.name,
        "joined_rows": len(joined),
        "joined_events": len({r.get("event_id") for r in joined}),
    }
    summary_path = run_dir / "run_summary.json"
    if summary_path.exists():
        try:
            doc = json.loads(summary_path.read_text(encoding="utf-8"))
            meta["run_id"] = doc.get("run_id", meta["run_id"])
            meta["joined_events"] = doc.get("joined_events", meta["joined_events"])
            meta["joined_rows"] = doc.get("joined_rows", meta["joined_rows"])
        except (json.JSONDecodeError, OSError):
            pass
    return meta


def run_toplist(run_dir: Path, *, low_sample_n: int = LOW_SAMPLE_N) -> dict[str, Any]:
    """Build and write toplist.csv + TOPLIST_NOTES.md for one join run dir."""
    run_dir = Path(run_dir)
    joined = read_joined_rows(run_dir)
    toplist = build_candidate_toplist(joined, low_sample_n=low_sample_n)
    hints = fingerprint_hints(joined)
    triage = triage_fields(hints)
    meta = _read_meta(run_dir, joined, toplist)

    csv_path = run_dir / "toplist.csv"
    md_path = run_dir / "TOPLIST_NOTES.md"
    write_toplist_csv(csv_path, toplist)
    write_notes_md(md_path, toplist, hints, triage, meta)

    low = sum(1 for r in toplist if r["sample_flag"] == "LOW SAMPLE")
    return {
        "run_dir": str(run_dir),
        "toplist_csv": str(csv_path),
        "notes_md": str(md_path),
        "buckets": len(toplist),
        "low_sample_buckets": low,
        "horizons": hints["horizons"],
        "triage": triage,
    }


def _bucket_key(row: dict) -> tuple:
    return (
        str(row["auto_candidate"]),
        int(row["horizon"]) if row["horizon"] is not None else 0,
        str(row["relation"]),
        str(row["fib_level"]),
    )


def sample_inventory(toplist: list[dict], *, low_sample_n: int = LOW_SAMPLE_N) -> dict[str, Any]:
    """Count candidate buckets reaching each sample-size threshold (descriptive)."""
    inv: dict[str, Any] = {
        "total_buckets": len(toplist),
        "low_sample_buckets": sum(1 for r in toplist if (r.get("n_events") or 0) < low_sample_n),
    }
    for t in SAMPLE_THRESHOLDS:
        inv[f"buckets_n_ge_{t}"] = sum(1 for r in toplist if (r.get("n_events") or 0) >= t)
    return inv


def _field_stability(base: dict[str, Any], exp: dict[str, Any], field: str) -> dict[str, Any]:
    """Compare per-horizon Spearman(field, mfe) between two runs (descriptive)."""
    horizons = sorted(set(base["horizons"]) | set(exp["horizons"]))
    rho_base = base["per_field"].get(field, {}).get("rho_mfe", {})
    rho_exp = exp["per_field"].get(field, {}).get("rho_mfe", {})
    sign_flip = False
    max_shift = 0.0
    both_seen = False
    for h in horizons:
        b = rho_base.get(h)
        e = rho_exp.get(h)
        if b is None or e is None:
            continue
        both_seen = True
        max_shift = max(max_shift, abs(b - e))
        if b != 0 and e != 0 and (b > 0) != (e > 0):
            sign_flip = True
    base_max = max((abs(v) for v in rho_base.values() if v is not None), default=None)
    exp_max = max((abs(v) for v in rho_exp.values() if v is not None), default=None)
    if sign_flip:
        verdict = "UNSTABLE (sign flip)"
    elif not both_seen:
        verdict = "insufficient overlap"
    elif base_max is not None and exp_max is not None and (base_max - exp_max) >= 0.2:
        verdict = "WEAKENED (small-sample artifact)"
    elif max_shift <= 0.15:
        verdict = "stable-ish"
    else:
        verdict = "shifted"
    return {
        "field": field,
        "rho_base": rho_base,
        "rho_exp": rho_exp,
        "base_max_abs": base_max,
        "exp_max_abs": exp_max,
        "max_shift": round(max_shift, 4) if both_seen else None,
        "verdict": verdict,
    }


def compare_runs(baseline_dir: Path, expanded_dir: Path) -> dict[str, Any]:
    """Descriptive baseline-vs-expanded comparison: inventory + stability.

    Both args are join run dirs. ``expanded_dir`` is treated as the combined
    (superset) run. No tuning, no thresholds changed — only counts and rho deltas.
    """
    base_joined = read_joined_rows(baseline_dir)
    exp_joined = read_joined_rows(expanded_dir)
    base_top = build_candidate_toplist(base_joined)
    exp_top = build_candidate_toplist(exp_joined)

    base_n = {_bucket_key(r): int(r["n_events"] or 0) for r in base_top}
    exp_n = {_bucket_key(r): int(r["n_events"] or 0) for r in exp_top}

    bucket_rows: list[dict] = []
    for key in sorted(set(base_n) | set(exp_n)):
        candidate, horizon, relation, level = key
        nb = base_n.get(key, 0)
        ne = exp_n.get(key, 0)
        bucket_rows.append(
            {
                "auto_candidate": candidate,
                "horizon": horizon,
                "relation": relation,
                "fib_level": level,
                "n_baseline": nb,
                "n_expanded": ne,
                "delta": ne - nb,
                "reached_5": ne >= 5,
                "reached_10": ne >= 10,
                "reached_20": ne >= 20,
                "still_low_sample": ne < LOW_SAMPLE_N,
            }
        )

    base_hints = fingerprint_hints(base_joined)
    exp_hints = fingerprint_hints(exp_joined)
    stability = [_field_stability(base_hints, exp_hints, f) for f in HINT_FIELDS]

    newly_5 = [r for r in bucket_rows if r["reached_5"] and r["n_baseline"] < LOW_SAMPLE_N]
    return {
        "baseline": {
            "run_id": baseline_dir.name,
            "joined_events": len({r.get("event_id") for r in base_joined}),
            "joined_rows": len(base_joined),
            "inventory": sample_inventory(base_top),
        },
        "expanded": {
            "run_id": expanded_dir.name,
            "joined_events": len({r.get("event_id") for r in exp_joined}),
            "joined_rows": len(exp_joined),
            "inventory": sample_inventory(exp_top),
        },
        "bucket_rows": bucket_rows,
        "newly_reached_5": len(newly_5),
        "still_low_sample": sum(1 for r in bucket_rows if r["still_low_sample"]),
        "stability": stability,
    }


def write_sample_inventory_csv(path: Path, bucket_rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "auto_candidate",
        "horizon",
        "relation",
        "fib_level",
        "n_baseline",
        "n_expanded",
        "delta",
        "reached_5",
        "reached_10",
        "reached_20",
        "still_low_sample",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(bucket_rows)


def _multirun_lines(cmp: dict[str, Any]) -> list[str]:
    base = cmp["baseline"]
    exp = cmp["expanded"]
    bi = base["inventory"]
    ei = exp["inventory"]
    lines: list[str] = []
    lines.append("# Multi-run notes — fib fingerprint × outcome (data expansion triage)")
    lines.append("")
    lines.append(f"Baseline run: `{base['run_id']}` (narrow window)")
    lines.append(f"Expanded run: `{exp['run_id']}` (combined / wider candle window)")
    lines.append("")
    lines.append("> DESCRIPTIVE DATA-EXPANSION TRIAGE ONLY. Same method and thresholds;")
    lines.append("> only the candle data scope widened to grow sample size. Not an edge,")
    lines.append("> not a signal, not a strategy. No tuning. No candidate-logic change.")
    lines.append("")
    lines.append("## Combined summary")
    lines.append("")
    lines.append(
        f"- Events: {base['joined_events']} → **{exp['joined_events']}** "
        f"(rows {base['joined_rows']} → {exp['joined_rows']})"
    )
    lines.append(f"- Candidate buckets: {bi['total_buckets']} → **{ei['total_buckets']}**")
    lines.append(
        f"- Buckets newly reaching n≥5 (were LOW SAMPLE in baseline): **{cmp['newly_reached_5']}**"
    )
    lines.append(
        f"- Buckets still LOW SAMPLE (n<{LOW_SAMPLE_N}) in expanded: {cmp['still_low_sample']}"
    )
    lines.append("")
    lines.append("## Sample-size inventory")
    lines.append("")
    lines.append("| metric | baseline | expanded |")
    lines.append("|---|---|---|")
    lines.append(f"| total buckets | {bi['total_buckets']} | {ei['total_buckets']} |")
    for t in SAMPLE_THRESHOLDS:
        key = f"buckets_n_ge_{t}"
        lines.append(f"| buckets n≥{t} | {bi[key]} | {ei[key]} |")
    lines.append(
        f"| LOW SAMPLE buckets | {bi['low_sample_buckets']} | {ei['low_sample_buckets']} |"
    )
    lines.append("")
    lines.append("Per-bucket detail: `sample_inventory.csv`.")
    lines.append("")
    lines.append("## Fingerprint stability over more events")
    lines.append("")
    lines.append("Compares Spearman(field, mfe) per horizon between runs (direction-")
    lines.append("inferred events, candidates pooled). `WEAKENED` = a baseline signal")
    lines.append("shrank with more data (small-sample artifact). `sign flip` = direction")
    lines.append("reversed. Descriptive only.")
    lines.append("")
    lines.append(
        "| fingerprint field | base max\\|rho\\| | exp max\\|rho\\| | max shift | verdict |"
    )
    lines.append("|---|---|---|---|---|")
    for s in cmp["stability"]:
        lines.append(
            f"| {s['field']} | {_fmt(s['base_max_abs'])} | {_fmt(s['exp_max_abs'])} | "
            f"{_fmt(s['max_shift'])} | {s['verdict']} |"
        )
    lines.append("")
    lines.append("## What to look at next (triage, not conclusions)")
    lines.append("")
    lines.append("- `WEAKENED` / `sign flip` fields were noise at low N — deprioritize.")
    lines.append("- `stable-ish` fields kept their (weak) co-occurrence as N grew — the")
    lines.append("  only ones worth a closer, per-candidate look once buckets are larger.")
    lines.append("- Buckets still LOW SAMPLE need more events (older BTC pre-2016 and SOL")
    lines.append("  pre-2022 1d need a network refetch before they can join).")
    lines.append("")
    return lines


def run_compare(
    baseline_dir: Path, expanded_dir: Path, *, out_dir: Path | None = None
) -> dict[str, Any]:
    """Write MULTIRUN_NOTES.md + sample_inventory.csv into the expanded run dir."""
    baseline_dir = Path(baseline_dir)
    expanded_dir = Path(expanded_dir)
    out_dir = Path(out_dir) if out_dir else expanded_dir
    cmp = compare_runs(baseline_dir, expanded_dir)

    inv_csv = out_dir / "sample_inventory.csv"
    notes_md = out_dir / "MULTIRUN_NOTES.md"
    write_sample_inventory_csv(inv_csv, cmp["bucket_rows"])
    notes_md.write_text("\n".join(_multirun_lines(cmp)), encoding="utf-8")
    return {
        "baseline_run": cmp["baseline"]["run_id"],
        "expanded_run": cmp["expanded"]["run_id"],
        "sample_inventory_csv": str(inv_csv),
        "multirun_notes_md": str(notes_md),
        "newly_reached_5": cmp["newly_reached_5"],
        "still_low_sample": cmp["still_low_sample"],
    }


def _latest_run_dir() -> Path:
    if not JOIN_RUNS.exists():
        raise FileNotFoundError(f"No join runs under {JOIN_RUNS}")
    candidates = [p for p in JOIN_RUNS.rglob("fingerprint_outcomes.jsonl")]
    if not candidates:
        raise FileNotFoundError(f"No fingerprint_outcomes.jsonl under {JOIN_RUNS}")
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest.parent


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Descriptive low-sample triage top-list for fib fingerprint × outcome joins."
    )
    p.add_argument("--run-dir", type=Path, default=None, help="Join run dir (default: latest).")
    p.add_argument("--low-sample-n", type=int, default=LOW_SAMPLE_N)
    p.add_argument(
        "--compare-to",
        type=Path,
        default=None,
        help="Baseline join run dir. When set, also writes MULTIRUN_NOTES.md + "
        "sample_inventory.csv comparing it to --run-dir (treated as expanded).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    run_dir = args.run_dir or _latest_run_dir()
    result = run_toplist(run_dir, low_sample_n=args.low_sample_n)
    if args.compare_to is not None:
        result["compare"] = run_compare(args.compare_to, run_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
