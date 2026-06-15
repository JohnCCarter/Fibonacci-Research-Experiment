# BTC/USD 4H Overlap / Near-Duplicate Candidates (2026-06-15)

Report-only triage of possible overlapping / near-duplicate 4H source fibs, produced by
[`research/overlap_detector.py`](../../../src/fibengine/research/overlap_detector.py)
(stdlib-only). **Candidates for human review — not errors.** No source labels changed.

CSV: [btc-4h-overlap-candidates-20260615.csv](btc-4h-overlap-candidates-20260615.csv).

## Method

Each fib is a box in `(time, log-price)` space over its `anchor_a → anchor_b` segment.
Per pair: 1-D IoU per axis (`time_iou`, `price_iou`), 2-D `box_iou`, and `shared_anchor`
(identical anchor_a and/or anchor_b). A pair is flagged when `box_iou >= 0.5` **or** it
shares an anchor. The geometry is log-scale (matching the fib profile).

## Real run

- Input: 366 BTC/USD 4H source fibs.
- **22 candidate pairs**, **all 22 sharing `anchor_b`** — no pair reached `box_iou >= 0.5`
  on geometry alone. Lowering the threshold surfaces only a few weak geometric overlaps
  (23 at 0.3, 24 at 0.2, 31 at 0.1), confirming the dominant signal is *shared endpoint*,
  not duplicated boxes.

**Interpretation:** the common pattern is several sub-legs ending at the **same swing
low/high** (shared `anchor_b`) but starting from different `anchor_a` — i.e. legitimately
distinct sub-legs of one move, not duplicates. This is expected in dense zones and is a
review aid, not a defect list.

## Known cases

- **2021 crash pair (confirmed):** `20210110T080000` ~ `20210110T200000` — shared
  `anchor_b`, `box_iou` 0.51, `price_iou` 0.82. The exact pattern noted in the Tier 2
  review (two sub-legs, same endpoint). Distinct legs — keep both.
- **2017_h2 cluster:** 8 pairs involve 2017 fibs (e.g. `20171025`/`20171026`,
  `20171105`/`20171106`, `20171217`/`20171222`) — shared-anchor sub-legs in the parabola,
  consistent with the Tier 1 density finding.
- **Strongest near-duplicate:** `20250506T080000` ~ `20250506T120000` — `box_iou` 0.70,
  4h apart, shared `anchor_b`, 92% price overlap. Worth a human look (possible duplicate).
- **`20171228T200000` (correction-candidate) does NOT appear** — it shares no anchor and
  has no high overlap. Correct: its issue is anchor_a *quality*, not duplication. Tracked
  separately in the [review ledger](ledgers/btc-4h-source-quality-ledger.csv).

## Regenerate

```bash
uv run --no-sync python -m fibengine.research.overlap_detector \
  --fib-dir data/labels/human_fib/bitfinex/BTC-USD/4h \
  --out docs/research_wiki/reviews/btc-4h-overlap-candidates-20260615.csv \
  --min-iou 0.5
```

`--min-iou` lowers the geometric threshold; shared-anchor pairs are always included.
The detector reports only — promote any candidate to the review ledger by human decision.
