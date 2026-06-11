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
| 2 | 1W | Pending — re-draw required (log scale) |
| 3 | 1D | Pending — re-draw required |
| 4 | 4H | Pending — re-draw required |
| 5 | 1H | Deferred — 1h cache not fetched yet |

**ETH/USD:** blocked until BTC protocol approved.

## Recent Changes

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

- `data/labels/human_fib/bitfinex/BTC-USD/1M/` — **9** base `fib_*.json` (log scale);
  1w/1d/4h empty pending re-draw.
- `data/raw/bitfinex/BTC-USD/1M/limit_500.csv` — 115 bars (2016-12 .. 2026-06),
  fetched with `--config config/settings.expansion.yaml` to cover old anchors.
- `experiments/review/fib_level_events/` — active 1M pack `human_fib_review_20260609T135548Z`.
- Pre-reset archive (local disk; git tracks manifest only):
  [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)

## Open Questions

- Minimum monthly fib count before 1W mapping?

## Next Useful Action

1. Re-draw **1W** source fibs (log scale, `tradingview_log_chamoun`) — then run weekly
   source-segment map (`weekly_projection_map`) for visual confirmation before LTF review.
2. When ready for 1h: fetch 1h cache, then label (preflight currently FAIL on 1h).

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
  approved 2026-06-11. Do not resume 1M reaction review unless an explicit
  bug or gap is discovered.
- **Next phase: manual BTC/USD 1W source fibs** — draw in the labeling tool
  (log scale, `tradingview_log_chamoun`), then run `weekly_projection_map`
  for visual confirmation.
- Do not auto-fib. Do not infer 1W anchors. Do not treat 1M projected levels
  as 1W source fibs.

## Links

- [BTC-first protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
