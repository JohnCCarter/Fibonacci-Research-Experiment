# BTC Horizontal-Structure Event Study — Pre-registration (2026-06-17)

**Lean Fib Research, one falsifiable question. DOCS-ONLY — authorises no code, no run, no
dependency, no label/corpus change.** This pre-registers the rules **before** results, then they
are frozen. It is the post-fib-null follow-up (track **B-1**): the closed BTC/Fib behaviour line
found any weak level reaction is **generic horizontal structure, not Fibonacci-specific**
([behaviour results](btc-fib-behaviour-event-study-results-20260616.md),
[context-conditioned](btc-fib-context-conditioned-study-results-20260616.md)). This prereg asks
the question that survived. It is bound by the standing
[horizontal-structure addendum](horizontal-structure-prereg-addendum-20260617.md) (NU-1..NU-3) and
**explicitly states how each is met** (§7, §8, §12).

It does **not** mutate the frozen preregs of the closed fib line — those stay as historical record.

## 1. Question

> Does BTC/USD price **repel measurably more** at causally-valid **generic horizontal levels**
> (swing extremes, round numbers, prior-period extremes) than at a matched **synthetic
> random-walk null**?

Null: no measurable difference vs the random-walk null. Support/resistance levels emerge
spontaneously in pure random walks (Lo, Mamaysky & Wang 2000) — so a level repelling price is
**only** evidence of a mechanism if it beats a matched random-walk series. If generic levels are
statistically indistinguishable from the RW null on the primary metric out-of-sample → answer is
**no** → stop; **no strategy sanity-check.** Behaviour question only (does the level repel), not a
buy/sell/profit claim.

**Why this is a materially different question (not a tweaked re-run of the closed fib study):**
the closed study only ever tested **fib-as-subject** (`fib_beats_placebo`, `fib_beats_swing`).
The subject here is **generic structure**, and the **primary comparison is the random-walk null,
which was never computed** — `synthetic_baseline` has never been wired into any study. That unseen
quantity is the load-bearing element; without it this would be a forbidden re-look.

## 2. Data (locked, offline)

- BTC/USD only; timeframes **1M, 1w, 1d, 4h**. **1H rejected fail-closed.**
- Candles read-only from existing cache via `config/settings.expansion.yaml`; no fetch, no network.
- **No fib JSON is read.** All three subjects derive from candles alone — swing pivots
  (`detect_swing_levels`), the 1-2-5 round ladder, and prior-period candle extremes. The locked
  fib corpus plays **no role** in B-1 (it is the *prior* line's facit, not an input here).
- No JSON written or mutated; locked corpus unchanged.

## 3. Causality (binding, fail-closed)

- A level contributes at bar `t` **only if** `known_after_ts <= t`. Per subject:
  - **SWING** — knowable `pivot_k` bars after the pivot bar (`pivot_k = 3`, frozen).
  - **ROUND** — a round/psychological price is "known" at all `t` (no hindsight), but only counts
    as **active** while it lies inside the causal trailing range `[min low, max high]` over bars
    strictly before `t` (a round number price has never reached is not a live reference).
  - **PRIOR-EXTREME** — prior calendar-period high/low, knowable at that period's close
    (`known_after_ts = period_close`).
  - **RW-NULL** — generated from history strictly **before** the matched real level's
    `known_after_ts`; inherits that same `known_after_ts` (§4).
- Forbidden (fail-closed if detected): future information of any kind, full-sample statistics as a
  feature, any level known only in hindsight, naïve (tz-missing) timestamps. (No fib JSON is read
  at all per §2, so fib hindsight cannot leak in.)

## 4. Subjects and control

**Subjects (generic horizontal structure — all causal, tested individually; NO cherry-picking
to swing-only):**

1. **SWING** — fractal swing highs/lows (`detect_swing_levels`, existing), `pivot_k = 3`.
2. **ROUND** — the canonical **1-2-5 decade ladder**, frozen now and applied identically to all
   TFs: every price `p = m × 10^k` with `m ∈ {1, 2, 5}` and integer `k` (…, 1000, 2000, 5000,
   10000, 20000, 50000, 100000, …). No per-TF variation, no tuning. The §3 active-range rule
   selects which ladder rungs are live at each bar; the ladder itself is fixed here.
3. **PRIOR-EXTREME** — the high and low of the immediately preceding **completed** period of the
   next-higher TF in the protocol ladder, as a static level, `known_after_ts = that period's
   close`. Mapping (frozen): `4h → prior 1d`, `1d → prior 1w`, `1w → prior 1M`, `1M → prior
   12 completed monthly bars` (top of the ladder, so the preceding annual window).

**Control (PRIMARY comparison — NU-1):**

- **RW-NULL** — for every real subject level, simulate a **deterministic, seeded** synthetic
  random-walk price path calibrated on the causal history strictly before that level's
  `known_after_ts` (`research/synthetic_baseline.random_walk_swing_levels`, `seed = 20260616`),
  and take the random-walk's spontaneous swing levels — matched **count** and **known_after_ts**.
  Run through the **same** event/outcome machinery as the subjects so it cannot favour any source.

**Descriptive-only (NOT a gate):**

- **SHUFFLE-PLACEBO** (`make_placebo_levels`, existing) — reported for continuity with the closed
  study, but its reject rates on this OOS window are **already seen**, so it **cannot** be a
  pre-registered comparison here (would be peeking). Reported descriptively only.

**Level recency window** (frozen, applied identically to all sources): `level_active_bars` per TF
— 4h `720`, 1d `365`, 1w `104`, 1M `36`.

## 5. Event definition (identical across sources)

Reuse the frozen definition from the closed study (`find_events`): a **fresh touch** of the
nearest causally-active level within `eps_atr * ATR(t)` (`eps_atr = 0.25`), one event per bar per
source, ATR = Wilder(14) rolling only. Unchanged so subjects and RW-null are measured identically.

## 6. Outcome metrics (per event, per horizon)

Reuse frozen horizons and metrics (`event_reject`): per TF 4h `{6,18,36}` / 1d `{4,12,24}` /
1w `{2,4,8}` / 1M `{2,3,6}`; primary = middle horizon. PRIMARY metric = **`reject`**
(direction-agnostic repulsion). Secondary: `close_through`, `abs_fwd_move_atr`, `mfe/mae_atr`.

## 7. Out-of-sample split — purged/embargoed (NU-3 satisfied)

- Time-ordered 70 % train / 30 % test per TF (`split_positions`).
- **Embargo / purge** of `max(horizon)` bars at the boundary (`_window_of`) so no event's outcome
  horizon straddles the split. Per NU-3 this mechanism is **named** a *purged/embargoed split* and
  cited to **López de Prado, *Advances in Financial Machine Learning* (2018), Ch. 12** (purging /
  embargo / CPCV). A full combinatorial purged-CV module (SENARE-2) is **not** adopted — the
  single-split embargo already neutralises horizon-straddle leakage for this design.

## 8. Statistics — anytime-valid (NU-2 satisfied; THIS IS THE EXECUTION GATE)

This study is a **3rd look at the same BTC OOS window** (behaviour → context-conditioned "second
look" → B-1). Per **NU-2**, a fresh fixed-horizon permutation p-value on that window is **invalid**
(optional stopping / peeking) and is **forbidden here**.

- **Required inference:** **anytime-valid** — an **e-value** per subject vs RW-NULL on the
  test-window `reject` counts. Anytime-valid lineage anchor: Johari, Pekelis & Walsh,
  arXiv:1512.04922.
- **Multiplicity** (3 subjects × 4 TFs): convert each e-value to its calibrated anytime-valid
  p-value `p = min(1, 1/E)` (Markov / Ville) and apply the repo's **existing tested Holm-Bonferroni**
  (`fib_context_conditioned_study._holm`) across the family. Holm controls FWER under arbitrary
  dependence, so this is the e-value analogue of the Holm the repo already uses.
- **Dependency:** no e-value code exists (**SENARE-1**, gated/unbuilt). **This study cannot be
  executed until SENARE-1 is built and `synthetic_baseline` is wired into a horizontal-structure
  harness (DELAR-1 wiring).**

### §8 amendment — 2026-06-17 (pre-execution, blind to any B-1 result)

Made **before** SENARE-1 was run and **without** seeing any B-1 output — a correctness fix, not a
goalpost move. The exact e-value construction is pinned to the **conditional 2×2 / Fisher
noncentral-hypergeometric e-value** (safe-testing lineage: Grünwald, de Heide & Koolen, *Safe
Testing*, 2024; Turner, Ly & Grünwald, two-sample / 2×2 safe tests), **not** a two-sample mSPRT
mixture. Rationale (both blind to output): (a) **exactness at small N** — conditioning on the total
reject count removes the nuisance base-rate, so `E[E]=1` under H0 holds *exactly at every N*,
whereas mSPRT's normal approximation only holds asymptotically and §9 admits 1M/1w often have
N<30; (b) it avoids hand-rolling a mixture (bug risk flagged pre-build). Johari/Pekelis/Walsh stays
as the anytime-valid *lineage* anchor (NU-2 requires "via e-values" generically, not a pinned
equation). **Free parameter pinned here, before running:** the alternative is a fixed equal-weight
grid of odds-ratios `ψ ∈ {1.5, 2.0, 3.0}` (one-sided, subject repels *more*). Crucially, validity is
**exact for any prior over ψ** (each `E_ψ` has `E[E_ψ]=1` under H0, so any convex combination does
too) — the grid affects **power only, never the Type-I guarantee**; it is pinned solely to remove
post-hoc selection. **Ship-gate:** a null-simulation test (equal Bernoulli rates, many draws)
must empirically confirm `mean(E) ≤ 1` at small *and* large N before the harness is trusted.

## 9. Pre-registered robustness criterion (stop/go)

A generic-structure subject shows **robust repulsion → strategy sanity-check authorised** iff, for
that subject, **all** hold:

1. `N_events >= 30` for the subject **and** RW-NULL in the **test** window (else underpowered).
2. Subject `reject_rate` **>** RW-NULL `reject_rate` in the **test** window.
3. **Same sign** (subject − RW-NULL > 0) in the **train** window too.
4. Anytime-valid **e-value clears the e-Holm threshold** (test) across the subject × TF family.

If every subject fails → **stop**, write the results report, **no strategy sanity-check.**
A 1M/1w result with `N < 30` is reported descriptively but **cannot** satisfy the gate.

## 10. Optional strategy sanity-check (only if §9 passes for some subject)

One simple, **non-optimised** rule (fade a fresh touch in the rejection direction), fixed
fee+slippage, unit notional, gross **and** net, drawdown, trade count, train/test separately.
Labelled **"research sanity-check," not a trading edge.** Dies on costs/OOS → say so and stop. No
parameter search.

## 11. Outputs (when executed)

- New harness alongside `research/fib_behaviour_event_study.py` (reuses its event/outcome code) +
  `research/synthetic_baseline.py` + SENARE-1 e-value module + tests.
- Run artifacts → `experiments/review/...` (gitignored); key numbers in the report.
- Results report: `btc-horizontal-structure-event-study-results-YYYYMMDD.md` (Observed / Inferred
  / Unverified; beats-RW-null-or-not per subject, N, TFs, robust-or-weak, sanity-check
  run-or-stopped; **no trading claim**).

## 12. Execution gate (docs-only status; two unblock paths)

This prereg is **registered, not run.** Execution requires a **separate explicit go** AND one of:

- **(a) Same-window, rigorous** — build **SENARE-1** (small, direct e-value / e-Holm; not a
  pre-release package) and wire **DELAR-1** `synthetic_baseline` into the harness, then run with
  the §8 anytime-valid inference. This is the path consistent with NU-2 on the seen window.
- **(b) Fresh data** — when a genuinely fresh window exists (new BTC bars accumulated, or a new
  symbol **after** BTC protocol sign-off), the peeking exposure resets and a fixed-horizon
  permutation becomes legitimate again. Not viable today (corpus ends 2026-06-05; other symbols
  blocked).

## 13. Non-goals honoured

No Genesis touch/import/export, no 1H, no ML/Optuna/optimisation, no parameter tuning on test, no
fixed-horizon p-value on the seen window, no live/paper trading, no exchange, no label/corpus
mutation, no large binary artifacts. Subject prices (round ladder, prior-extreme rule, swing
`pivot_k`) are frozen **here**, before any result. If a step needs any non-goal → **pause and
report.**

---

### Evidence discipline

- **Observed:** the event/outcome/split code cited (`find_events`, `event_reject`,
  `split_positions`, `_window_of`) exists in `fib_behaviour_event_study.py`; `synthetic_baseline`
  exists as a standalone generator never wired into a study; the closed study reported swing &
  placebo test-window reject rates (so those are "seen").
- **Inferred:** that RW-null is the correct primary control post-fib-null; that this is the 3rd
  look and thus NU-2 binds; that e-Holm composes with the repo's existing Holm use.
- **Unverified / out of scope here:** whether any generic subject actually beats the RW null —
  that *is* the study question, and all subject parameters (§4 round ladder, prior-extreme
  mapping, swing `pivot_k`) are frozen above before any result, as a valid prereg requires.

> Docs-only. Authorises no code, no dependency, no run, no source-label change. Plan:
> `C:\Users\fa06662\.claude\plans\clever-yawning-catmull.md` (SENARE-1 / DELAR-1 wiring gated).
