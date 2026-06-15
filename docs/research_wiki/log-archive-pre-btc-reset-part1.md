# Archived wiki log (pre-BTC monthly reset, part 1)

Moved from log.md on 2026-06-09. Part 1 of 3. Next: [part 2](log-archive-pre-btc-reset-part2.md).

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

