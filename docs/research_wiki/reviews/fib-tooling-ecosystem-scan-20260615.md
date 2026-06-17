# Fib Tooling / Ecosystem Scan (Issue #32, 2026-06-15)

Research / inventory only. **No code, no dependency changes, no generated artifacts, no
source-label changes.** This is a discovery/radar report to decide what to build or copy
next — not an implementation plan.

Constraints honored: no 1H proposed as immediate work, no reaction-review expansion, no
auto-fib, no heavy frameworks, no cloud dashboards, source-facit / visual-confirmation /
reaction-review kept distinct.

---

## Observed / Inferred / Unverified

**Observed** (grounded in the repo, 2026-06-15):
- Runtime deps: `pandas, numpy, ccxt, matplotlib, mplfinance, loguru, pyyaml, pydantic>=2,
  pandera>=0.20, duckdb` ([pyproject.toml](../../../pyproject.toml)).
- Dev deps: `pytest, pytest-cov (fail-under=60), ruff, pre-commit, hypothesis`.
- Schema enforcement already strong: pydantic v2 (`HumanFibAnnotation`), pandera
  dataframe schemas ([validation/schemas.py](../../../src/fibengine/validation/schemas.py)),
  and per-module fail-closed guards (e.g. `_validate_source_fibs` in
  `fourh_source_fib_zoom.py`: timeframe/profile/scale/0.236/human-manual).
- A **markdown index generator already exists** (`_write_index` →
  `fourh_source_fib_map_index.md` in
  [fourh_source_fib_map.py:312](../../../src/fibengine/research/fourh_source_fib_map.py#L312)).
- Single-fib isolation already exists (`--fib-id` in `fourh_source_fib_zoom.py`).
- Artifacts are gitignored under `experiments/review/**`; `check_repo_bounds.py` enforces
  anti-blob + module-size in CI and pre-commit.
- Property-based testing is already in the toolbox (`hypothesis`).

**Inferred** (from this week's 4H Tier 1/Tier 2 pain points):
- The dominant bottleneck is **manual review throughput over many PNGs**, not chart
  generation. The pieces to leverage are review/index/ergonomics — not new charting libs.
- Most fixes are **repo-native and stdlib-only**; almost nothing here justifies a new
  dependency.

**Unverified** (needs a small spike before committing):
- Whether a self-contained HTML gallery renders acceptably for ~100+ images in a local
  browser without a build step.
- Whether any image-regression approach can avoid committing binary baselines (anti-blob
  policy tension).
- The real frequency of overlapping/near-duplicate anchors in dense zones (e.g. 2017_h2).

---

## 1. Executive Summary

The Fib repo already has solid schema enforcement, deterministic tests, and a markdown
index generator. The gaps exposed by the 4H flow are all in **review ergonomics**: (a)
batch image review is slow and unstructured, (b) verdicts/correction-candidates are
tracked ad-hoc in prose, (c) dense zones risk duplicate/overlapping anchors with no
detector, (d) the body/close-vs-wick convention is undocumented, (e) the labeling GUI is
too cluttered for safe single-fib correction.

None of these need a framework. The three highest-ROI moves are **stdlib-only**: a static
HTML gallery (extend the existing index generator), a structured review-ledger pattern,
and a label-overlap detector paired with a documented anchor convention.

## 2. Current Repo Capability Snapshot

| Capability | Status | Evidence |
|---|---|---|
| Candlestick charting | ✅ Have | matplotlib + mplfinance |
| Schema/label validation | ✅ Strong | pydantic + pandera + fail-closed guards |
| Time-series quality checks | ✅ Partial | pandera; preflight cache checks |
| Deterministic tests | ✅ Have | pytest, pytest-cov, hypothesis |
| Artifact markdown index | ✅ Have | `_write_index` (map module) |
| Single-fib isolation | ✅ Have | `--fib-id` (zoom module) |
| Repo hygiene / anti-blob | ✅ Have | `check_repo_bounds.py` (CI + hook) |
| **Static HTML image gallery** | ❌ Gap | only markdown index exists |
| **Structured review ledger** | ❌ Gap | verdicts tracked in prose (this week) |
| **Label overlap/dedup detection** | ❌ Gap | none |
| **Visual regression / golden images** | ❌ Gap | no pytest-mpl / baseline set |
| **Anchor convention (body/close)** | ❌ Gap | observed but undocumented |
| **Single-fib declutter edit mode** | ❌ Gap | GUI shows all fibs + HTF overlays |

## 3. Core-Category Findings (Layer 1)

1. **Financial charting** — mplfinance is sufficient; the Tier1/Tier2 split already
   solved density. No change. *(reject new charting libs.)*
2. **Static artifact galleries** — **gap.** Best fit: extend the existing `_write_index`
   to emit a self-contained HTML file (inline `<img>` + simple JS filter by scope/verdict).
   Stdlib only. *(adopt-pattern; build later via follow-up.)*
3. **Visual regression** — candidate: `pytest-mpl` (matplotlib-native) or the
   already-transitively-available `matplotlib.testing.compare.compare_images`. Tension:
   golden PNGs are binary blobs vs anti-blob policy. *(evaluate later; prefer
   structural/hash assertions over committed baselines.)*
4. **Manual labeling UI patterns** — heavy platforms (Label Studio, CVAT) are overkill for
   solo fib labeling. The actionable pattern is a **single-fib edit mode** in the existing
   tool (load one fib's anchors, hide overlays). *(copy-pattern; later, separate issue.)*
5. **Data/schema enforcement** — already strong. Optional: export a JSON Schema via
   pydantic `model_json_schema()` as self-documenting facit spec (no new dep).
   *(evaluate later.)*
6. **Time-series quality checks** — pandera covers dataframe-level; gap-detection for
   candle cache continuity could be a small pandera check. *(document gap.)*
7. **Dedup / overlap detection** — **gap.** No library needed: interval-overlap / IoU on
   (time-span × log-price-span) of anchors, surfaced as a research/validation pass.
   *(adopt-pattern; high value in dense zones.)*
8. **Research artifact indexing** — markdown index exists; HTML gallery is the upgrade
   (see #2).
9. **Review workflows for large image batches** — **gap.** A **review ledger** (CSV or
   markdown: fib_id, scope, verdict, note, status) formalizes exactly the manual pass we
   ran this week. *(adopt-pattern.)*
10. **Lightweight local dashboards** — static HTML is the right answer; *(reject
    Streamlit/Dash/Panel — webserver + heavy.)*
11. **Markdown/report generation** — f-strings already work; `tabulate` is tiny but
    unnecessary. *(reject for now.)*
12. **Test infra / golden-file patterns** — for non-image data (e.g. computed levels,
    index contents) golden-text files are cheap and policy-safe. *(adopt-pattern for
    text, not images.)*
13. **CLI ergonomics** — argparse is consistent across modules; a shared `--fib-id`/
    `--scope` convention is already emerging. Optional: a thin `rich`-free status print
    helper. *(document; low priority.)*
14. **Plot performance** — Agg backend handles batch fine; *(reject datashader / accel
    libs — overkill.)*

## 4. Open-Discovery Findings (Layer 2)

- **Verdict provenance gap.** This week's verdicts (OK / watchlist / correction-candidate)
  live only in prose review docs. There is no machine-readable link from a verdict back to
  the exact artifact + facit version it was based on. Reveals a need for a small review
  ledger with a content hash of the source fib JSON. *(document gap → follow-up.)*
- **Correction-candidate lifecycle gap.** `20171228T200000` is now a deferred
  correction-candidate with no tracked state beyond the markdown. A ledger with a `status`
  column (candidate → in-progress → corrected) closes this. *(document gap.)*
- **Anchor-convention gap.** Body/close-vs-wick is a real, repeatedly-observed convention
  with no doc. This is a **documentation** fix, not a tooling one. *(copy-pattern: one
  paragraph in labeling docs + a validator that warns if an anchor sits on a wick extreme
  far from body/close.)*
- **GUI declutter gap.** Correction was blocked purely by visual clutter — a leverage
  point the categories above only partly cover. *(copy-pattern: single-fib edit mode.)*

## 5. Candidate Tool / Pattern Table

| Name | Solves | Fit | Decision |
|---|---|---|---|
| **Static HTML gallery (stdlib, extend `_write_index`)** | Batch PNG review | Excellent; no dep | **Adopt-pattern (build later)** |
| **Review ledger (CSV/markdown + source-hash)** | Verdict tracking, correction lifecycle | Excellent; no dep | **Adopt-pattern** |
| **Anchor overlap/IoU detector (stdlib)** | Duplicate/overlap anchors in dense zones | Strong; no dep | **Adopt-pattern** |
| **Anchor-convention doc + wick-distance warning** | body/close metoddoc | Strong; doc + tiny check | **Adopt-pattern** |
| `pytest-mpl` / `matplotlib.testing.compare` | Chart visual regression | Partial; binary-baseline tension | **Evaluate later** |
| pydantic `model_json_schema()` export | Self-documenting facit schema | OK; no dep | **Evaluate later** |
| Single-fib declutter edit mode (in `tool.py`) | Safe correction-pass | Strong; code change, separate issue | **Evaluate later** |
| `tabulate` | Pretty tables | Minor; f-strings suffice | **Reject** |

## 6. Rejected Options and Why

- **Streamlit / Dash / Panel / Gradio** — webserver + heavy deps; violates "no webserver"
  and "no heavy frameworks." Static HTML covers the need.
- **Plotly / Bokeh** — interactive but new deps; mplfinance already sufficient.
- **Label Studio / CVAT** — full annotation platforms; massive overkill for solo
  human-fib labeling.
- **DVC / MLflow / Weights & Biases** — artifact/experiment tracking heavyweight;
  gitignore + markdown/HTML index + a CSV ledger is enough at this scale.
- **great-expectations** — heavy vs the existing pandera + pydantic stack.
- **datashader** — large-scale rendering accel; irrelevant at current data sizes.
- **sigal / thumbsup** (gallery generators) — extra deps for what a stdlib f-string
  template does.

## 7. High-ROI Repo-Native Adaptations

All three reuse existing primitives and add **zero** dependencies:

1. **HTML gallery** = generalize `_write_index` to emit `index.html` alongside the
   existing `.md`, with `<img>` thumbnails grouped by scope and inline verdict slots.
2. **Review ledger** = a small append-only CSV/markdown (fib_id, scope, verdict, note,
   status, source-hash) — formalizing this week's manual pass; lives under
   `docs/research_wiki/reviews/` (text, policy-safe).
3. **Overlap detector** = a research/validation function computing time×log-price overlap
   between anchor spans; reports near-duplicates for human triage.

## 8. Risks and Verification Requirements

- **Anti-blob tension:** any image-regression baseline set risks committing binaries.
  *Verify* a non-binary strategy (structural/hash assertions) before adopting golden
  images. Galleries themselves stay gitignored (like current PNGs).
- **Scope creep:** a "review ledger" must not drift into reaction-review or auto-fib.
  Keep it source-quality-only with an explicit column meaning.
- **GUI edit mode** is a real code change — out of scope for #32; must be its own
  approved issue with tests.
- **No dependency** should be added without a follow-up issue showing a stdlib approach
  was insufficient.

## 9. Suggested Follow-up Issues

- **#A — Static HTML artifact gallery (stdlib):** extend `_write_index` to emit
  self-contained `index.html`; gitignored output. *(highest ROI.)*
- **#B — Source-quality review ledger:** CSV/markdown schema + source-fib content hash;
  migrate this week's verdicts + the `20171228` correction-candidate into it.
- **#C — Anchor overlap/dedup validator + anchor-convention doc:** stdlib overlap check +
  one labeling-docs paragraph on body/close vs wick.
- **#D (later) — Single-fib declutter edit mode** in `labeling/tool.py` (the
  `20171228` correction blocker).
- **#E (later) — Chart regression strategy** spike: structural/hash vs `pytest-mpl`,
  resolving the binary-baseline question.

## 10. Final Recommendation — Top 3 Next Actions

1. **Static HTML gallery** (follow-up #A) — biggest review-throughput win; pure stdlib;
   directly fixes "many artifacts, hard to review."
2. **Source-quality review ledger** (follow-up #B) — makes verdicts and correction
   candidates (like `20171228`) machine-trackable instead of prose-only.
3. **Overlap detector + anchor-convention doc** (follow-up #C) — closes the duplicate-risk
   and body/close gaps surfaced repeatedly in 4H.

Defer (per current rules): visual regression strategy, single-fib GUI edit mode, JSON
Schema export. **No 1H, no reaction-review expansion, no auto-fib.** This report adds no
code, no dependencies, and no artifacts.
