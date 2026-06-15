# BTC/USD Source-Fib — Next Research Pass (Design, 2026-06-15)

Read-only research design. **Docs-only — no code, no source-label changes, no artifacts,
no deps.** Question: with the BTC/USD source-fib corpus now in a clean state, what is the
highest-ROI next research pass?

Scope guards honored: no 1H, no reaction-review expansion, no auto-fib, no trading
conclusions, no ML/Optuna/tuning, no new tooling, no committed artifacts. Fib stays a
research workshop, not a Genesis-heavy pipeline.

---

## Observed

- Corpus on disk (base `fib_*.json`, `*_events.json`/`*_interactions.csv` sidecars
  excluded — verified by `ls | grep -v`): **1M=9, 1w=21, 1d=67, 4h=365**. Matches
  [INDEX.md](../../../data/labels/INDEX.md) and [handoff.md](../handoff.md).
- All ladders: log scale, profile `tradingview_log_chamoun`, levels
  `[0, 0.382, 0.5, 0.618, 0.786, 1]` (no 0.236), endpoint mapping 0.0=anchor_b /
  1.0=anchor_a, human/manual origin. Coverage 2017-01-05 → 2026-06-05.
- 4H corpus is **post-triage clean**: Tier 1 map (11 annual groups, 366 drawn) + Tier 2
  zoom sample-pass done; `20171228` anchor_a corrected; `20250506` near-duplicate
  superseded (366→365). Verdicts tracked in the
  [source-quality ledger](ledgers/btc-4h-source-quality-ledger.csv).
- Reusable research modules already exist (no new tooling needed for the leading options):
  - `research/overlap_detector.py` — boxes fibs in (time, log-price), box-IoU +
    shared-anchor near-duplicate/overlap detection. **Currently 4H-only** (`require_timeframe="4h"`).
  - `research/monthly_fib_map.py` — `_draw_map`/`_load_fibs`/`_nearest_pos`/`_short_id`
    primitives (log y-axis); the base for every combined-map flow.
  - `research/weekly_source_fib_map.py` — combined 1W/1D/4H map (1W/1D usable, combined 4H
    too compressed); `research/weekly_source_fib_zoom.py` — per-fib 4H zoom.
  - `research/fourh_source_fib_map.py` / `fourh_source_fib_zoom.py` — 4H annual map + per-fib zoom.
  - `research/mtf_fib_level_projection.py` — existing MTF level-projection math.
  - `research/render_summary.py` — stdlib structural summaries + golden JSON (verification
    layer for any new render).
  - `research/artifact_gallery.py`, `research/review_ledger.py`, `research/ledger_query.py`
    — gallery / verdict ledger / queries.
- 1H is paused (cache not fetched). ETH/USD is blocked until BTC protocol sign-off.

## Inferred

- The corpus was *just* declared clean; the natural capstone is a **read-only integrity
  report that closes the dataset as a research base** — near-zero scope-creep risk, ~no
  code, and it produces the "known caveats" foundation any later analytical pass should
  build on.
- The richest *insight* pass is a **MTF confluence atlas** (where 1M/1W/1D/4H source-fib
  level families cluster in price/time). It reuses `overlap_detector` + `monthly_fib_map`
  primitives, but cross-TF log-price alignment + a proximity threshold + time-window
  overlap is genuinely more complex than it reads → highest scope-creep risk of the five.
- Options #3 (4H-only behavior) and #4 (ETH source-facit) are **user-deferred by the
  user's own framing** ("måste hållas som observation"; "kanske senare") — treat as lower
  priority, not equal contenders. #5 (combined source-map review) is largely the **visual
  companion** to #1, not an independent track.

## Unverified

- Whether a useful cross-TF confluence threshold exists at all (price proximity in log
  space + time overlap) before measuring it — the atlas could surface few or noisy
  clusters; that is itself a finding, not a failure.
- Exact extension cost to make `overlap_detector` multi-timeframe (it is 4H-fail-closed
  today) — assumed small but not measured.
- Whether the combined 4H layer renders legibly at MTF scale (weekly map already showed
  combined 4H "too compressed") — likely needs per-window slicing, not a single chart.

---

## Alternatives compared

Each alternative answers: **solves / data / reusable / scope-creep risk / smallest safe
slice / useful outputs / verification needs / do-not.**

### #1 — MTF confluence atlas

- **Solves:** where 1M/1W/1D/4H source-fib level families cluster in price/time — shows the
  corpus's structural "hot zones" as a map.
- **Data:** all four TFs' `fib_*.json` levels (log prices) + anchor time spans.
- **Reusable:** `overlap_detector.py` (extend beyond 4H), `monthly_fib_map.py` primitives,
  `mtf_fib_level_projection.py`, `render_summary.py` (verify any render).
- **Scope-creep risk:** **highest.** Cross-TF log-price proximity threshold, time-window
  overlap, multi-TF rendering, and the temptation to interpret clusters as
  signals/levels-that-work (forbidden).
- **Smallest safe slice:** a **read-only confluence table** (no chart) — for a fixed price
  band, list which TFs have a level within ε (log) over a shared time window. Counts only.
- **Useful outputs:** confluence table CSV (gitignored or docs), later a windowed atlas chart.
- **Verification:** every cited level traces to a real `fib_*.json`; `render_summary`
  golden test if a chart is added; threshold ε stated and held constant.
- **Do-not:** call a cluster a tradeable level; auto-generate fibs; tune ε to taste.

### #2 — Source-fib corpus integrity report  ⟵ leading slice

- **Solves:** closes the dataset as a stable research base — counts, coverage, up/down,
  corrections, superseded, known caveats, conventions in one authoritative read-only doc.
- **Data:** the four `fib_*.json` dirs + ledger + correction/dedup reports + INDEX/handoff.
- **Reusable:** `review_ledger.py`/`ledger_query.py` (read verdicts), `ledger_query` for
  rollups; no rendering. Likely **zero new code** (pure aggregation/prose).
- **Scope-creep risk:** **lowest.** Read-only aggregation of facts already established.
- **Smallest safe slice:** the report itself — per-TF counts (sidecar-excluded), coverage
  span, up/down split, the two known caveats (body/close-vs-wick convention; 20171228
  correction + 20250506 supersede), cross-links to ledger/reports.
- **Useful outputs:** one canonical integrity doc; an INDEX/handoff cross-link.
- **Verification:** counts via `ls fib_*.json | grep -v _events|_interactions`; ledger via
  `review_ledger --validate`; every claim cites a committed file.
- **Do-not:** introduce new analysis or verdicts; re-open closed phases; touch labels.

### #3 — 4H-only behavior study (no 1H)

- **Solves:** how 4H candles behave around active 4H source levels — descriptive only.
- **Data:** 4H `fib_*.json` levels + 4H candle cache.
- **Reusable:** `level_events.py`, `human_review_level_events.py`, `source_fib_projection_*`.
- **Scope-creep risk:** **high — user-flagged.** Easily becomes reaction-review expansion or
  an implied edge claim.
- **Smallest safe slice:** observation of one well-understood fib's level touches, counts
  only, explicitly labeled "observation, not reaction-review."
- **Useful outputs:** a touch-count observation note.
- **Verification:** counts reproduce from cache; no outcome/PnL framing.
- **Do-not:** expand to all 365 fibs; compute win-rates; conclude tradability.

### #4 — ETH/USD next source-facit

- **Solves:** begins generalizing the protocol to a second market.
- **Data:** ETH/USD candle cache (must be fetched) + new manual labels (none yet).
- **Reusable:** entire labeling/preflight/fetch stack; protocol doc.
- **Scope-creep risk:** moderate, but **gated** — blocked until BTC protocol sign-off;
  high manual cost.
- **Smallest safe slice:** none yet — it is a new labeling effort, not a research pass on
  the existing corpus. Out of scope for "use the clean BTC corpus."
- **Useful outputs:** (future) ETH 1M source fibs.
- **Verification:** preflight + schema, as with BTC.
- **Do-not:** start before explicit sign-off; mix ETH into BTC facit/index.

### #5 — MTF combined source-map review

- **Solves:** visual check that active 1M/1W/1D/4H source levels read as a usable map on
  shared windows — "is the corpus navigable?"
- **Data:** all four TFs' levels on common chart windows.
- **Reusable:** `weekly_source_fib_map.py` (already combines 1W/1D/4H), `monthly_fib_map`
  primitives, `render_summary` (verify).
- **Scope-creep risk:** moderate — combined 4H legibility (weekly map already showed it too
  compressed) tempts per-window proliferation.
- **Smallest safe slice:** one shared window (e.g. one cycle leg) rendered with 1M+1W+1D
  only (defer 4H legibility); visual-only.
- **Useful outputs:** a small set of windowed combined maps (gitignored).
- **Verification:** `render_summary` golden snapshot; every level traces to a real fib.
- **Do-not:** treat the map as a signal source; force all 365 4H fibs onto one chart.

### Summary matrix

| # | Pass | Insight | Code | Scope-creep | Safe-slice cost | Status |
|---|------|--------|------|-------------|-----------------|--------|
| **#2** | Corpus integrity report | medium | **~none** | **lowest** | **smallest** | **Recommend now** |
| #1 | MTF confluence atlas | **highest** | medium | highest | small (table-only) | **Next analytical pass** |
| #5 | Combined source-map review | medium | low–med | moderate | small | Visual companion to #1 |
| #3 | 4H-only behavior study | medium | medium | high (user-flagged) | small | Defer (observation-only) |
| #4 | ETH/USD source-facit | high (long-term) | high (manual) | gated | n/a (new labeling) | Defer (blocked) |

---

## Recommendation

**Do #2 (corpus integrity report) next**, then **#1 (MTF confluence atlas) as the
designated follow-on analytical pass**, with #1's first slice a *read-only confluence
table* (no chart). Rationale: #2 is the highest-certainty, lowest-risk step and the natural
capstone for a corpus just declared clean; it produces the "known caveats" base that #1
should build on. #5 is folded in as #1's visual companion. #3 and #4 stay deferred per the
user's own framing.

### Smallest implementation slice (for #2)

A single docs-only report — e.g.
`docs/research_wiki/reviews/btc-source-fib-corpus-integrity-20260615.md` — containing:
per-TF base counts (sidecar-excluded) + up/down split, coverage span, ladder conventions,
the two known caveats (body/close-vs-wick; 20171228 correction + 20250506 supersede),
ledger summary (via `ledger_query`), and cross-links. **No code unless a one-shot read-only
rollup is trivially small and stdlib.** No artifacts, no labels.

---

## Non-goals (explicit)

- No 1H. No reaction-review expansion. No auto-fib. No trading conclusions / edge claims.
- No ML / Optuna / tuning. No new tooling for #2. No committed artifacts/PNGs/blobs.
- No source-label changes. No ETH/USD work before BTC sign-off. No re-opening closed phases.

## Acceptance criteria (for this design doc)

- Docs-only; no code, no artifacts, no source-labels, no deps. ✔ (this file only)
- All five alternatives compared on all eight sub-questions. ✔
- One clear singular recommendation + smallest safe slice + explicit non-goals. ✔
- Counts verified sidecar-excluded; every claim cites a committed file. ✔
- Indexed in [reviews/README.md](README.md). (added with this doc)

## Recommended next Claude prompt

> Kör nästa pass: **BTC/USD source-fib corpus integrity report** (Alternativ #2 från
> next-research-plan-20260615). Read-only/docs-first. Skapa
> `docs/research_wiki/reviews/btc-source-fib-corpus-integrity-20260615.md`:
> per-TF base counts (sidecar-exkluderade: `ls fib_*.json | grep -v _events|_interactions`),
> coverage-span, up/down, ladder-konventioner, de två kända caveats (body/close-vs-wick;
> 20171228 correction + 20250506 supersede), ledger-sammanfattning (`ledger_query`),
> cross-links till ledger/INDEX/handoff. **Inga source-label ändringar, ingen 1H, ingen
> reaction-review, ingen auto-fib, inga trading-slutsatser, inga deps, inga committade
> artifacts.** Kod endast om en engångs read-only rollup är trivialt liten och stdlib.
> Uppdatera reviews/README.md + ev. handoff "Next Useful Action" (respektera 300-rad-bound).
> Docs-only commit om rapporten är bra. Därefter: stanna och erbjud #1 (MTF confluence
> atlas, table-first) som nästa analytiska pass.
