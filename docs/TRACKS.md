# Repo Tracks

Den här filen definierar de tre officiella spåren i repot:

1. **Research / Experiment**
2. **Validate**
3. **Promotion**

Syftet är att separera discovery från verifiering och från trusted behavior.

## 1) Research / Experiment

**Mål:** snabb discovery, hypotesdriven iteration.

**Tillåtet:**
- fri experimentation
- snabb iteration
- AI/reflection/premortem (obligatoriskt enligt policy)
- Optuna/tuning och andra utforskande metoder

**Inte krav:** full correctness eller production-grade stabilitet.

**Primära ytor:**
- `config/variants/*.yaml`
- `src/fibengine/tuning/`
- `experiments/runs/optuna/`
- `experiments/label_review/`
- `premortem/reflections/`

## 2) Validate

**Mål:** bevisa att en kandidat håller, reproducerbart.

**Krav:**
- reproducerbara testkörningar
- replay/backtest
- stabilitetskontroller
- tydlig jämförelse mot baseline

**Primära ytor:**
- `tests/`
- `experiments/runs/stability/`
- `experiments/results/backtests.jsonl`
- `experiments/results/backtest_matrix.jsonl`
- `experiments/results/pivot_recall.jsonl`

## 3) Promotion

**Mål:** minimal, tydlig, trusted canonical surface.

**Krav:**
- verifierad via Validate-spåret
- låg regressionsrisk
- dokumenterad och spårbar

**Canonical ytor:**
- `config/settings.yaml` (baseline)
- `src/fibengine/core/` + etablerade runtime-moduler
- `README.md` snabbstart
- `REPO_POLICY.md`

## Promotion-gate (MÅSTE)

En förändring får promoted status först när:

1. Kandidaten finns i `config/variants/*.yaml` (Research).
2. Relevant Validate-körning finns dokumenterad i `experiments/results/*` och/eller
   `experiments/runs/stability/*`.
3. Tester passerar (`uv run pytest`).
4. Kort reflektion finns i `premortem/reflections/` med beslut och nästa steg.

Först därefter får ändring övervägas till `config/settings.yaml` eller canonical behavior.
