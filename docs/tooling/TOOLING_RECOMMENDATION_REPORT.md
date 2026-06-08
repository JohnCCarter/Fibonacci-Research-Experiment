# Tooling recommendation report (issue #25)

> **Status:** read-only evaluation — **not** adoption. Closes the deliverable in
> [GitHub #25](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/25).
> No dependency changes, trading logic, or Genesis integration. Adoption only via
> separate scoped issues (`REPO_POLICY.md` §13).
>
> **Per-tool tables:** [TOOLING_RECOMMENDATION_TOOLS.md](TOOLING_RECOMMENDATION_TOOLS.md)
>
> **Related (separate scope):** open PR #26 adds an *agent/CI* inventory layer — useful
> supplement, **not** a substitute for this report (see § Relation to PR #26).

## Scope

Evaluate external tools for the Fib **Python research workflow**: visualization, review,
validation, annotation, event-study, artefacts, querying, CI, and data provenance —
while preserving deterministic outputs, human facit, and separation from Genesis V2.

**Out of scope:** implementation, new deps, promotion, edge claims, Genesis merge.

## Repo grounding (Observed, 2026-06-08)

| Already in stack | Role |
|------------------|------|
| `uv` + `uv.lock` | Reproducible env |
| `ruff`, `pytest`, `pre-commit` | Fail-fast quality |
| `pydantic` | Config + models |
| `matplotlib` | Review PNG + labeling GUI |
| `ccxt` | Candle fetch |
| Custom `research/*` | Event-study (#22), fingerprints (#23), MTF projection, review pack |

**Prior art on main:** [FIB_AWARE_TOOLING_SPIKE.md](FIB_AWARE_TOOLING_SPIKE.md) (#16 — keep
Matplotlib JSON review path). Fib-aware review (#15–#21) **done**.

## Strategy (summary)

1. **Protect facit first** — schema contracts on labels/ledgers (`pandera` + extend `pydantic`).
2. **Keep review JSON-first** — improve existing `human_review_level_events`; optional
   `mplfinance` only if it *reduces* matplotlib maintenance.
3. **Query ledgers before new storage** — `DuckDB` over append-only JSONL; keep JSONL git-friendly.
4. **Event-study stays repo-native** — `fib_candidate_outcomes` / fingerprints already built; external
   backtest libs = reference/sandbox only.
5. **Sandbox isolation** — vectorbt, ruptures, stumpy, tsfresh, indicators never become facit.
6. **Defer platforms** — Label Studio, docs-sites, multi-agent frameworks until volume demands.

## Priority vs issue #25 hypothesis

| Issue #25 hypothesis | This report |
|----------------------|-------------|
| Adopt Now: mplfinance, pandera, pydantic, duckdb, pre-commit/ruff/pytest, uv | **Agree** except mplfinance → **Adopt Later** (hand-rolled fib overlay works; #16 spike) |
| Adopt Soon: Streamlit+Plotly, hypothesis, Parquet | **Agree** — all **Adopt Later** |
| Sandbox: vectorbt, ruptures, stumpy, tsfresh, swing baselines | **Agree** |
| Later: Label Studio, MLflow, DVC, Quarto/marimo/mkdocs | **Agree** |

## Recommendation categories used

`Adopt Now` · `Adopt Later` · `Research Sandbox Only` · `Annotation Later` ·
`Documentation/Reference Only` · `Reject` · **`In repo`** (already adopted or built custom)

## Follow-up implementation issues (suggested, not opened here)

| Priority | Topic | Typical tools |
|----------|--------|---------------|
| 1 | Label/ledger schema contracts | pandera, pydantic |
| 2 | DuckDB report SQL over JSONL | duckdb |
| 3 | hypothesis invariants | hypothesis |
| 4 | Optional mplfinance simplification | mplfinance |
| 5 | Streamlit review workbench (if matplotlib blocks) | streamlit, plotly |
| 6 | Isolated sandboxes | vectorbt, ruptures, … |

## Key risks (from #25)

- Indicator/feature soup obscuring the fib hypothesis → **Reject** or strict sandbox.
- Swing/anchor libs becoming silent facit → baseline/diagnostic only.
- Interactive UI maintenance without volume → defer (#16 outcome).
- Sandbox output leaking into governance → reconcile to deterministic ledgers only.

## Success criteria (#25) — mapping

| Criterion | Met by |
|-----------|--------|
| High-ROI tools identified | [TOOLS.md](TOOLING_RECOMMENDATION_TOOLS.md) + § Strategy |
| Avoid unnecessary custom infra | Prefer DuckDB/SQL over bespoke DB; keep JSONL; optional mplfinance |
| Genesis separation | Explicit out-of-scope |
| Deterministic auditable outputs | Sandbox + annotation rules in tables |
| Each candidate classified | TOOLS.md |
| Follow-up issues only where justified | § Follow-up (suggested list) |

## Relation to PR #26

[PR #26](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/pull/26) (`claude/fib-tools-ecosystem-inventory-jBjBN`)
documents **16 categories** including agent skills, subagents, CI hardening, and OWASP
checklists. That is **additive** research on the *agent/IDE* layer. Issue #25 targets
the *Fib Python research pipeline*; this report fulfills #25 on `main` without merging PR #26.
