# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

Fib research stack: `fib_candidate_outcomes` (#22) + `fib_level_fingerprints` (#23)
+ `fib_fingerprint_outcomes` (join) + `fib_toplist` (descriptive triage export).
Candle window now `history_start: 2022-10-31`. Next direction designed: **MTF fib
level projection** (HTF human fib -> LTF candle behavior), see
[MTF_FIB_LEVEL_PROJECTION.md](../MTF_FIB_LEVEL_PROJECTION.md).

## Recent Changes

- Review rendering was made fib-aware: H/L anchors, all fib levels, raw relation,
  and separate behavior candidates.
- `docs/research_wiki/` was expanded into a full seed wiki with glossary,
  concepts, references, decisions, sources, and logs.
- Atomic runnable artifact and agent handoff/log patterns are now repo workflow
  conventions.
- `.cursor/rules/research-wiki-maintenance.mdc` now makes wiki maintenance a
  persistent agent rule.
- `.cursor/rules/repo-aware-coding-agent.mdc` + `docs/REPO_AWARE_AGENT.md` — inspect
  repo before answer/edit; facts vs assumptions; for BYOK Qwen in Chat.

## Verification Snapshot

- Wiki docs have been checked against repo docs bounds.
- IDE lints reported no markdown diagnostics on the wiki files during setup.
- The wiki maintenance rule was added as an always-applied Cursor project rule.
- NVIDIA smoke: `scripts/nvidia_qwen_smoke.py` OK (~28s streaming, key in `.env`).
- Tooling stack merged to **`main`** via PR #27 (`bd22e87`, 2026-06-08): pytest 198
  passed, ~76% cov; aiohttp 3.14.1 + CI `permissions: contents: read`.
- Human-fib smoke pack `human_fib_review_20260605T064610Z` — #15 acceptance criteria met on PNG inspection.

## Open GitHub issues (not yet done)

None blocking research tooling. PR #26 remains a separate agent/CI supplement (not merged).

Closed 2026-06-08: **#25** (tooling report + A–F on `feature/research-spot-check`:
validation, DuckDB, review split, mplfinance, hypothesis, fetch manifest).
Also: #14 (minimal close — 1w→1d facit done; 4h/1h facit deferred; MTF projection =
active LTF path), #15–#19, #21–#23.

## Open Questions
- Should atomic artifact notes live only in the wiki, or should selected ones get
  small scripts under `scripts/`?
- When manual review findings exist, what review summary format is most useful?

## Next Useful Action

1D-only track is `working pipeline, no stable evidence yet`
([n>=20 review](reviews/2026-06-05-fib-n20-bucket-review.md)). New direction: **MTF
fib level projection** — project locked HTF human fib levels onto LTF candles and
measure LTF behavior. Design + inspection done in
[MTF_FIB_LEVEL_PROJECTION.md](../MTF_FIB_LEVEL_PROJECTION.md).

1. DONE — runner implemented: `fibengine.research.mtf_fib_level_projection` +
   `detect_ltf_level_interactions` + 4 tests (all pass; ruff clean; suite 75%).
2. Smoke (1W BTC fib -> 1D): 6 projected levels, 42 LTF interactions, 168 joined rows
   (×4 horizons), 0 unmatched, 0 skipped. Artifacts under
   `experiments/runs/mtf_fib_level_projection/2026-06-05/mtf_proj_20260605T122401Z/`;
   `fib_toplist --run-dir <that>` works directly on `fingerprint_outcomes.jsonl`.
3. DONE — checkpoint + toplist triage on the MTF run
   ([page](reviews/2026-06-05-mtf-fib-projection-checkpoint.md)): toplist stack reusable
   on MTF output; 116 buckets all LOW SAMPLE; no edge/signal/stable claim; 1W->1D
   technically validates HTF=map / LTF=behavior.
4. DONE — BTC 4h fetched (`limit_8000.csv`, 2022-10-31→2026-06-05) and projected:
   1W->4H = 87 interactions (vs 42 on 1D, same fib), 1D->4H = 23. 4H adds interaction
   *resolution* but no stable evidence (toplist watch sets disagree across runs; low N).
   See [MTF checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md).
5. DONE — 4H sample growth: fetched ETH/SOL 4h; ran all 136 base fibs → 4H (combined
   `mtf_proj_20260605T124041Z`): 7453 interactions, 29812 joined, 384 buckets, n≥20=332,
   0 unmatched/0 skipped. 4H sample is now sufficient for descriptive review.
   Caveat: pre-2022 1D fibs project cross-era (SOL 1D→4H = 5415 dominates); prefer
   anchor_b ≥ 2022-10-31 fibs for a clean forward window. See
   [MTF checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md).
6. DONE — cohort split (selection only): clean-forward (anchor_b ≥ 2022-10-31) = 14
   fibs / 617 interactions / n≥20=32 (`mtf_proj_20260605T124444Z`); cross-era = 122
   fibs / 6836 interactions / n≥20=308 (`mtf_proj_20260605T124448Z`). clean-forward is
   BTC+SOL only (all ETH fibs pre-2022). Keep cohorts separate.
7. DONE — clean-forward n≥20 read
   ([page](reviews/2026-06-05-mtf-clean-forward-n20-review.md)): 32 buckets; horizon
   "consistency" is mechanical (nested windows), BTC vs SOL disagree (no shared n≥20
   bucket), rates revert to coin-flip → **clean-forward 4H projection works, but no
   stable evidence yet**.
8. Next (deferred): grow per-symbol clean-forward N (more recent fibs per asset; add
   ETH once recent ETH fibs exist) before any further read. Cross-era stays a separate
   historical-level-revisit track. No edge claims, no logic changes. 1h optional later.

## Guardrails

- Do not treat `*_candidate` as facit.
- Do not add auto-fib or trading signals.
- Do not promote wiki notes into canonical behavior.
- Keep new artifacts small and linked from [index.md](index.md).

## Links

- [Research wiki index](index.md)
- [Atomic runnable artifacts](concepts/atomic-runnable-artifacts.md)
- [Agent handoff and log](concepts/agent-handoff-log.md)
- [Karpathy LLM wiki source](sources/karpathy-llm-wiki.md)
- [Relation vs candidate](concepts/relation-vs-candidate.md)
- [Fib-aware review decision](decisions/2026-06-04-fib-aware-review.md)
