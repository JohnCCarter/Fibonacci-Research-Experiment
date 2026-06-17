# BTC/USD 4H Visual Confirmation / Source-Quality Review — Design (2026-06-12)

## Decision

**4H is the lowest active timeframe. 1H is paused indefinitely.**

4H source-facit locked:

| Field | Value |
|-------|-------|
| Fib count | 366 |
| Coverage | 2017-01-05 → 2026-06-05 |
| Direction | up=169 / down=197 |
| Profile | `tradingview_log_chamoun` |
| Scale | log |
| Levels | `[0, 0.382, 0.5, 0.618, 0.786, 1]` |
| Forbidden ratio | 0.236 (absent in all 366 fibs) |
| Origin | human/manual only |
| Schema PASS | 366/366 (2026-06-12) |

**Next phase is 4H visual confirmation / source-quality review — not 4H→1H
reaction-review, not 1H source labeling.**

---

## What source-quality review means for 4H

The question: *"Are my anchor pins on the correct structural swings on the 4H chart?"*

Required inputs: anchor surroundings (pre/post context) + fib leg + levels on 4H candles.

**Out of scope for this phase:**

| Item | Why excluded |
|------|-------------|
| 1H cache / labeling | 1H paused |
| `source_fib_projection_review` | Reaction-review pipeline — event detection, lower TF |
| `source_fib_projection_chart` | Requires reaction events / `review_sample.csv` |
| `review_windows.yaml` | Used only for reaction-review window scoping |
| `review_sample.csv` / events | Reaction-review artifacts |
| Any lower-TF projection | 4H is the lowest active TF |

---

## Design

### Tier 1 — Annual combined maps (first implementation)

**Proposed module:** `src/fibengine/research/fourh_source_fib_map.py`

**Output (gitignored — `experiments/review/` is in `.gitignore`):**
```
experiments/review/fourh_source_fib_map/
    fourh_source_fib_map_2017_4h_clean.png
    fourh_source_fib_map_2017_4h_levels.png
    fourh_source_fib_map_2018_4h_clean.png
    fourh_source_fib_map_2018_4h_levels.png
    ...
    fourh_source_fib_map_2026_4h_clean.png
    fourh_source_fib_map_2026_4h_levels.png
    fourh_source_fib_map_index.md
```

**Scale:** ~10 annual maps × 2 variants = ~20 PNGs. Fast visual scan for 366 fibs.

**Approach:** Fibs are grouped by `anchor_a.time` year. Each year's map renders all fibs
from that year on a full 4H candle chart, each fib labeled with its short ID and direction.

**Rendering:** Reuses `_draw_map`, `_load_fibs`, `_short_id` from `monthly_fib_map`
unchanged.

**Usage (when built):**
```bash
uv run --no-sync python -m fibengine.research.fourh_source_fib_map \
    --fib-dir data/labels/human_fib/bitfinex/BTC-USD/4h \
    --config config/settings.expansion.yaml
```

**Fail-closed guard** (adapted from `_validate_source_fibs` in `weekly_source_fib_map`,
`SOURCE_TF` changed to `"4h"`):

```python
SOURCE_TF = "4h"                     # rejects 1M/1W/1D if --fib-dir is wrong
_REQUIRED_PROFILE = "tradingview_log_chamoun"
_REQUIRED_SCALE = "log"
_FORBIDDEN_RATIO = 0.236
# created_by == "human", "manual" in source
# no "candidate"/"auto"/"inferred" in fib_id or source
```

Violations raise `ValueError` listing every offending fib (same pattern as
`weekly_source_fib_map._validate_source_fibs`).

---

### Tier 2 — Per-fib zoom (on-demand, only after Tier 1)

**Proposed module:** `src/fibengine/research/fourh_source_fib_zoom.py`

**Build only if Tier 1 maps reveal that per-fib zoom is needed.**

Direct analog of `weekly_source_fib_zoom.py` with:

| Parameter | Value |
|-----------|-------|
| `SOURCE_TF` | `"4h"` |
| `chart_tfs` | `("4h",)` — same TF, no cross-TF snap needed |
| `pre_pad` | 40 bars (~1 week 4H context before anchor_a) |
| `post_pad` | 40 bars (~1 week context after anchor_b) |
| snap_window | 0 — anchor is exactly on a 4H bar (source_tf == chart_tf) |
| Reaction imports | **none** — `source_fib_projection_*` not imported |

**Output:**
```
experiments/review/fourh_source_fib_zoom/
    <fib_id>/
        4h_clean.png
        4h_levels.png
    fourh_source_fib_zoom_index.md
```

**Scale:** 366 fibs × 2 variants = 732 PNGs (local gitignored artifacts).

---

## Existing infrastructure reference

| Module | Role for this design |
|--------|---------------------|
| `research/monthly_fib_map` | `_draw_map`, `_load_fibs`, `_short_id`, `_nearest_pos` — reuse unchanged |
| `research/weekly_source_fib_map` | `_validate_source_fibs` guard pattern — adapt SOURCE_TF="4h" |
| `research/weekly_source_fib_zoom` | Direct structural analog — adapt SOURCE_TF="4h", snap_window=0 |
| `research/source_fib_projection_review` | **Not used** — reaction-review pipeline |
| `research/source_fib_projection_chart` | **Not used** — reaction-review pipeline |

---

## Estimated implementation size

| File | Lines | When |
|------|-------|------|
| `fourh_source_fib_map.py` | ~150 | Tier 1 — first |
| `fourh_source_fib_zoom.py` | ~200 | Tier 2 — only if needed |
| `scripts/run_btc_4h_source_fib_zoom.py` | ~50 | Optional batch runner |

Zero new dependencies. No changes to existing modules.

---

## Unverified (before implementation)

- Fib density per year: a year with 60+ overlapping short-leg fibs may require a wider
  figure or subgrouping. Verify with a quick `fib_count_per_year` query before building.
- `.gitignore` pattern `experiments/review/` covers `fourh_source_fib_map/` and
  `fourh_source_fib_zoom/` — confirmed 2026-06-12.
