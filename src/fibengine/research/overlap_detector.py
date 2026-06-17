"""Source-fib overlap / near-duplicate detector — stdlib-only, report-only.

Finds **candidate** overlapping or near-duplicate human source fibs so dense zones (e.g.
2017_h2, the 2021 crash legs) can be triaged without eyeballing 100+ charts. It reports
candidates for human review — it never says "wrong", never edits labels, never renders.

Each fib is a box in ``(time, log-price)`` space spanning its ``anchor_a → anchor_b``
segment. For a pair we compute:

- ``time_iou`` / ``price_iou`` — 1-D intersection-over-union per axis,
- ``box_iou`` — 2-D IoU of the boxes (high only when *both* axes overlap strongly),
- ``shared_anchor`` — whether the two fibs pin an identical anchor_a and/or anchor_b
  (e.g. two sub-legs of the same crash sharing one endpoint).

A pair is a candidate if ``box_iou >= min_box_iou`` **or** it shares an anchor. This is a
review aid, not a judgement: shared anchors and partial overlaps are often legitimate
distinct sub-legs.

Usage::

    python -m fibengine.research.overlap_detector \\
        --fib-dir data/labels/human_fib/bitfinex/BTC-USD/4h \\
        --out docs/research_wiki/reviews/btc-4h-overlap-candidates.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CANDIDATE_FIELDS: tuple[str, ...] = (
    "fib_a",
    "fib_b",
    "time_iou",
    "price_iou",
    "box_iou",
    "shared_anchor",
)


@dataclass
class FibBox:
    """A source fib as a box in (epoch-seconds, log-price) space."""

    fib_id: str
    timeframe: str
    t_lo: float
    t_hi: float
    p_lo: float
    p_hi: float
    a_epoch: float
    a_price: float
    b_epoch: float
    b_price: float


@dataclass
class OverlapCandidate:
    fib_a: str
    fib_b: str
    time_iou: float
    price_iou: float
    box_iou: float
    shared_anchor: str  # "", "anchor_a", "anchor_b", or "anchor_a,anchor_b"


def _epoch(iso_time: str) -> float:
    return datetime.fromisoformat(iso_time).timestamp()


def load_boxes(fib_dir: Path | str, require_timeframe: str | None = None) -> list[FibBox]:
    """Load source fibs as boxes. Fail-closed on empty dir or timeframe mismatch.

    If ``require_timeframe`` is set, every fib must match it (the guard that keeps this
    from silently consuming 1D/1W fibs when ``--fib-dir`` points at the wrong folder).
    """
    files = sorted(Path(fib_dir).glob("fib_*.json"))
    if not files:
        raise FileNotFoundError(f"No fib_*.json annotations found in {fib_dir}")
    boxes: list[FibBox] = []
    violations: list[str] = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        tf = d.get("timeframe")
        if require_timeframe is not None and tf != require_timeframe:
            fid = d.get("fib_id", f.name)
            violations.append(f"{fid}: timeframe {tf!r} != {require_timeframe!r}")
            continue
        a_e, b_e = _epoch(d["anchor_a"]["time"]), _epoch(d["anchor_b"]["time"])
        a_p, b_p = float(d["anchor_a"]["price"]), float(d["anchor_b"]["price"])
        boxes.append(
            FibBox(
                fib_id=d["fib_id"],
                timeframe=tf,
                t_lo=min(a_e, b_e),
                t_hi=max(a_e, b_e),
                p_lo=math.log(min(a_p, b_p)),
                p_hi=math.log(max(a_p, b_p)),
                a_epoch=a_e,
                a_price=a_p,
                b_epoch=b_e,
                b_price=b_p,
            )
        )
    if violations:
        joined = "\n  - ".join(violations)
        raise ValueError(f"overlap_detector refuses non-matching-timeframe fibs:\n  - {joined}")
    return boxes


def _overlap_len(lo1: float, hi1: float, lo2: float, hi2: float) -> float:
    return max(0.0, min(hi1, hi2) - max(lo1, lo2))


def _iou_1d(lo1: float, hi1: float, lo2: float, hi2: float) -> float:
    inter = _overlap_len(lo1, hi1, lo2, hi2)
    union = (hi1 - lo1) + (hi2 - lo2) - inter
    return inter / union if union > 0 else 0.0


def box_iou(a: FibBox, b: FibBox) -> float:
    """2-D IoU of two fib boxes (0 if either axis does not overlap)."""
    inter = _overlap_len(a.t_lo, a.t_hi, b.t_lo, b.t_hi) * _overlap_len(
        a.p_lo, a.p_hi, b.p_lo, b.p_hi
    )
    area_a = (a.t_hi - a.t_lo) * (a.p_hi - a.p_lo)
    area_b = (b.t_hi - b.t_lo) * (b.p_hi - b.p_lo)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _shared_anchor(a: FibBox, b: FibBox) -> str:
    shared: list[str] = []
    if abs(a.a_epoch - b.a_epoch) < 1.0 and math.isclose(a.a_price, b.a_price, rel_tol=1e-6):
        shared.append("anchor_a")
    if abs(a.b_epoch - b.b_epoch) < 1.0 and math.isclose(a.b_price, b.b_price, rel_tol=1e-6):
        shared.append("anchor_b")
    return ",".join(shared)


def find_overlap_candidates(
    boxes: list[FibBox],
    min_box_iou: float = 0.5,
    include_shared_anchor: bool = True,
) -> list[OverlapCandidate]:
    """Return candidate pairs, sorted by ``box_iou`` desc. Pure read; mutates nothing."""
    out: list[OverlapCandidate] = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            biou = box_iou(a, b)
            shared = _shared_anchor(a, b)
            if biou >= min_box_iou or (include_shared_anchor and shared):
                out.append(
                    OverlapCandidate(
                        fib_a=a.fib_id,
                        fib_b=b.fib_id,
                        time_iou=round(_iou_1d(a.t_lo, a.t_hi, b.t_lo, b.t_hi), 4),
                        price_iou=round(_iou_1d(a.p_lo, a.p_hi, b.p_lo, b.p_hi), 4),
                        box_iou=round(biou, 4),
                        shared_anchor=shared,
                    )
                )
    out.sort(key=lambda c: (c.box_iou, c.shared_anchor), reverse=True)
    return out


def write_candidates_csv(path: Path | str, candidates: list[OverlapCandidate]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        for c in candidates:
            writer.writerow(
                {
                    "fib_a": c.fib_a,
                    "fib_b": c.fib_b,
                    "time_iou": c.time_iou,
                    "price_iou": c.price_iou,
                    "box_iou": c.box_iou,
                    "shared_anchor": c.shared_anchor,
                }
            )
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Detect overlapping / near-duplicate source fibs (report-only, stdlib)."
    )
    p.add_argument("--fib-dir", required=True, help="Directory of fib_*.json annotations")
    p.add_argument("--out", default=None, help="CSV report path (default: print summary only)")
    p.add_argument("--min-iou", type=float, default=0.5, help="Min box IoU to flag (default 0.5)")
    p.add_argument(
        "--require-timeframe",
        default="4h",
        help="Fail-closed: every fib must match this timeframe (default 4h; '' disables)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    boxes = load_boxes(args.fib_dir, require_timeframe=args.require_timeframe or None)
    candidates = find_overlap_candidates(boxes, min_box_iou=args.min_iou)
    shared = sum(1 for c in candidates if c.shared_anchor)
    print(
        f"overlap detector: {len(boxes)} fibs, {len(candidates)} candidate pair(s) "
        f"(box_iou>={args.min_iou} or shared anchor); {shared} share an anchor"
    )
    if args.out:
        out = write_candidates_csv(args.out, candidates)
        print(f"report written: {out}")
    else:
        for c in candidates[:20]:
            print(f"  {c.fib_a}  ~  {c.fib_b}  box_iou={c.box_iou} shared={c.shared_anchor or '-'}")
