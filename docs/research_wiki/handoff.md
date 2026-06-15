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
| 4 | **4H** | **Complete** — 366× source fibs, 2017-01-05 → 2026-06-05 (2026-06-12) |
| 5 | 1H | Deferred — 1h cache not fetched yet |

**ETH/USD:** blocked until BTC protocol approved.

## Recent Changes

- **2026-06-15 4H Tier 1 map review complete** — all 11 annual groups inspected.
  9/11 map-OK. Two groups need Tier 2: **2017_h2** (103 fibs, Sep–Dec 2017 parabola —
  full Tier 2) and **2021** (partial — Dec 2020 → Mar 2021 cluster only, anchor_a
  in [2021-01-01, 2021-04-01), ~37 fibs). Threshold rule confirmed: local density per
  zone, not total fib count. Y-axis log confirmed (line 246 `monthly_fib_map.py`).
  Full review: [`reviews/btc-4h-tier1-map-review-20260615.md`](reviews/btc-4h-tier1-map-review-20260615.md).
- **2026-06-12 4H visual confirmation Tier 1 built** — `research/fourh_source_fib_map.py`
  renders **annual combined 4H source-fib maps** (fibs grouped by `anchor_a` year; dense
  years >60 fibs split into calendar half-years). Reuses `monthly_fib_map` primitives
  unchanged; no snap (source TF == chart TF == 4h); each group windowed by its fib span.
  Real run (facit + expansion cache): **366/366 fibs drawn, 0 skipped, 11 groups** —
  2017=13h1/**103h2**, 2018=33, 2019=26, 2020=31, 2021=55, 2022=24, 2023=17, 2024=22,
  2025=34, 2026=8. Mid-density maps scan cleanly. **2017_h2 (~103 fibs, Sep–Dec parabola)
  exceeds map-reviewable density → flags 2017 for Tier 2 zoom.** 14 tests pass; ruff +
  repo-bounds + full suite green. Output gitignored under
  `experiments/review/fourh_source_fib_map/`. No reaction-review, no events, no auto-fib.
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
- **2026-06-11 1M reaction-review cycle complete** — all 9 BTC/USD 1M source fibs
  reviewed through 1D + 4H. Review windows confirmed in `review_windows.yaml`.
  62 1D events, 127 4H events. Summary:
  [reviews/btc-1m-reaction-review-cycle-20260611.md](reviews/btc-1m-reaction-review-cycle-20260611.md).
- **2026-06-10 Addendum 2 — retire golden-zone sampling** — issue #30: removed
  `primary_active_levels` / golden-zone review-sampling from configs, `core/config.py`,
  `human_review_pack`/`rows`/`constants`, and docs. All levels are event-capable and
  sampled equally (round-robin). Added `human_highlights` (presentation-only) to
  `HumanFibAnnotation`. Prior golden-zone 1M pack superseded by an unbiased regenerated pack.
- **2026-06-09 log-scale + profile fix** — fib levels computed log-scale
  (`scale_mode: log`); profile `tradingview_log_chamoun` `[0, 0.382, 0.5, 0.618,
  0.786, 1]` (no 0.236). Charts render a log price axis (labeling tool + both review
  tools). (Golden-zone `primary_active_levels` sampling was later retired — see 2026-06-10.)
  Prior linear/0.236 labels, events, and review packs archived to
  `archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/`.
- **2026-06-09 1M re-label** — 9 monthly fibs re-drawn; `human_fib_events` +
  BTC-only review pack `human_fib_review_20260609T135548Z` (golden-zone biased).
- **2026-06-09 events log-scale fix** — `detect_level_events` / `human_fib_events`
  now compute level prices with the annotation's `scale_mode` (was always linear);
  events + pack regenerated so review level prices match the log facit.
- **2026-06-08 reset** — prior experiments + mixed-symbol data archived to
  `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.

## Verification Snapshot

- `data/labels/human_fib/bitfinex/BTC-USD/1M/` — **9** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1w/` — **21** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1d/` — **67** base `fib_*.json` (log scale);
  source-facit complete, verified 2026-06-11.
- `data/labels/human_fib/bitfinex/BTC-USD/4h/` — **366** base `fib_*.json` (log scale);
  source-facit complete, verified 2026-06-12. Coverage 2017-01-05 → 2026-06-05; up=169 / down=197.
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

1. **4H visual confirmation — Tier 2** — implement `fourh_source_fib_zoom.py` (per-fib
   windowed 4H charts). Tier 1 review (2026-06-15) confirmed two scopes:
   - `2017_h2`: all 103 fibs (Sep–Dec 2017 parabola — globally unreadable on map)
   - `2021_dec2020_mar2021`: anchor_a in [2021-01-01, 2021-04-01), ~37 fibs
   Design: [`reviews/btc-4h-visual-confirmation-design-20260612.md`](reviews/btc-4h-visual-confirmation-design-20260612.md).
   Review: [`reviews/btc-4h-tier1-map-review-20260615.md`](reviews/btc-4h-tier1-map-review-20260615.md).
2. **1H source labeling** — deferred. 4H is the current lowest active timeframe. Fetch
   1H cache first (`data.fetch --timeframes 1h`). Separate decision before starting.

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
- **4H visual confirmation Tier 1 is built** (`research/fourh_source_fib_map.py`,
  2026-06-12). Annual combined 4H maps, 366/366 drawn across 11 groups. Next is **human
  review of the generated maps**, then Tier 2 (`fourh_source_fib_zoom.py`) on-demand —
  2017_h2 (~103 fibs) is already flagged as needing per-fib zoom. Do not start with 1H.
  Do not start with reaction-review. Design:
  [`reviews/btc-4h-visual-confirmation-design-20260612.md`](reviews/btc-4h-visual-confirmation-design-20260612.md).
- Do not auto-fib. Do not infer anchors. Keep the four flows distinct: 1M source /
  1M→1W projection / true 1W source / true 1D source fibs.

## Links

- [BTC-first protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
