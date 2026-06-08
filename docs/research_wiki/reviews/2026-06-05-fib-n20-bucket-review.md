# 2026-06-05 n≥20 Bucket Review (fib fingerprint × outcome)

Descriptive review of the candidate buckets that reached **n≥20** in the expanded
join run `fp_outcomes_20260605T115819Z`. Read-only analysis of existing summary
output — no new logic, no tuning, no trading signal, no edge claim, no candidate
changes.

## 1. Which buckets reached n≥20

80 bucket-rows = **20 (candidate × relation × level) groups, each with all 4
horizons (5/10/20/50) at n≥20**. All timeframe `1d` (single TF, so cross-TF
consistency is not testable yet).

| candidate | rel | level | n | fr h5→h50 | mfe h5→h50 | mae h50 | appr h5→h50 | class |
|---|---|---|---|---|---|---|---|---|
| continuation | cross | 0.236 | 43 | -0.047 → -0.046 | 0.150 → 0.436 | 0.159 | 0.00 → 0.23 | noise-like |
| continuation | cross | 0.382 | 42 | -0.035 → -0.084 | 0.131 → 0.375 | 0.200 | 0.00 → 0.29 | noise-like |
| continuation | cross | 0.5 | 43 | -0.056 → -0.071 | 0.148 → 0.452 | 0.170 | 0.00 → 0.21 | noise-like |
| continuation | cross | 0.618 | 41 | -0.045 → -0.060 | 0.136 → 0.413 | 0.168 | 0.00 → 0.20 | noise-like |
| continuation | cross | 0.786 | 38 | -0.032 → -0.072 | 0.155 → 0.433 | 0.154 | 0.00 → 0.18 | noise-like |
| continuation | cross | 1 | 42 | -0.030 → +0.060 | 0.164 → 0.511 | 0.192 | 0.00 → 0.24 | weak |
| continuation | touch | 0.236 | 33 | -0.054 → +0.003 | 0.202 → 0.441 | 0.256 | 0.00 → 0.42 | weak |
| continuation | touch | 0.382 | 21 | -0.089 → -0.037 | 0.209 → 0.506 | 0.133 | 0.00 → 0.14 | weak |
| continuation | touch | 0.618 | 25 | +0.002 → **+0.279** | 0.233 → 0.781 | 0.114 | 0.00 → 0.20 | worth more data |
| continuation | touch | 0.786 | 28 | -0.051 → **+0.270** | 0.197 → 0.743 | 0.148 | 0.00 → 0.25 | worth more data |
| failure | cross | 0.236 | 25 | +0.027 → -0.115 | 0.176 → 0.350 | 0.237 | 1.00 → 0.40 | weak |
| failure | cross | 0.382 | 30 | +0.054 → +0.027 | 0.194 → 0.393 | 0.322 | 1.00 → 0.33 | weak |
| failure | cross | 0.5 | 26 | +0.014 → -0.010 | 0.175 → 0.351 | 0.280 | 1.00 → 0.50 | noise-like |
| reaction | touch | 0.5 | 22 | -0.037 → +0.142 | 0.132 → 0.599 | 0.599 | 0.36 → 0.64 | no evidence (neutral) |
| rejection | touch | 0.236 | 35 | +0.022 → +0.050 | 0.152 → 0.516 | 0.260 | 1.00 → 0.63 | weak |
| rejection | touch | 0.382 | 48 | +0.037 → -0.042 | 0.159 → 0.395 | 0.231 | 1.00 → 0.56 | weak |
| rejection | touch | 0.5 | 43 | +0.045 → -0.018 | 0.178 → 0.519 | 0.201 | 1.00 → 0.58 | weak |
| rejection | touch | 0.618 | 49 | +0.033 → +0.153 | 0.162 → 0.633 | 0.148 | 1.00 → 0.76 | worth more data |
| rejection | touch | 0.786 | 28 | -0.013 → +0.087 | 0.150 → 0.427 | 0.305 | 1.00 → 0.57 | weak |
| rejection | touch | 1 | 20 | +0.050 → +0.084 | 0.156 → 0.721 | 0.153 | 1.00 → 0.65 | worth more data |

## 2. Consistent direction across horizons?

- **mfe and mae rise monotonically with horizon in all 20 groups.** This is
  mechanical (longer horizon = more bars = larger max excursion), not signal.
- **`rate_crossed_back` rises with horizon in essentially all groups** — also
  mechanical (more time = more chance to cross at least once).
- **Raw `mean_forward_return`** is sign-consistent across horizons in ~9/20 groups,
  but the dominant sign tracks sample market drift (BTC/ETH down-legs → continuation
  `cross` negative), not a candidate property. Confounded.

## 3. Stable within candidate (not just one horizon)?

- **`rate_close_on_approach_side` is definitional**: starts 1.0 for `rejection`/
  `failure` (closed back at event) and 0.0 for `continuation cross` (crossed at
  event), then decays toward the base rate as horizon grows. Consistent across
  every level — but it is encoded by the candidate label, so it is not evidence.
- No candidate shows an outcome pattern that is both (a) beyond label-definition /
  market-drift and (b) consistent across levels **and** horizons.

## 4. Directly dismiss as noise

- mfe/mae growth with horizon (mechanical).
- `crossed_back` growth with horizon (mechanical).
- continuation `cross` negative `fr` (sample down-drift, not candidate property).
- `reaction touch 0.5`: mfe == mae by construction (direction not inferred) → no
  information about direction.

## 5. Worth more data later (NOT evidence now)

Four single-relation groups where direction-aware `mae` stays modest while `mfe`
and (for rejection) elevated `appr` persist at long horizon:

- `rejection touch 0.618` (n=49) and `rejection touch 1` (n=20): `fr` stays positive
  and rising, `mae` low, `appr` still 0.65–0.76 at h50.
- `continuation touch 0.618` / `0.786`: large positive `fr` at h50 — but driven by
  the h50 column only (near-zero at h5–h20), so likely a few large trend moves.

Caveats: each is one relation × one level × one timeframe; raw `fr` is drift-biased;
the h50 spikes are not corroborated at shorter horizons. Treat as *collect more
events*, not as a pattern.

## Conclusion

**Working pipeline, no stable evidence yet.** With n≥20 the only consistent
structures are mechanical (horizon-length effects) or definitional (candidate label
encodes the at-event side). Nothing is stable across candidate × level × horizon,
and timeframe is still single (`1d`). A handful of single-relation groups are worth
revisiting once sample grows, but none constitutes evidence of an edge or signal.

## Source

- Run: `experiments/runs/fib_fingerprint_outcomes/2026-06-05/fp_outcomes_20260605T115819Z/`
  (`summary.json`, `sample_inventory.csv`, `MULTIRUN_NOTES.md`)
- Checkpoint: [2026-06-05 checkpoint](2026-06-05-fib-fingerprint-outcome-checkpoint.md)
