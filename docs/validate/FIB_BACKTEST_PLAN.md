# Fibonacci Backtest Plan

Staged roadmap for Layer A (swing selection) and Layer B (trade simulation) on real market data.

| Doc | Role |
|---|---|
| [TRACKS.md](TRACKS.md) | Research / Validate / Promotion |
| [GENESIS_BITFINEX_VALIDATE.md](GENESIS_BITFINEX_VALIDATE.md) | Bitfinex validate before Genesis-Core import |
| [../repository-layout-policy.md](../repository-layout-policy.md) | Structure, premortem, promotion gate |
| [../premortem/PREMORTEM.md](../premortem/PREMORTEM.md) | Risks this plan mitigates |

Premortem: record surprises in `premortem/reflections/` (short, not essays).

**Baseline config:** `config/settings.yaml` â€” do not overwrite from Research runs.  
**Candidates:** `config/variants/*.yaml` â€” see [../config/variants/INDEX.md](../config/variants/INDEX.md).

---

## Phase index

| Phase | Track | Status | Primary output |
|---|---|---|---|
| 1 Real-data stability matrix | Validate | **done** | `experiments/results/backtest_matrix.jsonl` |
| 2 Stability triage | Validate | **ongoing** | Reflection + ranked notes |
| 3 Manual label recall | Validate | **in progress** | `experiments/results/pivot_recall.jsonl` |
| 4 Layer B trade simulation | Validate | **smoke done** | `experiments/results/trade_*.jsonl` |
| 5 Iteration discipline | All | **active** | Policy + reflections |
| 6 Promotion gate | Promotion | **next** | Merge into `config/settings.yaml` |
| 7 Bitfinex / Genesis validate | Validate | **ready to run** | `backtest_matrix.jsonl` rows `exchange=bitfinex` |

---

## Phase 1 â€” Real-data stability matrix

**Status:** done (`matrix_20260528T072357Z` â€” see `premortem/reflections/2026-05-28-real-data-matrix.md`).

**Goal:** Layer A stays stable across liquid markets and timeframes with one scoring config.

**Scope (first matrix):** Bitfinex spot `BTC/USD`, `ETH/USD`, `SOL/USD` Ã— `15m`, `1h`, `4h`, 500 candles.

**Run:**

```bash
uv run python -m fibengine.backtest.matrix
```

**Output:** one JSONL row per case â†’ `experiments/results/backtest_matrix.jsonl`.  
**Runs:** `experiments/runs/stability/{YYYY-MM-DD}/bt_*/`.

**Success:** symbol, timeframe, limit, config hash, run id, metrics; failures as rows; comparable without opening every run folder.

**Later:** re-run matrix with expanded labels/timeframes (`30m`, `1d`, `1w`, `1M`) when label coverage is ready.

---

## Phase 2 â€” Stability triage

**Status:** ongoing (insights in real-data matrix reflection; no separate triage ledger yet).

**Goal:** Classify where the swing engine is strong enough for deeper work.

**Review:** low `flip_rate`, high `confirmed_rate`, high `direction_consistency`; investigate high `mean_endpoint_drift_bars`; flag `n_none > 0`.

**Output:** short ranked summary (stable / borderline / weak) in a reflection or batch note under `premortem/reflections/`.

---

## Phase 3 â€” Manual label recall

**Status:** in progress (labels under `data/labels/{exchange}/{symbol}/{timeframe}.json`; tooling active).

**Goal:** Pivot candidates can contain human-drawn swing endpoints before scoring changes.

**Note:** labels and screenshots are **reference**, not the objective function.

**Run:**

```bash
uv run python -m fibengine.evaluation.pivot_recall
```

**Output:** `experiments/results/pivot_recall.jsonl`.

**Success:** recall metrics exist per labeled market; failures separate detection vs scoring vs confirmation.

---

## Phase 4 â€” Layer B trade simulation

**Status:** smoke done (`trade_matrix_20260528T075650Z` in same reflection as Phase 1).

**Goal:** Test a simple trade model on **confirmed** Layer A swings only.

**Run:**

```bash
uv run python -m fibengine.backtest.trade
uv run python -m fibengine.backtest.trade_matrix
```

**Output:** `experiments/results/trade_backtests.jsonl`, `trade_matrix.jsonl`.

**Guardrail:** Layer B must not feed back into detection, scoring, or confirmation.

---

## Phase 5 â€” Iteration discipline

**Status:** active (codified in `repository-layout-policy.md` and [TRACKS.md](TRACKS.md)).

**Rules:**

- One meaningful change at a time.
- Config hash on every output row.
- Compare per symbol/timeframe, not only aggregates.
- Short reflection when assumptions change.

---

## Phase 6 â€” Promotion gate (Validate â†’ Promotion)

**Status:** next after variant beats baseline on Validate checks.

**Goal:** Move a proven candidate into trusted canonical config.

**Checklist (all required):**

1. Variant run with `fibengine.experiment --config config/variants/<candidate>.yaml` vs baseline â€” comparable metrics on same label set.
2. Stability matrix or single-market stability with variant â€” no regression vs baseline on weak rows from Phase 2.
3. `pivot_recall` not worse on held-out labeled pairs (or documented trade-off).
4. Short reflection: what changed, why promoted, what was rejected.
5. Update `config/settings.yaml` only after the above; archive variant rationale in `config/variants/INDEX.md`.

**Do not promote** from label agreement alone â€” Validate (stabilitet + recall) first, then Promotion. ViktÃ¤ndringar motiveras av principer (premortem), inte auto-tuning mot ritningar.

---

## Phase 7 â€” Bitfinex / Genesis-Core validate

**Status:** ready to run (profil + docs; krÃ¤ver nÃ¤t fÃ¶r CCXT-hÃ¤mtning).

**Goal:** Bevisa att Lager A hÃ¥ller pÃ¥ **Bitfinex**-candles (samma gates som baseline), innan Fib porteras till Genesis-Core paper/subaccount.

**Config:** `config/settings.bitfinex.yaml` (rÃ¶r inte `settings.yaml`).

**Guide:** [GENESIS_BITFINEX_VALIDATE.md](GENESIS_BITFINEX_VALIDATE.md).

**Run (matrix):**

```bash
uv run python -m fibengine.backtest.matrix \
  --config config/settings.bitfinex.yaml \
  --symbols BTC/USD,ETH/USD,SOL/USD \
  --timeframes 15m,1h,4h
```

**Success:** JSONL-rader med `"exchange": "bitfinex"`; gate/jÃ¤mfÃ¶relse mot Bitfinex Phase 1 dokumenterad i `premortem/reflections/`.

---

## Quick command reference

| Task | Module |
|---|---|
| Layer A experiment / plots | `fibengine.experiment` |
| Walk-forward stability | `fibengine.backtest.runner` |
| Stability matrix | `fibengine.backtest.matrix` |
| Pivot recall | `fibengine.evaluation.pivot_recall` |
| Trade backtest / matrix | `fibengine.backtest.trade`, `.trade_matrix` |
| Label UI | `fibengine.labeling.tool` |

All ledgers: `experiments/results/*.jsonl`. Run artifacts: `experiments/runs/{experiment|stability}/{date}/{run_id}/`.

