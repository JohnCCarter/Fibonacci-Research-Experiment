# Fib → Genesis V2 — Phase 1 Feature-Export Spec (2026-06-15)

Docs-only **data-contract spec** for a *future*, causally-safe feature export between the Fib
repo and Genesis V2. This note **does not build the export.** It defines schema, invariants, and
how leakage is prevented — nothing more. No code, no feature export, no Genesis touch, no code
move, no ML, no pipeline, no tuning, no new charts, no 1H, no auto-fib, no trading/signal/edge
claim.

Gated by [Phase 0 pre-registration](btc-fib-to-genesis-v2-phase0-prereg-20260615.md), which
registered the one falsifiable question this export would later serve:

> **Does price react measurably differently at causally-valid, robust fixed-band MTF confluence
> zones than at matched naïve / placebo levels, out-of-sample?**

Corpus base: the locked BTC/USD source-fib corpus (1M=9, 1w=21, 1d=67, 4h=365; 462 fibs) —
[integrity capstone](btc-source-fib-corpus-integrity-20260615.md). MTF-confluence geometry
context: [interpretation & decision note](btc-mtf-confluence-interpretation-decision-20260615.md).

## 1. Purpose

The Fib repo should be **able** to produce a future **point-in-time feature table** — but only
if every feature can be constructed without leakage under the Phase 0 §3 causal rules. This spec
describes *what that table would look like* and *what an exporter would have to guarantee* so the
decision to build it can be judged on a concrete contract, not a vague intention.

Genesis V2 would **later** read these features as **external, read-only columns** joined on
`(symbol, timeframe, timestamp)`. **No Genesis touch happens now.** Genesis never sees source
fibs, anchors, or corpus internals — only finished causal feature columns. If a feature cannot
satisfy §5 invariants, it is simply absent from the table; an empty or near-empty table is itself
a Phase 0 stop signal, not something to be patched by relaxing causality.

## 2. Feature artifacts

Two tables. **A** is the zone catalogue (one row per causally-valid confluence zone); **B** is
the bar-level join target (one row per bar, referencing only zones already known at that bar).

### A. Zone registry table

A catalogue of causally-valid confluence zones. One row per zone.

| Column | Meaning |
|--------|---------|
| `zone_id` | Stable structural-signature id (not a positional cluster id — CP cluster ids drift). |
| `symbol` | `BTC/USD` (one symbol per Phase 1). |
| `method` | `fixed_band` (primary) or `single_linkage` (contrast only; never the live feature). |
| `epsilon_log` | Band parameter, frozen from train/validation — never tuned on test. |
| `zone_price_repr` | Representative price of the zone. |
| `zone_price_min` / `zone_price_max` | Band edges (equal for zero-span exact-price zones). |
| `price_span_log` | Log-price span; the central CP2 robustness metric. |
| `tf_count` | Number of distinct timeframes contributing a level (2–4). |
| `level_count` | Number of member levels. |
| `timeframes` | Sorted TF set, e.g. `1M,1w,1d,4h`. |
| `ratios` | Member fib ratios contributing levels. |
| `anchor_a_min` | Earliest member `anchor_a` timestamp. |
| `anchor_b_max` | Latest member `anchor_b` timestamp — the zone's last-confirmed swing point. |
| `known_after_ts` | First timestamp the zone may be used (see rule below). |
| `confirmation_buffer` | Predeclared lag applied after `anchor_b_max`. |
| `source_member_count` | Number of source fibs behind the zone (provenance count, not a feature). |
| `feature_version` | Schema/version tag for reproducibility. |

**Zone-knowability rule (binding):**

```
known_after_ts = max(member.anchor_b_time) + confirmation_buffer
```

A zone may be referenced **only at or after** `known_after_ts`, or stricter if a member needs
extra confirmation. This is what makes a CP1–CP3 (full-corpus, hindsight) zone safe to reuse:
the *geometry* is reused, but each zone is stamped with the first time it could have been known
live, and may never appear before it.

### B. Bar feature table

One row per `(symbol, timeframe, timestamp)` bar that Genesis can later left-join against.

| Column | Meaning |
|--------|---------|
| `symbol` | `BTC/USD`. |
| `timeframe` | Bar timeframe (no 1H). |
| `timestamp` | Bar timestamp — the join key and the causality anchor. |
| `feature_version` | Matches the registry version used. |
| `nearest_confluence_price` | Price of the nearest **already-known** zone. |
| `nearest_confluence_distance_log` | Log-price distance to it. |
| `nearest_confluence_distance_atr` | Same distance in ATR units (rolling ATR only). |
| `in_confluence_band` | Bool: bar price inside a known zone band. |
| `nearest_zone_tf_count` | `tf_count` of the nearest known zone. |
| `nearest_zone_level_count` | `level_count` of the nearest known zone. |
| `nearest_zone_price_span_log` | `price_span_log` of the nearest known zone. |
| `nearest_zone_age_bars` | Bars since `known_after_ts` of the nearest known zone. |
| `nearest_zone_method` | Method of the nearest known zone. |
| `num_zones_within_x_atr` | Count of known zones within X rolling-ATR of the bar. |
| `num_fixed_band_zones_active` | Count of known fixed-band zones active at the bar. |
| `has_robust_4tf_zone_nearby` | Bool: a known robust 4-TF zone within a predeclared distance. |

**Per-row rule (binding):** every value in a row may reference a zone **only if**

```
zone.known_after_ts <= timestamp
```

Any zone with `known_after_ts > timestamp` is invisible to that row. A row that violates this is
feature leakage by definition.

## 3. Baseline artifact specs

Each baseline is its own future table with the **same distance/feature columns** as table B, so
confluence features and baselines are compared on identical metrics. All are causal.

**A. Causal swing high/low baseline** — only swings whose confirming pivot is established
**before** `timestamp` (rolling, confirmation-lagged); same distance metrics as confluence. The
honest analogue of "what a fib would capture."

**B. Shuffled / placebo confluence baseline** — same **count** and same **time distribution** of
levels as the real zones, but price-locations shuffled / randomly placed. Must use **no future
information** (the shuffle draws only from a causal price range known at `t`). The hardest
control; confluence features must beat it OOS or the track stops.

**C. ATR / prior-period baseline** — rolling ATR band or prior-period high/low. **Rolling only;
no full-sample normalisation.**

## 4. Genesis V2 ingestion contract

A deliberately thin contract — describes *consumption*, authorises *nothing*.

- **Format:** start with the simplest — **CSV** (human-diffable, no deps). Parquet only later if
  size/dtype fidelity demands it. Recommend CSV first.
- **Join keys:** `symbol`, `timeframe`, `timestamp` (left join, bar → feature row).
- **Read-only input:** the feature table is an external input to Genesis; Genesis never writes it.
- **No fib internals cross the boundary:** Genesis does **not** know source fibs, anchors, fib
  ids, or the corpus. It sees only finished causal feature columns.
- **No code moves in Phase 1** — and none would move when this is built either; the export would
  be a separate read-only producer, not a Genesis-internal module.

## 5. Causal invariants

A future exporter MUST verify all of these (each is mechanically checkable):

1. `known_after_ts <= timestamp` for every zone referenced by every bar row.
2. **No 1H** — off-protocol timeframe rejected, fail-closed.
3. **No future anchor** — no `anchor_b` used before its `confirmation_buffer` has passed.
4. **No CP1–CP3 static full-corpus zone as a live feature** — zones may be reused as geometry
   only with a `known_after_ts` stamp; never as undated facit.
5. **No full-sample statistics** — all normalisation rolling/expanding up to `t` only.
6. **No holdout parameter tuning** — `epsilon_log`, band-width, buffers frozen from train/val.
7. **No random split** — time-ordered windows only.
8. **No source-fib id leakage into model features** — `zone_id` / provenance counts are
   metadata-only, never model inputs, unless explicitly declared metadata-only.
9. **Deterministic feature generation** — same corpus + same version ⇒ byte-identical output.

## 6. What not to export

These must **never** appear as live features:

- Raw human-fib *existence* drawn from the full corpus (selection leakage).
- Future-known confluence zones (any zone before its `known_after_ts`).
- CP3 **card labels** as features (c001/c002/c004/… are hindsight presentation artifacts).
- Hindsight **cluster ids** (positional, drift across corpus versions).
- `anchor_b` before its confirmation buffer.
- Source paths / `fib_id`s as **model input** (metadata-only at most).

## 7. Minimal Phase 2 preview (design only, not authorised)

If Phase 1 clears stop/go, the *next* docs-only step would be:

- A **Genesis V2 ingestion-contract review** (confirm column semantics against a real consumer).
- A **dummy feature-file test** — a tiny synthetic CSV in this schema to prove the join/contract,
  with **no real Fib features yet** and **no backtest yet**.

Still docs/spec only. No real export, no Genesis change, no behaviour test.

## 8. Stop / go

**Continue to Phase 2 only if all hold:**

- The schema is clear and every column is operationally defined.
- The causal invariants (§5) are mechanically verifiable.
- The baseline tables (§3) can be described without leakage.
- The feature table does not require heavy Genesis integration.

**Stop / pause if any hold:**

- Features become near-empty after applying causality + confirmation buffer.
- The schema can only be filled by smuggling in hindsight.
- Genesis would have to know fib internals (anchors, ids, corpus) to use the features.
- The baselines cannot be made clean (non-leaking).

## 9. Recommendation

**The Phase 1 spec is sufficient as a written contract.** It pins down two concrete tables, a
binding zone-knowability rule (`known_after_ts = max(anchor_b) + buffer`), a per-row causality
invariant, three clean baselines, a thin read-only Genesis contract, and an explicit do-not-export
list. Nothing here requires hindsight or Genesis internals on paper.

**Recommended next step: a small docs-only Phase 2** — the dummy-feature-file test (§7) — to prove
the schema and join contract mechanically **before** any real feature is computed. That is the
cheapest way to surface a near-empty-features or leakage problem early.

**But do not start Phase 2 without an explicit go.** The one real risk the spec cannot resolve on
paper is whether causal features are **non-empty** in practice (Phase 0 §8 stop condition): how
many zones actually have `known_after_ts` early enough to produce useful bar-feature history. If
the human prefers, **pause here** — this spec is durable and loses nothing by waiting.

## Non-goals honoured

No code, no export, no Genesis touch, no ML, no pipeline, no tuning, no new charts, no 1H, no
auto-fib, no trading/signal/edge claim. Docs-only spec; this note authorises **nothing** beyond
itself, and Phase 2 needs an explicit go.
