# Post-lock addenda — daily wick-pair anchor prereg (2026-06-29)

Append-only companion to the **locked** prereg
[`btc-fib-daily-wick-pair-anchor-prereg-20260629.md`](btc-fib-daily-wick-pair-anchor-prereg-20260629.md).
The locked file is immutable after sign-off (guarded); run results, scope notes, and sign-off status
live here so the registration itself is never edited against its result.

### A1 — Build scope: A/B selector only (2026-06-29, human-confirmed)

The locked **Decision rule** tests **bar selection only** (coverage + agreement of the A/B pair). The
locked **Detector** section describes the full #38 phase machine (trend → discovery → stabilizing →
golden-zone-active → invalidation). The phases **after** A/B is chosen are continuation tracking and
contribute **nothing** to coverage or agreement. To stay lean (don't build continuation scaffolding
before the selector is shown to recover facit), the build is **scoped to the wick-pair A/B
selector** — with an audit trail of A/B choices — and the **continuation state machine
(stabilizing / golden-zone-active / invalidation) is deferred** until the selector demonstrably
recovers facit. The decision-rule outcome is identical either way. Locked sections unchanged.

### A2 — Eval-infra reality vs "no new eval code" (2026-06-29, honesty)

The named infra does **not** ingest the fib-anchor facit as-is, so "reuse — no new eval code" holds
for the **metric functions** but not literally:

- The daily facit is `anchor_a`/`anchor_b` fib JSON under `human_fib/`, which
  [`store.iter_label_files`](../../../src/fibengine/labeling/store.py) **explicitly excludes** (line
  136) and whose shape is `high`/`low` `SwingLabel`, not anchors. → thin adapter
  `fib_*.json → SwingLabel(high, low, source="human")` (same top/bottom-by-price mapping the sonde
  used). New code, but no new metric.
- [`pivot_recall.evaluate_label_recall`](../../../src/fibengine/evaluation/pivot_recall.py) hardcodes
  the control detector (`detect_pivots(..., settings.pivots)`). → make the candidate producer an
  optional injected arg (default `detect_pivots`, every existing caller unchanged); call it twice
  (control vs wick-pair) on the **same** frames/tol. Same metric, apples-to-apples.
- [`compare.compare_label`](../../../src/fibengine/evaluation/compare.py) runs the **old** engine
  (`select_swing`), not this detector → agreement is obtained by building a `Swing` from the
  detector's A/B pick and calling [`metrics.evaluate`](../../../src/fibengine/evaluation/metrics.py)
  directly.

This diff is reported plainly in the run writeup; the locked Method wording is **not** edited to hide
it.

### A3 — Run result: `wick_pair_no_better` (2026-06-29, awaiting sign-off)

Run `experiments/results/chamoun_wick_pair_accuracy.jsonl` (wick_frac=0.5 a priori, k=3, **N=71**):

| metric | control (pivot) | wick-pair |
|---|---|---|
| coverage `both_hit` | **0.90** | **0.08** |
| mean agreement | 0.078 | 0.006 |
| pairs selected | 32/71 | 44/71 |

Per the locked **Decision rule**, `wick_pair_recovers_facit` requires coverage **and** agreement
**≥ control**. Both are far below → **`wick_pair_no_better`** (one-shot, no redefinition). The
wick-pair philosophy is not justified on daily; **#31's fractal line remains the candidate**.

**What exactly is falsified (scope — calibrated):** the wick universe is **not** sparse — the
selector picked a pair in **44/71** cases, yet coverage is 0.08. So the dominant-wick pivots sit at
**different bars** than the human's anchors; "detector found nothing" is ruled out. This cleanly
falsifies the **strong form** — *"the human's daily anchors sit on ≥50%-range rejection-wick
candles"* — at the a-priori `wick_frac=0.5`. It says **little about the weak/rank form** (*"wick
geometry helps rank among candidates"*): the `agreement` limb is floor-level for **both** arms
(control's `select_swing` is not localized to the facit leg), and a coverage gate structurally favors
the 811-pivot control over any restrictive filter. The rank-form question is **left open** for a
separately-registered `wick_frac` sweep (not a rescue of this locked test). `wick_frac` is **not**
re-tuned against facit. Full writeup: [log 2026-06-29](../log.md).

### A4 — Locked baselines not fully executed (honesty, moot for this null)

The locked **Baselines** name (a) the primary control in **both** `fractal` and `window` modes and
(b) a **trivial floor** (random/most-prominent pair). The run used the control in **window mode only**
and **did not** run the floor. Both are **moot for a null**: the wick-pair failed against the
*more-permissive* window control (fractal is stricter → lower control coverage, wick still loses at
0.08), and the floor only contextualizes a *positive*. They are **required before any positive
claim** — flagged here rather than silently omitted (validity over convenience). Not re-run (no
verdict impact; saves redundant interpreter launches).

### A5 — Fractal control WAS run; A4's mode label corrected (B-closure, 2026-06-29)

Pre-sign-off validity review (`leakage-validity-reviewer`) flagged that A4's "#31 fractal stays the
candidate" rests on a control mode A4 said was never run. **B-closure**
([`scratchpad/fractal_control_coverage.py`](../../../scratchpad/fractal_control_coverage.py)) re-runs
the control coverage under **both** modes — expansion config, k=3, same N=71 facit, only `pivots.mode`
flipped:

| control mode | `both_hit` coverage | median candidates |
|---|---|---|
| window | 0.7887 | 175 |
| **fractal** (`fractal_n=1`) | **0.9014** | 394 |
| wick-pair (recorded) | 0.08 | — |

**The recorded 0.90 control reproduces under FRACTAL (0.9014), not window (0.7887).** Both
`config/settings.yaml` and `config/settings.expansion.yaml` set `pivots.mode: fractal`, and only the
expansion config covers all 71 facit (history_start 2016) — so the recorded run used the **fractal**
control.

→ **A4 is corrected:** the control ran in **fractal mode**, not "window only"; and A4's directional
note ("fractal is stricter → lower control coverage") is **wrong** for `fractal_n=1` here — fractal
yields *more* candidates (394 vs 175) and *higher* coverage (0.90 vs 0.79). The substantive conclusion
is unchanged and now **directly supported**: wick-pair (0.08) loses to the fractal control — i.e. to
**#31's own line** — so "#31's fractal line remains the candidate" is empirically earned, not assumed.
The null `wick_pair_no_better` is **robust under both control modes** (wick 0.08 ≪ window 0.79, ≪
fractal 0.90).

**k=3 reconciliation** (review nit): the locked Method says "index ≤ B"; the harness truncates at
`b_bar + k + 1` with k=3 (an a-priori confirmation lag, not tuned). It is applied **identically** to
both arms (same `cut`), so it cannot differentially bias the control-vs-wick comparison — symmetric,
no leakage. Recorded for completeness; no verdict impact.

**Status:** run output + B-closure — **awaiting human sign-off** before it becomes "truth".
