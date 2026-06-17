# BTC/USD MTF Confluence — Sensitivity / Robustness (Checkpoint 2, 2026-06-15)

Read-only robustness pass over the [CP1 confluence table](btc-mtf-confluence-table-20260615.md).
Answers one question: **is the MTF-confluence result robust, or mostly an effect of the
chosen epsilon and single-linkage chaining?**

**Scope honored:** read-only, no chart, no visual atlas, no trading/signal/edge
interpretation, no 1H, no reaction-review, no auto-fib, no source-label change, no new deps,
no committed PNG/artifacts. Epsilon values are **predeclared** (`0.0025, 0.005, 0.01`), not
tuned. New code is stdlib-only + tested. Helper:
[`research/mtf_confluence.py`](../../../src/fibengine/research/mtf_confluence.py) (+ 9 new
tests). Committed summary: [btc-mtf-confluence-sensitivity-20260615.csv](btc-mtf-confluence-sensitivity-20260615.csv).

---

## Observed

- **Epsilon sensitivity (single-linkage, CP1 method):** cluster count scales with epsilon —
  **173 → 222 → 266** at epsilon_log `0.0025 / 0.005 / 0.01`. 4-TF clusters: **1 → 2 → 6**;
  3-TF: 13 → 24 → 40; 2-TF: 159 → 196 → 220.
- **Chaining grows fast with epsilon.** Clusters whose `price_span_log > epsilon` (only
  possible under single-linkage): **12 / 30 / 70** (= 7% / 14% / 26% of all clusters). The
  widest single-linkage cluster reaches `price_span_log` **0.0046 / 0.0164 / 0.0822** — i.e.
  at epsilon 0.01 one "cluster" spans ~8.6% in price, far beyond the 1% threshold.
- **Fixed-band removes all over-epsilon clusters by construction** (`clusters_over_epsilon`
  = 0 at every epsilon) and yields fewer clusters: **144 / 188 / 242**. 4-TF under fixed-band:
  **1 / 1 / 0**.
- **c001 (~29274, ratios 0/1, 2021 cycle):** survives as a **4-TF** cluster intact under
  *both* methods at epsilon `0.0025` and `0.005` (span 0.00123, well inside epsilon). At
  epsilon `0.01` single-linkage keeps it 4-TF, but fixed-band's greedy band cut places the
  1M level in the neighbouring band → it reads as **3-TF** (1w,1d,4h, ~29283). A binning
  boundary effect, not a structural loss — the 1M level is still at ~29274.
- **c002 (~21167, ratios 0.382/0.618, 2022–23 bottom):** does **not** survive as a tight
  cluster. Its CP1 4-TF status exists only under single-linkage at epsilon ≥ 0.005, and there
  its `price_span_log` is **0.00627 > 0.005** — it is itself a chained cluster. Details:
  - epsilon 0.0025, single-linkage: **no** 4-TF cluster near 21167 (closest is a 3-TF
    `1M,1w,4h` at ~20881). The 4-TF agreement does not exist at the tight epsilon.
  - epsilon 0.005, fixed-band: dissolves into several **2-TF** fragments (`1d,4h`; `1M,4h`;
    `1w,4h`; `1w,1d`) near 20386–21884 — no 4-TF or 3-TF survivor.
  - epsilon 0.01, single-linkage: balloons to a **7-level** 4-TF cluster spanning `0.023`
    (~2.3%) — heavy chaining. Fixed-band splits it into `1M,1d,4h` and `1w,1d,4h` (both 3-TF).

## Inferred

- **The result is partly robust, partly chaining-dependent — and the two strongest CP1
  clusters fall on opposite sides of that line.** c001 is a genuine, tight, epsilon- and
  method-stable 4-TF confluence. c002 is *not* a tight 4-TF coincidence; it is a region of
  several looser 2-TF pairings near the 2022–23 bottom that single-linkage chained into one
  4-TF cluster at the primary epsilon.
- **Chaining inflates the headline counts at the loose end.** The jump to 6 four-TF clusters
  at epsilon 0.01 is largely chaining (fixed-band gives 0 four-TF there). The dense-TF
  dominance (`1d,4h`) persists across all cells, as expected from row counts.
- **Local structure near c002 is real but weaker than CP1 implied:** fixed-band keeps the
  pieces multi-timeframe (≥2-TF), so they do not dissolve to 1-TF noise — there *is* MTF
  agreement in that price region, just not a single 4-TF point.

## Unverified

- **Greedy band cut points are price-position-dependent** (a known fixed-width-binning
  property). The c001→3-TF drop at epsilon 0.01 is an instance; a different deterministic
  banding could keep it 4-TF. Fixed-band is a robustness *probe*, not a canonical clustering.
  The parameter-free intact/chained metric (below) does not depend on cut placement.
- Whether c002's region "should" count as one confluence or several is a definitional
  choice, not a fact the data settles.
- No claim about price behavior, support/resistance strength, or predictive value — these
  remain geometric counts.

---

## Epsilon policy

Predeclared before running: **`epsilon_log ∈ {0.0025, 0.005, 0.01}`** (≈0.25% / 0.5% / 1.0%
in price). `0.005` is the CP1 primary. Not tuned to produce a desired count.

## Method definitions

- **Single-linkage (CP1):** rows are connected iff `|Δlog_price| ≤ epsilon` **and** anchor
  windows overlap; a cluster is a connected component spanning ≥2 distinct timeframes. A
  cluster's total `price_span_log` **can exceed epsilon** when rows chain via intermediates.
- **Fixed-band (CP2, new):** *complete-linkage in price, single-linkage in time.* Greedy
  banding over log-sorted rows — a band starts at the lowest unassigned row and extends while
  `log_price − band_min ≤ epsilon`, so **every cluster has `price_span_log ≤ epsilon`** (all
  member pairs within epsilon). Within a band, rows split into time-overlap connected
  components; keep components spanning ≥2 timeframes. Every fixed-band cluster is a **subset
  of one single-linkage cluster** at the same epsilon (partition refinement); the ≥2-TF
  survivor count can therefore *fall* (a 2-TF cluster may split into two dropped 1-TF bands).

## Count table (per epsilon × method)

| epsilon_log | method | total | 4-TF | 3-TF | 2-TF | over-ε | max span_log |
|---|---|--:|--:|--:|--:|--:|--:|
| 0.0025 | single-linkage | 173 | 1 | 13 | 159 | 12 | 0.00456 |
| 0.0025 | fixed-band | 144 | 1 | 11 | 132 | 0 | 0.00248 |
| 0.005 | single-linkage | **222** | **2** | 24 | 196 | 30 | 0.01643 |
| 0.005 | fixed-band | 188 | 1 | 15 | 172 | 0 | 0.00471 |
| 0.01 | single-linkage | 266 | 6 | 40 | 220 | 70 | 0.08225 |
| 0.01 | fixed-band | 242 | 0 | 28 | 214 | 0 | 0.00992 |

### Parameter-free chaining probe (single-linkage, no band-cut dependence)

Of all single-linkage clusters, share with `span ≤ epsilon` (intact) vs `> epsilon` (chained):

| epsilon_log | total | intact | chained | chained % |
|---|--:|--:|--:|--:|
| 0.0025 | 173 | 161 | 12 | 7% |
| 0.005 | 222 | 192 | 30 | 14% |
| 0.01 | 266 | 196 | 70 | 26% |

**Most clusters are intact at the primary epsilon (192/222);** chaining is a minority effect
at 0.005 but becomes material (26%) at 0.01.

### TF-combo breakdown (top combos per cell)

- **0.0025 SL (173):** 1d,4h=114 · 1w,4h=21 · 1M,4h=11 · 1w,1d,4h=9 · 1w,1d=6 · 1M,1w=4 · … · 1M,1w,1d,4h=1
- **0.0025 FB (144):** 1d,4h=97 · 1w,4h=16 · 1M,4h=10 · 1w,1d,4h=9 · 1M,1w=4 · … · 1M,1w,1d,4h=1
- **0.005 SL (222):** 1d,4h=143 · 1w,4h=30 · 1w,1d,4h=16 · 1M,4h=13 · … · 1M,1w,1d,4h=2 · 1M,1w,1d=1
- **0.005 FB (188):** 1d,4h=122 · 1w,4h=25 · 1M,4h=12 · 1w,1d,4h=11 · 1w,1d=6 · … · 1M,1w,1d,4h=1
- **0.01 SL (266):** 1d,4h=164 · 1w,1d,4h=28 · 1w,4h=27 · 1M,4h=14 · … · 1M,1w,1d,4h=6
- **0.01 FB (242):** 1d,4h=152 · 1w,4h=33 · 1w,1d,4h=21 · 1M,4h=15 · … · 1M,1w,1d=1 (no 4-TF)

`1d,4h` dominates every cell (dense-TF bias by construction, unchanged by method).

## Survival of top CP1 clusters

| CP1 cluster | 0.0025 SL | 0.0025 FB | 0.005 SL | 0.005 FB | 0.01 SL | 0.01 FB | verdict |
|---|---|---|---|---|---|---|---|
| **c001** ~29274 | 4-TF | 4-TF | 4-TF | 4-TF | 4-TF | 3-TF\* | **robust** |
| **c002** ~21167 | (3-TF, ~20881) | 2-TF frags | 4-TF (span>ε) | 2-TF frags | 4-TF (7-lvl, span 0.023) | 3-TF×2 | **chaining-dependent** |

\* c001's 4th TF (1M) lands in the adjacent greedy band at the loose epsilon — a cut-position
effect, not a structural loss. c003–c010 are predominantly `1w,1d,4h` / `1M,*` 3-TF and many
have `span = 0` (exact-price coincidences, e.g. c004/c006/c007 at $64829/$13764/$9085); those
zero-span clusters are immune to both epsilon and chaining and survive trivially.

## Chaining impact

- At the primary epsilon, **30/222 (14%)** single-linkage clusters are chaining-affected
  (span > ε); fixed-band removes all of them (0 over-ε) and reduces the total 222 → 188 (−34,
  −15%). The 4-TF count drops 2 → 1: **c002 is the cluster lost**, c001 is kept.
- The picture **remains meaningful**: 188 fixed-band clusters at primary epsilon, still
  including a true 4-TF (c001), 15 three-TF, and 172 two-TF. MTF confluence is not an artifact
  of chaining — but the *strength* of the second-ranked cluster (c002) was overstated by CP1's
  single-linkage definition.

---

## Stop/Go → Checkpoint 3 (visual atlas)

**CONDITIONAL GO — with a corrected headline.** The core finding holds: real, epsilon- and
method-stable MTF confluence exists (c001 the clearest case; 188 fixed-band clusters at primary
epsilon). But CP2 corrects CP1: **c002 is chaining-dependent, not a tight 4-TF confluence**,
and 4-TF counts at loose epsilon are inflated by chaining. A visual atlas (CP3) is justified
*if* it (a) renders the **fixed-band** clusters (or shows both definitions side by side), and
(b) annotates `price_span_log` so wide/chained clusters are visible. Do not promote any
cluster as support/resistance or signal. Still no chart in CP2; CP3 remains the first step that
draws anything, and stays conditional on this corrected basis.

## Verification

- Counts re-derived on disk via `run_sensitivity` over the 2772-row / 462-fib corpus;
  predeclared epsilons only.
- Fixed-band invariant checked: `clusters_over_epsilon = 0` at all epsilons (test +
  CLI output).
- c001/c002 survival traced directly from cluster outputs at each epsilon × method.
- 9 new unit tests (known-chain split, fixed-band max-span ≤ ε, fixed-band cross-TF &
  time-overlap requirements, refinement, deterministic ordering, span-partition,
  sensitivity determinism, sensitivity CSV header). Full suite: 394 passed, 75% coverage.
- No source labels changed; committed output is the 6-row summary CSV under `docs/`; full
  per-epsilon cluster CSVs are gitignored under `experiments/review/mtf_confluence/`.

## Links

- [CP1 confluence table](btc-mtf-confluence-table-20260615.md) · [corpus integrity](btc-source-fib-corpus-integrity-20260615.md) · [next-research-plan](btc-source-fib-next-research-plan-20260615.md)
- [committed sensitivity summary CSV](btc-mtf-confluence-sensitivity-20260615.csv)
