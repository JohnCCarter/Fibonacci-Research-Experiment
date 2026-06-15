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

- **2026-06-15 MTF confluence atlas CP3 (c001 approved + c002 contrast)** — `research/mtf_confluence_atlas.py`
  now method-aware (`--cluster c001|c002`). c001 (fixed-band, tight 4-TF) **human-approved**.
  c002 (single-linkage, span 0.00627 > ε → **chaining-dependent**, dissolves under fixed-band;
  never labelled tight). Member-reconstruction tolerance fix + fail-closed count check (c001
  unchanged). 404 tests green. c002 **pending human inspection.** [Report](reviews/btc-mtf-confluence-atlas-cp3-c002-20260615.md).
- **2026-06-15 Structural chart-contract snapshots (#F)** — `research/render_summary.py`
  (stdlib): stable text summaries of map/zoom/gallery renders + golden JSON under
  `tests/research/snapshots/`. Automatic structural regression; no PNG baselines/deps.
- **2026-06-15 20171228 source fib corrected** — preview-first flow: anchor_a moved
  2017-12-28T20:00 @ 13611 → 2017-12-28T08:00 @ 13145 (candidate_1). Only anchor_a + levels
  changed; anchor_b/fib_id unchanged; guard PASS; ledger candidate → corrected. Closes the
  declutter→correction→ledger track. [Report](reviews/btc-4h-fib-20171228-correction-20260615.md).
- **2026-06-15 Single-fib declutter edit-mode** — `labeling/tool.py --edit-fib-id` opens
  one saved human fib, hides HTF overlays, auto-fits window, preloads anchors (read-only;
  fail-closed `human_fib.find_annotation`). Default unchanged. 10 tests.
- **2026-06-15 Overlap/dedup detector + anchor convention** — `research/overlap_detector.py`
  (stdlib, report-only): boxes fibs in (time, log-price), flags near-duplicate/overlap
  candidates (box IoU + shared-anchor); never edits labels. Real run: 22 candidates (all
  shared anchor_b). Body/close-vs-wick convention noted in `HUMAN_FIB_ANNOTATION.md`.
  Issue #32 top-ROI #3. [Report](reviews/btc-4h-overlap-candidates-20260615.md).
- **2026-06-15 Source-quality review ledger** — `research/review_ledger.py` (stdlib): flat
  CSV making verdicts machine-trackable (controlled vocab + deterministic `source_hash`).
  First ledger = 4H Tier 2 (8 rows). Issue #32 top-ROI #2.
- **2026-06-15 Static HTML artifact gallery** — `research/artifact_gallery.py` (stdlib-only):
  scans a review PNG dir → self-contained `index.html` (relative links, clean+levels paired,
  auto-detects map/zoom layouts). Standalone; markdown index untouched; output gitignored.
  Issue #32 top-ROI #1. `python -m fibengine.research.artifact_gallery --root <dir>`.
- **2026-06-15 4H Tier 2 first manual sample-pass + first correction-candidate** — 8 fibs
  inspected (4 per scope). Zoom resolves Tier 1 readability. **1 correction-candidate:**
  `20171228T200000` — visual review found a better anchor_a candle adjacent to leg A →
  suspicious; **deferred to a future correction-pass** (GUI too cluttered for safe manual
  edit; needs isolated single-fib view or exact target candle timestamp). No label changed.
  Watchlist: body/close vs wick convention (undocumented).
  Full review: [`reviews/btc-4h-tier2-sample-review-20260615.md`](reviews/btc-4h-tier2-sample-review-20260615.md).
- **2026-06-15 4H Tier 1 map review complete** — all 11 annual groups inspected.
  9/11 map-OK. Two groups need Tier 2: **2017_h2** (103 fibs, Sep–Dec 2017 parabola —
  full Tier 2) and **2021** (partial — Dec 2020 → Mar 2021 cluster only, anchor_a
  in [2021-01-01, 2021-04-01), ~37 fibs). Threshold rule confirmed: local density per
  zone, not total fib count. Y-axis log confirmed (line 246 `monthly_fib_map.py`).
  Full review: [`reviews/btc-4h-tier1-map-review-20260615.md`](reviews/btc-4h-tier1-map-review-20260615.md).
- **2026-06-12 4H visual confirmation Tier 1 built** — `research/fourh_source_fib_map.py`
  renders annual combined 4H maps (366/366 drawn, 11 groups; dense 2017_h2 flagged for
  Tier 2). Reuses `monthly_fib_map` primitives; output gitignored. Full detail in log.md.
- **2026-06-12 4H source-fib phase complete** — **366** manual BTC/USD 4H source fibs
  drawn and verified (timeframe `4h`, log scale, `tradingview_log_chamoun`, levels
  `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236, endpoint mapping ratio 0.0=anchor_b /
  1.0=anchor_a, anchor direction, log-spacing, human/manual only). Coverage
  **2017-01-05 → 2026-06-05**; **up=169 / down=197**. This is **source-labeling
  completion, not reaction-review** — visual confirmation / reaction-review is a later,
  separate decision. No auto-fib, no trading conclusions. 366/366 schema verification PASS.
- **2026-06-12 1D reaction-review complete** — all **67** BTC/USD 1D source fibs
  reviewed on **4H** (expansion config, 4H history to 2017-01-01). Review window:
  anchor_b + 90 days (fixed horizon). **1 816** total 4H interactions.
  `review_windows.yaml` written; artifacts in `experiments/review/source_fib_projection/`.
  Summary: [`reviews/btc-1d-reaction-review-cycle-20260612.md`](reviews/btc-1d-reaction-review-cycle-20260612.md).
  Outliers: Jan–Feb 2022 cluster (52–65 events); Dec 2020 breakout (2 events).
  Batch script: `scripts/run_btc_1d_reaction_review.py`. 1H deferred (cache missing).
- **2026-06-11 1D source-fib labeling complete (source-facit only)** — **67** manual
  BTC/USD 1D source fibs drawn and verified (timeframe `1d`, log scale,
  `tradingview_log_chamoun`, levels `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236,
  endpoint mapping ratio 0.0=anchor_b / 1.0=anchor_a, anchor direction, log-spacing,
  human/manual only). Coverage **2017-01-05 → 2024-12-20**; **34 down / 33 up**.
- **2026-06-11 1W source-fib phase complete** — **21/21** BTC/USD manual 1W source
  fibs drawn (log scale, `tradingview_log_chamoun`) and verified (profile, scale,
  levels `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236, anchor direction,
  human/manual only). Two new research modules:
  - `research/weekly_source_fib_map` — combined 1W/1D/4H map (all fibs per TF).
    **1W/1D usable; combined 4H too compressed** for candle-level confirmation.
  - `research/weekly_source_fib_zoom` — per-fib windowed 4H confirmation
    (one chart per fib, A→B + bounded context). **Per-fib 4H usable.**
  Strict separation kept: **1M source**, **1M→1W projection** (`weekly_projection_map`),
  and **true 1W source** fibs are distinct flows; fail-closed guards reject any
  non-1W / non-log / wrong-profile / 0.236 / non-human fib. No auto-fib, no
  trading conclusions. Commits `4eb2f4b` (map + facit), `939de97` (zoom),
  `e379fae` (CI: format + bounds fix).
- **2026-06-08…11 (earlier milestones)** — 1M reaction-review cycle (9 fibs, 1D+4H),
  Addendum 2 golden-zone retirement (issue #30, added `human_highlights`), log-scale +
  profile fix, 1M re-label, events log-scale fix, and the BTC monthly-first reset. Full
  detail in [log.md](log.md) (append-only trail).

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

## Next Useful Action

**Milestone:** Issue #32 top-3 complete + pushed (gallery `8f1e7a8`, ledger `d6ab9ec`,
overlap detector + anchor convention `84b42db`). local == origin, tree clean, source-fib
JSON unchanged, no new deps, no artifacts committed.

**#32 tooling track — all DONE** (single-fib declutter edit-mode, `20171228` correction,
chart-regression spike + #F render_summary/golden snapshots; detail in [log.md](log.md)).
**Corpus declared clean and
locked** (integrity capstone 2026-06-15:
[`reviews/btc-source-fib-corpus-integrity-20260615.md`](reviews/btc-source-fib-corpus-integrity-20260615.md)).
**MTF confluence atlas in progress.** CP1 ([table](reviews/btc-mtf-confluence-table-20260615.md))
+ CP2 ([sensitivity](reviews/btc-mtf-confluence-sensitivity-20260615.md)) DONE —
`research/mtf_confluence.py` (stdlib). CP2: c001 robust 4-TF; **c002 chaining-dependent** (not
tight 4-TF); fixed-band 188 clusters @0.005; chaining 14% @0.005→26% @0.01. **CP3 slice 1 DONE
(generated, pending human inspection)** — `research/mtf_confluence_atlas.py` renders the c001
card (fixed-band, ε=0.005, 1d backdrop, `price_span_log` annotated; signature-resolved,
fail-closed; PNGs gitignored). [CP3 report](reviews/btc-mtf-confluence-atlas-cp3-c001-20260615.md).
**Next: human visual inspection of the c001 card** → approve card design or adjust; only after
approval, c002 chaining-dependent contrast card. No signal/edge.

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
