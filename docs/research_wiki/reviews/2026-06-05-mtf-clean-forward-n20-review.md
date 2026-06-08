# Review — clean-forward 4H projection, n≥20 buckets only

Date: 2026-06-05 · Cohort: **clean-forward** (`anchor_b ≥ 2022-10-31`) ·
Run: `mtf_proj_20260605T124444Z` · LTF: 4H

> Descriptive only. No tuning, no new logic, no trading signal, no edge claim.
> Cross-era is a **separate** "historical level revisit" question and is excluded here.
> Bucket = `candidate × relation × level × horizon` (timeframe constant = 4h).

Scope: 2468 joined rows, 336 buckets, **32 buckets reach n≥20**, two symbols only
(BTC/USD, SOL/USD — clean-forward has no ETH; all ETH fibs are pre-2022).

## 1. Which buckets reach n≥20?

8 families (`candidate × relation × level`), each across all 4 horizons → 32 buckets.
`ret` = mean forward_return (pooled BTC+SOL); per-symbol split shown in the last column.

| candidate | relation | level | n | ret h5 | ret h10 | ret h20 | ret h50 | BTC n / SOL n |
|---|---|---|---|---|---|---|---|---|
| continuation | cross | 0.236 | 22 | −0.0013 | −0.0051 | −0.0156 | −0.0159 | 13 / 9 |
| continuation | cross | 0.382 | 31 | +0.0066 | +0.0172 | +0.0126 | +0.0049 | 21 / 10 |
| continuation | cross | 0.5 | 25 | +0.0013 | +0.0147 | +0.0050 | +0.0224 | 12 / 13 |
| continuation | touch | 0.236 | 21 | +0.0074 | −0.0054 | −0.0057 | +0.0058 | 14 / 7 |
| continuation | touch | 0.618 | 20 | −0.0070 | −0.0058 | +0.0212 | +0.0313 | 6 / 14 |
| rejection | touch | 0.236 | 24 | −0.0030 | −0.0102 | −0.0020 | −0.0138 | 15 / 9 |
| rejection | touch | 0.5 | 22 | +0.0092 | +0.0090 | +0.0054 | −0.0279 | 9 / 13 |
| rejection | touch | 0.618 | 32 | +0.0057 | −0.0011 | −0.0016 | −0.0091 | 14 / 18 |

All n≥20 counts are **pooled**. No single family reaches n≥20 within one symbol
(BTC max 21, SOL max 18).

## 2. Consistent across horizons?

Sign of mean forward_return across h5/h10/h20/h50:

- **Sign-stable:** continuation cross 0.236 (− − − −), continuation cross 0.382
  (+ + + +), continuation cross 0.5 (+ + + +), rejection touch 0.236 (− − − −).
- **Flips:** continuation touch 0.236, continuation touch 0.618, rejection touch 0.5,
  rejection touch 0.618.

Caveat (mechanical): h5⊂h10⊂h20⊂h50 are **nested cumulative windows** of the same
event, so their signs are autocorrelated by construction. Horizon "consistency" is
therefore weak evidence, not independent confirmation. Magnitudes are tiny (≤~1.6%
mean) and `mfe ≈ mae` grow together (symmetric, random-walk-like).

## 3. Consistent between BTC and SOL?

**No.** No `candidate × relation × level × horizon` bucket has n≥20 for **both** BTC
and SOL, so no like-for-like comparison is even available at this sample size. Within
the pooled buckets the per-symbol signs frequently **disagree**, e.g.:

- continuation touch 0.618 h50: BTC −0.092 vs SOL +0.084
- continuation cross 0.382 h50: BTC −0.015 vs SOL +0.048
- rejection touch 0.236 h50: BTC −0.041 vs SOL +0.031

The pooled sign mostly reflects whichever symbol contributed more events, not a shared
behavior.

## 4. Clearly noise-like?

- `rate_close_on_approach_side` is **definitional at h5** (rejection ≈ 1.0,
  continuation = 0.0) and then **decays toward ~0.5** as horizon grows → reversion to a
  coin flip.
- `rate_crossed_back` **rises monotonically with horizon** (more time → more chance to
  cross) → mechanical, not structural.
- Returns hover around 0 (±1–2%) with symmetric mfe/mae expansion.

The flip families (continuation touch 0.236/0.618, rejection touch 0.5/0.618) are
noise-like on this evidence.

## 5. Worth more data?

Only as *collection targets*, not as signals. The least-noisy families (sign-stable +
larger n) are continuation cross 0.382 (n=31) and 0.5 (n=25), and rejection touch 0.236
(n=24). But every one of them **fails the BTC-vs-SOL agreement test**, so none is
evidence. The first real unlock is **per-symbol n≥20** (need more clean-forward fibs
per asset) and **more assets** (clean-forward currently has no ETH).

## Verdict

**clean-forward 4H projection works, but no stable evidence yet.**

The pipeline produces deterministic, layer-separated MTF rows and enough sample for a
first descriptive read, but: horizon "consistency" is mechanical (nested windows),
cross-asset consistency fails (BTC vs SOL disagree; no shared n≥20 bucket), interaction
rates revert to coin-flip, and magnitudes are tiny. Nothing here is an edge.

## Related

- [MTF projection checkpoint](2026-06-05-mtf-fib-projection-checkpoint.md) (cohort split + 4H runs)
- [MTF_FIB_LEVEL_PROJECTION.md](../../MTF_FIB_LEVEL_PROJECTION.md)
- Cross-era cohort is tracked separately (historical level revisit), not mixed in here.
