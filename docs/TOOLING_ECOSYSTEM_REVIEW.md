# Verktygs- & ekosysteminventering (read-only review)

> Status: **utvärdering & rekommendation** — **inte** adoption. Svarar mot issue #25 och
> vidgar den med ett agent-ekosystemlager. Auktoriserar **ingen** dependency-ändring,
> trading-logik eller Genesis-integration. Adoption sker först via separata scoped issues
> (`REPO_POLICY.md §13`).
>
> Delar: denna fil (grounding + evidensläge) · `TOOLING_ECOSYSTEM_CATEGORIES_A.md`
> (kat. 1–8) · `TOOLING_ECOSYSTEM_CATEGORIES_B.md` (kat. 9–16) ·
> `TOOLING_ECOSYSTEM_DECISIONS.md` (kopiera/undvik · struktur · roadmap · risk · checklist).

## Scope-avvikelse (flaggad)

Den efterfrågade grounding-branchen `cursor/fib-context-review-overlay-64ac` fanns **inte**
i klonen vid granskningen (endast `main` + arbetsbranch). Grounding gjordes mot aktuell
branch (utgrenad från `main`). Overlay-koden (PR #20 / issue #21) är därför **ej direkt
granskad** → markerad *Unverified*. Scannen är i den meningen ofullständig för overlay-arbetet.

## 1. Repo-grounding (Observed)

**Vad Fib är:** deterministisk research-/prototyp-engine (`fibengine`, ~6 100 LOC) som väljer
swing high/low "som en teknisk analytiker", ritar Fib och itererar. MVP. Ingen webbserver/DB —
CLI-moduler (`experiment`, `backtest`, `labeling`) + valfri Matplotlib-GUI (`AGENTS.md:7`).

Befintlig disciplin som **inte** ska återuppfinnas:

| Pelare | Mekanism | Evidens |
|---|---|---|
| 3-spårsmodell | Research → Validate → Promotion | `docs/TRACKS.md:1-73` |
| Promotion-gate (MÅSTE) | variant-kandidat + Validate-evidens + grön pytest + reflektion | `docs/TRACKS.md:63-73`, `REPO_POLICY.md §13` |
| Human vs machine labels | `source="human"`=facit; `source="machine"`=kandidat, aldrig facit | `labeling/store.py`, `docs/MACHINE_LABELING.md` |
| → maskin överskriver aldrig human | skip om human-label finns (`skipped_human`) | `labeling/autolabel.py` |
| → maskin exkluderas från eval | agreement/recall mäts bara mot human | `experiment.py`, `worklist.py` |
| Anti-optimering | Optuna borttaget medvetet ("labels = referens, inte domare") | `archive/.../optuna/`, reflektion 2026-05-28 |
| Append-only ledgers | `experiments/results/*.jsonl` + immutabla per-run-mappar | repo |
| Reproducerbarhet | pydantic-config + `config_hash=sha256[:12]`; Loguru binder run_id+hash | `core/config.py`, `core/logging_conf.py` |
| Validation-gate (kod) | causal walk-forward + `stability_gate` (flip/confirmed/direction/drift) | `backtest/stability.py`, `config/settings.yaml:61-70` |
| Anti-blob bounds | `.py` ≤400/25KiB; docs ≤200/20KiB; reflektioner ≤80/8KiB | `REPO_POLICY.md §2B`, `scripts/check_repo_bounds.py` |
| Kvalitetsgrindar | pre-commit (ruff/bounds/pytest); CI cov ≥60%; 134 tester, syntetiska fixtures | `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| Premortem-disciplin | 13 failure-modes + obligatorisk reflektion per beslut | `premortem/PREMORTEM.md`, `.../INDEX.md` |
| Stack | uv + ruff + pytest + pydantic + loguru + matplotlib + ccxt | `pyproject.toml`, `uv.lock` |

**Aktiv hypotes (Research):** Hypotes A — kan maskin-kandidater för fib-level-events approximera
mänsklig review så människan bara spot-checkar? (`docs/RESEARCH_HANDOFF.md`, issue #12).

**Faktiskt behov (öppna issues):** #24 research-tooling (plotting/validering/backtest); #15–#21
review-chart/fib-overlay UX; #16 spike: fib-aware annotation/review-verktyg; #22 backtesta
kandidater mot forward outcomes; #23 MTF interaction-fingerprints; #14 top-down fib-ladder.
→ Tyngdpunkt: **visuell review/annotation + data-validering + lättviktig event-study**. Inte
agent-orchestration, inte tung governance.

**Greenfield (Observed):** ingen `.claude/`-katalog, inga skills/subagents/prompt-/eval-filer,
ingen tracing. Endast `AGENTS.md` (Cursor) + `.vscode/settings.json`.

## Evidensläge — Observed / Inferred / Unverified

**Observed:** all grounding i §1 (lästa filer); issue #14–#25 via GitHub; externa
verktygsfakta cross-checkade mot primärkällor (anthropics/skills öppen standard 2025-12-18,
Claude Code subagents-format, LangGraph 1.0, AutoGen maintenance mode, Letta v0.16.8, DSPy 3.2.1,
promptfoo/DeepEval/Inspect MIT, Phoenix/Langfuse/OpenLLMetry, OWASP LLM 2025 + Agentic 2025-12,
Semgrep 1.160, pandera 0.31.1, pydantic 2.13.4, duckdb 1.5.x, pyarrow 21, ruptures 1.1.10,
stumpy 1.13, uv 0.11.19, ruff 0.15, vectorbt 1.0 Apache+Commons Clause, empyrical övergivet 2020,
pandas-ta arkiveringsrisk, TA-Lib wheels).

**Inferred:** Loguru + immutabla run-mappar ≈ tracing/replay för engine-körningar;
ROI-ordning (label-kontrakt > review-rendering > query-lager) utifrån öppna issues + filosofi;
multi-agent-orchestration = negativ ROI för detta single-dev-repo.

**Unverified (kräver kontroll före beslut):**
- Branch `cursor/fib-context-review-overlay-64ac` saknas → overlay (PR #20/issue #21) ej granskad.
- Exakta versioner märkta *UV* i kategorifilerna (vissa patch-nummer, senaste-releaser).
- Vissa licenser *UV* (mplfinance, streamlit, bokeh, backtesting.py [misstänkt AGPL], TA-Lib,
  ruptures, stumpy, tsfresh m.fl.) — verifiera mot PyPI/GitHub/release före adoption.
- pre-commit.ci status; Claude Agent SDK exakt license/version.
