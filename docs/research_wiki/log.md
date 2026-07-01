# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.


> Older entries (2026-06-11→06-12 source-fib milestones):
> [post-reset part 1](log-archive-btc-postreset-part1.md).
> Pre-reset (2026-06-10 and earlier): [part 3](log-archive-pre-btc-reset-part3.md) →
> [part 2](log-archive-pre-btc-reset-part2.md) → [part 1](log-archive-pre-btc-reset-part1.md)

## [2026-07-01] decision | Rule decomposed generate→select; BOTH halves done → LANDED (no selector beats prominence)

**Origin half — the CRUX** (`origin_rank_probe.py`, advisor-guarded, mirror of the endpoint probe).
Given his "0", rank his "1" among backward-running-max fine highs (the swing highs the fall retraced
from) by **most-extreme** (prominence-like) vs **last-push** (nearest to "0"); guards pre-registered
(neutral orderings, pooled continuation for power, fresh-conditioned Poisson-binomial null, admissibility
reported not signal). **Pre-verify looked like a first positive:** last-push beat null (1d-continuation
63% vs 38%, **p=0.002**; pooled-continuation p=0.005; 1w-major p=0.011) and most-extreme was rejected —
the opposite of the endpoint (depth), matching HO-B (n=1). **Verification collapsed the exciting half
(trap #5):** last-push-rank-1 ⟺ **k_between=0** (no fresh high between "1" and "0") ⟺ a **clean monotonic
impulse = his cleanliness rule**, so P(last-push) ≡ P(k_between=0)=59% *by identity* — recency is
admissibility, NOT a distinct selector. The **only non-circular residual: his continuation origin is
NON-maximal** (not the towering prior peak) — most-extreme below null at every horizon (H×0.5/1/2),
strengthening with H, but only **marginally significant** (lower-tail p≈0.04 at H×1/H×2); major-swing
origin ~ null. This residual = the already-known scale/continuation finding, not a new mechanism.

**LANDING (honest step-1 endpoint).** Six probes now converge — DC, BOS/CHoCH, structure_alignment,
generator-coverage, endpoint-rank, origin-rank: **his leg selection ≈ prominence-ranked fresh/clean
impulse legs.** The continuation residual (origins fine-scale + non-maximal) is real but below decisive
power at this corpus; the unconditioned "which leg with nothing given" is likely out of reach at this n.
**No novel geometric selector beats prominence.** This is a descriptive map, not a sixth-feature failure:
we have localized where signal is (prominence + his own admissibility rules) and is not (a separate
geometric selector). Descriptive, no edge. Scratchpad `origin_rank_probe.py`, `endpoint_rank_probe.py`,
`impulse_leg_generator_coverage.py`. Gates green (ruff, bounds).

## [2026-07-01] decision | Rule decomposed generate→select; endpoint-half done → ORIGIN is the crux

**Reframe (advisor-led):** split Chamoun's rule (retracement extreme "1" → next fresh impulse endpoint
"0") into a candidate **generator** and a **selector**, and probe the **endpoint-given-origin** half
first — the one branch that is structurally neither prominence nor cleanliness.

**(1) Generator** (`impulse_leg_generator_coverage.py`): his anchors, **including continuation-mode
origins**, are **fine-scale (fractal_n=1) local extrema at 96-100%** → the continuation gap is a
**SCALE issue** (finer than the major-pivot detector), not un-findable. Coverage 83-89% at
magnitude-only, but precision poor (10-44 candidates/fib); cleanliness a weak generative filter.

**(2) Endpoint RANK probe** (`endpoint_rank_probe.py`): given his origin, his "0" is a **fresh break
100%** (1w 20/20, 1d 68/68) — but that is **his rule verbatim** (definitional), only a precision lever
(cuts endpoints ~8-12 → ~4 losing none). The honest **fresh-conditioned** test (null = random fresh
break, Poisson-binomial exact baseline `1/n_fresh`): **depth-among-fresh survives** (1d 47% vs 36%,
z=+2.08, **p=0.019**; 1w 50% vs 34%, p=0.024) — but depth = magnitude = **prominence, the known
survivor**, so real-but-not-novel. **Recency / "first-fresh" is DEAD** (1d 32% vs 36%, p=0.79 — his
"0" is NOT literally the *next* fresh extreme). Continuation behaves like major-swing on the endpoint
half (depth underpowered, n=20, p=0.35, but same kind). **Conclusion: endpoint-given-origin is NOT the
bottleneck — ORIGIN selection is**, and the continuation hole lives there. That is the untouched crux.
**Next:** an origin-selection probe (which fine extremum does he pick as "1" among plausible origins?).
Descriptive, no edge. Method note: fresh-conditioning is trap #4 of the session's definitional-leak
lesson (condition the null on the near-definitional property). Gates green (ruff, bounds).

## [2026-07-01] decision | Structure-engine → top-down M/W/D (1h parked); DC multi-scale NULL

**Pivot (Chamoun):** 1h too noisy → move the structure-engine to top-down **Monthly → Weekly → Daily**
(locked flow), validated against committed facit. Chamoun drew **20 new M/W/D fibs** (4M/7W/9D, 10 down/
10 up), transcribed to a scratchpad working set (`newfacit_topdown.py`) — **not promoted** to committed
`fib_*.json`. Single-scale prominence captures his new origins only 1M 1/4, 1w 5/7, 1d 6/9 (rest are
continuation-mode, mid-structure).

**Absorb → test → NULL.** Web-verified two external patterns (reimplement in-repo, no dep): **Directional
Change** multi-scale swings ([arxiv 2406.07354](https://arxiv.org/html/2406.07354v1)) + **SMC BOS/CHoCH**
([smc.py](https://github.com/joshyattridge/smart-money-concepts/blob/master/smartmoneyconcepts/smc.py)).
DC multi-scale *looked* like 18/20 coverage but that was **saturation** vs a weak all-bars null; a
permutation test (B=20k, seed 20260701) vs a **fair null (random same-kind detected pivots)** gives
pooled W+D **p=0.099**, per-TF p=0.17–0.50 → **DC-scale does NOT survive**. DC-θ swings ≈ our existing
detected pivots. **Lesson (echoes Stage-1): detection is not the bottleneck, SELECTION is.** Untested
lever = **BOS/CHoCH structure-context** as a *selection* signal (next). No edge/PnL; nothing committed;
scratchpad only. TZ note locked: screenshots = Europe/Stockholm (DST), cache = UTC → snap by price.

## [2026-07-01] direction | Chamoun's rule as a GENERATOR — continuation gap is a SCALE issue

Chamoun articulated his selection rule in his own words: leg = retracement/swing extreme (1) → next
fresh impulse endpoint (0), and the leg must be a **clean directed impulse, not chop**. That is
`cleanliness` (net/path) verbatim — and `cleanliness` is Stage-2's dominant weight (0.9), the one leg
feature that survived. Every failed test this session was **per-pivot** (structure); his criterion is
**per-leg** (impulse quality), which a single pivot cannot even express (Stage-1 excluded leg features).
Advisor reframed it from a ranking test (redundant: Stage-2 weak + the 2026-06-24 artifact-mechanics
span-confound) to a **generator/coverage** question (`impulse_leg_generator_coverage.py`). Result on
committed M/W/D: his anchors — origin AND endpoint, **including the continuation-mode origins** every
pivot test was blind to — are **fine-scale (fractal_n=1) local extrema at 96-100%**. So the continuation
gap is a **SCALE issue** (finer than the major-pivot detector), not un-findable. Coverage high at
magnitude-only (83-89%) but **precision poor** (10-44 candidates/fib) and **cleanliness only a weak
generative filter** (raising C drops coverage nearly as fast as candidates; his legs span a wide
close-to-close cleanliness range). **Containment achievable; selection/precision remains the hard part.**
Descriptive, no edge, nothing promoted. Next = a *selective* proposer.

## [2026-07-01] decision | STRUCTURE-MEMBERSHIP thread CLOSED — structure_alignment also NULL (committed corpus)

Ran the new tools on the powered COMMITTED facit corpus (Chamoun's ask), not the 20 transcriptions.
Used the repo's own `structure_alignment` (BOS/CHoCH is its coarse form) vs committed M/W/D origins
(anchor_a), prominence-matched permutation (`structure_alignment_committed_test.py`). **First read looked
like a real surprise:** his anchors sit at LOWER structure_alignment than prom-matched pivots (pooled
0.40 vs 0.47; 4h n=300 p<1e-4), and it survived a **tight prominence caliper** (≤0.25 ATR, p=0.012), the
0.5-fallback guard, a one-sided plausible-origin null, AND held on anchor_b — seeming to contradict
Stage-1. **Adversarial verification killed it:** the a+b symmetry was the tell (anchor_b, which he does
not select for structure, is *even more* low-align → it is the pure turning-point property). The
discriminating check — a **two-sided-plausible null** (backward AND forward move ≥ his median = other
DRAWABLE reversal extremes) — **collapses the gap** (4h 0.400 vs 0.398, p=0.55; anchor_b collapses too).
So low-alignment was the **trend-termination TAUTOLOGY** (every fib anchor bounds a real move → lower-align
than random locally-prominent pivots that include continuation highs), NOT a selection preference. Fully
consistent with Stage-1 (its AP-lift asks the among-candidates question directly). **Thread CLOSED:** four
features (DC, BOS/CHoCH, structure_alignment, + prominence-as-survivor) all say detection/structure-
membership is not the bottleneck — **selection among plausible candidates is**, still uncracked.
Continuation-mode / non-pivot origins remain unaddressed; 1w the consistent null cell. No edge; scratchpad only.

## [2026-07-01] decision | BOS/CHoCH structure-context → NULL on the selection question

Ran the untested lever (`bos_choch_selection_test.py`). Reimplemented SMC swings + BOS/CHoCH in-repo
(no dep). **Design A** (advisor, avoids the DC artifact): null drawn from **SMC swings** (not
`detect_pivots`), scoped to the swing-origin subset, **CHoCH (reversal) vs BOS (continuation) split**,
swing_length **LOCKED=3** (= repo `pivots.lookback`) + **=5** echo; origin mapped to the leg-launching
extreme (down-origin = the swing high that launches the fall), not the break bar.
**First pass looked positive** (BOS 75% (9/12) vs 33% null, p=0.003) — but a second advisor pass caught it
as a **~definitional break-rate artifact**: each swing carries one of {none,bos,choch}, so this mostly
measured that his origins **break structure** (83% vs 45% null, p=0.008), which a fib origin does **by
construction**. **The non-tautological question needs the null conditioned on breaking swings.**
Conditional: **BOS|broke 90% (9/10) vs 71% null, p=0.16** (Daily 86% p=0.27, Weekly p=0.49; n=5 pooled
75% p=0.55) → **no continuation-vs-reversal selection preference survives.** BOS/CHoCH adds no selection
signal beyond the definitional break-rate. Lesson (3rd time — DC, Stage-1): structure-membership is not
the bottleneck, **SELECTION among swings is**. Descriptive, no verdict; continuation-mode (non-swing)
origins still unaddressed; no edge/PnL; nothing committed to facit.

## [2026-06-30] decision | Chamoun structure engine v1 — origin proposer landed as a module

Pivot executed (set 2026-06-30): **stop testing edges; build an engine that represents Chamoun's drawing
structure first.** Chamoun supplied dated 1h TradingView screenshots — 7 structures with date axes after
an initial undated batch. Gated anchor identity against the recurrence ambiguity (each anchor price
recurs 11–54× over 60–800 days; the dates resolved the instance) — **origins pinned to the exact candle**,
"0" approximate. Non-circular test (neutral ±-bar windows, not his framing): each of his **4 clean DOWN
origins is the #1 most-prominent swing high at a ~3-day (72-bar) scale**; they drop to #2–#4 at ±144 bars
(he passes the higher highs that sit farther away — confirms his own "bägge" answer and pins the scale).

Promoted to [`research/chamoun_structure_engine.py`](../../src/fibengine/research/chamoun_structure_engine.py)
(+9 tests) — `propose_structures(df, pivots, StructureConfig)`; **frozen v1** params (local_scale=72,
min_move=2%, max_horizon=480, min_bars=3), DOWN-only, descriptive proposer. Re-finds all 4 calibration
origins; proposed 115 down-structures over 2024–2026. Chamoun eyeballed a sample → "inte perfekta, men
inte dåliga … snarlikt och träffa rätt är en bra vinst": **acceptance bar = recognizably-similar + right
region**, not tick-exact. Gates green (679 pytest, 74% cov, ruff/format/bounds/wiki). Commit `24a3bb5`.

**Deferred next layers (each its own GO):** "0" sustained-low rule (his Q2 — current a0 takes the lowest
low, so it sits on early spikes), UP-structures, volume/clarity tie-break for near-tie higher wicks.
**Owed:** validate the frozen engine on a few FRESH / held-out structures before trusting beyond n=4.
No edge/PnL. Details: `scratchpad/chamoun_1h_batch2.txt`.

## [2026-06-30] decision | GROW-FACIT 4h — +6 source fibs via screenshot transcription (1 dropped, 1 nudged)

North-star grow-facit on **4h** (the only powered cell), per the 2026-06-30 direction set in
[handoff.md](handoff.md). Chamoun supplied 8 cropped 4h TradingView screenshots, then 5 full-view
re-shots when price-only `n_within_near` snapping proved ambiguous on the cropped set. Flow: read anchor
prices off the on-chart labels (obscured top anchors reconstructed via log-interpolation from the
visible levels, then snapped to the candle extreme) →
[`fib_transcribe`](../../src/fibengine/labeling/fib_transcribe.py) candidates in
`data/labels/candidates/bitfinex/BTC-USD/4h/` → human review+promote via
[`--review-candidate`](../../src/fibengine/labeling/tool.py) `w`.

**Result: 4h facit 365 → 371 (+6).** Promoted ids `20240223T120000` (50,227→73,666), `20240501T160000`
(56,711→65,628), `20251006T160000` (103,332→126,110, all-time-high top, `n_within_near=1`),
`20251102T120000` (99,129→111,360), `20260114T200000` (60,060→97,850), `20260202T160000`
(60,100→79,408). All `created_by=human`, `source=manual_screenshot_transcription_reviewed`.

**Two review-step saves (why the human gate matters):** (1) candidate **C** (~108,100/66,880, 2024-11→12,
`n_within_near=38`) was **dropped** — too ambiguous to confirm against the drawing; its candidate removed
so the set matches facit. (2) candidate **E** snapped the low to 2024-05-01 **12:00**; Chamoun **nudged**
it to **16:00** at review (the near=23 heuristic bar was one candle off). The full-view re-shots also
corrected a transcription error the cropped guess made (a swing first placed in 2026 is really **Feb–Mar
2024**), and replaced a reconstructed ~122,670 top with the true all-time-high **126,110**.

**Discipline:** frozen 4h cache (no `data.fetch --refresh`; every anchor is a historical extreme
2024-05→2026-02, none in the live ~63k tail). Transcription is an ingestion aid, **never** auto-fib —
the human supplies both prices and confirms every bar; the tool refuses `human_fib/` writes. 6
pre-review candidates kept as audit trail (E's is the pre-nudge 12:00 version). Gates green
(ruff/format/bounds/wiki-lint; pytest skipped — no `*.py` changed). Screenshots stayed in-chat (not
committed); provenance rests on each candidate's `_transcription` audit block.

## [2026-06-30] decision | checkpoint reminder hook wired — early ~25% ping (UserPromptSubmit)

Resolves the `ACTION for another agent` below (thread-health drift / invocation gap, same date). Built
[`pre-compact-checkpoint.sh`](../../.claude/hooks/pre-compact-checkpoint.sh) + a `UserPromptSubmit` hook
in [`settings.json`](../../.claude/settings.json) (`db439c1`): reads the transcript's latest usage
(`input + cache_read + cache_creation` = real tokens sent — the `/context` figure) and auto-injects one
reminder when context crosses **~25% of a 1M window (250k, tunable `CONTEXT_THRESHOLD`)** — the owner's
chosen sweet spot, *in time* before drift/compaction lose detail. Fires **once per session**; a reminder
only (never invokes the skill). **The late `PreCompact` event was rejected** — it fires only at
compaction, too late for the sweet spot. Live-fired in-session at ~35%. Pure bash + perl, `exit 0`
(SONAR-safe). Skill "When to act" + "Future option" updated to match.

## [2026-06-30] maintenance | thread-health drift observed + checkpoint-invocation gap (ACTION for another agent)

**Observed (this session, live):** the conversation drifted across ~7 topic switches (owner interview →
script adaptation → pre-compact skill → grow-facit → transcription → review loop → token accounting →
skill refinement) while the context window sat at only ~26% (`/context`: 263k/1M). That is a textbook
**early thread-health** case — *lost-in-the-middle*, *recency bias*, *context rot* — which is **invisible
in `/context`** and arrives **well before** the capacity bands.

**The gap (why this matters):** the [`pre-compact-checkpoint`](../../.claude/skills/pre-compact-checkpoint/SKILL.md)
skill's only triggers today are (1) **model discretion** (the agent invokes it when its description
matches) and (2) the manual `/pre-compact-checkpoint` command. (1) **failed here** — the agent expected
to notice the drift *is* the drifting agent (self-defeating); there is **no automatic trigger**. A
`PreCompact` hook does **not** fix this: it fires only at compaction (the late ~90% *capacity* case),
and hooks are shell commands that can only **inject a reminder**, never *invoke* a model skill.

**ACTION (for another agent — pure tooling, no research-code/conclusion change):** add hook-driven
reminders in [`.claude/settings.json`](../../.claude/settings.json) (versioned, travels via git):
1. **Early trigger (the observed case):** a `UserPromptSubmit` (or `PostToolUse`) hook that, after **N
   user turns or M tool-calls**, injects a reminder to consider `/pre-compact-checkpoint`. Caveat:
   turn/tool count is a **proxy**, not a thread-health *measurement* — present it as a reliable nudge,
   not a metric.
2. **Late trigger (capacity):** a `PreCompact` hook that injects a reminder to run the checkpoint (six
   sections → [handoff.md](handoff.md)) before compaction summarises.

**Constraints/acceptance:** hooks only *remind*, never invoke a skill — say so in the nudge text;
thread-health is qualitative — never claim it is auto-measured; keep nudges non-spammy (cooldown / once
per threshold; verify no spurious firing); flip the skill's "Future option" note from *deferred* to
*done* with the chosen design once wired.

## [2026-06-30] decision | labeling tool: `--review-candidate` promote mode (transcription → facit)

Built the missing candidate→facit promote path so screenshot-transcribed daily fibs can become
human-reviewed facit. New `--review-candidate <path>` mode in
[`labeling/tool.py`](../../src/fibengine/labeling/tool.py) reuses the `--edit-fib-id` single-fib
machinery: loads a candidate's anchors (read-only), shows a scrutiny banner flagging the guessed
bars (`n_within_near>1`) / `near` matches, and on `w` saves to `human_fib` as facit. **Provenance is
preserved, not erased** (leakage-validity review): selection is human → `created_by="human"`, but
`source="manual_screenshot_transcription_reviewed"` records the method (still contains `"manual"` so
the source-fib-map guards accept it; avoids the `candidate`/`auto`/`inferred` forbidden tokens). The
candidate JSON (with `_transcription` audit incl. `n_within_near`) travels via git. Overwrite of an
existing facit needs a second `w` (confirm guard). Fail-closed: refuses non-candidate files. +7 tests
([`test_review_candidate_mode.py`](../../tests/labeling/test_review_candidate_mode.py)). Gates green
(669 pytest, 74% cov). Drives north-star **grow-facit**: daily facit had **no** 2025–26 fibs; the two
2026-06-29 chamoun screenshots fill that gap (5 candidates transcribed, all anchor-prices exact).

## [2026-06-30] maintenance | new `pre-compact-checkpoint` skill (adapted to this repo)

Added skill [`.claude/skills/pre-compact-checkpoint/SKILL.md`](../../.claude/skills/pre-compact-checkpoint/SKILL.md)
— captures the verified frontier (Observed/Inferred/Unverified + repo state + user constraints + next
smallest safe step) before context compaction. Adapted from a shared script: paths point to this
repo's [handoff.md](handoff.md) / [log.md](log.md) / [owner-preferences.md](owner-preferences.md),
honesty ladder tied to AGENTS.md *Facts vs assumptions*, and a SONAR-economy note (reuse the last
green `/run-gates`; don't re-run gates per checkpoint). Distinct from `/prepare-home-computer`
(cross-machine) — this is in-session, pre-compaction.

## [2026-06-30] maintenance | owner interview — preferences captured + `/owner-interview` command

Ran a button-driven owner interview (no research-code/conclusion change). Two coupled additions:
**(1)** new versioned command [`/owner-interview`](../../.claude/commands/owner-interview.md) — the
shared interview script adapted to this repo (`[[…]]` → markdown links, persist target = git-synced
wiki, wiki-lint orphan-awareness, guardrail that working-style never overrides
[AGENTS.md](../../AGENTS.md)/validity). **(2)** new synced page
[owner-preferences.md](owner-preferences.md), linked from [index.md](index.md).

Changes vs prior run: tech-pull broadened (+ Architecture/AI); success sharpened to **live
Trader-agent only**; "frontend" redefined as the **labeling tool** (his real fib-drawing surface),
not a separate app; *teach-me-as-we-go* added; **all four** frictions checked (bottleneck · too much
text · things-break · unclear-what-changed) → run autonomously but always leave a short readable trail
of what changed + that gates are green. Forks: recommendation-first + `AskUserQuestion`, **no
shortcuts** (simple path only if significantly more value).

## [2026-06-29] decision | LOCK leg-agreement ruler prereg (north-star step 1 measurement)

Locked the **measurement instrument** for "does X improve human-like leg selection vs facit" — the
free facit-checker the selection campaign lacked (in #38 `agreement` floored for both arms;
`compare_label`/`select_swing` not localized to the facit leg). **Ruler only**; the learned selector
is a separate later prereg. Knobs fixed by selector-independent **pre-lock calibration** (not guessed):
`leg_agreement = mean(s_high, s_low)`, `s = max(0, 1 − Δbar/W)`, absolute **W=2**, direction-gated.
Calibration (`scratchpad/calibrate_leg_agreement_ruler.py`, seed 20260629; 365 4h facit legs, 7215
fractal pivots): inter-pivot spacing median **2.0 bars** → W must stay below it; **W=5 rejected**
despite higher AUC (neighbour-matching leniency); at the spacing-safe W=2 only `mean` clears
**AUC(ceiling vs null) ≥ 0.90** (0.968). Gate rests on [synthetic sanity] + [ceiling-vs-null AUC];
reference selector = descriptive colour only (resolves the ruler-broken-vs-selector-bad confound).
Build of `evaluation/leg_agreement.py` authorized under the lock — descriptive, step-1, no edge/OOS.
[Prereg](reviews/btc-fib-leg-agreement-ruler-prereg-20260629.md) /
[postlock](reviews/btc-fib-leg-agreement-ruler-prereg-20260629-postlock.md).

## [2026-06-29] maintenance | `.claude/` portability + locked-prereg guard + command source flip

Tooling/process work (no research-code or conclusion change). Three coupled changes:

1. **`.claude/` is now versioned-portable.** The blanket `.claude/` gitignore + `POLLUTION_GLOBS`
   entry were narrowed to **`.claude/settings.local.json`** only; shared parts (`commands/`, `hooks/`,
   `settings.json`) travel via git across machines (home/work/web). Stale machine-perms were dropped,
   not migrated. Updated: `.gitignore`, [`check_repo_bounds.py`](../../scripts/check_repo_bounds.py)
   (`POLLUTION_GLOBS`), [CLAUDE.md](../../CLAUDE.md), [AGENTS.md](../../AGENTS.md) §2 table,
   [source-authority.md](reference/source-authority.md), [layout-policy](../../repository-layout-policy.md) §2.
2. **Locked pre-registration discipline + guard.** On human sign-off a prereg gets the
   `<!-- prereg:locked -->` sentinel and becomes immutable; all post-lock material moves to a
   `*-postlock.md` sibling. A `PreToolUse` hook
   ([`.claude/hooks/guard-locked-prereg.sh`](../../.claude/hooks/guard-locked-prereg.sh), perl/JSON::PP,
   Git-Bash → SONAR-safe) **asks** before any Edit/Write to a sentinel-bearing file (fail-open if
   unlocked, fail-closed on grep error). Registered in `.claude/settings.json` (`shell:"bash"`).
   Carried as a binding rule in AGENTS.md *Research easy, authority hard*. First applied to the #38
   prereg (split into `…-prereg-20260629.md` + `…-postlock.md`). Note: a mid-session hook is inactive
   until the next Claude Code restart.
3. **Command playbooks: source-of-truth flipped to `.claude/commands/`.** The 2026-06-22 decision
   placed playbooks in `docs/agent/commands/` *because* `.claude/` was local-only; with `.claude/` now
   portable that premise is **superseded**. The 4 duplicate `.md` were removed from
   `docs/agent/commands/` (kept: README as pointer), `chamoun-fib-style-distiller.md` moved into
   `.claude/commands/`, and the `cp`-mirror ceremony retired. Decision doc carries a SUPERSEDED banner;
   `index.md` updated.

**Pre-existing, NOT fixed here (flag):** [layout-policy](../../repository-layout-policy.md) §6 size
table has drifted from `check_repo_bounds.py` (e.g. log.md 500/28K in policy vs 1500/120K in code) —
separate source-wins cleanup. `handoff.md` is also 415 lines (>400 cap) — pre-existing breach.

## [2026-06-29] review | #38 daily wick-pair anchor accuracy — clean NULL (awaiting sign-off)

Pre-reg [locked 2026-06-29](reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md) (build scope =
A/B **selector** only, post-lock addendum A1; eval-infra diff in A2). Question: does a daily
**wick-pair** A/B selector recover the human's `anchor_a`/`anchor_b` **at least as well** as the
existing pivot control? Descriptive only — **no edge/OOS/PnL claim**; small-N (N=71) reported.

**Result (`experiments/results/chamoun_wick_pair_accuracy.jsonl`, wick_frac=0.5 a priori, k=3, N=71):**

| metric | control (pivot) | wick-pair |
|---|---|---|
| coverage `both_hit` | **0.90** | **0.08** |
| mean agreement | 0.078 | 0.006 |
| pairs selected | 32/71 | 44/71 |

→ **`wick_pair_no_better`** (locked decision rule, one-shot, no redefinition). Coverage **and**
agreement are far below the control, so the wick-pair detection philosophy is **not justified on
daily**; **#31's fractal line remains the candidate** anchor-detection approach. The selector +
candidate universe live in [`strategies/chamoun_daily_wick_pair.py`](../../src/fibengine/strategies/chamoun_daily_wick_pair.py);
the run harness in [`research/chamoun_wick_pair_accuracy.py`](../../src/fibengine/research/chamoun_wick_pair_accuracy.py).

**Why it failed (honest read):** the wick universe is **not** sparse — the selector picked a pair in
**44/71** cases, yet coverage is 0.08. So the dominant-wick pivots sit at **different bars** than the
human's anchors ("detector found nothing" is ruled out). The `wick_frac=0.5` filter requires the
swing extreme to sit on a candle whose rejection wick is ≥ half the range; the human's daily anchors
are mostly **not** such candles. The sonde's earlier "94% on the wick extreme" meant the price sits
on bar high/low (tool snap), **not** that the candle has a long wick.

**What is falsified (scope — calibrated):** this cleanly falsifies the **strong form** — *"the
human's daily anchors sit on ≥50%-range rejection-wick candles"* — at the a-priori threshold. It says
**little about the weak/rank form** (*"wick geometry helps rank among candidates"*): `agreement` is
floor-level for **both** arms (control's `select_swing` is non-localized), and a coverage gate
structurally favors the 811-pivot control over any restrictive filter. Rank-form **left open** for a
separately-registered `wick_frac` sweep.

**Honesty caveats (binding):**
- `wick_frac=0.5` set **a priori**, **not** re-tuned against facit (that would be redefinition). The
  sensitivity sweep is a *separate, newly-registered* probe, not a rescue.
- `agreement` near-floor for **both** arms (control mean 0.078, median 0.0) → **coverage is the
  meaningful discriminator**, and it is unambiguous (0.90 vs 0.08).
- **Locked baselines not fully run** (prereg addendum A4): control ran in **window mode only**;
  `fractal` mode + the **trivial floor** were **not** executed. Moot for a null (wick lost to the
  *more-permissive* window control; floor only contextualizes a positive) — **required before any
  positive claim**. Flagged, not silently omitted.
- Daily is data-thin (N=71); descriptive accuracy, not a powered/OOS claim.

**Status:** run output — **awaiting human sign-off** before it becomes "truth" (per the locked gate).

## [2026-06-26] review | Nesting REFRAME (within-TF, not cross-TF) + two honest nulls

Session headline is **not** a feature win — it is a **corrected model of how the human selects**:
he decomposes a single trend into **successive impulse legs on the SAME timeframe**, he does **not**
nest a parent-TF swing into the child TF. Established from facit screenshots (user-supplied): each
chosen leg's endpoint **extends** the trend (breaks the prior extreme) and its start is the
**retracement extreme**; multiple fibs step down a trend in sequence. Anchor convention verified
against source JSON (both dirs): `anchor_b` = ratio-0 = later-in-time = endpoint; `anchor_a` =
ratio-1 = retracement extreme.

Two pre-registered tests, both **NULL**, both leakage-disciplined (no redefinition after results):

1. **Cross-TF nesting prediction (1w→1d) — NULL, directional, N=9.**
   [Prereg](reviews/btc-fib-nesting-prediction-prereg-1w1d-20260626.md). Question: does 1w parent
   context predict the blind 1d leg beyond prominence? Cohort v2 (`ed98dc4`) was **disqualified**
   (drawn with parent markers visible → leakage by construction); only the **frozen** corpus is
   blind. **Method was re-locked before any run:** a feasibility count showed the first locked method
   (temporal split + logreg + cluster bootstrap) returns **null by construction** (all 42 positives
   pre-split, test positives = 0), so it was retracted and replaced — *before* seeing any result —
   with a within-window **rank** test (per window: does `parent_alignment` rank the human's actual 1d
   pick above `prominence`? paired sign test over the 9 windows with a reachable pick). Degeneracy
   gate PASSED first (alignment ≠ most-prominent in 9/10 reconstructible windows). Result: **6/9
   positive, median d_w +0.067, sign-test p=0.51** → `no_parent_context_signal`. The two data-richest
   windows (2017/2020 bull, 10+11 legs) ran *strongest against* H1 — the human picked prominent legs
   that do **not** reconstruct the 1w parent. So the cross-TF axis was simply the wrong model (see
   reframe above); the null is the *right* answer, not a setback. `scratchpad/nesting_rank_test.py`,
   summary `experiments/review/fib_nesting_prediction/summary.json` (gitignored).

2. **`impulse_leg` feature enrichment (4h) — clean NULL, POWERED.**
   [Prereg](reviews/btc-fib-impulse-leg-feature-prereg-20260626.md). The within-TF axis operationalized
   as a leg-aware, leakage-free feature: `impulse_leg = (endpoint_BOS + start_dominance)/2`
   (endpoint breaks prior same-kind extreme; start is the dominant opposite swing in the retracement
   zone). Pre-lock sonder (train-only, do not touch target): orthogonal to the baseline it must beat
   (corr prominence +0.19, magnitude +0.08, cleanliness +0.36, structure_alignment +0.14 — all <0.5),
   and leg-aware on **5132/5132** multi-start endpoints (solves the within-decision-point blindness
   that gave `structure_alignment` ~0 weight). Run = enrichment harness mirrored verbatim (per-endpoint
   causal truncate at `anchor_b+k`, nested AP-lift vs full Stage-2, decision-point cluster bootstrap),
   4h k=3, powered (65 test-pos). **AP 0.0567→0.0619, lift +0.0052, bootstrap CI [−0.032, +0.027]
   straddles 0, p=0.34 → `impulse_leg_no_signal`.** Verdict is final; the per-leg-feature line stays
   closed. **Framing (advisor, binding):** the +0.119 model weight is the *in-sample* association the
   OOS test just refuted — it is **not** independent evidence and must not be cited as "plausibly
   informative" (that double-counts what the test threw out). Honest reading = "consistent with no
   effect at this power," **not** "a likely-real effect we couldn't confirm." One firewalled factual
   difference from `exclusivity`: this is a **clean** null (CI straddles 0), not `enriched_worse` (CI
   excluded 0 below) — recorded only as forward-pointer hypothesis (*if test-positives ever grow, the
   feature most worth re-testing*), **never** as a finding. `scratchpad/impulse_enrich.py`, summary
   `experiments/review/fib_impulse_leg/summary.json` (gitignored).

**Side diagnostic — HTF is intrinsically data-starved, not detector-broken.** Reachability per TF
(can the candidate universe even produce the human's legs?): 1M **1.00**, 1w 0.88, 1d 0.87, 4h 0.85,
**no epoch gaps**. So 1M/1w underpowered = too few swings exist (1M has 13 legs total), **not** a
candidate-gen crux — no detector/feature fix buys power there; top-down-on-HTF is data-starved by
nature. Powered selection signal lives on **4h** (N=365). `scratchpad/reachability_diag.py`.

Net for the day: two honest nulls + a corrected process model, no p-hacking, no leakage survived.
Durable win = the within-TF reframe (stands on the facit images regardless of either run).

## [2026-06-26] decision | Top-down nesting — tool support built, cohort v2 drawn + committed

After deleting v1 (entry below), built the tool support nesting actually needed, then redrew. Three
additions to `htf_fib_overlay.py` + `tool.py`, all behind pure helpers (+7 tests, suite 619 green):
- **anchor markers** (`htf_anchor_markers`, `f79d7d2`): each parent fib's H/L as hollow diamonds at their
  own (time, price) on the child chart — shows *where in time* the parent swing sits, not just price lines.
- **session-only overlay** (`filter_to_session`, `3f3dc05`): HTF overlays default to fibs drawn THIS
  session, so the frozen corpus (9 1M + 21 1w) does not clutter the child chart; `b` toggles frozen back
  on. `session_fib_ids` persists across TF switches so a 1M draw stays visible on 1w/1d.
- **nesting focus** (`c`, `3f3dc05`): cycle parent fibs overlapping the current view, show only that
  parent's H/L and fit the view to it (new `redraw(set_view=...)` param; advisor caught that the naive
  version would no-op the zoom).

Workflow now: draw on 1M, `w`/`s`; drop to 1w/1d and your own 1M/1w lines follow down, clean. User redrew
**cohort v2** (`ed98dc4`): 12 nested `human_fib` (1M/1w/1d × four eras — 2017 bull, 2017-18 bear, 2019,
2020-21), consistently nested per era (unlike v1's wrong-candle anchors), schema 12/12 PASS.

**fib_id collision (resolved, user kept new):** the new 2017-bull 1w starts 2017-03-16, same as a frozen
`1w_20170316` (a short 2017-03→05 swing, top 2444.9), so it replaced that frozen file. Frozen corpus is
otherwise intact but **no longer 100% the analysed set** — and the shared namespace (filename = TF +
start date) means nesting swings starting on a frozen swing's date will clash again. If frequent, build a
separate nesting namespace. Layer-A swing-labels left untracked. Still gated: `RESOLUTION_TIMEFRAME`
1M→1w prereq + explicit GO before any model/run.

## [2026-06-26] decision | Top-down nesting — tool fix (parent anchor markers) + cohort deleted (clean slate)

Reviewing the first nested cohort (entry below) against candle data showed several child-TF anchors on
the WRONG candle: `1w_20180614` had its low on 2018-06 (6560) instead of the 2020-09 bottom (~9882 on
1M/1d, 10010 on the 1w candle), and `1d_20181215` used the dec-2018 low (3215) while 1M/1w used the
jan-2019 low (3405). Root cause: the labeling tool's HTF overlay drew only higher-TF *price* lines, so
when switching down to 1w/1d you could not see *where in time* the 1M H/L sat — near-in-price bottoms
were easy to confuse.

Fix (`f79d7d2`): new `htf_anchor_markers()` in `htf_fib_overlay.py` draws each parent fib's H/L as hollow
diamonds at their own (time, price) on the child chart (only anchors inside the visible window), toggled
with the existing `f`. +3 pure-helper tests; full suite 615 green, cov 74%. Doc note: anchors are
TF-specific candles, so "same swing" gives slightly different prices per TF (9882 vs 10010) — expected.

Then, at the user's request, deleted the entire cohort for a clean redraw (`879b754`): the 8 committed
nesting fibs + untracked extras + Layer-A swing-labels removed; frozen `1M_20211101` (timestamp-touched
today) restored. Verified `human_fib` is now bit-identical to frozen `f0f4b8d` (1M=9, 1w=21, 1d=67,
4h=365). Next: user redraws nested labels with the markers on; `RESOLUTION_TIMEFRAME` 1M→1w prereq and
the explicit GO still gate any model/run.

## [2026-06-26] review | Top-down nesting — first nested facit cohort drawn + committed

User opened the labeling tool on BTC/USD 1M (preflight: 1M/1w/1d/4h cache OK; 1h still deferred, no
cache) and drew the first deliberately-nested labels for the top-down line: the SAME swing decomposed
1M→1w→1d over three eras — 2017-18 (down), 2019 (up), 2020-21 (up). **8 new `human_fib` annotations**
committed as a SEPARATE cohort (`b9a7aa2`, 8 files / +376 lines), deliberately kept apart from the
frozen 1M/1w/1d/4h source-fib corpus — new nesting data, **not** a corpus revision.

Schema/integrity 9/9 PASS via a one-off check that loads each file through `load_annotation` and
verifies: `scale_mode=log`, profile `tradingview_log_chamoun`, ratio-set `{0,0.382,0.5,0.618,0.786,1}`
(no 0.236), levels equal the log-interpolation of the anchors, and `direction` consistent with anchors.

Hygiene: a timestamp-only re-save of the frozen `1w_20171214` (geometry unchanged) was reverted with
explicit user confirmation, so the locked corpus stays bit-identical. Layer-A swing-labels under
`data/labels/bitfinex/` were left untracked — incomplete by-product (only the last active swing per TF).

Watch item (open, user to confirm): `1w_20180614` is an up-leg 6560→64829 spanning 2018→2021; it does
not nest as cleanly per-era as the other pairs (possible deliberate parent swing or a stray multi-leg).

**Still gated:** no model/build/run on this cohort. The `RESOLUTION_TIMEFRAME` 1M→1w prerequisite
(`same_candle_mtf_resolution` covers only 1w→1d) and the separate explicit GO both remain.

## [2026-06-25] maintenance | Status sweep — research-line status registry + stale-index fix

Semantic-lint pass (stale docs / status drift). Finding: `index.md` and `reviews/README.md` had not
kept up with the whole selection-learning arc (06-17→06-25) — `index.md` Reviews section pointed only
to "superseded", `reviews/README.md` was titled "(superseded)" yet omitted selection-learning,
behaviour/horizontal nulls, MTF-confluence, and Genesis-V2 docs; no status overview existed. Created
[reference/research-line-status.md](reference/research-line-status.md) — one row per LINE with status
(active / pending-input / complete / closed / parked / dormant / superseded) + open issues; linked it
from `index.md` (Wiki Operations + Reviews) and added a status banner to `reviews/README.md`. Issue
state confirmed via `gh`: only **#31** (fractal anchor detection — now relevant, user resumes with new
fibs next day) and **#37** were open. **#37 verified a verbatim duplicate of closed #35** (byte-identical
body; #35 closed with "Done — principle added to AGENTS.md commit 27232cb"; principle present at
AGENTS.md) → **closed #37** as a stale tracking dup. Also created root **[/STATUS.md](../../STATUS.md)**
(at-a-glance snapshot pointing to the registry). Docs-only, no code, no claim change.

## [2026-06-25] review | Top-down MTF nesting premise check → facit does NOT nest (different eras)

User reframed toward a top-down "sniper" idea: model the SAME swing decomposed 1M→1W→1D (parent TF as
the relational context that makes a leg "yours"), a few deliberately-nested labels instead of hundreds
of flat ones — operationalizing "context, not geometry" (`duration` & `magnitude` both ~0 weight;
candle-count A→B median 5, range 1–272). Cheap premise check on frozen facit (descriptive, no lock):
strict nesting (child swing within parent A→B window) = **1W-in-1M 5%** (1 of 21), **1D-in-1W 46%**
(price 85%), 1D-in-1M 25%. Date-range check (advisor-prompted) is decisive: the TFs are **different
eras** — 1W anchors mostly 2017–18, 1M anchors 2020+; they barely overlap. So the corpus was never
drawn as nested decompositions and CANNOT test the idea; pursuing it needs **new deliberately-nested
labels on ONE era** (user redraws LATER, not today), not re-analysis of these 97 HTF legs. Secondary:
the labeling tool's `same_candle_mtf_resolution` (flag ON) resolves 1w→1d anchors to the exact day but
has **no 1M→1w entry**, so monthly anchors stay coarse (whole month) — the user's felt imprecision;
must extend `RESOLUTION_TIMEFRAME` before the redraw. Also recorded: **matched-null crux REJECTED**
(artifact LOCK A8 trigger not met / A11 asymmetric-weak / A9 out-of-scope). Descriptive only, no claim,
no code.

## [2026-06-25] review | Learning-curve diagnostic RUN → marginally `saturated` (4h k=3)

Blind Commit-2 of the [learning-curve LOCK](reviews/btc-fib-selection-learning-learning-curve-lock-20260625.md)
(harness `c4bd330`, seed 20260618, frozen-data parity, preflight READY). **Parity OK:** `ap_full_facit`
(4h k=3) = 0.0567 = Stage-2 headline, n_test_pos=65, n_train_legs=246. Curve (mean AP over R=64
train-subsamples): 0.0501 → 0.0522 → 0.0541 → 0.0545 → 0.0551 → 0.0560 → 0.0567 at
f=0.25/.5/.75/.8/.9/.95/1.0. **Verdict `saturated` — but marginally** (advisor-flagged): means rise
**monotonically**, no clean plateau; the label rests only on the last 5 % increment (+0.0008) sitting
inside the tightest f=0.95 band (±0.0030) — "marginal label within noise", not "curve flattened". AUC
flat ~0.914 throughout. Per the locked ASYMMETRIC rule this is **expected** for a ≈1-effective-param
(`cleanliness`-dominated) model → **bottleneck is the feature side, not 4h data**. Honest bound:
grinding more 4h labels is low-leverage *for this model* (and ceiling is low ~0.057), but a
monotone-rising curve does NOT license "never label". Context 1M/1w/1d underpowered (1d shape rising
but 7 test pos, not interpretable). Diagnostic only — no edge/behaviour/PnL/Genesis; does NOT resolve
the cleanliness crux (matched-null A8 still unbuilt). Fork surfaced (crux / A′ / label-anyway) under
handoff Next Step. [Results](reviews/btc-fib-selection-learning-learning-curve-results-20260625.md).

## [2026-06-25] decision | Learning-curve diagnostic LOCKED (Commit 1, docs-only); awaiting GO

User picked "learning curve first" as the next step toward [north-star](north-star.md) step 1 (does
the engine select like the human). Lean blind lock for a cheap data-sensitivity shot: is the Stage-2
model **data-starved or saturated** w.r.t. facit size? Reuses Stage-2 verbatim, fixes the held-out
test set, varies only the **training-facit fraction** (whole human legs dropped), build-once-vary-
labels. Advisor-refined before lock: **(1) ASYMMETRIC verdict** — model is ≈1-effective-parameter
(`cleanliness` carries the lift) so saturation is the EXPECTED default; a flat curve means "this
1-feature model is capacity-bound → back to the feature/crux", **NOT** "don't grow facit". (2) finer
grid near f=1.0 + R=64 (build is once, relabel+refit is cheap). (3) `inconclusive_underpowered` is a
LIKELY branch with 65 test positives. (4) report addable-supply (365 labeled vs ~86k candidates;
if starved but little history left → more history/symbols, not grind same chart). Diagnostic only —
no edge/behaviour/PnL/Genesis; does NOT resolve the cleanliness crux. Commit 2 (build/run) needs a
separate explicit GO. [Lock](reviews/btc-fib-selection-learning-learning-curve-lock-20260625.md).

## [2026-06-25] decision | North-star vision documented (canonical [north-star.md](north-star.md))

Docs-only. Captured the user's original intent verbatim: *lär maskinen att se chartet som människan*
— chart → meaningful high/low → rätt leg/range → rita Fib som Chamoun (facit = manuella source-fibs).
Key correction recorded: this is **step 1 of a staged path** whose destination IS an edge / trading-
signal → backtest → **Genesis-V2 integration**. The repo's standing "no edge/behaviour/PnL/backtest/
Genesis claim" is therefore a **validity gate** ("not yet / not from this sub-study"), **not** a cap —
it protects the future edge from inheriting a leaked/overfit signal. Selection-learning was NOT the
drift; the drift was the detector-mechanics side-quest inside it. Honest status: step 1 not in goal
(AP 0.057, ranks > chance but no reproduction). Handoff NORTH STAR block re-pointed to the canonical
doc and its "not an edge" lean corrected to the staircase. No code, no claim change.

## [2026-06-25] review | Fib SELECTION-LEARNING model-enrichment RUN → `enriched_worse_check`; line CLOSED

Blind Commit-2 of the [enrichment LOCK](reviews/btc-fib-selection-learning-enrichment-lock-20260624.md)
(Track A; harness `c80acb0`, seed 20260618, frozen-data parity, preflight READY). **Parity gate passed:**
`ap_baseline_stage2` (4h k=3) = **0.056737** = the Stage-2 headline 0.0567, `n_test_pos` = 65, `excl=0`
(every row reconstructs causally, no look-ahead) — the nested baseline IS the current model. Spec note:
the pre-run "n_candidates ≈ 24852" was a label mix-up (24852 = n_test; full universe 86244).

**Verdict (4h primary, powered):** adding causal `exclusivity` *lowers* pooled OOS AP 0.0567→0.0387;
AP-lift −0.018, decision-point cluster bootstrap CI95 **[−0.070, −0.0019]** (excludes 0 below),
p(lift≤0)=0.994 → **`enriched_worse_check`**. Direction-guard checks (parity, excl=0, bootstrap unit,
power) all pass → **not a bug**. Mechanism (Inferred, per E1): `corr(exclusivity, cleanliness)` = 0.80
on train — near-proxy, variance cost on 65 positives. **Per-leg-feature modeling line CLOSED**;
substantive north-star implication = the E8 route (grow the facit). The `enriched_worse_check` branch
is not pre-committed to a direction, so the fork (B = grow facit, recommended; A′ = decorrelated
exclusivity under a NEW lock, low prior) is surfaced to the user — no direction chosen by the agent.
No edge/behaviour/PnL/Genesis/auto-fib claim. Artifacts gitignored.
[Results](reviews/btc-fib-selection-learning-enrichment-results-20260625.md).

## [2026-06-25] maintenance | Consolidated the A/B next-step into a handoff `## Next Step` block

Docs-only. The next step (the enrichment-lock GO-fork: **A** = build/run the `exclusivity` Commit 2,
**B** = grow the facit) was spread across several handoff bullets without one clear record. Added a
single `## Next Step` block (fork + discriminator + recommendation "A first, then B" + "requires
explicit GO"); trimmed the enrichment-lock and checkpoint bullets to absorb it under the 400-line
bound. **No new claim, no code, no direction chosen — GO stays with the user.**

## [2026-06-24] decision | Fib SELECTION-LEARNING — line PAUSED at model-enrichment lock

Checkpoint for the selection-learning side-quest. After the Stage-2 headline (modest single-feature
`cleanliness` lead, 4h), the line ran a chain of **controls** — prominence-family + k-sweep
(`k_stable_live_selection_signal`), W-gap (`no_causal_gap`), Stage-1 per-pivot
(`no_pivot_signal_above_prominence`), the `cleanliness` artifact-probe (inflationary detector-artifact
**unsupported** on 4h; direction guards → investigate), and a descriptive mechanics + snapping-flip pass
(span/duration confound + net-vs-path/candle-granularity). A **main-quest reset** then stopped the
mechanics drift and re-anchored the north star (*learn how the human selects meaningful fib legs/ranges;
facit = truth*) with a binding no-drift guardrail. The single open crux (`cleanliness` genuine vs
artifact) stays **OPEN**.

**Now PAUSED** at the **model-enrichment LOCK** (`bc85a69`, blind Commit-1): one lean shot — does a
single causal **leg-completeness / `exclusivity`** feature raise pooled OOS AP **over the current
Stage-2 model** (nested baseline) on 4h live k=3? Verdict `enrichment_helps` / `no_enrichment_signal →
park modeling + grow facit`; honest prior **low**. **Resume = GO Commit 2 (build/run) or route to
labeling (§E8).** No code started; matched-null/new-universe/Genesis/1H/ETH/refresh all out.
[Enrichment LOCK](reviews/btc-fib-selection-learning-enrichment-lock-20260624.md).

## [2026-06-22] decision | Fib SELECTION-LEARNING retrospective W / causal-availability-gap LOCK (docs-only, gated)

Commit-1 lock for side-quest #1, **blind** (no retrospective model built, no gap value ever
computed). Reuses §A5 pins (4h `W=180`, cells `{0,3,6,12}`, primary `k=3`, pooled AP, ε, §6 family;
`recency` viewport-relative). **New locks:** gap(k) = `AP(retro W) − AP(live k)` on the **identical
live-at-`k` rows** (same-row parity → isolates *feature availability*, not universe size); **common
embargo = `W`** for both models (leakage-safe parity); decision-point cluster bootstrap 2000×, seed
20260618; verdict `no_causal_gap` / `gap_closes_with_buffer` / `gap_persists` / `inconclusive` /
`artifact_check_needed` (4h primary; gap cells `{3,6,12}`, k=0 degenerate-excluded). **Secondary /
sensitivity**, descriptive with CIs — **not** in the Holm headline family, **no** new positive claim.
Non-claims binding: not a reproduction; no edge/behaviour/PnL/Genesis/auto-fib/1H/ETH; cleanliness-
artifact stays open. Execution (Commit 2) needs a **separate explicit GO**.
[Lock doc](reviews/btc-fib-selection-learning-w-gap-lock-20260622.md).

## [2026-06-17] decision | New line pre-registered — Fib SELECTION-LEARNING (docs-only, gated)

A genuinely different question from the closed behaviour/B-1 lines: not "do fib levels repel price"
(closed NULL) but **"can a model reproduce how the human selects swings/ranges"** — selection
learning, labels as facit, **no edge/backtest/Genesis claim**. Target = **Stage 2 leg/range gestalt**
(5 components: scale, pairing, direction, exclusivity, context/HTF; structure first, levels second);
Stage 1 per-pivot = diagnostic floor (Stage 2 ≤ Stage 1 recall). Two viewports — live-equivalent
(`anchor_b+k`) vs **bounded** retrospective (`anchor_b+W`, finite, not omniscient) — and the
**causal-availability gap** attributed per feature-group, `k`-sweep mandatory. Binding
**feature-provenance rule** (every feature tagged left-available/right-edge-sensitive, fail-closed,
structurally enforced). One pre-registered **primary cell** (forking-paths defence) + candidate
**coverage ceiling** (B-1 power-honesty parallel). Docs-only, two-step gate: feature/param addendum
(blind) then separate go. Designed collaboratively with Chamoun (the labeler is facit on his own
process). [Prereg](reviews/btc-fib-selection-learning-prereg-20260617.md). **Next: addendum tomorrow.**

## [2026-06-18] review | Fib SELECTION-LEARNING k-sweep {0,3,6,12} (4h) → k_stable_live_selection_signal

Mandatory confirmation-buffer sweep (addendum §A5), live-only, so the headline `k=3` is not a
forking-paths artifact. **Verdict rule locked before the run:** a `k` cell survives only if powered
**and** its model AP-lift CI excludes 0 vs **every** causally-allowed §6 baseline (the locked
prominence-FAMILY criterion — magnitude + prominence A/B); cross-k verdict
`k_stable_live_selection_signal` iff ≥2 cells survive. Result: **k=0 degenerate** (0 candidates,
`reachable_fraction=0.0`, unpowered — *not interpretable*, excluded); **k=3/6/12 all powered and
survive** (`p_one_sided lift≤0 = 0/2000` throughout; lowest CI floor k=12 vs prom-sum 0.025). 3/3
powered cells survive → **`k_stable_live_selection_signal`**: the lead is not a narrow-buffer
artifact. Modest framing intact — `cleanliness` dominates (~0.20) at every powered k; k=12
`scale_confluence` (~0.13) is a **secondary hint** once causally available, not a second pillar; AP
0.057→0.066 (far under 0.83 ceiling); **single-feature, not a reproduction, no edge/behaviour/Genesis
claim**; 1M/1w/1d underpowered, not refuted. Code+tests committed `ea6c2ea` (ruff/format/bounds/544
pytest green, cov 75.52%); artifacts gitignored/regenerable. Next candidate tracks (NONE started,
separate GO each): retrospective `W`/causal-availability gap; Stage-1 per-pivot diagnostic.
[Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING prominence-baseline sensitivity (4h) → survives_prominence_family

Scoped sensitivity (4h only): does the cleanliness-driven AP-lift survive the stronger §6
prominence baseline? **Both instantiations + the verdict rule locked before the run** (not chosen
after): A = summed endpoint prominence (= `prominence` feature col, rank-equiv to raw sum), B = max
endpoint prominence. Same candidate universe / viewport / `k=3` / ε / purged split / held-fixed
model — only the baseline ranking differs. Decision-point cluster bootstrap (2000×). Result: model
AP-lift robust vs **all three** §6 baselines — magnitude +0.052 [0.023,0.120], prominence-A +0.043
[0.018,0.104], prominence-B +0.049 [0.021,0.116]; every CI excludes 0, 0/2000 ≤ 0. Sanity: both
prominence baselines (0.0138 / 0.0079) beat magnitude (0.0051) as expected; model beats both.
**Pre-committed verdict = `survives_prominence_family`.** Weights unchanged → **`cleanliness` still
carries the lift** (0.20), structure_alignment ≈ 0. So the lead is **not** a magnitude- or
prominence-artifact — but still single-feature, low absolute AP (0.057 vs 0.83 coverage ceiling),
**not a reproduction of human selection, no edge/behaviour claim**; 1M/1w/1d underpowered. Open
interpretive question: is `cleanliness` a detection/anchoring artifact? +1 test (19 total).
[Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING AP-lift inference (4h) → MODEST single-feature lead

Inference slice (scoped: 4h AP-lift only). Decision-point cluster bootstrap (2000 resamples by
`anchor_b` group, model held fixed): lift +0.052, **95% CI [0.023, 0.120] excludes 0**, 0/2000
resamples ≤ 0 — the 4h AP-lift is **robustly positive vs the magnitude baseline, OOS** (a
bootstrap-stability statement, not a permutation-null p). **But** the §10 interpretable weights show
it is **carried almost entirely by `cleanliness`** (std weight 0.20 vs prominence 0.07,
structure_alignment ≈ 0): human-marked legs are *cleaner/more efficient* than magnitude predicts —
a single coherent correlate, **not** a multi-feature reproduction of human selection. Scope limits:
beats **magnitude only** (§6 most-prominent baseline untested; prominence carries weight so the lift
may shrink against it); AP 0.057 capped by 0.83 coverage ceiling (human not reproduced); 1M/1w/1d
**underpowered, not refuted**. **No edge/behaviour claim.** Recommended next (separate go):
prominence-baseline sensitivity on 4h. [Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING Stage-2 headline built + run → POINT ESTIMATE (no claim)

§12.3 go granted. Built `research/selection_learning.py` (+15 tests) and ran the single
pre-registered headline cell (Stage 2, live-equivalent `k=3`, pooled-AP per A5.1). Causal by
construction: features computed on a frame **truncated at `anchor_b+k`** with the `k*≤3` whitelist
(`{magnitude,cleanliness,duration,prominence,structure_alignment}`), candidate universe re-detected
on the truncated frame, ε-match to human legs (A4), purged split (embargo = reach `k`), numpy
logistic regression (zero new deps, §10) vs §6 magnitude baseline. **Only 4h powered** (65 test
pos): AP model 0.057 vs base 0.005 (≈11×, ≈22× base rate), secondary AUC 0.914; AUC≈0.88–0.91 on
1M/1d too (1w 0 test pos). **STATUS: point estimate, inference PENDING** — `lift_pos_powered` is a
flag, not a significance test; no CI/p-value on the AP-lift yet → **no finding claimed**. Next:
inference on the AP-lift resampled by decision point, then k-sweep/W/gap/Stage-1. Artifacts
gitignored. [Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] decision | Fib SELECTION-LEARNING §12 addendum frozen (docs-only, blind)

Step-2 of the two-step gate, blind to output. Reuses the engine's **8 existing interpretable
features** (`core/features.py`) — no new ones — and tags each with a **minimum confirmation buffer
`k*`** (magnitude/cleanliness/duration/round_number=0; prominence/structure_alignment=3;
scale_confluence=12; recency=∞). This refines §5's binary left/right tag: a bare binary + mechanical
exclusion would freeze the live model at every `k`, making the mandatory `k`-sweep (§8) **vacuous**
(advisor catch) — `k*` makes the sweep admit features as the buffer grows, so the causal-availability
gap is empirical not a tagging artifact. `recency` dropped from the live model (dataset-end ref);
exclusivity #4 operationalized set-level over `structure_window=6` base-pivot chunks (`k*=3`, no
parent-degree boundaries); ε **reused** from `EvaluationConfig` (`time_tol=3`, `price_tol=0.5` ATR —
blindness defense). `k`-sweep {0,3,6,12}, `W` per TF (1M=24/1w=52/1d=120/4h=180 bars), **single
primary cell = Stage 2 + live-equivalent + `k=3`** (base detector confirmation), all else secondary.
Pinned to `settings.expansion.yaml`. **Still gated:** §12.3 separate explicit go before any build/run.
[Addendum](reviews/btc-fib-selection-learning-addendum-20260618.md).

## [2026-06-17] review | B-1 horizontal-structure study — RUN, result NULL (§12 go granted)

Built then ran (prereg §12 path (a)). Commits `474f320` (SENARE-1 e-value) → `edcc87c` (slice) →
`92a0cdf` (ROUND); all prereg pins (§4 RW-null, §8 e-value, §3/§4 ROUND) locked **before** the run.
**Result: `any_robust = False`** across all 12 subject×TF cells — no generic horizontal level
(SWING / 1-2-5 ROUND / PRIOR-EXTREME) repels BTC more than its matched random-walk null under the
anytime-valid e-Holm test. Powered cells (N≥30 both sides): swing-4h/1d, prior_extreme-4h, round-4h.
Only SWING shows a directional edge (4h 0.841 vs 0.780) but it is **not even individually marginal**
(e=1.70, p≈0.59); e-Holm needed E≈240 at 12-way multiplicity, so **low power for subtle effects**.
Reject ~0.76–0.84 across **all** sources incl. RW-null = generic mean-reversion / spontaneous RW
structure, not a mechanism. **Extends the closed fib-null** (fib not special vs swing → generic
structure not special vs a random walk). §10 strategy sanity-check **not run**. No trading claim,
no fib JSON read, no label/corpus mutation; artifact gitignored.
[Results](reviews/btc-horizontal-structure-event-study-results-20260617.md) ·
[prereg](reviews/btc-horizontal-structure-event-study-prereg-20260617.md).

## [2026-06-17] maintenance | S-3: viz/plot.py routed through shared candle helper

`viz/plot.py:plot_prediction` drew its own black close-line; it now routes through the shared
`research/human_review_candles.draw_review_candles` (same palette/path as the review charts). New
keyword args `candlestick=False` (default — close-line, needs only `close`) / `dark_theme`;
`candlestick=True` renders mplfinance candles (needs full OHLCV), so the function finally matches
its "plotta candles" docstring. **No layering inversion:** `plot.py` already imports
`labeling.store`, so it is application-tier like `labeling/tool.py` (which imports the same helper).
Parametrised test added (both paths render a non-empty PNG); ruff + 486 pytest (`viz/plot.py` 100 %)
+ bounds green. SENARE-3 done. Working-tree only (not committed).

## [2026-06-17] decision | B-1 horizontal-structure study pre-registered (docs-only, gated)

Post-fib-null follow-up registered, **not run**:
[btc-horizontal-structure-event-study-prereg-20260617.md](reviews/btc-horizontal-structure-event-study-prereg-20260617.md).
Question: do *generic* horizontal levels (swing / 1-2-5 round ladder / prior-period extremes) repel
BTC more than a matched **random-walk null** (`synthetic_baseline` — the unseen quantity that makes
the question legitimate post-fib-null)? Shuffle-placebo demoted to descriptive (already seen).
Satisfies NU-1..NU-3; as the **3rd look at the same OOS window**, execution **requires** anytime-
valid inference (e-values / e-Holm = SENARE-1, unbuilt), so a fixed-horizon permutation is
forbidden here. Unblock: (a) build SENARE-1 + wire DELAR-1, or (b) fresh data. All subject
parameters frozen in the prereg before any result.

## [2026-06-17] maintenance | feature/research-fib promoted to main; PR review fixes + dep bump

Branch promoted to `main` via **PR #33** (89-commit fast-forward; **merge-commit** to keep the
wiki's commit-hash citations valid — squash/rebase would have orphaned them). Two PR-review
fixes (Codex) landed on the branch first:
- **P1** (`labeling/tool.py`): a windowed editing session now keeps out-of-window legs in memory
  and merges them on save — pressing `s` no longer silently deletes saved legs (facit-safety).
- **P2** (`research/level_events.py` + `human_review_rows.py`): level-event detection now threads
  `fib.scale_mode` (= **log** per protocol) instead of defaulting to linear, so level-event
  prices/rows match the log charts. **Behaviour change:** older level-event outputs were linear;
  new ones are log.

**PR #34** (security): bumped `cryptography` 48.0.0 → 49.0.0 (Dependabot `GHSA-537c-gmf6-5ccf`,
High — vulnerable OpenSSL in wheels; transitive via ccxt, no upper bound). Lockfile-only;
ccxt imports clean, gates green. Dependabot alert auto-closed.

## [2026-06-17] decision | Standing prereg addendum for future horizontal-structure studies

NU block of the external pattern scan, docs-only:
[horizontal-structure-prereg-addendum-20260617.md](reviews/horizontal-structure-prereg-addendum-20260617.md)
(NU-1 random-walk control; NU-2 anytime-valid/e-Holm re-looks; NU-3 name embargo as purged-CV).
DELAR-1/2/3 since implemented (commits `ca5ae73`/`0b380e6`/`7b03837`): synthetic random-walk
baseline (`research/synthetic_baseline.py`), uncertainty-ordered labeling worklist
(`labeling/worklist.py --by-uncertainty`), fail-closed swing-label JSON validation
(`validation/schemas.py`). SENARE still gated (`clever-yawning-catmull.md`).

## [2026-06-16] decision | BTC/Fib behaviour/backtest line — PAUSED / CLOSED (reviewed PASS)

Commit `f4e96f1` reviewed **PASS / CLOSED**. Final conclusion across both pre-registered studies:
unconditioned Behaviour Event Study = **no signal**; Context-Conditioned Study = **no candidate**.
**Fib does not beat the placebo/swing baselines** on the current BTC corpus; the **swing baseline
matches or beats fib**, so the weak level reaction is **generic horizontal structure, not
Fibonacci-specific**. Strategy sanity-check **not authorised / not run**. The BTC/Fib
behaviour/backtest line is **paused/closed**. **Discipline:** do **not** re-run these studies on the
same BTC data with tweaked parameters; any future behaviour test must be a **new prereg on fresh
data** or a **materially different question**; **no active next implementation is authorised**.
Future possible tracks (listed only, none started): fresh-data validation on other symbols/TFs
(new prereg); source-label quality / correction-candidate cleanup; non-fib horizontal-structure
research; separate visual/research tooling; Genesis/Fib remains paused unless explicitly reopened.

## [2026-06-16] review | BTC/Fib Context-Conditioned Study — NO CANDIDATE (reviewed PASS / CLOSED)

Second Lean Fib question, opened after the unconditioned null: do fib levels react differently
than placebo/swing **only in specific causal contexts**? Advisor flagged the prior `reject_rate`
as saturated → switched primary to a **continuous** metric `reaction_asym_atr = MFE−MAE`,
rank-permutation test, **Holm** across K=2 frozen confirmatory contexts (**trend regime**, **deep
0.618/0.786**), MDE pre-registered, confirmatory TF=4h. Disclosed second-look (same OOS window
reused; power pre-flight peeked) → train-sign is the guard, ceiling = candidate not confirmation.
**Result: no confirmatory context passes.** Fib beats *random placebo* in the predicted direction
(trend gap +0.64, deep +0.46 ATR; train-sign consistent) but only **nominally** (p=0.042/0.056,
**fails Holm**) and **never beats the swing baseline** (swing reacts ≥ fib in both). Gaps ≪ MDE
(~1.3–1.9). 1d underpowered (N<30, train sign flips). Insight: faint level-reaction = generic
horizontal structure, not Fibonacci. Gate fails → **no strategy work.** New
`research/fib_context_conditioned_study.py` (17 tests), reuses the event-study engine; artifact
gitignored. No Genesis/1H/ML/export/label change.
[Prereg](reviews/btc-fib-context-conditioned-study-prereg-20260616.md) /
[results](reviews/btc-fib-context-conditioned-study-results-20260616.md).

## [2026-06-16] review | BTC/Fib Behaviour Event Study — NO SIGNAL (reviewed PASS / CLOSED)

First Lean Fib Research question, run end-to-end. Causal event study on the locked corpus
(1M/1w/1d/4h, no 1H): fresh touches of causally-known fib **interior retracements** vs two
baselines — **matched deterministic placebo** (same count/time, random causal-range price) and
**causal fractal swing** highs/lows. OOS 70/30 + embargo; permutation test on test-window
reject_rate. **Result: fib levels are not measurably different from placebo/swing.** At the only
powered TF (4h, N≥138/source) fib reject 0.78 ≈ placebo 0.80 ≈ swing 0.84 (p=0.63/0.19); 1d
nominal-only (not sig, N<30); 1w/1M too sparse (N≤2). High ~0.8 reject across *all* sources =
generic mean-reversion, not a fib property. Gate fails on every TF →
**strategy sanity-check NOT run** (Phase 0 §8 placebo stop). Code
`fib_behaviour_event_study.py` (19 tests); artifact gitignored. No Genesis/1H/ML/export/label
change. [Prereg](reviews/btc-fib-behaviour-event-study-prereg-20260616.md) /
[results](reviews/btc-fib-behaviour-event-study-results-20260616.md).

## [2026-06-16] decision | BTC/Fib — post-Phase-2.5 fork decision (docs-only)

Clean decision point after Phase 2.5 closed. Compares 4 next-step options (A pause / B new
falsifiable question / C conceptual Genesis prep / D BTC-Fib quality, not 1H) with
observed/inferred/unverified kept separate. **Rec: A (pause) primary; D the only no-new-risk
continuation.** B's real value needs code/export (breaches scope, trends to Phase 3) and its
docs form duplicates Phase 0; C is redundant with Phase 1 + risks Genesis drift. Builds
nothing; no Phase 3, no export, no Genesis touch, no 1H, no ML/backtest/signal. Choice is the
human's. [Note](reviews/btc-fib-post-phase25-fork-decision-20260616.md).

## [2026-06-16] review | Fib → Genesis V2 — Phase 2.5 reviewed PASS / closed

Human review of commit `4599819` — **verdict PASS**, Phase 2.5 closed. Confirmed docs-only:
3-state separation (no zone known / nearby / ATR-warmup not-applicable), per-column nullability,
distance-null as empty CSV field (not 0/inf), empty-meta ⇔ no-known-zone invariant, Genesis
read-only consumer rules (dense table, no imputation across `known_after_ts`, meta never a
feature). **Non-blocking pre-export note:** decide whether `has_robust_4tf_zone_nearby` is
log-price- or ATR-thresholded (ATR ⇒ warmup-null or a separate availability flag). No Phase 3,
no real export, no Genesis touch, no ML/backtest/signal.

## [2026-06-16] decision | Fib → Genesis V2 — Phase 2.5 feature nullability policy (docs-only)

Docs-only policy pinning how the future bar feature table represents empty values — the
precondition flagged by the Phase 2 review. Defines **three** states (no zone known / no zone
nearby / not-applicable ATR-warmup), per-column nullability (join keys + bools + ATR-free count
+ meta always non-null; the 7 non-ATR `nearest_*` null only when no zone known; ATR-denominated
columns null during warmup), distances as **null not 0/inf**, the empty-meta ⇔ no-known-zone
invariant, and read-only Genesis consumer rules (dense table, no imputation across
`known_after_ts`). No code, no export, no Genesis touch, no ML/backtest/signal. Not Phase 3.
[Policy](reviews/btc-fib-to-genesis-v2-feature-nullability-policy-20260616.md).

## [2026-06-16] review | Fib → Genesis V2 — Phase 2 reviewed PASS / closed

Human review of commit `68dc006` — **verdict PASS**, Phase 2 closed. Confirmed: contract-test
only inside Fib, no Genesis coupling, no real export, no feature recomputation, schema/join/
causality validated mechanically, fail-closed cases covered, `confirmation_buffer_hours` pins
the unit. **Follow-up (not now):** before any real export, define a **nullability policy** for
feature columns. No Phase 3, no real export, no Genesis touch, no ML/backtest/signal.

## [2026-06-16] feat | Fib → Genesis V2 — Phase 2 dummy contract test (narrow slice)

Mechanical contract/dummy test **inside the Fib repo only** — not export, not Genesis
integration. New stdlib-only `research/feature_contract.py` validates two synthetic dummy CSVs
(committed under `reviews/contracts/phase2_dummy/`: 3 zones, 4 bars incl. a multi-zone row)
against the Phase 1 schema: exact-header schema, join keys `(symbol,timeframe,timestamp)`
non-null + unique, causality `known_after_ts <= timestamp` over the whole reference set,
knowability floor `known_after_ts >= max(anchor_b)+buffer`, 1H fail-closed, feature/metadata
boundary asserted at import. No fib computation, no Genesis import, no pipeline/ML/backtest/
signal/edge. 20 tests; ruff + 426 passed (76%) + repo-bounds green; CLI smoke OK. **Stop after
this.** [Report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md).

## [2026-06-15] review | Fib → Genesis V2 — Phase 1 closed (PASS)

Phase 1 feature-export spec reviewed — **verdict: PASS**; **closed as a docs-only contract**.
Remaining risk (causal features **non-empty** after all rules) is **empirical, belongs to Phase
2**. **Phase 2 still requires explicit GO.**

## [2026-06-15] question | Fib → Genesis V2 — Phase 1 feature-export spec

Docs-only **data-contract** spec (builds nothing) for a future causally-safe feature export Fib →
Genesis V2, gated by the Phase 0 question. Defines a **zone registry** + **bar feature table** with
binding rules `known_after_ts = max(anchor_b)+buffer` and per-row `zone.known_after_ts ≤ timestamp`,
**3 baseline specs**, a **read-only CSV-first Genesis contract**, **9 causal invariants**, and a
**do-not-export list**.
[Spec](reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md).

## [2026-06-15] question | Fib → Genesis V2 — Phase 0 pre-registration

Docs-only pre-registration of the one falsifiable behaviour question (does price react measurably
differently at causal robust fixed-band MTF confluence zones than at matched naïve/placebo levels,
OOS?) + why-not-anchor-first (selection leakage), causal feature rule, leakage manifest, ≥3
baselines (causal swing + shuffled/placebo = primary), time-split/embargo holdout, neutral success
metrics, stop/go. Authorises nothing beyond the note.
[Note](reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md).

## [2026-06-15] decision | MTF confluence CP1–CP3 — interpretation & decision note

Docs-only synthesis closing the MTF-confluence track. **Observed:** 222 single-linkage
clusters @ε=0.005 (188 fixed-band); c001 robust tight 4-TF; c002 chaining-dependent (dissolves
under fixed-band); c004/c006/c007 zero-span; all 5 CP3 cards human-approved. **Inferred:** MTF
confluence exists as *geometry* — c001 shows tight method-stable confluence can exist, c002
shows single-linkage can overstate strength, zero-span shows exact-price coincidence; none of
it proves edge/support-resistance/predictive value. **Unverified:** price-behaviour effect,
vs-naïve-baseline usefulness, ETH generalisation, whether more cards inform or just confirm,
behaviour-study scope risk. **Decision options** (5) compared with value/risk/scope/smallest
slice. **Recommendation: STOP the MTF track here** — don't expand cards, don't start a
behaviour study without a pre-registered falsifiable question + naïve-level baseline; ETH gated
on BTC sign-off. Next active decision is a fork: **pause Fib, or open a new track with one
clear question.** [Note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md).

## [2026-06-15] decision | MTF confluence atlas CP3 — first pack closed (all cards approved)

First CP3 visual-atlas pack **complete and human-approved (2026-06-15)**. Five cards across
three structural archetypes: **c001** robust fixed-band 4-TF (span 0.00123 ≤ ε); **c002**
chaining-dependent single-linkage contrast (span 0.00627 > ε, dissolves under fixed-band,
never presented as tight 4-TF); **c004/c006/c007** zero-span exact-price 3-TF (span = 0 at
~$64829/$13764/$9085). All resolved by structural signature (cluster ids are positional and
unstable), out_dir keyed on stable label, charts assert geometry only — no edge/signal/
support-resistance. PNGs gitignored, none committed. **Next decision (not started):** stop
here as the first pack, or later expand with fixed-band clusters only on an explicit go.
Docs-only close; gates green (406 passed). [Capstone](reviews/btc-mtf-confluence-atlas-cp3-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 3 — zero-span 3-TF cards (generated)

c002 contrast card **human-approved**. Slice 3 adds three **zero-span** (exact-price) 3-TF
cards under **fixed-band**: `c004`/`c006`/`c007` at ~$64829/$13764/$9085, where
`price_span_log == 0` — several human-drawn fib levels from three timeframes on the
*identical* price (immune to epsilon and chaining; the structural opposite of c002). **Label
discipline:** c004/c006/c007 are CP2's stable labels; cluster ids are positional and have
since shifted (they resolve to c002/c003/c004 under the current corpus), so resolution is by
structural signature (`tf_count==3`, exact TF set, `repr ± 50`, `price_span_log == 0`,
window-year range) — each matches exactly one fixed-band cluster. Output dir is now keyed on
the **stable signature label** (not the positional id); titles show `label (cluster_id)`.
The degenerate `[min,max]` band (min==max) renders as the single exact-price line; metadata
says *zero-span (exact-price coincidence) / N levels share one price across M TFs*. Fail-closed
`len(band)==level_count` cross-check passed (5/4/4). c001 re-renders identically (label==id).
406 tests green (+2 zero-span resolution tests in a new file to respect the 300-line bound; no
golden snapshots for the three cards — synthetic zero-span corpus would exceed it). PNGs
gitignored, none committed. **Pending human inspection.**
[Report](reviews/btc-mtf-confluence-atlas-cp3-zero-span-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 2 — c002 contrast card (generated)

c001 card **human-approved** (title dedup + member-table polish). Slice 2 adds the
chaining-dependent **contrast** card: `mtf_confluence_atlas` is now method-aware
(`--cluster c001|c002` pairs a structural signature with its clustering method). c002
(~21167, 2022-12 → 2023-07) resolves only under **single-linkage** — `price_span_log`
0.006272 **> ε=0.005**, so it chains across log-price and **dissolves entirely under
fixed-band**. New signature fields `min_span_log` (= ε guarantees chaining; fail-closed if
tight) + `window_year_end` (multi-year window). Headline/metadata never say "tight 4-TF":
they state *chaining-dependent (span > epsilon) / NOT tight fixed-band 4-TF*. Fixed a shared
`band_member_rows` rounding bug (1M level on the rounded band edge dropped 4→3): added a
1-cent tolerance + a fail-closed `len(band)==level_count` check; **c001 re-renders
identically** (verified 4/4). 404 tests green (+1 resolution test); c001 golden unchanged.
PNGs gitignored, none committed. **Pending human inspection.**
[Report](reviews/btc-mtf-confluence-atlas-cp3-c002-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 1 — c001 card (generated)

First visual-atlas slice. New `research/mtf_confluence_atlas.py` (stdlib + existing matplotlib
stack) renders one confluence card for the robust 4-TF cluster **c001** under **fixed-band** at
the primary `epsilon_log=0.005`, on a **1d** candle backdrop. Target resolved by **structural
signature** (tf_count==4, exactly {1M,1w,1d,4h}, repr≈29274±200, span≤0.005, window year 2021),
never a hard-coded id — exactly one fixed-band cluster matches. Fail-closed: zero/ambiguous
signature match, superseded `20250506T080000` in any member, off-protocol timeframe (no 1H),
and missing candle cache (no auto-fetch). Members reconstructed in-process from `LevelRow`
(not the truncated CSV); 4 members (1M/1w/1d/4h) at 29247–29283, `price_span_log=0.00123`
annotated in a metadata box (CP2-corrected headline). Card = candles + shaded [min,max] band +
representative line + per-TF member lines (levels view). `render_summary` gained
`cluster_atlas_summary` (includes the analytical numbers — `price_span_log` is the central CP2
metric) + golden snapshot. PNGs under `experiments/review/mtf_confluence_atlas/fixed_band/c001/`
(gitignored, none staged). 10 tests; no new deps; no source labels changed. **Generated,
pending human visual inspection** — observed: the four members within $36 render as a near-single
band (label stacking noted as a candidate adjustment). Next: approve card design or adjust, then
c002 chaining-dependent contrast card. No chart-as-signal, no edge.
[Report](reviews/btc-mtf-confluence-atlas-cp3-c001-20260615.md).

## [2026-06-15] review | MTF confluence CP2 — sensitivity / robustness

Robustness pass over CP1. Added stdlib `cluster_confluence_fixed_band` (complete-linkage in
price + single-linkage in time) + `run_sensitivity` (9 new tests). Predeclared epsilons
0.0025/0.005/0.01. Single-linkage total 173/222/266; chaining (span>ε) 12/30/70 = 7%/14%/26%.
Fixed-band 144/188/242 (0 over-ε by construction). **c001 (~29274) robust 4-TF** across
methods/epsilons (3-TF under fixed-band only at 0.01, a band-cut effect). **c002 (~21167)
chaining-dependent** — 4-TF only under single-linkage at ε≥0.005 with span 0.00627>ε; dissolves
to 2-TF fragments under fixed-band. Verdict: confluence is real but CP1 overstated c002.
Conditional GO to CP3 visual atlas (render fixed-band + annotate span). No chart, no tuning,
no source change. Full suite 394 passed, 75%. Report:
[`reviews/btc-mtf-confluence-sensitivity-20260615.md`](reviews/btc-mtf-confluence-sensitivity-20260615.md).

## [2026-06-15] review | MTF confluence atlas CP1 — confluence table

First analytical slice on the locked corpus. New stdlib module `research/mtf_confluence.py`
(10 tests): flattens 462 fibs → 2772 level rows, clusters by log-price proximity
(epsilon_log=0.005, chosen before results) + overlapping anchor windows, requires ≥2 TFs.
Result: **222 clusters** (2×4-TF, 24×3-TF; 1d,4h dominates 143). Chaining visible
(30/222 span>eps, reported). **Stop/go: GO** to CP2 (sensitivity/robustness, multi-eps +
complete-linkage). No chart, no trading conclusions, no tuning. Committed CSV under docs;
large levels CSV gitignored.
[Report](reviews/btc-mtf-confluence-table-20260615.md).

## [2026-06-15] review | BTC source-fib corpus integrity report (capstone)

Read-only capstone locking the corpus before the MTF analytical pass. Re-derived on disk:
1M=9, 1w=21, 1d=67, 4h=365 (462 total; up=219/down=243), coverage (anchor-derived)
2016-12-29 → 2026-06-07, log scale + `tradingview_log_chamoun`, no 0.236. Source-quality:
Tier 1+2 done, 20171228 corrected, 20250506 superseded (1), ledger validates (10 rows).
Corpus declared clean. Next: #1 MTF confluence atlas (table-first). Docs-only.
[Report](reviews/btc-source-fib-corpus-integrity-20260615.md).

## [2026-06-15] decision | Next research-pass design — corpus integrity then MTF atlas

Read-only design comparing 5 candidate passes (5×8 sub-questions). Recommends corpus
integrity report (#2) now, MTF confluence atlas (#1) next; #5 visual companion to #1;
#3/#4 deferred. Docs-only.
[Report](reviews/btc-source-fib-next-research-plan-20260615.md).

## [2026-06-15] maintenance | Reconcile data/labels/INDEX.md with current facit

`data/labels/INDEX.md` was stale (2026-06-10: 1w/1d/4h listed absent/0). Reconciled to
on-disk base counts (excl. sidecars): 1M=9, 1w=21, 1d=67, 4h=365; authority pointed to
handoff.md. Docs-only. (Note: log.md near its size bound — archive old entries next.)

## [2026-06-15] fix | 20250506 dedup — fib A superseded, fib B retained

Resolved the strongest overlap-detector near-duplicate. `fib_BTC-USD_4h_20250506T080000`
and `…120000` are the same up-leg to the same high (shared anchor_b 97840; box_iou 0.70).
Candle data: 05-06 12:00 low (93663) is the true bottom = B's anchor_a; A's anchor_a
(08:00 @ 93988) is one bar early on a higher low — a redundant, worse version (not a
complementary sub-leg). Decision: **supersede A, retain B.** No retired-label pattern
exists, so A's `fib_*.json` was deleted from active facit and documented. Active 4H count
**366 → 365** (current-state docs updated; dated historical 366 entries kept). Ledger gained
a tested `superseded` status; both fibs now tracked (B ok/accepted, A suspicious/superseded
with provenance hash). fib B unchanged (verified no diff); only A deleted; no other source
JSON touched. Report:
[`reviews/btc-4h-fib-20250506-dedup-20260615.md`](reviews/btc-4h-fib-20250506-dedup-20260615.md).

## [2026-06-15] feat | Structural chart-contract + metadata snapshots (Issue #F)

Implemented the chart-regression spike's recommendation. Added `research/render_summary.py`
(stdlib-only, no deps): `map_summary` / `zoom_summary` / `gallery_summary` produce stable,
text-diffable dicts from existing render results/output dirs — repo-relative forward-slash
paths, no timestamps, no absolute paths, sorted order, no level prices (those stay in the
source JSON). Committed golden JSON snapshots under `tests/research/snapshots/` (text only,
no binary baselines); tests regenerate with `UPDATE_SNAPSHOTS=1`. Covers all three primary
flows (4H map, 4H zoom, artifact gallery) + a guard test that snapshots are JSON-only.
5 tests; ruff + full suite green (375 passed, 75.16% cov). No PNG baselines, no pixel diff,
no new deps. Automatic structural layer; HTML gallery + ledger remain the manual visual
layer. Closes the chart-regression follow-up (#F).

## [2026-06-15] decision | Chart regression strategy — structural-first (spike)

Design spike for Issue #32 evaluate-later. Recommendation: **structural chart-contract
tests + text/metadata snapshots first; defer pixel regression.** Grounded in the repo's
existing style (~170 structural assertions across 22 render test files) and the anti-blob
policy. Adopt now: extend structural assertions on render dataclasses + committed golden
JSON/markdown summaries (no blobs). Keep HTML gallery + ledger as the manual visual layer.
Defer `pytest-mpl`/`matplotlib.testing.compare` (need committed PNG baselines, flaky across
versions); reject image/perceptual hashing (new dep, version-sensitive). No binary
baselines committed. Follow-up issue #F drafted (render_summary + golden snapshots, stdlib).
Report: [`reviews/chart-regression-strategy-20260615.md`](reviews/chart-regression-strategy-20260615.md).
Docs-only; no code/deps/artifacts.

> **2026-06-11→06-12 entries** (1M reaction-review, 1W/1D/4H source phases, 4H Tier 1
> design/maps) **and the oldest 2026-06-15 tooling/correction entries** (4H Tier 1/Tier 2
> visual-review, Issue #32 gallery/ledger/overlap detector, single-fib edit-mode, 20171228
> correction, #32 milestone) archived to
> [post-reset part 1](log-archive-btc-postreset-part1.md).

