# Fib → Genesis V2 — Phase 0 Pre-registration (2026-06-15)

Docs-only **pre-registration** for a *possible* next research track: use the locked BTC
human-fib corpus as a **causal feature source** and test it in Genesis V2 as a backtest /
behaviour harness. This note registers the question, rules, baselines, and stop/go **before**
any code exists. No implementation, no feature export, no Genesis touch, no ML, no pipeline,
no trading/signal/edge claim.

Background: the MTF-confluence track (CP1–CP3) closed with the finding that multi-timeframe
Fibonacci confluence **exists as geometry but is not edge proof** — see the
[interpretation & decision note](btc-mtf-confluence-interpretation-decision-20260615.md). The
decision-note fork was: pause Fib, or open a new track with **one** falsifiable question. This
note is the written candidate for that question — not a commitment to run it.

## 1. Research question

> **Does price react measurably differently at causally-valid, robust fixed-band MTF
> confluence zones than at matched naïve / placebo levels, out-of-sample?**

Properties this question is held to:

- **Testable** — every term is operationalised below (causal zone, baseline, behaviour
  metric, out-of-sample window).
- **Falsifiable** — the null is "no measurable difference vs baselines." If confluence-zone
  behaviour is statistically indistinguishable from placebo/naïve levels OOS, the answer is
  **no** and the track stops.
- **No trading/signal claim** — it asks about *behaviour of price near a level*, not about
  buying, selling, profit, or edge. "Edge" is not asserted anywhere before a test exists.

## 2. Why not anchor-recognition first?

Teaching the machine to *reproduce human source-fib anchors* is **not** the first edge step,
because the corpus is hindsight-selected:

- **`anchor_b` is only known after the move.** The second swing point is confirmable only once
  the leg has played out. A feature using it at time `t` would import the future.
- **The existence of a label is selection leakage.** A human drew a fib only where a swing
  *turned out* to matter. "Recognise the human anchor" therefore learns to recognise
  hindsight-chosen structures that cannot be reproduced live without hindsight.
- **Consequence:** anchor-recognition is a *descriptive* task (it characterises the corpus),
  not a *causal/predictive* one. It belongs after — and gated by — a clean behaviour result,
  if at all. The first causally-meaningful step is the behaviour question above.

## 3. Causal feature principle

A fib or confluence zone may contribute to a feature value at time `t` **only if all** hold:

1. **Both anchors confirmed before `t`** — `anchor_a` and `anchor_b` timestamps are strictly
   before `t`.
2. **Confirmation buffer passed** — a predeclared lag after `anchor_b` (not just
   `anchor_b ≤ t`) so the swing is confirmed, not still forming.
3. **No future labels** — the feature uses only fibs/zones knowable at `t`; it never consults
   the full corpus set or any later-drawn fib.
4. **No full-sample statistics** — any normalisation uses only data in the causal window up to
   `t` (rolling / expanding), never whole-series mean/std/min/max.

A feature that cannot be built under all four rules is **out of scope**, by design.

## 4. Leakage manifest (forbidden)

- Using `anchor_b` before its confirmation buffer has passed.
- Feeding the whole source-fib corpus directly into a backtest (ignores selection leakage).
- Using the CP1–CP3 confluence zones as **live features** — they were built from the *entire*
  corpus and are facit, not point-in-time knowledge.
- Tuning epsilon / band-width / cluster parameters on the holdout or test period.
- Full-sample normalisation (whole-series statistics in any feature).
- Random (non-time) train/test splits.
- A baseline that itself leaks (e.g. placebo levels derived from future-confirmed swings).

## 5. Naïve baselines

At least three, all causal:

1. **Causal prior swing high/low** — rolling swings confirmed before `t`. Closest honest
   analogue to what a fib "would" capture.
2. **Shuffled / placebo confluence** — same *count* and *time distribution* of levels as the
   real zones, but price-locations shuffled / randomly placed. The hardest control.
3. **ATR band or prior period high/low** — secondary structural reference.
4. *(Optional sanity)* **Round numbers** — only if relevant, as a sanity control.

**Most important:** controls **2 (shuffled/placebo confluence)** and **1 (causal swing
high/low)** are the primary controls. Fib confluence features must beat *both* out-of-sample;
failing to beat the placebo is by itself a stop signal.

## 6. Walk-forward / holdout

- **Time-based split only** — never random. Ordered train → validation → test windows.
- **Purge / embargo gap** between windows so a fib's anchor window cannot straddle a boundary
  and leak across it.
- **No parameter chosen on the test period** — epsilon, buffers, band-width frozen from the
  train/validation windows.
- **BTC first.** ETH only later, gated on BTC protocol sign-off and a clean BTC result.

## 7. What would count as success?

**Not profit.** Neutral, behaviour-only metrics, each measured **at the zone vs at the
baselines** in the same OOS window:

- **Touch frequency** — how often price reaches the level.
- **Rejection / acceptance frequency** — bounce away vs trade through.
- **ATR-normalised move after touch** — size of the subsequent move, volatility-scaled.
- **Close-through vs bounce** — does the candle close beyond the level or revert.
- **Time-to-reaction** — latency from touch to a defined reaction.

"Success" = a confluence-zone metric that is **statistically distinguishable** from the
placebo and causal-swing baselines OOS. This section describes a *future* study only — nothing
here is implemented now.

## 8. Stop / go

**Continue to Phase 1 only if all hold:**

- The question stays falsifiable when fully operationalised.
- The baselines (esp. placebo) can be defined without leaking.
- Causal features look *constructible* — i.e. survive the §3 rules without collapsing to near-empty.
- Scope stays small (one symbol, read-only export, no integration).

**Stop / pause if any hold:**

- Features become **near-empty** after causality + confirmation buffer (too few fibs are
  knowable at `t`).
- A clean, non-leaking baseline cannot be defined.
- The question can only be made interesting by smuggling in hindsight.
- The track demands heavy Genesis integration up front rather than a read-only feature export.

## 9. Phase 1 preview (design only, not authorised)

If Phase 0 clears stop/go, the *next* docs-only step would be a **feature-export spec**:

- A schema for a point-in-time, causally-valid feature table keyed by
  `(symbol, timeframe, timestamp, features…)`, each row guaranteeing `anchor_b + buffer ≤ t`.
- A short **Genesis V2 ingestion contract** (how columns are consumed and tested against the
  baselines on a time-split holdout).

No code, no export, no Genesis change in Phase 1 either — still spec only.

## Non-goals honoured

No code, no feature export, no Genesis V2 touch, no ML, no pipeline, no tuning, no new charts,
no 1H, no auto-fib, no trading/signal/edge claim. Docs-only pre-registration; this note
authorises **nothing** beyond itself.
