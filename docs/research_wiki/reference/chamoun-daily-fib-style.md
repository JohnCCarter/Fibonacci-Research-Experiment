# Chamoun daily-fib drawing style — distilled rules

Consolidated so the human's daily fib-drawing style is **captured once, not re-explained to every
agent**. Produced by [`/chamoun-fib-style-distiller`](../../../.claude/commands/chamoun-fib-style-distiller.md)
over the 76 daily facit in `data/labels/human_fib/bitfinex/BTC-USD/1d/fib_*.json` plus the #38
prereg/postlock and [handoff.md](../handoff.md).

**Authority:** this is layer-5 wiki synthesis. The facit (layer 1) and the signed-off run results
win on any conflict — see [source-authority.md](source-authority.md). Every rule is tagged
**Observed** (in the facit), **Inferred** (pattern across ≥2 examples/probes), or **Unverified**
(plausible, missing input named). This is descriptive note-taking only — **no edge / PnL /
continuation claim**, no new label-schema fields.

## Observed — directly in the facit (N=76 daily)

- **O1 — A/B are chronological.** `anchor_a` is always the earlier bar, `anchor_b` the later
  (75/76 strictly before; 1 same-day degenerate = `fib_BTC-USD_1d_20210907T000000`).
- **O2 — 0.0 sits at the move's END (`anchor_b`), 1.0 at its START (`anchor_a`).** For
  `direction:"down"` A>B (40/40, A=high→B=low); for `"up"` A<B (36/36, A=low→B=high). **Zero
  violations.** The fib measures retracement of the A→B impulse — matching the DECOMPOSITION rule
  ("1" = origin A, "0" = fresh impulse end B). Examples: `fib_..._1d_20170105` (down 1166→735),
  `fib_..._1d_20200330` (up 5880.9→7420).
- **O3 — Fixed level profile.** `levels_profile: tradingview_log_chamoun`, `scale_mode: log`,
  ratios `{0, 0.382, 0.5, 0.618, 0.786, 1.0}`; **0.236 never used (0/76).** 100% consistent.
- **O4 — Anchors sit on bar high/low (wick tip), but this is tool-enforced.** The labeling tool
  snaps every click/drag to the nearest bar high/low
  ([`labeling/tool.py`](../../../src/fibengine/labeling/tool.py)), so the sonde's 94%-wick / 0%-body
  split is the *tool*, not an independent style measurement. **Wick-vs-body is not observable from
  facit** (see prereg §"Sonde RESULT", lines 53–69).
- **O5 — Direction is balanced.** 40 down / 36 up — no strong long/short bias in what is labeled.
- **O6 — Leg length is not fixed.** Calendar-day span between anchors: median 8d, min 0d
  (`20210907`), max 360d (`20171216`). Daily fibs range from ~a week to ~a year → **scale is a free
  parameter** (connects to the "continuation gap = SCALE issue", handoff DECOMPOSITION thread).
- **O7 — No `human_highlights` (0/76).** No level is marked special; all levels drawn equally
  (consistent with the retired golden-zone bias).

## Inferred — pattern across ≥2 examples / probes

- **I1 — Admissibility holds on BOTH anchors.** Each anchor terminates a *clean, directed impulse*
  (fresh break, no intervening counter-push, `k_between=0`). Real but **definitional** — it
  constrains the candidate set, it does not uniquely pick.
- **I2 — "0" = a fresh break** (100% in the endpoint probe); fresh-conditioned depth modestly
  elevated (47% vs 36%, p=0.019). **Recency is dead** — the most-recent extreme is not automatically
  chosen.
- **I3 — Selection is not "most-prominent pivot".** The human's A/B sit at *different bars* than the
  detectors' prominent/wick pivots (#38 wick-pair coverage 0.08 vs fractal control 0.90). The
  selection is a *retracement frame*, not a swing-detector output.

## Unverified — plausible, missing input named

- **U1 — CASCADE / scale-consistency is the top self-reported signal, untested.** The claim: legs
  chain as a cascade ("furthest = downtrend"). Facit is too sparse to chain automatically, and the
  1w cascade the human drew is blocked because price-only snapping scrambles chronology (BTC hit
  16–30k twice). **Missing to promote:** rough **years + direction per cascade leg** to window the
  snap. See the cascade-input template below.
- **U2 — The positive selection rule is non-geometric.** *Which* admissible extreme is picked is
  origin-flat-null (p≈0.45/0.59) — **not** prominence, **not** recency. Six probes bound what it is
  *not*. **Missing:** a non-geometric feature hypothesis (context? cascade membership? a verbal rule
  not yet externalized).
- **U3 — body/close-vs-wick intent.** A prior repo note ("crash-leg anchors use body/close") cannot
  be tested against tool-snapped facit (O4). **Missing:** the human's explicit intent (does he mean
  the wick tip or the close when drawing a crash leg?), or un-snapped placements.
  **Source wins — flagged for reconcile, does not block.**

## A/B anchor — winner / loser / why

- **Winner:** the pair (earlier extreme A, later fresh-impulse extreme B) forming a *clean directed
  impulse* with no intervening counter-push, on the scale being eyeballed.
- **Loser:** prominence / most-recent / wick-magnitude pivots — what the detectors pick, and they do
  **not** match the human (coverage 0.08; recency dead; prominence flat-null).
- **Discriminating feature:** *cleanliness / freshness* of the impulse, not geometric prominence.
  The residual — *which* clean extreme — is the open crux (U2).

## Reconcile items (open)

- **Count drift.** [handoff.md](../handoff.md) states 67 daily base fibs; the actual corpus is
  **76** (grow-facit growth). Reconcile the count in handoff / Verification Snapshot.
- **Degenerate leg.** `fib_BTC-USD_1d_20210907T000000` has `anchor_a.time == anchor_b.time`
  (leg = 0 days). Confirm intended vs mislabel.
- **U3 body/close intent** — carry until the human states intent or provides un-snapped placements.

## Cascade-input template (fill to unblock the paused CASCADE probe)

The paused CASCADE probe (handoff "Next Step") needs rough windowing so the price-only snap does not
scramble chronology. Fill one row per cascade leg (rough is fine):

| Cascade | Leg # | Approx years (start → end) | Direction | Notes |
|---------|-------|----------------------------|-----------|-------|
| 1 | 1 | e.g. 2021 → 2022 | down | "furthest = downtrend" |
| … | … | … | … | … |

Once filled, the next agent can window the snap and run the scale-consistency probe (magnitude /
duration CV vs independently-placed clean legs, chaining conditioned out).

## Sources

- Facit: `data/labels/human_fib/bitfinex/BTC-USD/1d/fib_*.json` (N=76).
- [#38 daily wick-pair anchor prereg (LOCKED)](../reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md)
  + [postlock (`wick_pair_no_better`, signed off)](../reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629-postlock.md).
- [handoff.md](../handoff.md) — DECOMPOSITION thread (2026-07-01), cascade probe, origin/endpoint probes.
- [source-authority.md](source-authority.md) — layer model (facit wins over wiki synthesis).
