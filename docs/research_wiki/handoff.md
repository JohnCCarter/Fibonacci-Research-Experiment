# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

**BTC monthly-first top-down protocol** — re-labeling on BTC/USD only after the
**2026-06-09 log-scale + profile reset** (prior linear / 0.236 labels archived).

**Canonical protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

| Step | Timeframe | Status |
|------|-----------|--------|
| 1 | **1M** | **Complete** — 9× source fibs, 1D + 4H reaction review approved (2026-06-11) |
| 2 | **1W** | **Complete** — 21× source fibs verified; combined map + per-fib 4H zoom (2026-06-11) |
| 3 | **1D** | **Complete** — 67× source fibs + 4H reaction-review (2026-06-12); 1816 events, 90-day window |
| 4 | **4H** | **Complete** — 365 active source fibs (366 drawn; 1 superseded 20250506 dedup) |
| 5 | 1H | Deferred — 1h cache not fetched yet |

**ETH/USD:** blocked until BTC protocol approved.

## Recent Changes

- **2026-06-17 External-pattern-scan absorption — landed on `main`** (PR #33→main, merge-commit;
  plan `clever-yawning-catmull.md`). NU (docs): standing
  [prereg addendum](reviews/horizontal-structure-prereg-addendum-20260617.md) (random-walk control /
  anytime-valid re-looks / embargo named as purged-CV). DELAR (code): synthetic RW baseline,
  uncertainty-ordered worklist (`--by-uncertainty`), fail-closed swing-label validation. SENARE gated.
  Review fixes: P1 windowed-save facit-safety, P2 level-events now log-scale. Sec (PR #34):
  cryptography→49.0.0 (GHSA-537c-gmf6-5ccf). No facit/signal/auto-fib touch.
- **2026-06-16 BTC/Fib studies — BOTH NULL, reviewed PASS / CLOSED** (commit `f4e96f1`, Lean Fib).
  **(1) Behaviour event study:** fib ≈ placebo ≈ swing (4h reject 0.78/0.80/0.84, p=0.63/0.19).
  **(2) Context-conditioned** (continuous MFE−MAE, rank-perm + Holm; contexts trend + deep
  0.618/0.786): no context passes — fib beats *random placebo* only nominally (p=0.042/0.056, fails
  Holm) and **never beats swing**. **Insight:** any faint level-reaction is generic horizontal
  structure, not Fibonacci. Both gates fail → **no strategy work.** Code:
  `fib_behaviour_event_study.py` (19 tests) + `fib_context_conditioned_study.py` (17); preregs +
  results `reviews/btc-fib-*-20260616.md`.
- **2026-06-16 Fib → Genesis V2 Phase 2.5 feature nullability policy — reviewed PASS / CLOSED**
  (docs-only) — pins how the future bar feature table represents empty values (3 states; distances
  null not 0/inf; empty-meta ⇔ no-known-zone; dense-table + no-imputation consumer rules).
  Precondition for any real export. **Open (non-blocking):** is `has_robust_4tf_zone_nearby`
  log-price- or ATR-thresholded (latter ⇒ warmup-null / availability flag).
  [Policy](reviews/btc-fib-to-genesis-v2-feature-nullability-policy-20260616.md).
- **2026-06-16 Fib → Genesis V2 Phase 2 dummy contract test — reviewed PASS / CLOSED** —
  mechanical contract/dummy test **inside Fib only** (not export, not Genesis integration).
  `research/feature_contract.py` (stdlib) validates two committed dummy CSVs vs the Phase 1
  schema (join keys, causality, knowability floor, 1H + feature/metadata fail-closed). No fib
  computation, no Genesis touch. 20 tests; gates green. Commit `68dc006`; **human review PASS**
  2026-06-16. Follow-up for any *real* export: define a **nullability policy** for feature
  columns. [Report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md).
- **2026-06-15 MTF confluence CP1–CP3 CLOSED + interpretation/decision note** — first atlas
  pack done (5 cards, 3 archetypes, all **human-approved**): c001 robust fixed-band 4-TF; c002
  chaining-dependent contrast (NOT tight); c004/c006/c007 zero-span exact-price 3-TF.
  [Decision note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md): confluence
  is **geometry, not edge proof** → **rec: stop MTF track**; next = pause Fib or new question.
- **2026-06-15 Structural chart-contract snapshots (#F)** — `research/render_summary.py`
  (stdlib): stable text summaries of map/zoom/gallery renders + golden JSON under
  `tests/research/snapshots/`. Automatic structural regression; no PNG baselines/deps.
- **2026-06-15 20171228 source fib corrected** — preview-first flow: anchor_a moved
  2017-12-28T20:00 @ 13611 → 2017-12-28T08:00 @ 13145 (candidate_1). Only anchor_a + levels
  changed; anchor_b/fib_id unchanged; guard PASS; ledger candidate → corrected. Closes the
  declutter→correction→ledger track. [Report](reviews/btc-4h-fib-20171228-correction-20260615.md).
- **2026-06-15 Issue #32 top-ROI tooling — DONE** (declutter edit-mode, overlap detector, review
  ledger, artifact gallery; all stdlib). Detail in [log part 1](log-archive-btc-postreset-part1.md).
- **2026-06-15 4H Tier 1 + Tier 2 visual reviews — complete** (11 groups; `20171228` corrected;
  corpus clean). Archived to [log part 1](log-archive-btc-postreset-part1.md).
- **2026-06-08→06-12 source-fib milestones (archived)** — 1M/1W/1D/4H source phases, reaction
  reviews (1816 interactions), 4H Tier 1 maps, Addendum 2 golden-zone retirement (#30), log-scale
  + profile fix + monthly-first reset. Detail: [log post-reset part 1](log-archive-btc-postreset-part1.md)
  + [log.md](log.md); current counts in Verification Snapshot below.

## Verification Snapshot

- `data/labels/human_fib/bitfinex/BTC-USD/1M/` — **9** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1w/` — **21** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1d/` — **67** base `fib_*.json` (log scale);
  source-facit complete, verified 2026-06-11.
- `data/labels/human_fib/bitfinex/BTC-USD/4h/` — **365** active base `fib_*.json` (log scale;
  366 drawn 2026-06-12, 1 superseded via 20250506 dedup 2026-06-15). Coverage 2017-01-05 →
  2026-06-05.
- `experiments/review/weekly_source_fib_map/` and `…/weekly_source_fib_zoom/` —
  generated charts (gitignored; regenerate via the two new CLIs).
- `data/raw/bitfinex/BTC-USD/1M/limit_500.csv` — 115 bars (2016-12 .. 2026-06),
  fetched with `--config config/settings.expansion.yaml` to cover old anchors.
- `experiments/review/fib_level_events/` — active 1M pack `human_fib_review_20260609T135548Z`.
- Pre-reset archive (local disk; git tracks manifest only):
  [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)

## Open Questions

- Minimum monthly fib count before 1W mapping?

## Status — BTC/Fib behaviour/backtest line PAUSED / CLOSED (2026-06-16, reviewed PASS)

Commit `f4e96f1` reviewed **PASS / CLOSED**. Final conclusion (both studies):

- **Unconditioned** [Behaviour Event Study](reviews/btc-fib-behaviour-event-study-results-20260616.md):
  **no signal.**
- **Context-Conditioned** [Study](reviews/btc-fib-context-conditioned-study-results-20260616.md):
  **no candidate.**
- **Fib does not beat the placebo/swing baselines** on the current BTC corpus. The swing baseline
  **matches or beats** fib; the weak level reaction is **generic horizontal structure, not
  Fibonacci-specific.**
- **Strategy sanity-check: not authorised, not run.**

**Discipline (binding):** do **not** re-run these studies on the same BTC data with tweaked
parameters. Any future behaviour test must be a **new prereg on fresh data** or a **materially
different question**. **No active next implementation is authorised.**

### Future possible tracks (listed only — none started, none authorised)

- Fresh-data validation on other symbols/timeframes — **requires a new prereg.**
- Source-label quality review / correction-candidate cleanup.
- Non-fib **horizontal structure** research (swing baseline performed at least as well).
- Separate visual / research **tooling** improvements.
- **Genesis/Fib remains paused** unless explicitly reopened.

**Milestone:** Issue #32 top-3 complete + pushed (gallery `8f1e7a8`, ledger `d6ab9ec`,
overlap detector + anchor convention `84b42db`). local == origin, tree clean, source-fib
JSON unchanged, no new deps, no artifacts committed.

**#32 tooling track — all DONE** (single-fib declutter edit-mode, `20171228` correction,
chart-regression spike + #F render_summary/golden snapshots; detail in [log.md](log.md)).
**Corpus declared clean and
locked** (integrity capstone 2026-06-15:
[`reviews/btc-source-fib-corpus-integrity-20260615.md`](reviews/btc-source-fib-corpus-integrity-20260615.md)).
**MTF confluence track CP1–CP3 — CLOSED.** CP1 ([table](reviews/btc-mtf-confluence-table-20260615.md))
+ CP2 ([sensitivity](reviews/btc-mtf-confluence-sensitivity-20260615.md)) + CP3
([capstone](reviews/btc-mtf-confluence-atlas-cp3-20260615.md)) done — 5 cards, 3 archetypes,
**all human-approved**. [Decision note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md):
confluence is **geometry, not edge proof** → **stop the MTF track**. **Fork written up
(docs-only):** [Phase 0 prereg](reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md) registers
one falsifiable behaviour question (causal confluence zones vs placebo/naïve levels, OOS) +
leakage manifest, baselines, time-split holdout, stop/go; [Phase 1 spec](reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md)
(zone+bar tables, `known_after_ts` rule) **reviewed PASS — Phase 1 closed as docs-only contract**. **Phase 2 (dummy-file test) — reviewed PASS / CLOSED 2026-06-16** (authorised narrow slice,
commit `68dc006`): `research/feature_contract.py` + committed dummy CSVs prove the contract
validates mechanically with no real export and no Genesis touch
([Phase 2 report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md)). **Stopped**
— any real export or Genesis touch needs a fresh go; first define a feature-column **nullability
policy**. No Phase 3.

**Deferred:** 1H source labeling — 4H is the lowest active timeframe; fetch 1H cache first
(`data.fetch --timeframes 1h`). Separate decision before starting.

## Guardrails

- Do not treat archived ledgers/reviews as current evidence.
- Do not treat `*_candidate` as facit.
- No ETH/SOL analysis until BTC protocol sign-off.
- No auto-fib or trading signals.

## Startup on another machine

Use this checklist when resuming from a home computer or any machine that does
not have the current working tree.

### Before leaving the current machine

- All code, tests, wiki, and data changes committed and pushed (`git status` clean).
- Gitignored review artifacts (`experiments/review/`) copied as a ZIP if wanted
  (optional — see restore step below).
- No required local-only state remains: committed facit (`fib_*.json`,
  `review_windows.yaml`) and wiki docs are the source of truth.

### On the new machine

**Bash:**
```bash
git pull
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_repo_bounds.py
```

**PowerShell:**
```powershell
git pull
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_repo_bounds.py
```

### BTC/USD candle-cache setup

`data/raw/` is gitignored — fetch it fresh:

**Bash:**
```bash
uv run --no-sync python -m fibengine.data.fetch \
  --symbols BTC/USD \
  --timeframes "1M,1w,1d,4h" \
  --refresh \
  --config config/settings.expansion.yaml
```

**PowerShell:**
```powershell
uv run --no-sync python -m fibengine.data.fetch `
  --symbols BTC/USD `
  --timeframes "1M,1w,1d,4h" `
  --refresh `
  --config config/settings.expansion.yaml
```

### Labeling preflight

Confirms cache is complete for all active TFs before opening the labeling tool:

**Bash:**
```bash
uv run --no-sync python -m fibengine.labeling.preflight \
  --symbol BTC/USD \
  --timeframes "1M,1w,1d,4h,1h" \
  --config config/settings.expansion.yaml
```

**PowerShell:**
```powershell
uv run --no-sync python -m fibengine.labeling.preflight `
  --symbol BTC/USD `
  --timeframes "1M,1w,1d,4h,1h" `
  --config config/settings.expansion.yaml
```

Expected: 1M/1w/1d/4h pass; 1h FAIL (cache not fetched yet — deferred).

### Optional: restore local review artifacts

`experiments/review/` is gitignored. The completed 1M review packages can be
restored from the ZIP if you want the charts and CSV files locally:

**Bash:**
```bash
unzip btc-1m-reaction-review-artifacts-20260611.zip -d .
```

**PowerShell:**
```powershell
Expand-Archive -Path btc-1m-reaction-review-artifacts-20260611.zip -DestinationPath .
```

This is **optional**. The committed repo files (`fib_*.json`, `review_windows.yaml`,
`btc-1m-reaction-review-cycle-20260611.md`) remain the source of truth.
Artifacts under `experiments/review/` are local convenience files only.

### Windows / Symantec SEP note

Plain `uv run` triggers a full `.venv` rebuild scan on each invocation when
Symantec Auto-Protect is active. Mitigate:

- Prefer `uv run --no-sync` for all run commands after the initial `uv sync`.
- Set `PYTHONDONTWRITEBYTECODE=1` (user-scope env var) to suppress `.pyc`
  generation and reduce scan surface.

**PowerShell — set env var for current session:**
```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
```

**PowerShell — set permanently (user scope):**
```powershell
[System.Environment]::SetEnvironmentVariable("PYTHONDONTWRITEBYTECODE", "1", "User")
```

### Resume point

- **BTC/USD 1M phase is complete.** 9 source fibs, 1D + 4H reaction review
  approved 2026-06-11. Do not resume unless an explicit bug or gap is found.
- **BTC/USD 1W source-fib phase is complete.** 21 source fibs verified;
  visual confirmation via `weekly_source_fib_map` (combined 1W/1D/4H) and
  `weekly_source_fib_zoom` (per-fib 4H). Combined 4H is too compressed — use
  the per-fib zoom for 4H. Do not resume unless a bug or gap is found.
- **BTC/USD 1D phase is complete.** 67 source fibs (2017-01-05 → 2024-12-20) and
  4H reaction-review (2026-06-12). 1816 4H interactions, 90-day windows.
  Summary: `docs/research_wiki/reviews/btc-1d-reaction-review-cycle-20260612.md`.
  Do not resume unless a bug or gap is found.
- **BTC/USD 4H source-fib phase is complete.** 366 source fibs (2017-01-05 → 2026-06-05),
  up=169 / down=197, 366/366 schema PASS (2026-06-12). Do not resume unless a bug or gap
  is found. 4H is the current lowest active timeframe (1H paused).
- **4H visual confirmation Tier 1 + Tier 2 sample-pass complete** (2026-06-15). Tier 1:
  `research/fourh_source_fib_map.py`, 11 annual groups, 366/366 drawn. Tier 2:
  `research/fourh_source_fib_zoom.py`, 103+37 fibs rendered; first manual sample-pass (8
  fibs) shows no suspicious labels. Two watchlist items: `20171228` (short-span) and
  body/close vs wick convention (undocumented). Do not start with 1H. Do not start with
  reaction-review. Review:
  [`reviews/btc-4h-tier2-sample-review-20260615.md`](reviews/btc-4h-tier2-sample-review-20260615.md).
- Do not auto-fib. Do not infer anchors. Keep the four flows distinct: 1M source /
  1M→1W projection / true 1W source / true 1D source fibs.

## Links

- [BTC-first protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
