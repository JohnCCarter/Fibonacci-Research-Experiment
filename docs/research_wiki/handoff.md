# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

**BTC monthly-first top-down protocol** — re-labeling on BTC/USD only after the
**2026-06-09 log-scale + profile reset** (prior linear / 0.236 labels archived).

**Canonical protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

| Step | Timeframe | Status |
|------|-----------|--------|
| 1 | **1M** | **Re-drawn** — 9× `fib_*.json` (log scale, golden zone); review in progress |
| 2 | 1W | Blocked until 1M signed off — re-draw required |
| 3 | 1D | Blocked — re-draw required |
| 4 | 4H | Blocked — re-draw required |
| 5 | 1H | Deferred — 1h cache not fetched yet |

**ETH/USD:** blocked until BTC protocol approved.

## Recent Changes

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

1. Sign off **1M** review pack `human_fib_review_20260609T135548Z`
   (`level_event_review_tool --config config/settings.expansion.yaml`).
2. After 1M approval: re-draw **1W** (log scale), then 1D, 4H.
3. When ready for 1h: fetch 1h cache, then label (preflight currently FAIL on 1h).

## Guardrails

- Do not treat archived ledgers/reviews as current evidence.
- Do not treat `*_candidate` as facit.
- No ETH/SOL analysis until BTC protocol sign-off.
- No auto-fib or trading signals.

## Links

- [BTC-first protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
