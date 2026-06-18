# Purged / embargoed out-of-sample split

**Query this before re-deriving the leakage-safe split.** The repo already implements the core of it
— do not rebuild a full CPCV module without a demonstrated need (that is SENARE-2, gated).

## The idea

A time-ordered train/test split where events whose **outcome horizon straddles the boundary** are
**dropped** (purged), with an **embargo** of `max(horizon)` bars at the split so no test event's
look-ahead window overlaps train data. This neutralises horizon-straddle leakage — the standard trap
in financial ML where overlapping label windows leak future information across the split.

Name + provenance: **purged / embargo / combinatorial purged CV (CPCV)**, López de Prado,
*Advances in Financial Machine Learning* (2018), Ch. 12. Cite this vocabulary; don't reinvent it.

## Where the repo implements it

- `split_positions()` and `_window_of()` in
  [`src/fibengine/research/fib_behaviour_event_study.py`](../../../src/fibengine/research/fib_behaviour_event_study.py)
  — `_window_of` returns `None` (drops the event) when `pos + max_h` crosses the split, which is the
  purge + embargo in one step.
- Reused unchanged by the B-1 harness
  (`horizontal_structure_event_study.py`) and pre-registered for the
  [selection-learning study §9](../reviews/btc-fib-selection-learning-prereg-20260617.md) (split on
  the leg's **anchor/chart time**, not `created_at`).

## Don't over-build

The single-split embargo already covers horizon-straddle leakage for the event studies. A full
combinatorial purged-CV module (**SENARE-2**) is gated on a need the single split does not cover —
adopting it carelessly (bad label-interval assignment) can *introduce* leakage. See
[addendum NU-3](../reviews/horizontal-structure-prereg-addendum-20260617.md).

## Sources

[methodology-anchors.md](../sources/methodology-anchors.md). [Source authority](../reference/source-authority.md):
the code is truth; this page is the map.
