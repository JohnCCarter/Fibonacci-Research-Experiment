# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.

## [2026-06-05] decision | MTF fib level projection — design + inspection

After the 1D-only track stalled at `working pipeline, no stable evidence yet`, scoped
a new direction: project the **locked HTF human fib levels** onto **LTF candles** and
measure LTF behavior around those exact prices (no auto-fib, no anchor moves, no
relabel).

Inspection (Observed): the fingerprint (#23), outcome (#22), join, and toplist layers
are already timeframe-agnostic — `extract_fingerprint` / `analyze_events` only need a
df + `event_bar` (int) + `fib_price` + `approach_side`; `classify_candle` /
`classify_candles` already accept any df + an HTF annotation; `load_candles` supports
all timeframes. The **only missing piece** is a deterministic LTF interaction detector
(explicit human level prices, scan from `anchor_b` on the LTF index). `level_events.py`
`detect_level_events` is close but bound to a machine swing + `fib_levels(swing)`.

Plan: thin new runner `fibengine.research.mtf_fib_level_projection` (detector + glue
to existing extract/analyze/join), artifacts under `experiments/runs/`, CLI
`--human-fib --lower-timeframes --pre-bars --post-bars`. First runnable slice (no
network) is **1W fib -> 1D candles**; `4h`/`1h` need a fetch first (ETH/SOL have no 4h
cache). Layer separation: human_fib / projected_level / relation / fingerprint /
outcome. Full design: [MTF_FIB_LEVEL_PROJECTION.md](../research/MTF_FIB_LEVEL_PROJECTION.md).

Guardrail: design/docs only so far; no code, no trading signal, no edge claim. No
runner implemented until go-ahead.

## [2026-06-05] decision | MTF fib level projection — runner implemented (1W -> 1D slice)

Implemented the minimal runner `fibengine.research.mtf_fib_level_projection` with
`detect_ltf_level_interactions(...)` (deterministic LTF touch scan from `anchor_b`
using explicit human level prices; reuses `level_events._classify` + `classify_candle`)
and glue to existing `extract_all` (#23) + `analyze_events` (#22) +
`join_fingerprints_outcomes`. Per-LTF join calls keep `event_id` collision-free.
Layers kept separate per row: human_fib / projected_level (`projected_from_timeframe`)
/ relation / fingerprint / outcome. CLI: `--human-fib --lower-timeframes --pre-bars
--post-bars --horizons` (+ `--config`). Artifacts: `config.json`, `interactions.jsonl`,
`fingerprint_outcomes.jsonl`, `unmatched.jsonl`, `skipped.jsonl`, `summary.json/csv`,
`run_summary.json`; appends `experiments/results/mtf_fib_level_projection.jsonl`.

Smoke (1W BTC fib `fib_BTC-USD_1w_20250116T000000` -> 1D): 6 projected levels, 42 LTF
interactions, 168 joined rows, 0 unmatched, 0 skipped. First 0.236 touch at 2025-04-04
(right after the leg end), `fib_price` exactly the human level. Tests: 4 new (detector
determinism, leg-end-after-cache skip, e2e artifacts, missing-cache skip); full suite
186 passed, coverage 75%, ruff clean on new files. Scope guard held: no swing/
`detect_level_events` refactor, no UI, no candidate-logic change, no edge claims. 4h/1h
deferred until a fetch populates LTF caches. Design:
[MTF_FIB_LEVEL_PROJECTION.md](../research/MTF_FIB_LEVEL_PROJECTION.md).

## [2026-06-05] review | MTF fib projection checkpoint + toplist triage (1W->1D)

Ran `fib_toplist --run-dir <mtf_proj_20260605T122401Z>` on the MTF run — the existing
triage stack works unchanged on MTF output (116 buckets, all LOW SAMPLE; watch fields
`pre_distance_atr_norm` / `post_retest_count` / `post_remained_near_level_rate` are
single-fib low-N co-occurrences, not evidence). Wrote checkpoint
[2026-06-05-mtf-fib-projection-checkpoint.md](reviews/2026-06-05-mtf-fib-projection-checkpoint.md):
proven = runner exists, human levels reused verbatim, 1W->1D works (42 interactions,
42 fingerprints, 168 joined, 0 unmatched/0 skipped, stack reusable); not proven = no
edge, no signal, no stable behavior, no cross-TF comparison, 4H/1H deferred. Interp:
technically validates HTF=map / LTF=behavior. Next: fetch 4H later, run 1W->4H and
1D->4H, compare vs 1D-only. No logic changes; no edge claims. Docs/triage only — no
src changes, so no ruff/pytest run needed.

## [2026-06-05] review | MTF projection to 4H — structural detail, still low sample

Fetched BTC/USD 4h only (7882 bars, 2022-10-31→2026-06-05; `limit_8000.csv`; ETH/SOL 4h
deferred). Ran the same MTF pipeline (no logic/threshold changes): 1W→4H on
`fib_BTC-USD_1w_20250116T000000` = 87 interactions / 348 joined / 0 unmatched / 0
skipped (vs 42 on 1D, same fib); 1D→4H on `fib_BTC-USD_1d_20260407T000000` = 23 / 92 /
0 / 0. Toplist: 1W→4H 184 buckets (16 reached n≥5); 1D→4H 60 buckets all LOW SAMPLE.
Finding: 4H adds interaction *resolution* (~2× more distinct touches on the same fib),
not *evidence* — `fib_toplist` watch sets differ across all three runs (low-N artifact).
No edge claims; only a data fetch + run artifacts changed (no src/test edits, so no
ruff/pytest). Details appended to
[MTF checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md).

## [2026-06-05] review | MTF 4H sample growth — sufficient for descriptive review

Fetched ETH/SOL 4h (7881 bars each, 2022-10-31→2026-06-05; BTC 4h already cached). Ran
the same MTF pipeline over all base human fibs per symbol×HTF → 4H + a combined run
(no logic/threshold changes). Combined: 136 fibs, 7453 interactions, 29812 joined rows,
384 buckets, 0 unmatched/0 skipped; n≥5=360, n≥10=336, **n≥20=332**, max n=299. Answer:
4H sample is now sufficient for descriptive review. Caveat (validity, not edge): the 4h
cache starts 2022-10-31, so pre-2022 1D fibs are projected cross-era; SOL 1D→4H alone =
5415 interactions (old 2021 levels intersected by the 2022–2026 range) and dominates the
n≥20 count, while BTC 1D→4H stays tiny (old levels far below current price). Prefer
anchor_b ≥ 2022-10-31 fibs for clean forward-window review. No edge claims; only data
fetch + run artifacts + wiki changed (no src/test edits → no ruff/pytest). Details in
[MTF checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md).

## [2026-06-05] review | MTF 4H cohort split — clean-forward vs cross-era

Split 4H projection inputs by `anchor_b` vs cache start 2022-10-31 (selection only, no
logic change). clean-forward (anchor_b ≥ 2022-10-31): 14 fibs, 617 interactions, 2468
joined, 336 buckets, n≥20=32. cross-era (< 2022-10-31): 122 fibs, 6836 interactions,
27344 joined, 384 buckets, n≥20=308. 0 unmatched/0 skipped both. Composition: clean-
forward is BTC+SOL only — all ETH fibs are pre-2022; clean 1D is recent BTC only.
Cross-era kept separate as historical level revisit analysis (different question; large
count reflects old levels inside the later range, not forward reaction). toplist
`watch=[]` in both. No edge claims; only run artifacts + wiki changed (no src/test → no
ruff/pytest). Runs `mtf_proj_20260605T124444Z` (clean) / `…124448Z` (cross). Details:
[MTF checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md).

## [2026-06-05] review | MTF clean-forward n≥20 read — no stable evidence yet

Descriptive read of clean-forward run `mtf_proj_20260605T124444Z`, n≥20 buckets only
(32 buckets / 8 families across 4 horizons; BTC+SOL only, no ETH). Findings: 4 families
sign-stable across horizons (continuation cross 0.236 −, cross 0.382 +, cross 0.5 +,
rejection touch 0.236 −) BUT that is mechanical (h5⊂h10⊂h20⊂h50 nested windows);
magnitudes tiny (≤~1.6%), mfe≈mae. BTC vs SOL: no shared n≥20 bucket and per-symbol
signs frequently disagree (e.g. cont touch 0.618 h50 BTC −0.092 vs SOL +0.084). Rates
revert to coin-flip; crossed_back rises with horizon (mechanical). Verdict: clean-forward
4H projection works, but no stable evidence yet. Cross-era kept separate. No edge claims;
only a review page + wiki links added (no src/test → no ruff/pytest). Page:
[clean-forward n≥20 review](reviews/2026-06-05-mtf-clean-forward-n20-review.md).

## [2026-06-04] ingest | Karpathy LLM wiki pattern

Source: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

Takeaway: use a persistent, agent-maintained wiki as a compounding research
artifact. Raw sources remain the source of truth; wiki pages summarize,
cross-link, and preserve decisions so future sessions do not re-derive context.

Repo mapping:

- `docs/research_wiki/index.md` is the content map.
- `docs/research_wiki/log.md` is the chronological trail.
- Future concept, decision, and review pages should link back to source docs and
  generated review artifacts.

Guardrail: this is documentation infrastructure only. It does not add auto-fib,
trading logic, ML behavior, or promotion-path changes.

## [2026-06-04] decision | Expand to full repo wiki

Decision: grow `docs/research_wiki/` from a minimal scaffold into a practical
repo knowledge base before the project structure grows further.

Added scope:

- glossary
- core concepts
- module and data reference pages
- CLI command reference
- first decision/source pages

Boundary: still docs-only. No runtime code, automation, promotion-path changes,
auto-fib, trading signals, or ML behavior.

## [2026-06-04] decision | Adopt atomic artifacts and handoff

Decision: adopt two workflow patterns from the Karpathy gist review as repo
conventions:

- atomic runnable artifacts for small, complete, bounded research work.
- agent handoff/log for current context and durable session trail.

Implementation:

- [Atomic runnable artifacts](concepts/atomic-runnable-artifacts.md)
- [Agent handoff and log](concepts/agent-handoff-log.md)
- [Current handoff](handoff.md)
- [Atomic artifact template](templates/atomic-artifact.md)
- [Handoff entry template](templates/handoff-entry.md)

Boundary: adopt the shape, not the external code. No ML code, auto-tuning,
runtime behavior, or promotion-path change.

## [2026-06-04] decision | Enforce wiki maintenance rule

Decision: operationalize the Karpathy LLM-wiki pattern with a persistent Cursor
rule.

Implementation:

- `.cursor/rules/research-wiki-maintenance.mdc`

Effect: future agents should read `index.md`, `log.md`, and `handoff.md` before
substantial work, then update the smallest relevant wiki pages after meaningful
research, review, architecture, workflow, or implementation changes.

Boundary: this is agent discipline, not runtime automation. It must not change
research results, promote behavior, add auto-fib, or turn candidates into facit.

## [2026-06-04] ingest | NVIDIA Qwen3 Coder API

Source: NVIDIA NIM / build.nvidia.com model `qwen/qwen3-coder-480b-a35b-instruct`.

Repo mapping:

- `scripts/nvidia_qwen_smoke.py` — stdlib smoke via `NVIDIA_API_KEY`.
- [NVIDIA Qwen API](reference/nvidia-qwen-api.md) — setup and guardrails.

Boundary: external assistant only; keys in env only; not fibengine runtime.

## [2026-06-04] verify | NVIDIA API docs + smoke

Source: [infer API](https://docs.api.nvidia.com/nim/reference/qwen-qwen3-coder-480b-a35b-instruct-infer)
confirms OpenAI-compatible `/v1/chat/completions` on `integrate.api.nvidia.com`.

Effect: smoke verified locally (~28s, streaming). Wiki reference updated with infer
link and cold-start latency note. Optional diag: `scripts/nvidia_qwen_diag.py`.

## [2026-06-04] doc | Cursor BYOK for Qwen3 Coder

Added [Cursor chat steps](reference/nvidia-qwen-api.md#cursor-chat-byok) for
`qwen/qwen3-coder-480b-a35b-instruct` via OpenAI override + custom model ID.

## [2026-06-04] maintenance | Repo-aware agent rules (Qwen in Chat)

Source: user request — Qwen should behave as repo-aware coding agent in Chat, not
memory-only chatbot.

Added:

- `.cursor/rules/repo-aware-coding-agent.mdc` (always apply)
- `docs/agent/REPO_AWARE_AGENT.md` — Cursor settings, `@` context, User Rules snippet
- `.github/copilot-instructions.md` — Copilot parity
- `AGENTS.md` section + link from [nvidia-qwen-api.md](reference/nvidia-qwen-api.md)

Note: BYOK still limits which Cursor modes route to Qwen; rules apply when project
rules are enabled in Chat.

## [2026-06-04] maintenance | Qwen repo-agent prompts + CLI check

Added `docs/prompts/qwen-chat-starter.md` and `scripts/qwen_repo_agent_check.py`
(repo excerpt → NVIDIA NIM; expects Inspected/Observed/Assumptions sections). Verified OK locally.

## [2026-06-04] maintenance | Cursor workspace agent shell

Added `docs/agent/CURSOR_WORKSPACE_AGENT.md`, `.cursor/README.md`, `.cursor/commands/repo-agent.md`
(slash command prefills wiki `@` + repo-aware prompt). AGENTS.md and wiki index updated.

## [2026-06-04] maintenance | Qwen hooks (sessionStart + beforeSubmitPrompt)

`.cursor/hooks.json`: when model contains `qwen`, inject repo-agent context at session
start and block bare prompts until `/repo-agent` or wiki `@` (see CURSOR_WORKSPACE_AGENT.md).

## [2026-06-04] decision | GLM-5.1 lead + Qwen3-Coder implement

Policy: GLM owns plan/review/approval; Qwen owns scoped implementation. Added
`docs/agent/MODEL_COLLABORATION.md`, `.cursor/rules/model-collaboration-policy.mdc`,
`/glm-plan`, `/qwen-implement`, `on_glm_session.py`, updated Qwen hooks, `nvidia_glm_smoke.py`,
wiki [nvidia-glm-api.md](reference/nvidia-glm-api.md), [model-handoff template](templates/model-handoff.md).

## [2026-06-05] maintenance | Fib-aware review implementation (#15)

Implemented fib-aware rendering in `human_review_level_events.py` and aligned
`level_event_review_tool.py` titles. Human-fib event JSON path via
`--human-fib-events`; tests in `test_human_fib_review_rows.py`,
`test_human_review_sampling.py`, updated `test_human_review_level_events.py`.

Verification: `ruff check` OK; 12 research tests passed.

## [2026-06-05] review | ETH 1d human-fib smoke (#15 gate)

Smoke pack `human_fib_review_20260605T064610Z` from
`fib_ETH-USD_1d_20170618T000000_events.json` (10/35 events sampled).

Acceptance: H/L anchors, all fib levels, relation vs `*_candidate`, and `fib_id`
visible on PNG charts. Distilled page:
[2026-06-05 ETH 1d smoke](reviews/2026-06-05-eth-1d-human-fib-smoke.md).

## [2026-06-05] decision | Tooling spike conclusion (#16)

After smoke: keep Matplotlib PNG + JSON review path; defer Dash/Panel/React/HTML
until a human reviewer flags pan/zoom as blocker. Spike doc updated with smoke
outcome. Issue #16 deliverable (recommendation + comparison) was already in
[FIB_AWARE_TOOLING_SPIKE.md](../../research/FIB_AWARE_TOOLING_SPIKE.md).

## [2026-06-05] maintenance | GLM delegates to Qwen subagent

Qwen is GLM's implementation subagent, not a manual peer chat by default.

Added/updated:

- `.cursor/agents/qwen-implementer.md` (`model: qwen/qwen3-coder-480b-a35b-instruct`)
- `.cursor/agents/glm-lead.md` (`model: z-ai/glm-5.1`)
- `model-collaboration-policy.mdc`, `glm-plan.md`, `on_glm_session.py`, `MODEL_COLLABORATION.md`

Delegate pattern: `Use the qwen-implementer subagent to implement this GLM handoff:` + handoff block.

## [2026-06-05] implement | issue #19 fib-leg direction overlay

Purple H→L / L→H leg arrow on review chart + panel `FIB LEG` section; off-screen
anchor hints. Layer order: leg → fib levels → event → callout.

## [2026-06-05] implement | issue #18 review chart polish

Follow-up UX: full H/L anchor labels with price on-chart (smart offset), spacier
review panel sections (H / FIB LEVELS / L / EVENT), more subdued inactive fib
lines, collision-safer event callout. Smoke `human_fib_review_*` regen.

## [2026-06-05] implement | issue #17 review chart UX

Matplotlib polish in `human_review_level_events` + `level_event_review_tool`:
ACTIVE badge, subdued inactive fib lines, review panel (fib ladder), split status
lines, improved event callout, no edge anchor clutter. Smoke pack
`human_fib_review_20260605T091458Z`.

## [2026-06-05] fix | fib review broken on short 1d cache

Root cause: ETH 1d cache was 1000 bars (from 2023-09-10); human-fib events from
2017 mapped to bar 0 via nearest-neighbor — fib lines invisible, wrong event candle.

Fix: `timeframe_limits.1d` → 3500, stricter `_bar_index`, resolve `event_bar` from
ISO timestamp, coverage check in `level_event_review_tool`. Verified pack
`human_fib_review_20260605T083224Z` (event 2017-08-21 bar 289, fib 346 in range).

## [2026-06-05] feat | fingerprint × outcome join (#22 + #23)

`fibengine.research.fib_fingerprint_outcomes` — joins fingerprint (#23) and
outcome (#22) layers on `event_id` (1 fingerprint × N horizons). Smoke: maj-BTC
(1 event, 4 rows). Full batch: 51 joined events, 204 rows, 104 load-skipped
(pre-2022-10-31). Docs: [FIB_FINGERPRINT_OUTCOMES.md](../research/FIB_FINGERPRINT_OUTCOMES.md).

## [2026-06-05] config | candle window 2022-10-31 → today

`data.history_start: "2022-10-31"` in settings; fetch paginates from that date;
`load_candles` trims older bars. `timeframe_limits` resized (1d: 1400, 1w: 220).

## [2026-06-05] feat | fib level interaction fingerprints (#23)

`fibengine.research.fib_level_fingerprints` — deterministic pre/at/post features
per human-fib event; complements #22. Docs: [FIB_LEVEL_FINGERPRINTS.md](../research/FIB_LEVEL_FINGERPRINTS.md).

## [2026-06-05] feat | fib candidate outcome backtest (#22)

`fibengine.research.fib_candidate_outcomes` — forward metrics per event×horizon
from human-fib `*_events.json`; summary by candidate/relation/level/TF. Docs:
[FIB_CANDIDATE_OUTCOMES.md](../research/FIB_CANDIDATE_OUTCOMES.md).

## [2026-06-05] feat | fib-context review view (#21)

`window_for_view` / `xlim_for_view` in `human_review_level_events`; interactive
`level_event_review_tool` defaults to fib-context (full H/L + event overlay), `g`
toggles event-zoom. PNG export uses fib-context by default. Docs:
[LEVEL_EVENT_HUMAN_REVIEW.md](../research/LEVEL_EVENT_HUMAN_REVIEW.md).

## [2026-06-05] doc | VS Code Copilot NVIDIA BYOK

Added [VSCODE_COPILOT_NVIDIA_MODELS.md](../agent/VSCODE_COPILOT_NVIDIA_MODELS.md) and
summary in `.github/copilot-instructions.md` — Custom Endpoint +
`chatLanguageModels.json` for `z-ai/glm-5.1` and
`qwen/qwen3-coder-480b-a35b-instruct` (same NIM API as Cursor).

## [2026-06-05] feat | fingerprint × outcome triage top-list

`fibengine.research.fib_toplist` — read-only exporter over one join run:
`toplist.csv` (candidate summary ranked per candidate × horizon, `LOW SAMPLE`
when `n_events` < 5) + `TOPLIST_NOTES.md` (inventory, top-1 preview, Spearman
fingerprint↔outcome hints, untuned watch/weak/noise buckets). Applied to
`fp_outcomes_20260605T114206Z`: 148 buckets, **all LOW SAMPLE** (max n=3) — the
honest triage takeaway is "needs more events", not edge. Descriptive only; no
signal/strategy/tuning. Docs: [FIB_FINGERPRINT_OUTCOMES.md](../research/FIB_FINGERPRINT_OUTCOMES.md).

## [2026-06-05] feat | data expansion + multi-run stability triage

`config/settings.expansion.yaml` (history_start 2016-11-05, 1d limit 3500) + new
`--config` flag on the join CLI widen the candle data scope **without** touching the
global 2022-10-31 default or any analysis threshold. Expanded run
`fp_outcomes_20260605T115819Z`: **51 → 1148 events** (204 → 4592 rows), recovering ETH
2017-2018 (BTC pre-2016 + SOL pre-2022 1d stay skipped, no deep cache). `fib_toplist
--compare-to` adds `sample_inventory.csv` + `MULTIRUN_NOTES.md`: 240 buckets reach n>=5
(152 >=10, 80 >=20). Key finding: with 22x data **every** baseline fingerprint-vs-mfe
co-occurrence WEAKENED or sign-flipped — the low-N "watch" signals were artifacts.
Descriptive triage only; no edge/signal/tuning/candidate-logic change.

## [2026-06-05] review | fib fingerprint × outcome checkpoint

Research checkpoint: #22/#23/join/triage implemented and proven mechanically;
expanded run (1148 events) found **no stable fingerprint/outcome relationship** and
prior small-N watch signals were likely artifacts. Not proven: no edge, no stable
candidate signal, no stable fingerprint, no trading logic. Next: analyze the 80
buckets at n>=20; if nothing consistent across candidate/level/TF/horizon, mark track
`working pipeline, no evidence yet`. Page:
[2026-06-05 checkpoint](reviews/2026-06-05-fib-fingerprint-outcome-checkpoint.md).

## [2026-06-05] review | n>=20 bucket analysis

Descriptive read of the 80 n>=20 buckets (20 candidate×relation×level groups, all 4
horizons, all 1d). Only consistent structures are **mechanical** (mfe/mae/crossed_back
grow with horizon length) or **definitional** (close_on_approach_side encodes the
candidate's at-event side). Raw forward_return tracks sample down-drift, not candidate
property. 4 single-relation groups (`rejection touch 0.618/1`, `continuation touch
0.618/0.786`) flagged *worth more data*, not evidence. Verdict: **working pipeline, no
stable evidence yet**. Page:
[2026-06-05 n>=20 review](reviews/2026-06-05-fib-n20-bucket-review.md).

## [2026-06-08] maintenance | Close implemented GitHub issues

Closed on GitHub (implementation already in repo): **#15** (fib-aware review),
**#16** (tooling spike), **#17–#19** (review chart UX/polish/leg overlay),
**#21** (fib-context view), **#22** (candidate outcomes), **#23** (fingerprints).
Each close comment links smoke/docs/checkpoint. Remaining open: **#14**, **#25**
(+ PR #24/#26 if applicable).

## [2026-06-08] decision | Close #14 minimal (facit vs MTF projection)

Updated [HTF_LTF_RESEARCH_ALIGNMENT.md](../research/HTF_LTF_RESEARCH_ALIGNMENT.md): spår **A**
(facit chain 1w→1d ✅; 4h/1h `legs[]` + 1d→4h disambiguation deferred) vs spår **B**
(MTF projection research — 1W→1D/4H, 1D→4H implemented; does not replace 4h facit).
Closed **#14** on GitHub with decision + links to
[MTF_FIB_LEVEL_PROJECTION.md](../research/MTF_FIB_LEVEL_PROJECTION.md) and MTF wiki checkpoints.
No code or research-logic changes.

## [2026-06-08] doc | Issue #25 tooling recommendation (main, not PR #26)

Added `docs/tooling/TOOLING_RECOMMENDATION_REPORT.md` + `TOOLING_RECOMMENDATION_TOOLS.md` —
issue #25 format (per-tool category, strategy, success-criteria map). Grounded in repo
(uv/ruff/pytest/pydantic/ccxt/matplotlib/custom research stack). PR #26 noted as separate
agent/CI supplement. No deps, no adoption. Next: human review → close #25 on GitHub.

## [2026-06-08] implement | Tooling A–F (#25 follow-ups)

- **A** `fibengine.validation` — pandera OHLCV + pydantic `FetchManifest`/`ReviewRow`; validate on `load_candles`.
- **B** `fibengine.research.ledger_query` + `scripts/query/ledger_row_counts.sql` (DuckDB over JSONL).
- **C** Split `human_review_level_events` → constants/rows/charts/pack + thin CLI re-exports.
- **D** mplfinance candles in `human_review_charts` (`--line` fallback kept).
- **E** `tests/core/test_fib_hypothesis.py` (hypothesis dev dep).
- **F** `manifest.json` beside CSV on fetch (`fetch.py`).
Verification: ruff OK; pytest 195 passed, 76% cov.

## [2026-06-08] refactor | Shared mplfinance candles (PNG + interactive)

`human_review_candles.py` — single `draw_review_candles` / `review_mpf_style` for
PNG (`human_review_charts`) and `level_event_review_tool` (dark theme). Same up/down
colors; fib overlays unchanged. Tests: `test_human_review_candles.py`.

## [2026-06-08] docs | Agent/subagent doc map (INDEX.md)

Added `docs/agent/INDEX.md` — layered inventory of all agent MD (constitution,
subagents, rules, hooks, setup, templates, wiki). Aligned cross-links to
*CONSTITUTION FOR AGENTS AND SUBAGENTS* in AGENTS.md.

## [2026-06-08] docs | AGENTS.md as agent constitution

Rewrote root `AGENTS.md` as canonical constitution for GLM lead, Qwen implementer
subagent, and universal duties/guardrails; product/Cloud moved to appendices.
Linked from `.cursor/agents/*`, `docs/agent/`, `.cursor/README.md`.

## [2026-06-08] chore | Categorize loose docs/ markdown files

Moved 22 top-level `docs/*.md` into `agent/`, `labeling/`, `research/`,
`validate/`, `tooling/` with per-folder README indexes; kept `CONTRIBUTING.md` and
`TRACKS.md` at `docs/` root. Updated cross-links repo-wide.

## [2026-06-08] release | Merge PR #27 to main

Merged `feature/research-spot-check` → `main` (`bd22e87`): tooling A–F, fib/MTF
research stack, docs/wiki, cursor collaboration, security fixes. Closed superseded
PRs #20/#24/#26. Local `main` verified: pytest 198 passed.

## [2026-06-08] chore | Close #25; remove scratch scripts

Closed **#25** on GitHub after tooling A–F landed on `feature/research-spot-check`
(3 commits: feat/docs/chore). Deleted one-off `_scratch_*.py` scripts — findings
already in wiki reviews (`fib-n20-bucket`, `mtf-clean-forward-n20`, MTF checkpoint).
Repo bounds tiers raised for `research/*.py` (750 lines).
