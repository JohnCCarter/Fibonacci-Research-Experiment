# Top-down nesting PREDICTION — 1w→1d pre-reg (RE-LOCKED 2026-06-26 — rank method, N=9)

**Status:** **RE-LOCKED 2026-06-26** (human sign-off, same day). The first lock (temporal split +
logreg + cluster bootstrap) was **retracted before any run**: a feasibility count (structure only,
no outcome) showed it returns **null by construction** — all 42 positive candidate rows fall in the
train region (bars < 2452), the test region (≈2022→) holds **zero** positives → `y_te.sum()==0` → no
fit. The method could not fire on the frozen 1w→1d data regardless of H1. Legitimate change: made
*before* seeing any result, transparent, re-locked with the user. **Question / data / feature /
baseline are unchanged; only the statistical Method + Decision rule changed** — now a within-window
**rank comparison** at the honest N. Build + run authorized under this re-lock.

Feasibility (frozen 1w parents, 1d candidates within each window):
- 21 parents → **9 windows** contain ≥1 reachable human 1d pick (the rest: too-short or epoch-gap).
- temporal 0.70 split (bar 2452 of 3503): **every** positive is pre-split → test positives = 0.
- → rank-based alternative N = **9 windows** (~35 human legs, hard-clustered: two windows hold 10+11).

## Question

Does **parent-TF (1w) context** predict the human's **1d** leg selection **beyond geometry
(prominence)** — on data drawn *blind* to the parent?

## Why this question, on this data (background)

- **Premise check** (frozen facit): human selections do **not** strictly nest 1M→1w (epoch
  mismatch: 1w mostly 2017–18, 1M 2020+, 5% overlap); 1w→1d overlap ~46%. → only **1w→1d** is testable.
- **Nesting cohort v2 (`ed98dc4`) is DISQUALIFIED** (leakage): its 1w/1d legs were drawn *with the
  parent's H/L markers + `c`-focus visible on the child chart* → parent "predicts" them by construction.
- **Frozen corpus = blind-ish, pre-tooling** (committed June, before today's anchor markers/redraw
  memory). Caveat: HTF *price lines* may have been visible in June → **weak** leakage (price, not
  time-position), a footnote — not disqualifying. Could not confirm overlay on/off from repo logs
  (tool stdout never committed).
- **Degeneracy gate — PASSED** (leakage-free, candidate geometry only; `scratchpad/divergence_check.py`):
  on reconstructible windows (`align_d < 0.10`), the parent-aligned 1d leg ≠ the most-prominent
  candidate in **9/10** windows, **6** with `prom_ratio < 0.7`. So alignment is **not collinear** with
  prominence — the test can separate H1 from H0.

## Data (locked)

- **Parents:** FROZEN blind **1w** fibs (21), from the `f0f4b8d` snapshot — **exclude** today's nesting
  cohort.
- **Targets:** FROZEN blind **1d** fibs (the human's actual 1d picks), same snapshot.
- **Testable subset (window-selection rule, pre-declared):** the **9** frozen 1w parents whose span
  contains **≥1 ε-matched human 1d pick** (feasibility count). A window with no reachable human pick
  has no target to locate → excluded; a window with <2 candidates has no rank contrast → excluded
  (none are). The other 12 parents (too-short span / epoch-gap → 0 reachable picks) drop out.
  *(The degeneracy gate's `align_d < 0.10` was a separate, geometry-only check that alignment ≠
  prominence — NOT the window-selection rule for this test.)*
- **1M→1w NOT tested** (epoch mismatch → no decision points).

## Candidate universe + target

- Per 1w-parent window: re-detect 1d candidate legs directly with `detect_pivots` (opposite-kind
  pivot legs inside the parent span) + `prominence` — the same primitives `build_candidates` uses,
  but driven by a window loop (NOT `run_timeframe`/`run_study`, which have no parent concept).
- **Human pick located** when a candidate ε-matches a human 1d leg in that window (`_matches_human`
  logic, ε reused from `EvaluationConfig`: `eps_time_bars`, `eps_price_atr`).
- **Tie-break (pre-declared):** if several candidates ε-match one human leg, the human pick = the
  **single** matching candidate with the smallest summed anchor distance
  (`|Δstart_bar|+|Δend_bar|` bars, price as ε-tiebreak) — one realised pick per human leg, then
  read that candidate's two percentile ranks.

## Feature / baseline / null (LOCKED pre-run — not chosen after seeing results)

- **New feature (the ONE new thing):** `parent_alignment` = how well a 1d candidate's (low, high)
  reconstruct the parent 1w swing — `align_dist = |cand_lo−par_lo|/par_lo + |cand_hi−par_hi|/par_hi`
  (the same `align_dist` used in the gate; **lower = better**). Uses the FROZEN 1w parent's H/L,
  which the human did **not** see when drawing 1d blind → non-circular.
- **Baseline:** §6 **prominence** = `max(start, end)` endpoint ATR-prominence (**higher = better**).
  Gate showed alignment is non-collinear with it.
- **H1:** within a window, `parent_alignment` ranks the human's actual 1d pick **higher** than
  `prominence` does.
- **H0 (null):** alignment ranks the human pick **no higher** than prominence (sign-balanced).

## Method (RE-LOCKED — within-window rank comparison, reuse only the primitives)

Reuse only `selection_learning.py` **primitives** (`detect_pivots`, `_matches_human`/ε, prominence)
— **not** `run_timeframe`/`run_study` (they have no parent-window concept and apply a temporal split
that is null here). New windowed driver:

1. **Windows:** the **9** frozen 1w parents whose span contains ≥1 ε-matched human 1d pick (from the
   feasibility count). Windows with <2 candidates are excluded (no rank contrast) — none are, but the
   rule is pre-declared. The other 12 parents (too-short / epoch-gap, 0 reachable picks) are excluded.
2. **Per window:** candidate universe = all 1d opposite-kind pivot legs inside the parent span. Score
   each candidate by (a) `align_dist` (asc → best) and (b) `prominence` (desc → best). Convert each to
   a **percentile rank** ∈ [0,1], 1 = best, defined as `(#candidates strictly worse)/(N_cand−1)`.
3. **Locate the human pick(s):** for each ε-matched human 1d leg in the window, read its alignment
   percentile and its prominence percentile. If a window holds several human legs (two do: 10, 11),
   **aggregate within window by median** → one `(align_pct_w, prom_pct_w)` per window. This is the
   per-window unit the user locked (robust to the two giant windows dominating).
4. **Per-window contrast:** `d_w = align_pct_w − prom_pct_w` (positive → alignment ranks the human
   pick higher than prominence does).
5. **Paired sign test** over the 9 `d_w`: count positive vs negative signs (zeros dropped), two-sided
   exact-binomial p. Report median `d_w` as the effect size. **Seeded? No randomness** — exact test,
   deterministic.

## Scale / honesty (BINDING)

- **N = 9 windows → DESCRIPTIVE / DIRECTIONAL ONLY.** Not powered. The decision rule **cannot** lean
  on the sign-test p as proof — with 9 windows even a clean 8/1 is a weak prior-shifter, not evidence
  of an edge.
- **No** reproduction / edge / behaviour / PnL / Genesis / auto-fib claim. Single feature, single cell.
- Weak price-line leakage caveat (above) stands in any write-up.
- Report the full per-window table (`d_w`, both percentiles, n_candidates, n_human_legs) — no hidden
  aggregation. Two windows carry most legs; that clustering is shown, not smoothed away.

## Decision rule (LOCKED)

- Report: #positive `d_w` / 9, median `d_w`, sign-test two-sided p — all as **directional** evidence.
- Verdict language: `alignment_ranks_human_pick_above_prominence (directional, N=9)` if a clear
  majority of windows have `d_w > 0`, else `no_parent_context_signal`. **Neither is a powered claim.**
- "Clear majority" pre-declared as **≥7/9** positive signs (drops to fit dropped-zero windows). Not a
  significance gate — a directional threshold fixed before the run.

## Gate

RE-LOCKED 2026-06-26 (human sign-off). Build + run authorized. Result is **directional, N=9** —
becomes "truth" only after human sign-off of the run output, not on production.
