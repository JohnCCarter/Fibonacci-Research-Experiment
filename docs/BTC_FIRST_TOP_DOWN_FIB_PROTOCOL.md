# BTC-first top-down Fib protocol

**Status:** Active research protocol (2026-06-08+). Supersedes mixed-symbol,
1D-first, and MTF-projection result reads archived under
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.

## Principles

1. **BTC/USD only** until monthly→weekly→daily mapping is approved.
2. **Human fib = facit** — manual anchors/levels; `*_candidate` ≠ facit.
3. **Top-down timeframe order:** `1M → 1W → 1D → 4H → 1H` (1H deferred until
   lower layers are stable).
4. **Machine work** measures interactions against **locked human levels** — no
   auto-fib as truth, no anchor moves, no optimization against facit.
5. **ETH/USD** starts only after BTC protocol sign-off.

## Active fib profile

| Property | Value |
|----------|-------|
| `scale_mode` | `log` — matches TradingView "Fib levels based on log scale" |
| `levels_profile` | `tradingview_log_chamoun` |
| `levels` | `[0.0, 0.382, 0.5, 0.618, 0.786, 1.0]` (all event-capable; no priority) |
| **Boundaries** | `0.0` / `1.0` are range edges (anchor_b / anchor_a), still event-capable |
| **Excluded** | `0.236` is not in the active profile |

Direction convention (TradingView):
- **Up fib (L→H):** ratio 0.0 = high (recent top), ratio 1.0 = low (swing origin)
- **Down fib (H→L):** ratio 0.0 = low (recent bottom), ratio 1.0 = high (swing origin)

**No level bias (issue #30, Addendum 2):** every configured level is equally
event-capable and review sampling treats all levels the same (round-robin, no golden-zone
priority). Visual focus is expressed per-fib via `human_highlights` (presentation only),
which never affect event detection, outcome logic, sampling, or level importance. An
explicit `--level` filter still narrows the pack to chosen levels.

**Log price axis:** with `scale_mode: log` the labeling tool and both review charts
render the y-axis logarithmically, so log-interpolated levels appear evenly spaced
(TradingView-style). The saved level *prices* are log-interpolated regardless of axis.

Config: all three yaml files (`settings.yaml`, `settings.expansion.yaml`,
`config/variants/settings.deep-4h.yaml`) include `scale_mode: log` and
`levels_profile: tradingview_log_chamoun` under the `fib:` section. `primary_active_levels`
has been retired (Addendum 2).

**Addendum 2 cleanup (2026-06-10):** `primary_active_levels` / golden-zone review-sampling
removed from configs, schema, review, and docs; all levels are event-capable and sampled
equally. Visual focus moves to per-fib `human_highlights` (presentation only). The prior
golden-zone 1M review pack is superseded by an unbiased regenerated pack.

**Reset note (2026-06-09):** all previously generated human_fib JSON files,
`*_events.json`, and review packs were archived to
`archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/` because they
were computed with linear scale and included the 0.236 level.

## Layer map

| Layer | Timeframe | Human | Machine |
|-------|-----------|-------|---------|
| VAD (range) | 1M | Draw/save monthly swing fib | — |
| Context | 1W | Map monthly levels onto weekly structure | — |
| HUR (behavior) | 1D | Validate weekly levels on daily candles | Level interactions vs human prices |
| Resolution | 4H | Optional finer read (later) | MTF projection runner (when invoked) |
| Fine | 1H | Deferred | Deferred |

## Workflow

1. **Fetch** — `uv run python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1M,1w,1d --refresh`
2. **Label facit** — `uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1M` (then 1w, 1d)
3. **Human fib events** — `uv run python -m fibengine.labeling.human_fib_events --fib <fib_id>.json`
4. **Review** — `human_review_level_events` / `level_event_review_tool` on BTC packs only
5. **Analysis runners** (when scoped) — fingerprint, outcome, join, toplist, MTF projection — **BTC inputs only**

## Output layout (active)

```
experiments/
  runs/          # per-run audit dirs (new protocol only)
  results/       # append-only jsonl ledgers (fresh after reset)
  review/        # human review packs (BTC only)
data/labels/human_fib/bitfinex/BTC-USD/...
```

## `data/` policy (fresh start)

Prior labels, human fib, candle cache, and screenshots were **archived** with
`experiments/` under `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/`.
Active facit rebuilt BTC-only. Previous labels (linear scale, included 0.236)
were archived to `archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/`
on 2026-06-09. **All new annotations must be drawn with the log-scale profile.**

| TF | `fib_*.json` (after log-scale reset) |
|----|-------------------------------------:|
| 1M | 9 — re-drawn (log scale, golden zone); review in progress |
| 1w | 0 — re-draw required |
| 1d | 0 — re-draw required |
| 4h | 0 — re-draw required |
| 1h | 0 (deferred) |

| Area | BTC protocol | ETH/SOL |
|------|--------------|---------|
| `data/labels/human_fib/` | Facit 1M→4h in progress (see table) | Blocked until BTC approved |
| `data/labels/bitfinex/*.json` | New swing labels as needed | Blocked |
| `data/raw/` | Cached 1M–4h; fetch 1h when labeling 1h | Do not fetch yet |
| `data/screenshots/` | Optional new references | — |

Detail: [DATA_CLASSIFICATION.md](../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/DATA_CLASSIFICATION.md)

## Out of scope (until BTC approved)

- ETH/SOL mixed toplists or bucket comparisons
- Cross-era cohorts (anchor_b before `history_start`)
- Promoting descriptive bucket reads to signals or facit
- Reusing pre-reset ledgers in `archive/research_superseded/` as current evidence

## Tooling (unchanged)

Runners and review code remain in `src/fibengine/research/` and
`src/fibengine/labeling/`. See [research/README.md](research/README.md) and
[LEVEL_EVENT_HUMAN_REVIEW.md](research/LEVEL_EVENT_HUMAN_REVIEW.md).

## Wiki

Current focus: [research_wiki/handoff.md](research_wiki/handoff.md)
