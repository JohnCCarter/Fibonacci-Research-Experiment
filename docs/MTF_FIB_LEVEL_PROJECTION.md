# MTF Fib Level Projection

> **Status:** implemented for the **1W human fib -> 1D candles** slice
> (`fibengine.research.mtf_fib_level_projection`). `4h`/`1h` LTFs are deferred until a
> candle fetch populates those caches. Sections 1–5 below are the original design +
> inspection; the runner follows that plan.

## Run it (no network)

```bash
uv run python -m fibengine.research.mtf_fib_level_projection \
  --human-fib data/labels/human_fib/bitfinex/BTC-USD/1w/<fib_id>.json \
  --lower-timeframes 1d \
  --pre-bars 50 --post-bars 100 --horizons 5,10,20,50
```

Outputs under `experiments/runs/mtf_fib_level_projection/<date>/<run_id>/`:
`config.json`, `interactions.jsonl` (one row per LTF interaction with
`projected_from_timeframe`), `fingerprint_outcomes.jsonl` (joined fingerprint×outcome),
`unmatched.jsonl`, `skipped.jsonl`, `summary.json` / `summary.csv`, `run_summary.json`;
appends `experiments/results/mtf_fib_level_projection.jsonl`. Then triage with
`uv run python -m fibengine.research.fib_toplist --run-dir <run_dir>`.

First smoke (1W BTC fib -> 1D): 6 projected levels, 42 LTF interactions, 168 joined
rows (×4 horizons), 0 unmatched, 0 skipped. Each joined row carries all layers:
`fib_level`+`fib_price`+`projected_from_timeframe` (projected_level), `relation`
(LTF geometry), `post_*`/`pre_*`/`at_*` (fingerprint), `forward_return`/`mfe`/`mae`/…
per `horizon` (outcome). Descriptive only — no edge claim.

---

# Design + inspection

Research direction after the 1D-only finding (*working pipeline, no stable evidence
yet*): treat 1D-only interaction as **too coarse**, not as a failure of the fib idea.
Reuse the exact human-drawn HTF fib levels and measure **lower-timeframe** candle
behavior around those same price levels.

Core principle:

```
HTF human fib = locked map / source-of-truth
LTF candles    = behavior around those levels
```

Not auto-fib. Not moving anchors. Not relabeling human fib. Not a trading signal,
buy/sell, edge claim, ML, or optimized rule.

## 1. Inspection result — what already exists (Observed)

The hard parts are already built and are **timeframe-agnostic**:

| Capability | Where | MTF-ready? |
|---|---|---|
| Human fib base JSON (anchors + absolute level prices) | `labeling/human_fib.py` `load_annotation` | ✅ levels carry absolute `price`, so they project to any TF unchanged |
| Candle↔level geometry (above/below/touch/cross) | `labeling/human_fib.py` `classify_candle(o,h,l,c,level)` | ✅ pure, works on any candle |
| Per-candle×level relation over a df + time window | `labeling/human_fib.py` `classify_candles(df, annotation, start_time, end_time)` | ✅ already accepts **any** df + an HTF annotation |
| Pre/at/post fingerprint (wick/body, acceptance, retest, chop, break-hold, extension, return, bars-held) | `research/fib_level_fingerprints.py` `extract_fingerprint(df, row, cfg)` / `extract_all` | ✅ only needs df + `event_bar` (int) + `fib_price` + `approach_side` |
| Forward outcomes per event×horizon | `research/fib_candidate_outcomes.py` `compute_outcomes` / `analyze_events` | ✅ same row interface |
| Join fingerprint × outcome on `event_id` | `research/fib_fingerprint_outcomes.py` `join_fingerprints_outcomes` / `summarize_joined` | ✅ reusable as-is |
| Triage / multi-run inventory + stability | `research/fib_toplist.py` | ✅ reusable on any join run dir |
| Touch-scan + candidate classify loop | `research/level_events.py` `detect_level_events` / `_classify` | ⚠️ logic is close but bound to a machine `swing` + `fib_levels(swing)`; scans from `swing.end.index` |
| Load candles for any timeframe | `data/loader.py` `load_candles` + `timeframe_limits` (4h/1d/1w/1M) | ✅ |

The fingerprint layer already measures **every** behavior the request lists
(touch/cross/above/below, wick vs body, close acceptance, retests,
compression/chop via choppiness + remained-near-rate, break-and-hold via
post-bars-on-break-side, break-and-fail via crossed-back, max extension away,
return to approach side, bars held). They are just currently fed HTF events.

## 2. What is missing (the only real gap)

A deterministic **LTF interaction detector**: given an LTF candle df + the explicit
HTF level prices + a scan-start time, find the LTF bars that interact with each
level and emit rows compatible with `extract_all` / `analyze_events`.

`detect_level_events` is the closest existing code but:

- it derives levels from a machine `swing` (`fib_levels(swing)`) — we must use the
  **human** level prices verbatim;
- it starts scanning at `swing.end.index` — we must start at the HTF leg end
  (`anchor_b.time`) mapped onto the LTF index;
- it is coupled to the swing-selection stack (imports scoring/backtest).

So a small, dedicated detector is justified rather than a broad refactor of
`detect_level_events`.

Secondary gaps:

- **No MTF runner / artifacts / CLI.**
- **LTF candle data is thin.** Caches: 1d is deep (≥2016 via expansion config), but
  `4h` is only a shallow recent BTC slice and `1h` is a tiny 2013 fragment; ETH/SOL
  have no 4h/1h cache. → The first runnable slice is **1W fib → 1D candles**
  (no network). `…→4h`/`…→1h` need `fibengine.data.fetch --timeframes 4h` first.
- The `labeling.mtf_disambiguation` / `enable_same_candle_mtf_resolution` flags are
  about the **labeling tool** resolving 1W H/L on 1D pivots — unrelated to level
  projection.

## 3. Layer separation (kept distinct per row)

```
human_fib       = locked HTF map            (load_annotation, never mutated)
projected_level = HTF fib level on LTF      (fib_level ratio + fib_price + projected_from_timeframe=HTF)
relation        = deterministic LTF geometry (classify_candle on the LTF bar)
fingerprint     = measurable LTF behavior   (extract_fingerprint on LTF df)
outcome         = forward empirical result  (compute_outcomes on LTF df)
```

`auto_candidate` (continuation/rejection/reaction/failure) stays a machine
hypothesis on the LTF interaction; it is needed only so outcome direction
(`expected_direction`) can be inferred. It is never facit.

## 4. Minimal implementation plan

New runner `fibengine.research.mtf_fib_level_projection` (thin; mostly glue):

1. **Input:** one or more **base** human fib JSONs (`<fib_id>.json`, not
   `_events.json`) via `load_annotation`. Read `symbol`, `direction`, `anchor_b.time`
   (leg end), and `levels` (ratio + absolute price). Human layer untouched.
2. **For each `--lower-timeframes` TF:** `load_candles` for `(exchange, symbol, TF)`
   (`fetch_if_missing=False`; skip + log if missing).
3. **New detector** `detect_ltf_level_interactions(ltf_df, levels, *, start_time, cfg)`:
   scan LTF bars from `start_time` (anchor_b) forward; for each level price, find
   touches (`low-band ≤ price ≤ high+band`), debounce repeats, set `approach_side`
   from the prior LTF close, `relation` via `classify_candle`, `touch_type`
   (wick/close above/below), and `auto_candidate` via a small forward-window
   classify (reuse the `_classify` rules). Emit rows with: `event_bar` (LTF index),
   `event_time`, `fib_level`, `fib_price`, `approach_side`, `relation`, `touch_type`,
   `auto_candidate`, `symbol`, `timeframe=TF`, `exchange`, `fib_id`,
   `projected_from_timeframe=<HTF>`, `swing_direction=direction`.
4. **Reuse downstream unchanged:** build `df_cache[(exchange,symbol,TF)] = ltf_df`,
   call `extract_all` (#23) + `analyze_events` (#22) + `join_fingerprints_outcomes`.
5. **Artifacts** under `experiments/runs/mtf_fib_level_projection/<date>/<run_id>/`:
   `config.json`, `interactions.jsonl`, `fingerprint_outcomes.jsonl`,
   `summary.json/csv` (group by `projected_from_timeframe × timeframe × candidate ×
   relation × level × horizon`), `run_summary.json`; append
   `experiments/results/mtf_fib_level_projection.jsonl`. Then `fib_toplist
   --run-dir <run_dir>` works directly.
6. **CLI:**

```bash
uv run python -m fibengine.research.mtf_fib_level_projection \
  --human-fib data/labels/human_fib/bitfinex/BTC-USD/1w/<fib_id>.json \
  --lower-timeframes 1d,4h \
  --pre-bars 50 --post-bars 100 --horizons 5,10,20,50
```

(`--all-human-fib --htf 1w` to batch all 1w base fibs; `--config` for the expansion
window, mirroring the join runner.)

7. **Tests:** detector determinism (touch/cross/approach_side/debounce on a synthetic
   LTF df); e2e on a synthetic LTF df + tiny annotation → join rows carry both layers
   + `projected_from_timeframe`; per-TF grouping in summary. `ruff` + `pytest`.

Scope guard: no refactor of `detect_level_events`/swing stack, no new UI, no
candidate-logic change, no settings/promotion changes. ~1 new module + 1 test file.

## 5. First runnable slice (no network)

**1W human fib → 1D candles** for BTC/ETH/SOL (1d cache is deep with
`config/settings.expansion.yaml`). Validates the path end-to-end. Add `4h` (and
`1h`) only after `fibengine.data.fetch --timeframes 4h` populates LTF caches.

## Acceptance (what a researcher can then answer)

- Which HTF fib level was projected? → `fib_level` + `fib_price` + `projected_from_timeframe`.
- Which LTF candles interacted? → `interactions.jsonl` (`event_bar`, `event_time`).
- Touch / cross / rejection / chop / retest / acceptance? → `relation` + fingerprint
  fields + `auto_candidate`.
- 1D vs 4H difference? → group summary by `timeframe`.
- Does LTF reveal structure 1D-only missed? → compare to the existing 1d-fib join
  runs / `fib_toplist` triage.

## Related

- [FIB_LEVEL_FINGERPRINTS.md](FIB_LEVEL_FINGERPRINTS.md) (#23) ·
  [FIB_CANDIDATE_OUTCOMES.md](FIB_CANDIDATE_OUTCOMES.md) (#22) ·
  [FIB_FINGERPRINT_OUTCOMES.md](FIB_FINGERPRINT_OUTCOMES.md) (join)
- [HUMAN_FIB_ANNOTATION.md](HUMAN_FIB_ANNOTATION.md) · [LEVEL_EVENTS.md](LEVEL_EVENTS.md)
- Checkpoint: [research_wiki/reviews/2026-06-05-fib-fingerprint-outcome-checkpoint.md](research_wiki/reviews/2026-06-05-fib-fingerprint-outcome-checkpoint.md)
