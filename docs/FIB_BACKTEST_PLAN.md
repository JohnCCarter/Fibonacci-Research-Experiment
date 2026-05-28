# Fibonacci Backtest Plan

Staged roadmap for Layer A (swing selection) and Layer B (trade simulation) on real market data.

| Doc | Role |
|---|---|
| [TRACKS.md](TRACKS.md) | Research / Validate / Promotion |
| [../REPO_POLICY.md](../REPO_POLICY.md) | Structure, premortem, promotion gate |
| [../premortem/PREMORTEM.md](../premortem/PREMORTEM.md) | Risks this plan mitigates |

Premortem: record surprises in `premortem/reflections/` (short, not essays).

**Baseline config:** `config/settings.yaml` — do not overwrite from Research runs.  
**Candidates:** `config/variants/*.yaml` — see [../config/variants/INDEX.md](../config/variants/INDEX.md).

---

## Phase index

| Phase | Track | Status | Primary output |
|---|---|---|---|
| 1 Real-data stability matrix | Validate | **done** | `experiments/results/backtest_matrix.jsonl` |
| 2 Stability triage | Validate | **ongoing** | Reflection + ranked notes |
| 3 Manual label recall | Validate | **in progress** | `experiments/results/pivot_recall.jsonl` |
| 4 Layer B trade simulation | Validate | **smoke done** | `experiments/results/trade_*.jsonl` |
| 5 Iteration discipline | All | **active** | Policy + reflections |
| 6 ~~Optuna / variants~~ | — | **withdrawn** | Archived under `archive/` (optimerade mot labels) |
| 7 Promotion gate | Promotion | **next** | Merge into `config/settings.yaml` |

---

## Phase 1 — Real-data stability matrix

**Status:** done (`matrix_20260528T072357Z` — see `premortem/reflections/2026-05-28-real-data-matrix.md`).

**Goal:** Layer A stays stable across liquid markets and timeframes with one scoring config.

**Scope (first matrix):** Binance spot `BTC/USDT`, `ETH/USDT`, `SOL/USDT` × `15m`, `1h`, `4h`, 500 candles.

**Run:**

```bash
uv run python -m fibengine.backtest.matrix
```

**Output:** one JSONL row per case → `experiments/results/backtest_matrix.jsonl`.  
**Runs:** `experiments/runs/stability/{YYYY-MM-DD}/bt_*/`.

**Success:** symbol, timeframe, limit, config hash, run id, metrics; failures as rows; comparable without opening every run folder.

**Later:** re-run matrix with expanded labels/timeframes (`30m`, `1d`, `1w`, `1M`) when label coverage is ready — still Validate, not Research tuning.

---

## Phase 2 — Stability triage

**Status:** ongoing (insights in real-data matrix reflection; no separate triage ledger yet).

**Goal:** Classify where the swing engine is strong enough for deeper work.

**Review:** low `flip_rate`, high `confirmed_rate`, high `direction_consistency`; investigate high `mean_endpoint_drift_bars`; flag `n_none > 0`.

**Output:** short ranked summary (stable / borderline / weak) in a reflection or batch note under `premortem/reflections/`.

---

## Phase 3 — Manual label recall

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

## Phase 4 — Layer B trade simulation

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

## Phase 5 — Iteration discipline

**Status:** active (codified in `REPO_POLICY.md` and [TRACKS.md](TRACKS.md)).

**Rules:**

- One meaningful change at a time.
- Config hash on every output row.
- Compare per symbol/timeframe, not only aggregates.
- Short reflection when assumptions change.

---

## Phase 6 — ~~Optuna / config variants~~ (WITHDRAWN)

**Status:** **withdrawn.** Automatisk vikt-optimering togs bort. Objektivet
maximerade `agreement`/`fib_err` mot de manuella labelsen — vilket bryter mot
filosofin (labels = referens, inte domare) och överanpassade ett för litet
labelset (best agreement ≈ 0.025, principvidriga negativa vikter). Se
`premortem/reflections/2026-05-28-optuna-rollback.md`. Artefakter arkiverade
under `archive/experiments/optuna/` och `archive/config_variants/`.

**Ersättning:** vikter sätts manuellt på principgrund och sparas som
`config/variants/<beskrivning>.yaml`, validerade enligt Phase 7 mot stabilitet/
recall — inte mot en label-agreement-objektivfunktion.

---

## Phase 7 — Promotion gate (Validate → Promotion)

**Status:** next after variant beats baseline on Validate checks.

**Goal:** Move a proven candidate into trusted canonical config.

**Checklist (all required):**

1. Variant run with `fibengine.experiment --config config/variants/<candidate>.yaml` vs baseline — comparable metrics on same label set.
2. Stability matrix or single-market stability with variant — no regression vs baseline on weak rows from Phase 2.
3. `pivot_recall` not worse on held-out labeled pairs (or documented trade-off).
4. Short reflection: what changed, why promoted, what was rejected.
5. Update `config/settings.yaml` only after the above; archive variant rationale in `config/variants/INDEX.md`.

**Do not promote** from a label-agreement objective alone — Validate against
stability/recall first, then Promotion. (Automatic optimization against labels
is disallowed; see Phase 6.)

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
