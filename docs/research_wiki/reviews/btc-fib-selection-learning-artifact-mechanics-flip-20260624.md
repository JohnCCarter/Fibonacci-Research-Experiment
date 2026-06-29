# BTC Fib Selection-Learning — snapping sign-FLIP mechanics (4H↔1D) (2026-06-24)

**Lean Fib Research. Research-only. DESCRIPTIVE-ONLY — NO verdict, NO claim, no edge/behaviour/PnL/
backtest/Genesis/auto-fib/1H/ETH/label-mutation.** A narrow follow-up to the
[mechanics note](btc-fib-selection-learning-artifact-mechanics-20260624.md): *why does the relationship
between snapping and cleanliness flip sign between 4H and 1D* (artifact-probe: 4H snapping **deflates**
cleanliness, 1D **inflates** it). Same **frozen data / locked detection** (no refresh, no new universe,
no matched-null, no new bins, no lock change). It explains the **measurement geometry of snapping** and
says **nothing** about human selection — the crux stays OPEN.

> **STATUS — the flip is a net-vs-path channel reversal driven by candle granularity (descriptive).**
> `cleanliness = net/path`, so a snap changes cleanliness via two channels: it moves the **net**
> (endpoint-to-endpoint move) and the **path** (summed intermediate move). Restricting to snaps that
> **actually moved the span** (the question's support; unmoved snaps have Δclean=0 by construction):
> on **4H** snapping grows **path faster than net** (median rel_path **0.231** > rel_net **0.181**;
> 63% path-dominated) → cleanliness **down**; on **1D** it grows **net faster than path** (median
> rel_net **0.063** > rel_path **0.025**; 60% net-dominated) → cleanliness **up**. The dominant channel
> **flips** between the two TFs — mechanically consistent with **candle granularity** (fine 4H bars add
> mostly intermediate retracement = path; coarse 1D bars put the detector pivot at a genuinely more
> extreme price = net). **No verdict, no claim, crux unchanged.**

## Method (descriptive decomposition; no new universe / bins / lock)

For each reached non-degenerate leg the probe already records the exact human span `[pos_a, pos_b]` and
the snapped detector-pivot span `[snap_a_idx, snap_b_idx]` (two new descriptive `ArtifactRow` fields,
used by no contrast/verdict). On the same frozen closes: `net = |close[hi] − close[lo]|`,
`path = Σ|Δclose|`; `rel_net = Δnet/net_exact`, `rel_path = Δpath/path_exact`. Since
`cleanliness = net/path`, `Δln(cleanliness) ≈ rel_net − rel_path` — an **arithmetic identity** (the
`d_clean ~ (rel_net−rel_path)` Spearman is **0.99 by construction**, flagged, **not** the finding). The
**non-trivial empirical content** is *which channel dominates per TF*. Domain = snaps that **moved the
span** (unmoved snaps are Δclean=0 — the question's support, not a post-hoc bin); the moved fraction is
reported.

## Results — channel medians on the moved-snap domain

| TF | moved / total | median `rel_net` | median `rel_path` | dominant channel | frac net-dom | Spearman(Δclean, rel_net) | Spearman(Δclean, rel_path) |
|----|--------------:|-----------------:|------------------:|------------------|-------------:|--------------------------:|---------------------------:|
| **4H** | 107 / 314 | 0.181 | **0.231** | **PATH** (clean ↓) | 0.374 | +0.476 | **−0.177** |
| **1D** | 20 / 60 | **0.063** | 0.025 | **NET** (clean ↑) | 0.600 | +0.864 | +0.201 |
| 1w (ctx) | 5 / 19 | 0.024 | 0.048 | path | 0.40 | +0.90 | +0.10 |
| 1M (ctx) | 6 / 9 | 0.244 | 0.253 | ~tie | 0.67 | +0.83 | +0.26 |

(`d_clean ~ (rel_net−rel_path)` identity Spearman = 0.99 on 4H/1D — validation, by construction.)

- **The flip is the channel reversal.** 4H: `rel_path > rel_net`, 63% of moved snaps path-dominated →
  net deflation of cleanliness (matches the locked `snapping_deflates`). 1D: `rel_net > rel_path`, 60%
  net-dominated → inflation (matches `snapping_inflates_cleanliness`). The `Spearman(Δclean, rel_path)`
  even changes sign (4H **−0.18** vs 1D **+0.20**): on 4H the path channel pulls cleanliness down, on 1D
  it does not.
- **Magnitude context:** 4H snaps move the span proportionally **more** (rel ~0.18–0.23) than 1D
  (~0.03–0.06) — but on 4H that movement is disproportionately **path**.
- **Caveat (honest):** the per-leg `median(rel_net − rel_path)` is ≈0 on 4H (the per-leg difference
  straddles 0); the sign is carried by the **channel medians + the net-dominated fraction**, not the
  per-leg median — reported as such, not overstated.

## Mechanical reading (descriptive — kept apart from any selection-claim)

The dominant-channel flip is **mechanically consistent with candle granularity**: on **fine 4H bars**,
a detector pivot a few bars off the human anchor adds **fine intermediate candles that are mostly
retracement** → path grows faster than net → cleanliness falls. On **coarse 1D bars**, the detector
pivot being a different bar means a **genuinely more extreme price reached comparatively directly** →
net grows faster than path → cleanliness rises. This is a statement about **how the detector's bar
granularity interacts with the cleanliness measurement when anchors are snapped** — it is **not** a
statement about human selection, the `cleanliness` lead, or the crux.

## Separation of mechanics from selection-claim (binding)

- This explains the **measurement geometry of snapping** (a net-vs-path channel reversal by TF). It is
  **not** evidence that the Stage-2 `cleanliness` lead is or is not a genuine human signal.
- The artifact-probe reading is **unchanged** (4H `snapping_deflates`, 1D `snapping_inflates`,
  combined `meta:` status); **no lock is touched**; **no new verdict / claim**.
- **The crux stays OPEN.** Explaining the snapping flip mechanically does not resolve "is `cleanliness`
  human intuition or artifact" either way.

## Observed / Inferred / Unverified

- **Observed (verified):** the table; 4H moved-snap median rel_path 0.231 > rel_net 0.181 (63%
  path-dominated); 1D rel_net 0.063 > rel_path 0.025 (60% net-dominated); `Spearman(Δclean, rel_path)`
  flips −0.18→+0.20; identity Spearman 0.99; deterministic; new tests green.
- **Inferred (descriptive, scoped):** the 4H↔1D snapping sign flip is a **net-vs-path channel reversal**
  mechanically consistent with **candle granularity** (fine bars add path, coarse bars add net).
- **Unverified / scope limits:** no verdict, no claim, no lock change; the granularity reading is a
  *mechanical interpretation*, not a tested hypothesis (no new universe was built to isolate it); 1M/1w
  are context (moved n = 6 / 5); the crux is unchanged and OPEN.

## Non-claims (binding)

Descriptive consolidation only. **No verdict, no positive claim, no lock change, no reproduction, no
edge/behaviour/PnL/backtest/strategy claim.** Explaining the snapping geometry is **not** evidence about
`cleanliness`-as-human-signal. No matched-null, no new candidate universe, no new model feature, no
Genesis, no auto-fib-as-truth, no 1H, no ETH, no label/corpus mutation, no `data.fetch --refresh`.

> The snapping sign flip is a **net-vs-path channel reversal**: 4H snaps add **path** (fine-bar
> retracement) → cleanliness down; 1D snaps add **net** (coarse-bar extreme) → cleanliness up —
> mechanically a **candle-granularity** effect. Descriptive only — measurement geometry, not human
> selection; no verdict, no claim, crux unchanged.
