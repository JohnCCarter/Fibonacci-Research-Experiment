# Fib → Genesis V2 — Phase 2 Dummy Contract Test (2026-06-16)

**Extremely narrow slice.** This is **not** Fib-in-Genesis, **not** Genesis integration,
**not** a real feature export. It is a **mechanical contract/dummy test inside the Fib
repo only**, gated on the [Phase 1 spec](btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md)
(closed PASS) and the [Phase 0 prereg](btc-fib-to-genesis-v2-phase0-prereg-20260615.md).

## Question answered

> Can a future external Fib feature contract be validated **mechanically**, without leakage
> and without any Genesis coupling?

**Yes.** The Phase 1 two-table schema, its join keys, and its causal invariants are all
mechanically checkable against synthetic dummy data, with fail-closed behaviour on every
violation — and with zero Fib computation and zero Genesis touch.

## What was built

- `src/fibengine/research/feature_contract.py` — stdlib-only validator (no new deps). Reads
  two dummy CSVs, validates schema + join keys + causality, fail-closed `ValueError`.
- Committed dummy pair under `docs/research_wiki/reviews/contracts/phase2_dummy/`:
  - `zone_registry.csv` (table A) — 3 synthetic zones (fixed-band 4-TF; zero-span 3-TF;
    single-linkage 2-TF) with the `known_after_ts` knowability stamp.
  - `bar_features.csv` (table B) — 4 synthetic bars (1d/1w/4h), incl. one **multi-zone**
    row, each referencing only zones already known at its timestamp.
- `tests/research/test_feature_contract.py` — 20 tests.

The dummy numbers are **arbitrary placeholders** — no fib, swing, or price computation
produced them. The validator never recomputes or asserts feature *values* (that would be
feature export, out of scope); it checks only structure and causality.

## Mechanical checks (Phase 1 §5)

| Check | Rule | Result |
|-------|------|--------|
| Column schema | exact header, both tables | drift → fail-closed |
| Join keys | `(symbol, timeframe, timestamp)` non-null + **unique** | dup triple → fail (left-join fan-out) |
| Causality §5.1 | every referenced zone: `known_after_ts <= timestamp` | leakage → fail; checked over the **whole** reference set, not just nearest |
| Knowability §2A | `known_after_ts >= max(anchor_b) + buffer` (floor; "or stricter" allowed) | early stamp → fail |
| No 1H §5.2 | `timeframe ∈ {1M,1w,1d,4h}` (zone members + bar tf) | `1h` → fail-closed |
| Feature/metadata boundary §8 | `meta_referenced_zone_ids` is metadata-only, never a feature/join key | asserted at import + test |

The metadata-only reference column is what makes §5.1 *observable*: without naming the zones
a row touches, the per-row causality invariant cannot be checked. It is explicitly **not** a
model feature (Phase 1 §6/§8).

## Unit note (Phase 2 finding fed back to the spec)

The buffer in the zone-knowability rule is **integer hours**. Phase 1 §2A named the column
unit-less (`confirmation_buffer`), which is an interpretation risk. This dummy resolves it at
the source: the schema column is `confirmation_buffer_hours`, parsed as `int` and applied as
`timedelta(hours=...)`. **Recommended spec amendment:** rename the Phase 1 §2A column to
`confirmation_buffer_hours` (or hard-state the unit) so a future real exporter cannot
misread it.

## Boundary held

- No real Fib feature export; no computation from human fibs.
- No Genesis V2 code, no import from Genesis, no Fib dependency on Genesis.
- No pipeline, no ML, no backtest, no signal, no edge claim, no 1H, no auto-fib.
- **Fib = producer / contract authority; Genesis = future read-only consumer.** Test patterns
  are inspired by contract/validator style only — no runtime code copied, no Genesis module
  imported.

## Gates

`ruff` clean · 426 passed (76% cov) · `check_repo_bounds.py` PASS · CLI smoke:
`contract OK: 3 zone(s), 4 bar(s); timeframes=['1d', '1w', '4h']`.

## Stop

**Stop after this** (as scoped). Nothing here authorises a real feature export, a Genesis
touch, or any behaviour study. Anything requiring real export or a Genesis dependency =
pause and report.

Run::

    python -m fibengine.research.feature_contract \
      --zones docs/research_wiki/reviews/contracts/phase2_dummy/zone_registry.csv \
      --bars  docs/research_wiki/reviews/contracts/phase2_dummy/bar_features.csv
