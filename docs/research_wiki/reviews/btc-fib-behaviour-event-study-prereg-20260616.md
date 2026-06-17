# BTC/Fib Behaviour Event Study — Pre-registration (2026-06-16)

**Lean Fib Research, one falsifiable question.** This pre-registers the rules **before**
results, then they are frozen. It operationalises the
[Phase 0 question](btc-fib-to-genesis-v2-phase0-prereg-20260615.md) as a **local** study inside
the Fib repo only. **Not** Fib → Genesis, **not** Phase 3. No Genesis touch/import/export, no
1H, no ML/optimisation, no trading/edge claim, no label mutation, no locked-corpus change.

## 1. Question

> Does BTC/USD price **react measurably differently** at causally-valid human-fib retracement
> levels than at matched placebo levels and a naïve causal-swing baseline?

Null: no measurable difference vs baselines. If fib levels are statistically indistinguishable
from placebo and causal-swing on the primary metric out-of-sample → answer is **no** → stop;
**no strategy sanity-check.** This is a *behaviour* question (does the level repel price), not a
buy/sell/profit claim.

## 2. Data (locked, offline)

- BTC/USD only; timeframes **1M, 1w, 1d, 4h** (corpus 9/21/67/365 fibs). **1H is rejected
  fail-closed.**
- Candles loaded read-only from the existing cache via `config/settings.expansion.yaml`
  (`history_start 2016-11-05`); no fetch, no network.
- Source fibs read read-only from `data/labels/human_fib/bitfinex/BTC-USD/<tf>/fib_*.json`.
  **No JSON is written or mutated.**

## 3. Causality (binding, fail-closed)

- A fib contributes levels at bar `t` **only if** `known_after_ts <= t`, where
  ```
  known_after_ts = max(anchor_a.time, anchor_b.time) + confirmation_buffer
  confirmation_buffer = k_confirm bars of the fib's own timeframe   (k_confirm = 1, frozen)
  ```
- **Fib level set = interior retracements only `{0.382, 0.5, 0.618, 0.786}`.** The `0.0`/`1.0`
  anchors are the swing extremes themselves and are **excluded** from the fib set so it cannot
  trivially coincide with the swing baseline.
- Forbidden (fail-closed if detected): future `anchor_b`, full-corpus/full-sample statistics as
  a feature, CP-card/visual labels as signal, label *existence* as implicit future info, any
  level known only in hindsight, naïve (tz-missing) anchor timestamps.

## 4. Level sources (≥2 baselines; all causal)

1. **FIB** — causal fib retracement levels per §3.
2. **SWING (naïve baseline)** — fractal swing highs/lows (`pivot_k` bars each side), each a
   static horizontal level **knowable only `pivot_k` bars after** the pivot bar. Honest analogue
   of "what a fib would capture." `pivot_k = 3` (frozen).
3. **PLACEBO (matched control, deterministic)** — for every real fib, at its **same**
   `known_after_ts`, emit the **same count** of levels but with prices drawn uniformly in
   log-price from the **causal trailing range** `[min low, max high]` over bars strictly before
   `known_after_ts`. Matches fib count and time distribution exactly; uses no future info.
   Seeded RNG `seed = 20260616` → byte-identical on re-run.

Round-number baseline deferred (not needed to falsify; keeps the pass lean).

**Level recency window (frozen, applied identically to all sources):** a level is "active"
only for `level_active_bars` bars after `known_after_ts` (a fib drawn years ago is not a *live*
reference). Per TF: 4h `720`, 1d `365`, 1w `104`, 1M `36`. This bounds cost and is applied to
FIB, PLACEBO and SWING identically, so it cannot favour fib.

## 5. Event definition (identical across sources)

At bar `t`, the nearest causally-known level `L` of a source is a **touch event** iff
- the level lies within `eps_atr * ATR(t)` of the bar range `[low, high]` (`eps_atr = 0.25`), and
- it is a **fresh** approach: at `t-1` the nearest level was farther than `eps_atr * ATR(t-1)`
  (prevents counting one consolidation as many events).

**One event per bar per source** (the single nearest level). ATR is Wilder(14), rolling only.

## 6. Outcome metrics (per event, per horizon)

Horizons (frozen, per TF): 4h `{6, 18, 36}`, 1d `{4, 12, 24}`, 1w `{2, 4, 8}`, 1M `{2, 3, 6}`.

- **`reject` (PRIMARY)** — within `H` bars price closes back on the approach side beyond `L` by
  `>= react_eps * ATR(t)` (`react_eps = 0.5`). Approach side from `close(t-1)` vs `L`. Bounce =
  the level repelled price. Direction-agnostic (no up/down prediction).
- `close_through` — a later close crosses `L` to the far side by `>= react_eps * ATR(t)`.
- `abs_fwd_move_atr` — `|close(t+H) - close(t)| / ATR(t)` (neutral move magnitude).
- `mfe_atr` / `mae_atr` — max favourable / adverse excursion over `(t, t+H]` in ATR units,
  relative to the approach side.

## 7. Out-of-sample split

- **Time-ordered only.** Per TF: first **70 %** of bars = train, last **30 %** = test.
- **Embargo / purge** of `max(horizon)` bars at the boundary (dropped) so no event's horizon
  straddles the split.
- No parameter is chosen on test; every parameter in §3–§6 is frozen here, before any result.

## 8. Statistics

- Primary horizon per TF = the **middle** horizon (4h:18, 1d:12, 1w:4, 1M:3).
- Per source per window: event count `N`, `reject_rate`, mean `abs_fwd_move_atr`,
  `close_through_rate`.
- **Permutation test** (seeded, `seed = 20260616`, 5000 reshuffles): FIB vs PLACEBO and FIB vs
  SWING on `reject_rate` in the **test** window → two-sided p-value.

## 9. Pre-registered robustness criterion (stop/go)

The behaviour signal is **robust → strategy sanity-check authorised** iff **all** hold:

1. `N_events >= 30` for FIB, PLACEBO and SWING in the **test** window (else underpowered).
2. FIB `reject_rate` **>** PLACEBO and **>** SWING in the **test** window.
3. Permutation `p < 0.05` for FIB-vs-PLACEBO **and** FIB-vs-SWING (test).
4. **Same sign** (FIB − baseline > 0) for both baselines in the **train** window too.

If any fails → **stop**, write the results report, **do not** run the strategy sanity-check.
A 1M/1w result with `N < 30` is reported descriptively but **cannot** satisfy the gate.

## 10. Optional strategy sanity-check (only if §9 passes)

One simple, **non-optimised** rule (e.g. fade a fresh fib touch in the rejection direction),
fixed fee+slippage, unit notional, report gross **and** net, drawdown, trade count, train/test
separately. Labelled **"research sanity-check," not a trading edge.** If it dies on costs or OOS
→ say so and stop. No parameter search, no variant-hunting.

## 11. Outputs

- `src/fibengine/research/fib_behaviour_event_study.py` + tests.
- Run artifacts (large) → `experiments/review/...` (gitignored); key numbers go in the report.
- Results report: `btc-fib-behaviour-event-study-results-20260616.md` (Observed / Inferred /
  Unverified; states beat-baselines-or-not, N, TFs, baselines, robust-or-weak, sanity-check
  run-or-stopped; **no trading claim**).

## 12. Non-goals honoured

No Genesis touch/import/export, no 1H, no ML/Optuna/optimisation, no parameter tuning on test,
no live/paper trading, no exchange, no label/corpus mutation, no large binary artifacts, no
"Phase 3". If a step needs any of these → **pause and report**.
