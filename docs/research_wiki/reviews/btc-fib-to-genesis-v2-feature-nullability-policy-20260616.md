# Fib → Genesis V2 — Feature Nullability Policy (Phase 2.5, 2026-06-16)

**Docs-only.** This note defines how the *future* bar feature table (Phase 1 §2B) represents
"no causally-known zone / not applicable / empty value". It **builds nothing**: no code, no
real feature export, no Genesis touch, no ML/backtest/signal, no Fib-feature computation, no
Phase 3. It is the missing rule flagged by the Phase 2 review (commit `68dc006`) as a
precondition for any future real export.

Grounded in the locked Phase 2 schema (`src/fibengine/research/feature_contract.py`) and the
[Phase 1 spec](btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md). It changes
neither — it pins the semantics the spec left open.

## 1. The core distinction — two different "empty" states

Most ambiguity here comes from collapsing genuinely different situations. The user named
three — "ingen kausalt känd zon / ej applicerbart / tomt värde". They must be
**distinguishable** in the table:

| State | When | Meaning |
|-------|------|---------|
| **No zone known** | bar is before *any* zone's `known_after_ts` (or no zone exists yet) | there is **no nearest zone at all** — the "nearest zone" columns have no referent |
| **No zone nearby** | ≥1 zone is known, but none is close (none within the proximity / band thresholds) | a nearest zone **exists** (possibly far); the *bounded* counts/bools are simply 0/false |
| **Not applicable / not computable** | a required rolling input is undefined at the bar — specifically **rolling-ATR warmup** | the *ATR-denominated* columns cannot be computed yet, **independent** of whether a zone is known (§3.1) |

`nearest_*` describes **the nearest *known* zone regardless of distance**. So a bar can have a
fully-populated `nearest_*` (a far zone) while `num_zones_within_x_atr = 0` and
`in_confluence_band = false`. "No zone nearby" is **not** a null state — it is the 0/false
state with `nearest_*` still populated. Only "no zone known" produces null `nearest_*`.

This answers *"hur representeras 'ingen zon nära'?"*: counts = 0, booleans = false, but the
`nearest_*` columns stay populated with the (far) nearest known zone. The all-null state is
reserved for *"ingen zon känd"*.

## 2. Per-column nullability

### 2.1 Always non-null (a null here = invalid row, fail-closed)

| Column | No-zone value | Why never null |
|--------|---------------|----------------|
| `symbol` | n/a | join key |
| `timeframe` | n/a | join key + causality anchor |
| `timestamp` | n/a | join key + causality anchor |
| `feature_version` | n/a | reproducibility tag |
| `in_confluence_band` | `false` | proposition "bar price is inside a known band" is **false**, not unknown |
| `has_robust_4tf_zone_nearby` | `false` | same — a definite false, not missing |
| `num_fixed_band_zones_active` | `0` | zero is a **true, informative count** (ATR-free) |
| `meta_referenced_zone_ids` | `""` (empty) | column always present; empty = references zero zones (see §4) |

### 2.2 Nullable — null **only** in the "no zone known" state

These describe the single nearest known zone; with no known zone there is no object to
describe, so they are **null/empty**:

| Column | No-known-zone value |
|--------|---------------------|
| `nearest_confluence_price` | null |
| `nearest_confluence_distance_log` | null |
| `nearest_confluence_distance_atr` | null |
| `nearest_zone_tf_count` | null |
| `nearest_zone_level_count` | null |
| `nearest_zone_price_span_log` | null |
| `nearest_zone_age_bars` | null |
| `nearest_zone_method` | null (empty string) |

When ≥1 zone is known, these **seven non-ATR columns are non-null** (they describe the nearest
one, even if far). Either all seven are null together, or all seven are populated together —
never a partial mix. `nearest_confluence_distance_atr` (the eighth `nearest_*`) carries the
**additional** warmup exception in §3.1.

The two count columns split by ATR-dependence: `num_fixed_band_zones_active` (count of known
zones, ATR-free) is **always non-null** (`0` when none); `num_zones_within_x_atr` is
ATR-denominated and follows §3.1.

## 3. Distances: null, not 0 and not `inf`

For the "no zone known" state, distance columns are **null** — explicitly **not**:

- **not `0`** — `0` means "exactly at a zone", the *opposite* of "no zone";
- **not `inf`** — `inf` asserts "infinitely far from an existing zone", but the truth is
  "no zone exists yet". `inf`/`NaN` also poison downstream rolling stats, normalisation, and
  many ML libraries silently.

`null` keeps "no zone exists" categorically separate from "a zone exists but is far" (which is
a real finite distance). **The producer never imputes.** A consumer may later map null to a
documented sentinel, but that is a consumer decision that must be logged (§5), not baked into
the export.

### 3.1 ATR warmup — the "not applicable" state

ATR-denominated columns require a defined **rolling** ATR (Phase 1 §3C: rolling only, no
full-sample normalisation). During the ATR warmup window the ATR is undefined, so these
columns are **null** — even if a zone is known. This is "ej applicerbart", distinct from "no
zone known":

- `nearest_confluence_distance_atr` — null during warmup (while the log-distance
  `nearest_confluence_distance_log` may still be populated for the same bar).
- `num_zones_within_x_atr` — null during warmup (the count cannot be formed without ATR);
  this is the **one count column exempt** from "counts are always non-null".
- any other column whose threshold is ATR-denominated (e.g. if `has_robust_4tf_zone_nearby`
  uses an ATR distance) follows the same rule; a log-price threshold does not.

`null` here means "not yet computable", **not** "no zone" and **not** "zero". The producer must
not back-fill warmup bars from later ATR.

**Empirical expectation (state the assumption, don't rely on it):** rolling ATR on the active
timeframes warms up within a few bars of the data start, whereas the earliest zone
`known_after_ts` (= earliest `max(anchor_b)+buffer`) is much later — so in this corpus the
warmup window is expected to contain **no known zone**, making warmup+known-zone co-occurrence
rare or empty in practice. The policy nonetheless defines it so a future exporter is correct
even if it occurs.

## 4. `meta_referenced_zone_ids` consistency

`meta_referenced_zone_ids` (metadata-only; never a model feature — Phase 1 §6/§8) is **always
present** and lists every zone the row's values touch, `;`-separated.

- **No zone known** → `""` (empty).
- Otherwise → the nearest zone id **plus** every zone counted in `num_zones_within_x_atr` /
  `num_fixed_band_zones_active` / `has_robust_4tf_zone_nearby`.

**Cross-consistency invariant (mechanically checkable, like Phase 2):**

```
meta_referenced_zone_ids == ""   ⇔   all seven non-ATR nearest_* are null
                                  AND nearest_confluence_distance_atr is null
                                  AND num_fixed_band_zones_active == 0
                                  AND num_zones_within_x_atr ∈ {0, null}   # null during warmup
                                  AND in_confluence_band == false
                                  AND has_robust_4tf_zone_nearby == false
```

i.e. the empty-meta row and the no-known-zone row are the *same* row. (The one ATR-denominated
count is `0` normally and `null` during warmup; both are consistent with no known zone.) Any
zone contributing to a non-default feature value MUST appear in meta (so §5.1 causality stays
observable).

## 5. CSV encoding + Genesis read-only consumer rules

CSV has no native null. Encoding convention (matches the Phase 2 validator's parsing —
`""` → `None` for numerics):

- **null = empty field** (`,,`), for the eight nullable columns only.
- booleans = literal `true` / `false` (never empty).
- counts = literal integer, `0` when none (never empty).
- `meta_referenced_zone_ids` = `""` when none (a present-but-empty field).
- (Parquet later would use real null; the empty-field rule is CSV-specific.)

A future **read-only** Genesis consumer MUST:

1. **Use a dense bar table** — one row per in-range bar. Then a *present row with*
   `num_zones_* = 0` and null `nearest_*` means "no known zone (causal, informative)", while a
   **missing** join row means "bar outside the exported range" — two different facts. A sparse
   table would collapse both into left-join nulls and is therefore disallowed.
2. **Read null `nearest_*` as "no nearest known zone"** — not as distance 0, not as a numeric.
3. **Not forward-fill / impute across the `known_after_ts` boundary.** Any imputation must use
   only information known at `t` and must be recorded as a consumer-side transform, never read
   back as if it were producer output.
4. Treat `false`/`0` as the **true** no-zone-nearby answers, not as missing data.
5. Never read `meta_referenced_zone_ids` as a model feature (provenance only).

## 6. Optional future schema note (not adopted here)

A dedicated `has_known_zone` boolean could make the "no zone known" state explicit in one
column. It is **redundant** with the §4 invariant (present row + empty meta + null `nearest_*`
already encodes it) and is **not** added — adding a column is a Phase 1 schema change, out of
this docs-only scope. Recorded only as a future option for the spec owner.

## 7. Stop

This note pins nullability semantics and stops. It authorises **no** code, **no** real export,
**no** Genesis change, **no** behaviour study. Building any of these — or computing real Fib
features to populate such a table — requires a fresh explicit go (and would be Phase 3+, not
this note). If a future step needs code or real export: **pause and report.**
