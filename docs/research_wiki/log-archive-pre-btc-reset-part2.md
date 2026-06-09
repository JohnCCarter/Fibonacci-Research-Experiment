# Archived wiki log (pre-BTC monthly reset, part 2)

Part 2 of 2. Previous: [part 1](log-archive-pre-btc-reset-part1.md).

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

