# Fib Fingerprint × Outcome Join (#22 + #23)

Research-only deterministic join of the interaction **fingerprint** layer
([FIB_LEVEL_FINGERPRINTS.md](FIB_LEVEL_FINGERPRINTS.md), #23) and the forward
**outcome** layer ([FIB_CANDIDATE_OUTCOMES.md](FIB_CANDIDATE_OUTCOMES.md), #22)
for the *same* events.

Lets a researcher ask: *which measurable fingerprints co-occur with which forward
outcomes, per candidate / relation / level / timeframe / horizon?*

**Not** trading logic. **Not** ML. **No** edge claims. No candidate logic changes —
this only merges two existing layers.

## Join key

Both layers emit identical `event_id`:

```
<fib_id>|<fib_level>|<event_bar>|<auto_candidate>
```

One fingerprint joins to many outcome rows (one per horizon).

## Layering (kept separate in each row)

```
human_fib  = locked map
relation   = geometry
candidate  = machine hypothesis
fingerprint= measurable pre/at/post behavior   (#23)
outcome    = forward empirical result           (#22)
```

## CLI

```bash
uv run python -m fibengine.research.fib_fingerprint_outcomes \
  --events data/labels/human_fib/bitfinex/BTC-USD/1d/fib_BTC-USD_1d_20260526T000000_events.json \
  --horizons 5,10,20,50 --pre-bars 20 --post-bars 50

uv run python -m fibengine.research.fib_fingerprint_outcomes --all-human-fib-events
```

`--all-human-fib-events` skips files whose anchors/events fall outside the loaded
candle cache (`data.history_start` in `config/settings.yaml`).

### Data expansion (wider window, same method)

To grow sample size without changing the global window or any analysis threshold,
pass an alternate settings file with a wider candle window:

```bash
uv run python -m fibengine.research.fib_fingerprint_outcomes \
  --all-human-fib-events --horizons 5,10,20,50 \
  --config config/settings.expansion.yaml
```

`config/settings.expansion.yaml` only widens `data.history_start` (2016-11-05) and
deepens the 1d `timeframe_limits` to select the `limit_3500.csv` caches — recovering
ETH 2017-2018 events. BTC pre-2016 and SOL pre-2022 1d have no deep cache and stay
skipped (would need a network refetch). `config/settings.yaml` keeps 2022-10-31 for
experiment/review/leaderboard reproducibility.

## Output

```
experiments/runs/fib_fingerprint_outcomes/<YYYY-MM-DD>/<run_id>/
    fingerprint_outcomes.jsonl   # one row per event × horizon (fingerprint + outcome)
    unmatched.jsonl              # events present in only one layer
    summary.json / summary.csv   # grouped means/rates by candidate/relation/level/TF/horizon
    config.json, run_summary.json

experiments/results/fib_fingerprint_outcomes.jsonl
```

Each summary row pairs **outcome** means/rates (`mean_forward_return`, `mean_mfe`,
`mean_mae`, `rate_close_on_approach_side`, `rate_crossed_back`) with **fingerprint**
means (`mean_pre_distance_atr_norm`, `mean_post_retest_count`, …) so the two layers
can be compared side by side without any modeling.

## Triage top-list (descriptive, low-sample)

A separate, read-only exporter turns one join run into a triage overview. It only
answers *what is worth more data / what looks like noise* — **not** edge, signal,
strategy, or tuning.

```bash
uv run python -m fibengine.research.fib_toplist                 # latest join run
uv run python -m fibengine.research.fib_toplist --run-dir <run_dir>
```

Writes into the same run dir:

```
toplist.csv        # candidate summary, ranked per candidate × horizon
TOPLIST_NOTES.md   # inventory + top-1 preview + fingerprint↔outcome hints
```

- `toplist.csv` sorts each (candidate, horizon) group by `mean_mfe` ↓, `mean_mae` ↑,
  `mean_post_bars_on_break_side` ↓ (expected-side proxy), then `n_events` ↓, and adds
  `rank_in_candidate_horizon` + `sample_flag` (`LOW SAMPLE` when `n_events` < 5).
- `TOPLIST_NOTES.md` adds deterministic **Spearman rho** hints (direction-inferred
  events only, candidates pooled) showing which fingerprint fields co-vary with
  `mfe`/`mae` per horizon, plus arbitrary (untuned) triage buckets
  watch / weak / noise-like.

Spearman is computed dependency-free (average-rank ties); `n/a` means <3 pairs or no
variance. Pooling across candidates makes it a coarse hint, not a per-candidate or
causal claim.

### Multi-run comparison (data-expansion triage)

`--compare-to <baseline_run_dir>` treats `--run-dir` as the expanded/combined run and
writes two more files into it:

```
sample_inventory.csv   # per bucket: n_baseline, n_expanded, delta, reached_5/10/20, still_low
MULTIRUN_NOTES.md      # combined summary + sample inventory + fingerprint stability
```

The stability table compares Spearman(field, mfe) per horizon between the two runs and
labels each fingerprint field `stable-ish`, `WEAKENED (small-sample artifact)`, or
`UNSTABLE (sign flip)`. This answers *which fields survive more data*, not *which is an
edge*.

## Related

- [FIB_LEVEL_FINGERPRINTS.md](FIB_LEVEL_FINGERPRINTS.md) — #23
- [FIB_CANDIDATE_OUTCOMES.md](FIB_CANDIDATE_OUTCOMES.md) — #22
- [LEVEL_EVENTS.md](LEVEL_EVENTS.md) — candidate taxonomy
