# Startup on another machine — checklist

> Moved verbatim from [handoff.md](../handoff.md) 2026-07-20 (repo-bounds §2B: handoff exceeded
> the 400-line cap). Content unchanged. Relative links from the old location updated where noted.


Use this checklist when resuming from a home computer or any machine that does
not have the current working tree.

### Before leaving the current machine

- All code, tests, wiki, and data changes committed and pushed (`git status` clean).
- Gitignored review artifacts (`experiments/review/`) copied as a ZIP if wanted
  (optional — see restore step below).
- No required local-only state remains: committed facit (`fib_*.json`,
  `review_windows.yaml`) and wiki docs are the source of truth.

### On the new machine

```bash
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

`experiments/review/` is gitignored (regenerable charts/CSVs). The completed 1M packages can
be restored locally from `btc-1m-reaction-review-artifacts-20260611.zip` (`unzip … -d .`) if
wanted — **optional**; committed `fib_*.json` + `review_windows.yaml` are the source of truth.

### Windows / Symantec SEP note

Use `uv run --no-sync` after the initial `uv sync` and set `PYTHONDONTWRITEBYTECODE=1`
(user-scope) to cut SEP scan surface. Full SONAR / Auto-Protect discipline + the env-var
commands: [CLAUDE.md](../../../CLAUDE.md) Gotchas.

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
  [`reviews/btc-4h-tier2-sample-review-20260615.md`](../reviews/btc-4h-tier2-sample-review-20260615.md).
- Do not auto-fib. Do not infer anchors. Keep the four flows distinct: 1M source /
  1M→1W projection / true 1W source / true 1D source fibs.

