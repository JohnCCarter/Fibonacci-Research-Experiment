<!-- prereg:locked -->
<!-- This file is immutable after lock. Run results / addenda go in the *-postlock.md sibling.
     A PreToolUse hook (.claude/hooks/guard-locked-prereg.sh) asks before any Edit/Write here. -->
# Daily wick-pair anchor — descriptive accuracy pre-reg (LOCKED 2026-06-29)

**Status:** LOCKED 2026-06-29 (human sign-off). Question + baselines + decision rule frozen pre-run;
precursor sonde run (premise gate resolved, wick-vs-body confound logged). Build + run of the
wick-pair detector authorized under this lock. Result becomes "truth" only after human sign-off of
the run output. Scope is **descriptive anchor-selection accuracy vs facit only** — no edge / PnL /
backtest / Genesis / auto-fib claim.
Issues: **#38** (rolling daily wick-pair A/B engine) + sequenced with **#31** (fractal anchor
detection vs human labels). See review plan in the approved plan file.

## Question

On **daily** BTC/USD, does a **wick-pair** A/B detector recover the **same anchor pair** as the
human's daily source-fib facit — i.e. are the human's `anchor_a`/`anchor_b` inside the detector's
candidate universe (coverage), and does the detector's top pick agree with facit (agreement) —
**better than the existing pivot detector** as a control, OOS?

This answers *only* "can the engine pick the same A/B as the human on the TF where he draws this
style?" It does **not** test continuation edge in the 0.5–0.618 zone.

## Why daily, why descriptive (background — locked framing)

- **Daily is where the human draws this style.** The wick-pair drawing is daily-native for the user;
  the daily facit (`data/labels/human_fib/bitfinex/BTC-USD/1d/`, **N≈67** source fibs) is the right
  target for a *descriptive accuracy* read of this specific style. (Decision locked 2026-06-29.)
- **Within-TF, not cross-TF.** Both A and B are wicks on **daily** candles — within-TF selection,
  which the 2026-06-26 within-TF reframe *supports*. This is **not** the falsified 1w→1d cross-TF
  nesting axis (`log.md` 2026-06-26); no parent→child nesting anywhere.
- **Edge / OOS-power is out of scope.** The only powered selection cell is 4h (N≈365); daily is
  data-thin. So **no edge or OOS-significance claim** may be drawn from the daily cell — the small-N
  caveat is reported with every result. A descriptive accuracy-vs-facit read is still valid at N≈67.
- **Per-leg-feature line on 4h is closed** (`exclusivity` enriched_worse; `impulse_leg` CI-straddles-0
  null, 2026-06-26). This is a **separate line on a separate TF with a different question
  (anchor recovery, not AP-lift)** — registered fresh here, not a reopen of the closed line.

## Key risk this study must confront FIRST (honesty — BINDING)

**The facit anchor convention may not sit on wick extremes.** Repo observation (handoff.md, tier2
review): crash-leg facit anchors use **body/close**, not the wick extreme. #38's premise is that A/B
**are** dominant rejection wicks. If the human's `anchor_a`/`anchor_b` prices coincide with
body/close rather than the candle's high/low wick tip, a wick-extreme detector **cannot** recover
them by construction.

→ **Precursor sonde (cheap, leakage-free, TRAIN only) before any detector build:** for each daily
facit, measure how often `anchor_a`/`anchor_b` price equals the candle **wick extreme** vs
**body/close** (within ε). Report the split. If anchors are predominantly body/close, the wick-pair
hypothesis is falsified at the premise and we stop before building the phased detector. This sonde
result is reported regardless of outcome.

### Sonde RESULT (run 2026-06-29, `scratchpad/wick_vs_body_sonde.py`, N=71 fibs / 142 anchors)

- **94% of anchors on the wick extreme** (top 90%, bottom 97%), **0% on body/close**, 6% tie
  (doji candles, no wick on that side). **median `d_wick` = 0.000** (exact), median `d_body` = 0.386
  of candle range. → **`premise_falsified` does NOT trigger.**
- **BUT confound (BINDING):** the labeling tool **snaps every click/drag to the nearest bar
  high/low** ([`labeling/tool.py`](../../../src/fibengine/labeling/tool.py) lines 11–13). Body/close
  anchors are therefore **impossible by construction** — the 94%/0% split is the *tool*, not an
  independent measurement of the human's style. The exact `d_wick`=0.000 median confirms the snap
  empirically.
- **Consequence:** the wick-vs-body distinction is **not testable from tool-snapped facit** and is
  dropped as a discriminator. The real, un-confounded question is **bar selection**: does a wick-pair
  heuristic pick the **same high/low bars** (and pair) as the human, vs the existing pivot detector?
  That is measured by `pivot_recall`/`compare` and is unaffected by the snap (facit *and* detector
  both live on bar high/low). The prior repo note ("crash-leg anchors use body/close") cannot refer
  to the tool-snapped price — flag for the human to reconcile (intent vs snapped placement), but it
  does not block.

## Baselines / controls (name before run — LOCKED)

- **Primary control:** the existing pivot detector candidate universe —
  [`pivots/detect.py`](../../../src/fibengine/pivots/detect.py) (`mode:"fractal"` Williams +
  `mode:"window"`), measured with [`evaluation/pivot_recall.py`](../../../src/fibengine/evaluation/pivot_recall.py).
  The wick-pair detector must recover human A/B **at least as well** as this to be worth anything.
  (This is the shared measurement infra with **#31** — reuse, do not reimplement.)
- **Trivial floor:** random/most-prominent A/B pair on the same daily frame.

## Method (reuse existing infra — no new eval code)

1. **Coverage:** is each human `anchor_a`/`anchor_b` inside the detector's candidate set?
   [`pivot_recall.py`](../../../src/fibengine/evaluation/pivot_recall.py) (`high_hit`, `low_hit`,
   `both_hit`, `*_dist_bars`).
2. **Agreement:** does the detector's selected pair match facit? [`evaluation/compare.py`](../../../src/fibengine/evaluation/compare.py)
   + [`evaluation/metrics.py`](../../../src/fibengine/evaluation/metrics.py) (`price_agree`,
   `time_agree`, `fib_agree`, `agreement`).
3. Causal only: detector sees pivots with index ≤ B (no peek), consistent with the existing
   truncate-and-whitelist convention.
4. Report coverage + agreement for wick-pair detector **vs** primary control on the **same** daily
   labels, with N and the small-N caveat.

## Detector (built only after lock; #38 phases)

Net-new `src/fibengine/strategies/chamoun_daily_wick_pair.py` — #38's phases (trend → wick-pair
discovery → stabilizing → golden-zone-active → invalidation), with an **audit trail** logging every
rolling A/B replacement and why. Golden zone (0.5/0.618) enters as a **stated hypothesis**, not as
given significance — the active protocol retired golden-zone bias (all levels equal). Daily OHLCV
only; no orderbook.

## Decision rule (LOCKED — reframed 2026-06-29 after the sonde)

**The test is BAR SELECTION**, not wick-vs-body. The precursor sonde resolved the premise gate
(`premise_falsified` does **not** trigger — anchors sit on bar high/low) and showed wick-vs-body is
confounded by the tool snap, so it is **removed** as a discriminator. The un-confounded question is
whether the wick-pair heuristic selects the **same high/low bars + pairing** as the human facit.

- **`wick_pair_recovers_facit`** if the wick-pair detector's coverage (human A/B bar in its candidate
  set) **and** agreement (top pick matches facit pair) are **≥ primary control** (existing
  fractal/window pivot detector) on the **same** daily labels.
- **`wick_pair_no_better`** if coverage/agreement do **not** beat the existing pivot detector → the
  wick-pair detection philosophy is not justified on daily; **#31's fractal line remains the
  candidate** anchor-detection approach.
- No redefinition against the result. Descriptive only; **null is a first-class result**. Small-N
  (N≈71) reported every time.

## Gate

LOCKED 2026-06-29 (human sign-off). Build + run of the wick-pair detector authorized under this
lock. Result becomes "truth" only after human sign-off of the run output.

---

## Post-lock addenda

This prereg is **immutable** after lock. All post-lock material — build-scope notes, eval-infra
honesty, the run result (`wick_pair_no_better`), unrun baselines, and sign-off status — lives in a
**separate, unguarded** companion file so the registration is never edited against its own result:

→ [`btc-fib-daily-wick-pair-anchor-prereg-20260629-postlock.md`](btc-fib-daily-wick-pair-anchor-prereg-20260629-postlock.md)
