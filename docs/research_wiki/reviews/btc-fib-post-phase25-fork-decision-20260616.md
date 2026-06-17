# BTC/Fib — Post-Phase-2.5 Fork Decision (2026-06-16)

**Docs-only decision note.** It compares four next-step options and recommends one. It
**builds nothing, exports nothing, touches no Genesis code, starts no 1H, starts no
ML/backtest/signal, and does not authorise Phase 3.** It exists only to create a clean
decision point now that Phase 2.5 is reviewed PASS / closed.

## 1. Where we are (observed — facts on disk / in history)

- **Source-fib corpus locked & clean:** 1M=9, 1w=21, 1d=67, 4h=365 (462 fibs), log scale,
  profile `tradingview_log_chamoun`, levels `[0,0.382,0.5,0.618,0.786,1]`, no 0.236
  ([integrity capstone](btc-source-fib-corpus-integrity-20260615.md)).
- **MTF confluence track CLOSED** — confluence is *geometry*, not edge
  ([decision note](btc-mtf-confluence-interpretation-decision-20260615.md)).
- **Fib → Genesis V2 paper track closed as far as docs allow:** Phase 0 prereg, Phase 1
  feature-export spec, Phase 2 dummy contract test (stdlib `feature_contract.py`, 20 tests,
  reviewed PASS), Phase 2.5 nullability policy (reviewed PASS). All docs-only except the
  isolated dummy-contract validator, which computes no real features.
- **1H deferred** — cache not fetched; explicitly out of scope.
- Working tree clean; `local == origin`; history linear through `3b6d341`.

## 2. Inferred (reasoned from the above, not directly measured)

- The Genesis-V2 contract is **fully specified as far as paper can take it.** The next *real*
  step (compute features, export, run the Phase 0 study) inherently requires **code and/or a
  real export** — which is outside the currently locked scope.
- Option **B's** valuable artifact — a single falsifiable question — **already exists** as the
  Phase 0 pre-registration (causal confluence zones vs placebo/naïve levels, OOS). What is
  missing is *execution*, and execution needs code. So B as a *docs* step would mostly
  restate Phase 0.
- Option **C** (conceptual Genesis prep) is **largely redundant** with the Phase 1 read-only
  ingestion contract, which already defines consumption conceptually — and it sits closest to
  the "no Genesis-touch" line.
- Option **D** (BTC/Fib quality, not 1H) is the **only option fully executable under the
  current constraints** (no code, no export, no 1H, no ML).

## 3. Unverified (open — cannot be settled without crossing the locked scope)

- Whether causal confluence zones have any **behavioural / predictive edge OOS** — the Phase 0
  question. **Unanswerable without code + export.**
- Whether more corpus-quality work (D) would surface **material** label issues or merely
  **confirm** the already-locked corpus (diminishing returns are unmeasured).
- Whether **pausing now** loses momentum that is costly to regain later.

## 4. Options

### A. Pause Fib here
- **What:** declare the Fib research arc at a natural stopping point; open no new track.
- **Value:** intellectually honest — the question reachable without code has been answered;
  avoids busywork. Durable: every artifact is committed and reviewed.
- **Risk:** momentum loss; the Phase 0 question stays unanswered indefinitely.
- **Scope fit:** fully compliant (does nothing).
- **Smallest slice:** this note + a one-line "paused" marker in handoff.

### B. Open a new track with one falsifiable question
- **What:** pick a single pre-registered falsifiable question and pursue it.
- **Value:** highest research value *if* executed — but the one good question (Phase 0) is
  already written.
- **Risk:** **its execution requires code + real export** → would breach the locked scope and
  trend toward Phase 3. As a docs step it largely duplicates Phase 0.
- **Scope fit:** docs-only restatement is compliant; **any execution is not.**
- **Smallest slice:** none that adds over Phase 0 without code → effectively blocked now.

### C. Prepare the Genesis V2 side conceptually (no code, no integration)
- **What:** sketch how Genesis would consume the feature contract, conceptually only.
- **Value:** low marginal — Phase 1 §4 already defines the read-only ingestion contract.
- **Risk:** sits closest to the "do not touch Genesis" line; easy to drift into Genesis-touch.
- **Scope fit:** compliant only if it stays strictly conceptual and Genesis-free; fragile.
- **Smallest slice:** a one-page consumer-contract recap — but it would mostly echo Phase 1.

### D. Return to the BTC/Fib quality track (not 1H)
- **What:** continue source-quality work on the locked corpus — e.g. document the body/close
  vs wick anchor convention globally, extend Tier 2 manual sampling, revisit remaining
  overlap-detector candidates — all read-only / docs.
- **Value:** modest but real; strengthens the facit that everything else rests on. **No new
  risk.**
- **Risk:** diminishing returns unknown (§3); could confirm rather than improve.
- **Scope fit:** fully compliant — no code, no export, no 1H, no ML.
- **Smallest slice:** one focused review doc (e.g. finalise the anchor-convention note).

## 5. Comparison

| Option | Value | Risk | Executable under locked scope? |
|--------|-------|------|-------------------------------|
| A Pause | Honest stop | Momentum loss | Yes (no-op) |
| B New question | High *if run* | Needs code/export → breaches scope | No (only restates Phase 0) |
| C Genesis prep | Low (redundant) | Closest to Genesis-touch | Fragile |
| D Fib quality | Modest, real | Diminishing returns | **Yes** |

## 6. Recommendation

**Primary: A (pause Fib here)** — the arc has answered what it can without code/export, and
pausing keeps the record clean and honest. **If continued work is preferred, D is the only
no-new-risk continuation** (read-only corpus quality, not 1H). **B and C are not recommended
now:** B's real value needs code (would breach scope / trend to Phase 3) and its docs form
duplicates Phase 0; C is largely redundant with Phase 1 and risks Genesis drift.

This is a genuine fork — **A or D** — and the choice is the human's. The recommendation is
explicitly **not Phase 3** and **not** any real export or Genesis work.

## 7. What this note does NOT authorise

No Phase 3, no real feature export, no Genesis touch, no code, no 1H, no ML/backtest/signal,
no new implementation. If the chosen next step needs code or a real export: **pause and
report** before starting.
