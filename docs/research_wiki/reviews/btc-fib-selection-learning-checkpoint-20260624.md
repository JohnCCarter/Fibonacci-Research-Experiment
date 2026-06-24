# BTC Fib Selection-Learning — CAMPAIGN CHECKPOINT (2026-06-24)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** This doc **locks what the
selection-learning line has actually established** across its committed runs and names the **single
open crux**. It starts **no** new track, authorises **no** code, run, or build, and adds **no** new
positive claim. Decision needs a separate explicit GO.

> **Update 2026-06-24 (artifact-probe ran).** The cheap-first scope of track B (the existing-data
> `cleanliness` artifact-probe) has now been built + run (`1573b56`). It **narrowed but did not close**
> the crux: the *inflationary* detector-artifact got **no support** on the 4h primary (both contrasts
> point the other way), but **marginally / non-replicating** → "investigate, not a finding", **not**
> `artifact_risk_reduced`. The crux stays **OPEN**. See the verdict chain row 6 + the CRUX section.

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
| 6 | `cleanliness` artifact-probe (06-24) | direction guards **`inverse_surfacing`** + **`snapping_deflates`** (A7-unregistered combined → `meta:` status, NOT a verdict) | surfacing gap **−0.0557** CI [−0.1150, −0.00095]; snapping gap **−0.0219** CI [−0.0320, −0.0102]; both exclude 0 **below** | `1573b56` |

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
about human choice.

**What the artifact-probe settled, and what it did not** ([results](btc-fib-selection-learning-artifact-results-20260624.md),
LOCK `b533385`): the cheap-first probe tested the two mechanisms of the *inflationary* version of this
artifact on existing facit data. On the 4h primary (both contrasts powered, fidelity OK reached 0.860):

- **Surfacing** — reached legs are *less* clean than unreached (gap −0.0557, CI excludes 0 **below**) →
  guard `inverse_surfacing`. The detector does **not** surface cleaner human legs — if anything the
  reverse (marginal: CI upper −0.00095).
- **Snapping** — snapping anchors to detector pivots *lowers* cleanliness (gap −0.0219, CI excludes 0
  **below**) → guard `snapping_deflates`. Snapping does **not** inflate it.

So the simple **"the detector inflates cleanliness"** story gets **no support** on the powered primary.
**But the crux stays OPEN:** (1) this is **not** `artifact_risk_reduced` (both CIs *exclude* 0, the
direction guards, not include); (2) the surfacing reversal is **marginal** and the snapping reversal
**does not replicate** (it flips to *inflation* on the 1d context cell, +0.0222) → TF-dependent,
**"investigate, not a finding"**; (3) the broader "is `cleanliness` special vs a matched non-human
swing" question is **out of scope** (matched-null gated, A8 — **not built**; its gate condition
`detector_artifact_supported` on the primary was **not** met, so it stays unjustified). The crux is now
**narrowed** (the inflationary mechanism is unsupported) with a sharper investigate-target: *why
reached/snapped legs are less clean, and why snapping flips sign by TF.*

**Secondary loose end:** set-level **`exclusivity`** (`k*=3`) was specced in the
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) but the Stage-2 live whitelist actually
built was `{magnitude, cleanliness, duration, prominence, structure_alignment}` — **exclusivity was
never implemented or run.** It is an unfinished feature, not a result.

## The next-step choice — where it stands after the artifact-probe

The original A/B/C framing has partly resolved: **cheap-first B (the existing-data `cleanliness`
artifact-probe) is DONE** (row 6). The remaining candidate doors — **none started, none authorised:**

| | Track | Status / what it would do | Main risk |
|--|-------|---------------------------|-----------|
| **(i)** | **investigate** the artifact-probe's own finding | on existing data: why reached/snapped legs are *less* clean, and why snapping flips sign 4h↔1d (mechanical hypothesis: detector reconstructs larger/longer swings; snapping extends spans → more path) | low — descriptive, detector-frame |
| **(ii)** | gated **matched-null** / detector-independent universe | **stays UNJUSTIFIED** — its A8 gate (`detector_artifact_supported` on the primary) was **not** met; would need its **own** separate blind lock and risks inventing an arbitrary frame | high (validity-over-convenience) |
| **A′** | set-level **`exclusivity`** feature (the unbuilt loose end) | build the specced-but-unimplemented feature; orthogonal to the artifact crux | low–medium |
| **C** | pause + write **"current theory of human fib selection"** | synthesis-only; consolidate KNOW + the now-narrowed crux; defers further empirics | risks theorizing past the evidence |

- Any empirical track must be **locked blind before any build** (two-commit gate, as with W-gap /
  Stage-1 / the artifact-probe) and respect validity-over-convenience — no quietly-chosen control or
  frame. **The matched-null specifically may not be built without meeting its A8 gate AND a new lock.**
- **No track is recommended here** — this is consolidation. The GO is the user's next turn.

## Non-claims (binding — carried from every prior lock)

Not a reproduction of human selection. **No edge / behaviour / PnL / backtest / strategy claim.** The
`cleanliness`-as-artifact question is **OPEN** and this doc does **not** resolve it. Underpowered TFs
are context, not refuted. No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH.
This checkpoint is **descriptive consolidation only** — it adds no new positive claim and starts no
track.
