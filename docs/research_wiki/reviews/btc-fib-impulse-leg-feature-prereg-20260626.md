# Impulse-leg feature — 4h enrichment pre-reg (LOCKED 2026-06-26)

**Status:** LOCKED 2026-06-26 (human sign-off). Feature def + baseline + decision rule frozen
pre-run; sonder green (orthogonal + leg-aware). Build + run authorized under this lock. Result
becomes "truth" only after human sign-off of the run output.

## Question

Does a **sequential-impulse** feature `impulse_leg` add **AP-lift over the Stage-2 baseline** (which
already has cleanliness + prominence) at reproducing the human's 4h leg pick, OOS?

## Why this feature, on this data (background)

- Facit images (2026-06-26): the human draws **sequential impulse legs decomposing a trend** —
  each chosen leg's endpoint **extends** the trend (breaks the prior extreme) and its start is the
  **retracement extreme**. This is **within-TF** sequential nesting, NOT cross-TF.
- That reframes the **1w→1d nesting null** (this session): we tested the wrong axis — the human does
  not nest a 1w parent into 1d; he decomposes a single-TF trend into successive legs.
- Per-leg **geometry** features saturate: `exclusivity` was redundant (r=0.80 with cleanliness,
  `enriched_worse`). Learning curve: `saturated; lever is the feature side`. `impulse_leg` is a
  **non-geometry, leg-aware** axis — the missing kind of feature, not more of the same.
- Anchor convention **verified against source** (facit JSON, both directions): `anchor_b` = ratio-0
  = later-in-time = endpoint (where BOS is measured); `anchor_a` = ratio-1 = retracement extreme.

## Feature definition (LOCKED, one shot — designed from facit, protected only by the OOS split)

For a candidate leg (start `A`, end `B` = later pivot), direction `d`:

```
endpoint_BOS    = 1 if B breaks the prior same-kind pivot (down: B.low < prev_low;
                       up: B.high > prev_high), else 0                         # endpoint-bound
start_dominance = 1 if A is the dominant opposite swing in the retracement zone
                       (zone = opposite-kind pivots between prev same-kind extreme and B;
                        down: highest high; up: lowest low), else 0            # varies over starts
impulse_leg     = (endpoint_BOS + start_dominance) / 2     ∈ {0, 0.5, 1}
```

Causal: only pivots with index ≤ B (no peek). Re-detected on the truncated frame at `B + k` exactly
as the other Stage-2 features (truncate-and-whitelist), `k* = k` so it is whitelisted at the primary
`k = 3`.

## Sonde evidence (TRAIN only, leakage-free — does not touch the target)

`scratchpad/impulse_probe.py`, 4h train (61476 legs):
- corr(impulse_leg, ·): prominence **+0.19**, magnitude +0.08, cleanliness +0.36, structure_alignment
  +0.14 — all < 0.5, orthogonal to the baseline it must beat (cf. exclusivity 0.80).
- within-endpoint variation: **5132/5132** multi-start endpoints have varying `impulse_leg` →
  leg-aware on every decision point (structure_alignment's blindness would be 0/N).
- distribution: impulse_leg 0=0.50 / 0.5=0.46 / 1=0.04; endpoint_BOS=0.46, start_dominance=0.08.

## Method (reuse the enrichment harness — same as the exclusivity test)

`AP(Stage-2 + impulse_leg) − AP(Stage-2)` on **identical** 4h test legs (nested model, NOT trivial
baseline), live-equivalent `k = 3`, decision-point cluster bootstrap for the lift CI/p. Same ε, same
0.70 temporal purged split, pooled-AP. **Baseline = the full current Stage-2** (cleanliness, duration,
magnitude, prominence, structure_alignment) — impulse_leg must beat a model that already has them.

## Scale / honesty (BINDING)

- 4h is **powered** (N≈365 source legs, ~65 test positives — same cell as the headline). This is a
  real powered test, unlike the N=9 nesting cell.
- Still only answers *"does this improve human-like leg selection vs the facit?"* — **no** edge / PnL /
  backtest / Genesis / auto-fib claim.
- Honesty: cleanliness corr is the highest (0.36); report it. If the lift is small, say so vs the
  modest headline (AP ~0.057 over a 0.008–0.014 baseline).

## Decision rule (LOCKED)

- `impulse_leg_carries_signal` if AP-lift CI lower bound > 0 (decision-point bootstrap), powered cell.
- `impulse_leg_no_signal` if CI includes 0 or lift < 0 → the per-leg-feature line stays closed; the
  durable win remains the within-TF sequential-nesting **reframe** (banked regardless of this result).
- No redefinition against the result. One shot.

## Gate

DRAFT. **Lock = human sign-off.** Build + run authorized in the same sign-off (sonder green).
Result becomes "truth" only after human sign-off of the run output.
