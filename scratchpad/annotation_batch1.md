# Contrastive annotation — batch 1 (toward the #42 ≥30 gate)

Goal: ~10 diverse windows. For EACH: draw your **accepted** origin→endpoint leg, then draw 1–2
**nearby rejected** alternatives (the tempting-but-wrong origin — usually the more prominent parent
high/low vs your tighter last-push) and say *why*. Contrast is the signal, not the accepted leg alone.

At ~10 we STOP and check: are your reasons/tags consistent (does `wrong_scale` recur, do accept vs
reject separate cleanly)? If yes → grind to 30; if not → adjust before spending more time.

## No restarting per drawing — open ONCE per timeframe, then pan/zoom

Window bounds are taken from the **legs you draw** (not the loaded chart), so open one broad chart per
TF and use the Matplotlib toolbar (pan/zoom) to move between structures. Draw → label → `e` reason →
`v` save (auto-clears + writes tight bounds) → pan to the next. Only relaunch to change TF (4 launches
for all 10, not 10). Filenames are per structure (first leg's day), so nothing overwrites.

**Launch once per TF (broad window):**
```bash
# 1w — windows #2,3,4,5 (2020–2026)
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1w --limit 1000 \
  --annotate-selection --config config/settings.expansion.yaml
# 4h — windows #6,7 (2024–2025)
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 4h --limit 8000 \
  --annotate-selection --window-start 2024-01-01 --window-end 2026-01-01 --config config/settings.expansion.yaml
# 1h — windows #8,9 (late-2025 → mid-2026)
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1h --limit 20000 \
  --annotate-selection --window-start 2025-10-01 --window-end 2026-07-01 --config config/settings.expansion.yaml
# 1d — window #10 (2020)
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1d --limit 3500 \
  --annotate-selection --window-start 2020-01-01 --window-end 2020-12-31 --config config/settings.expansion.yaml
```

Keys: `h`/`l`+click set anchors, `1`/`2`/`3` = accepted/rejected/ambiguous, `t` cycles tag, `e` types
the reason (terminal), `v` saves the window (auto-clears), `x` removes last. `--window-*` above is just
a broad framing; pan/zoom within it. (`z` resets view.)

## The 10 windows

| # | TF | window-start | window-end | structure to annotate | likely contrast |
|---|----|--------------|------------|-----------------------|-----------------|
| 1 | 1h | 2026-06-15 | 2026-07-01 | **HO-B — DONE** (`window_20260615.yaml`) | last-push 61,773 vs engine parent 63,229 |
| 2 | 1w | 2025-09-01 | 2026-06-30 | 2025→26 down-cascade off the ATH | last-push high (~116k) vs the 125.7k ATH origin |
| 3 | 1w | 2023-09-01 | 2024-05-01 | 2024 breakout up-leg (~38→74k) | fresh low vs the deep 2022-bear low |
| 4 | 1w | 2024-08-01 | 2025-11-01 | bull run to ATH (58.9→108→125.7k) | which swing low is the origin (last-push vs parent) |
| 5 | 1w | 2020-09-01 | 2021-05-01 | 2020–21 base (16.8→31k) | last-push low vs the COVID low |
| 6 | 4h | 2025-08-01 | 2025-12-01 | Oct-2025 ATH rollover → drop | last-push high vs the exact ATH high |
| 7 | 4h | 2024-02-01 | 2024-06-01 | 2024 Q1 top (~73.7k) + correction | local top vs the run's origin low |
| 8 | 1h | 2026-05-01 | 2026-06-15 | May–Jun 2026 down sub-move | last-push high vs a prior prominent high |
| 9 | 1h | 2025-11-01 | 2025-12-15 | late-2025 down leg | tighter origin vs prominent parent |
| 10 | 1d | 2020-02-01 | 2020-06-01 | COVID crash + reversal (mirrors the fixture) | crash-low origin vs an interior push |

Each `v` writes `data/labels/selection_annotations/bitfinex/BTC-USD/<tf>/window_<startday>.yaml`.
Different windows on the same TF get distinct filenames (by start day), so nothing overwrites.

## Optional: engine-proposed origins

For the DOWN 1h windows (#8, #9) I can run the frozen structure-engine (`chamoun_structure_engine`,
DOWN-only 1h) to pre-compute its #1-prominent origin as a concrete *rejected* candidate — like the
63,229 in HO-B. Ask if you want those numbers before annotating those two.
