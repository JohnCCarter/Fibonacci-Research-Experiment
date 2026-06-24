# BTC Fib Selection-Learning — CAMPAIGN CHECKPOINT (2026-06-24)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** This doc **locks what the
selection-learning line has actually established** across its five committed runs, names the **single
open crux**, and makes the **next-step choice (A / B / C) well-posed**. It starts **no** new track,
authorises **no** code, run, or build, and adds **no** new positive claim. Decision needs a separate
explicit GO.

## Scope of this line (unchanged since the 2026-06-17 prereg)

> *Can a model reproduce **how the human selects** swings/ranges* — labels = facit, **no
> edge/behaviour/PnL/backtest/Genesis/auto-fib claim**. Stage-2 (leg/range gestalt) = headline target;
> Stage-1 (per-pivot) = diagnostic floor. One primary cell `k=3`, coverage ceiling, **4h is the only
> adequately powered TF** (1M/1w/1d underpowered throughout — **context, not refuted**).

## Verdict chain (committed, blind-locked rules applied verbatim)

| # | Study (date) | Locked verdict | Headline number (4h, powered) | Commit |
|---|--------------|----------------|-------------------------------|--------|
| 1 | Stage-2 headline (06-18) | modest single-feature lead | lift **+0.052**, CI [0.023, 0.120] vs magnitude | `ea6c2ea` |
| 2 | Prominence-family sensitivity (06-18) | **`survives_prominence_family`** | lift survives vs summed (+0.043) AND max (+0.049) prominence | `ea6c2ea` |
| 3 | k-sweep {0,3,6,12} (06-18) | **`k_stable_live_selection_signal`** | k=3/6/12 all survive; k=0 degenerate | `ea6c2ea` |
| 4 | W-gap causal-availability (06-23) | **`no_causal_gap`** | gap(k=3) **−0.0045**, CI [−0.070, +0.031] incl. 0 | `b515b08`↩`61c41d1` |
| 5 | Stage-1 per-pivot (06-24) | **`no_pivot_signal_above_prominence`** | recall **0.902**; ranking lift +0.0228, CI [−0.035, +0.079] incl. 0 | `b515b08` |

## What we KNOW (positive, scoped to 4h + the frozen eight features)

1. **There is a real, modest selection correlate.** On the one powered cell the model out-ranks every
   §6 baseline OOS (magnitude + summed/max prominence), CI excludes 0, `p_one_sided(lift≤0)=0/2000`.
2. **It is carried almost entirely by ONE leg-level feature — `cleanliness`** (net move ÷ path,
   standardized weight ~0.20, ≈3× the next term). Human-marked legs are **cleaner / more efficient**.
   It is **not** a multi-feature reproduction.
3. **It is not hindsight** (W-gap `no_causal_gap`): a bounded 180-bar retrospective view buys no
   selection info the live view at `k=3` lacks — `cleanliness` is **live-available**.
4. **It is not a buffer artifact** (`k_stable_live_selection_signal`): stable across k∈{3,6,12}.
5. **It is not a coverage/detection failure** (Stage-1 recall ~0.90): the human's anchors **are** in
   the detector's pivot universe — the Stage-2 ceiling is **not** a detection problem.
6. **It does not live in the lone pivot** (Stage-1 `no_pivot_signal_above_prominence`): per-pivot
   features add nothing over prominence. **The signal lives in the leg/range GESTALT**, and the one
   feature carrying it (`cleanliness`) is structurally a **leg-level** quantity.
7. **Absolute agreement is LOW** — AP ~0.057–0.066 against a ~0.83 reachability ceiling. **The human
   is not "reproduced."**

> One-line state: *On 4h there is a modest, OOS, live-available, buffer-stable, baseline-robust
> selection correlate, carried by leg `cleanliness` and living in the leg gestalt (not the lone pivot,
> not detection coverage) — but at low absolute agreement, and on one powered TF only.*

## What we DON'T know — the single open CRUX

**Is the `cleanliness` lead a genuine human-selection signal, or a detection / anchoring artifact?**
The entire pipeline is **conditioned on the detector's pivot universe**, and `cleanliness` is computed
on **detector-defined legs**. If the detector preferentially surfaces or anchors clean/efficient legs,
then "human legs are cleaner" is partly **mechanical** — baked in by candidate generation, not a fact
about human choice. This question has been flagged at **every** stage (06-18 sensitivity, k-sweep,
W-gap, Stage-1) and **deliberately left OPEN**; nothing run so far can resolve it, because every run
lives inside the same detector frame.

**Secondary loose end:** set-level **`exclusivity`** (`k*=3`) was specced in the
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) but the Stage-2 live whitelist actually
built was `{magnitude, cleanliness, duration, prominence, structure_alignment}` — **exclusivity was
never implemented or run.** It is an unfinished feature, not a result.

## The next-step choice — A / B / C (all roads lead to the crux)

| | Track | What it does | Decides the crux? | Main risk |
|--|-------|--------------|:-----------------:|-----------|
| **A** | set-level exclusivity / `cleanliness`-artifact diagnostic | stays in the detector frame: (i) build the unbuilt `exclusivity` feature, does `cleanliness` survive its inclusion; (ii) a diagnostic separating "human prefers clean legs" from "detector surfaces clean legs" | **partly** | within-detector-frame circularity may be **irreducible** — a within-frame test may not fully break the circle |
| **B** | detector-independent anchor-probe | removes the detector as candidate-generator and tests whether the anchor / `cleanliness` signal survives **without** the suspected source of circularity | **most directly** | requires **inventing a detector-independent frame** → new arbitrary choices (validity-over-convenience hazard); MUST be locked blind |
| **C** | pause + write "current theory of human fib selection" | synthesis-only; consolidates KNOW/crux into a stated theory, defers the empirical crux | **no** (defers) | leaves the artifact question open; risks theorizing past the evidence |

- **A and B are two angles on the SAME crux** (cleanliness-as-artifact / detector-circularity); **C
  defers it.** Whichever empirical track is chosen, its verdict rule must be **locked blind before any
  build** (two-commit gate, as with W-gap and Stage-1), and must respect validity-over-convenience —
  no quietly-chosen control or frame.
- **Tentative lean (not a decision — the GO is the user's next turn):** the crux *is* the artifact
  question, and only **B** attacks its suspected source head-on; **A**'s within-frame test may not
  break the circularity and **C** defers it. So **B, but only behind a tight blind lock** — and if a
  detector-independent frame cannot be defined without arbitrary convenience choices, **fall back to
  A**'s narrow cleanliness-artifact diagnostic. Recommend: **this checkpoint first, then A or B.**

## Non-claims (binding — carried from every prior lock)

Not a reproduction of human selection. **No edge / behaviour / PnL / backtest / strategy claim.** The
`cleanliness`-as-artifact question is **OPEN** and this doc does **not** resolve it. Underpowered TFs
are context, not refuted. No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH.
This checkpoint is **descriptive consolidation only** — it adds no new positive claim and starts no
track.
