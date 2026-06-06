# Beslut: kopiera / undvik · struktur · roadmap · risk · checklist

> Del av `TOOLING_ECOSYSTEM_REVIEW.md`. Inga beslut här är adoption — varje steg kräver eget
> scoped issue + explicit order (`REPO_POLICY.md §13`).

## Kopiera **som idé** (repo-native, ej rakt av)

| Pattern/verktyg | Idé att extrahera | Varför Fib |
|---|---|---|
| Claude Agent Skills (SKILL.md) | filbaserade procedurminnen som kodar repo-regler | deterministiskt, anti-blob |
| Claude Code subagents | read-only-default roller med tool-allowlist | skyddar canonical-ytor |
| Anthropic context-engineering | compaction, note-taking, sub-agent-isolation, JIT | långa sessioner |
| CoALA-taxonomi | procedurellt=skills, semantiskt=docs, episodiskt=reflections/ledgers | organiserar artefakter |
| pandera/pydantic/jsonschema | fail-fast schema-grindar, `source`-enum | skyddar human-facit |
| DuckDB report-queries (incheckade `.sql`) | reproducerbar aggregering över JSONL/Parquet | frågbar evidens utan DB |
| mplfinance statiska PNG | deterministiska candlestick+fib-overlay | snabbare review |
| Streamlit+Plotly review-workbench | append-only `source`-märkt output | issue #16 minsta-verktyg |
| OWASP LLM/Agentic-checklistor | untrusted-data + tool-misuse-medvetenhet | agent+PR/CI-yta |
| Actions-härdning (SHA-pin, least-priv) | supply-chain-säkert CI | matchar determinism |
| reviewdog + *en* AI-reviewer | inline linter-feedback | låg-brus PR-review |
| ADR-light (MADR) | formalisera daterade reflektioner | bygger på befintligt |
| Minimal custom event-study | egen MFE/MAE/forward-outcome-modul | kärnan i hypotes A |
| vectorbt *som isolerad sandbox* | snabba sweeps, aldrig facit | acceleration utan black-box-beslut |

## Undvik (eller starkt villkora)

| Undvik | Skäl |
|---|---|
| Multi-agent-ramverk (CrewAI, AutoGen=maintenance, AG2, MAF) | fel modell för single-dev; tung yta |
| LLM-guardrail-stack (NeMo, Guardrails AI, Llama Guard, Rebuff, garak) | endast för exponerad LLM-endpoint |
| SaaS eval/observability (Braintrust, LangSmith, OpenAI Evals=deprekeras) | ej local-first/git-native |
| empyrical | övergivet (sista release 2020) → empyrical-reloaded |
| pandas-ta | repo-churn + arkiveringsrisk juli 2026 + paid-tier |
| stock-indicators | kräver .NET SDK + pythonnet → CI-friktion |
| doccano | inaktivt (ingen PyPI-release på 12 mån) |
| vectorbt/backtesting.py som beslutsgrund | Commons Clause / AGPL + black-box vs deterministiska ledgers |
| Label Studio/CVAT nu | Docker-stackar; overkill; risk maskin→facit-glidning |
| docs-site (mkdocs/Quarto) nu | för litet; bryter lättvikts-disciplin |
| tredjeparts-skills/agent-regler rakt av | kan bryta fib-filosofin; extrahera pattern |
| Jupyter som källa-till-sanning | icke-deterministisk cell-ordning |

## Rekommenderad Fib-native struktur

```
.claude/
  skills/
    fib-label-integrity/SKILL.md      # human=facit, machine=kandidat; aldrig override/agreement-opt
    promotion-gate-check/SKILL.md     # de 4 gate-kraven (TRACKS.md:63-73)
    research-reflection/SKILL.md      # mall: hypotes/scope/observationer/beslut/nästa steg (≤80 rader)
    experiment-run/SKILL.md           # kör experiment/backtest, läs ledgers, tolka stability_gate
    ecosystem-scan/SKILL.md           # read-only inventerings-metod (Observed/Inferred/Unverified)
  agents/
    explore.md                        # read-only sök (tools: Glob,Grep,Read)
    label-auditor.md                  # verifierar source-separation & label-invarianter (read-only)
    validate-runner.md                # kör Validate-spårets backtests/stability (ingen canonical write)
    promotion-gatekeeper.md           # read-only; blockar promotion utan Validate-evidens+reflektion
docs/
  CONTEXT_MAP.md                      # pekare till TRACKS/REPO_POLICY/RESEARCH_HANDOFF/PREMORTEM
  GLOSSARY.md                         # VAD/HUR/Lager A/B/facit/kandidat/confirmed/provisorisk
```
Principer: alla agent-instruktioner = git-incheckade filer; subagents read-only-default med minimal
tool-allowlist; skills citerar policy med file:line; anti-blob-bounds gäller även `.claude/`-filer;
**ingen** skill/subagent får optimera mot agreement eller behandla maskin som facit.

## Prioriterad roadmap (allt gated på explicit order; varje steg = eget scoped issue)

**Fas 0 (klar):** denna read-only inventering. Inga kodändringar.

**Fas 1 — permanent dev-infra, låg risk, högst ROI:**
1. Label-/ledger-schemakontrakt (pandera+pydantic) som upprätthåller `source`-separation. *(kärnskydd)*
2. Repo-native `.claude/skills` + read-only subagents (`fib-label-integrity`, `promotion-gate-check`, `label-auditor`, `explore`).
3. CI-/supply-chain-härdning: SHA-pin, least-priv token, push protection, gitleaks pre-commit, pip-audit.
4. mplfinance statisk review-renderare i `viz/`.
5. GLOSSARY.md + CONTEXT_MAP.md; formalisera reflektioner som ADR-light.

**Fas 2 — när behov bekräftats:**
6. DuckDB report-query-lager (incheckade `.sql`) över JSONL-ledgers.
7. Minimal custom event-study-modul (`research/`) för forward-outcomes (#22) — append-only, causal.
8. hypothesis property-tester för fib-invarianter (range/level/event-window).
9. Lätt Streamlit+Plotly review-workbench (#16), `source`-märkt append-only-output.
10. PR-review: reviewdog + en AI-reviewer (Claude Code Action, `claude-opus-4-8`).

**Fas 3 — sandbox/senare, strikt isolerat:**
11. vectorbt-sandbox (efter license-godkännande), ruptures/stumpy/tsfresh isolerat.
12. Evals/observability (promptfoo/DeepEval; Phoenix/Langfuse) — endast om agent-/LLM-i-loop införs.
13. Label Studio, mkdocs/Quarto, Parquet-migrering — endast vid skala.

## Riskregister

| Risk | Allvar | Mitigering |
|---|---|---|
| Maskin-labels→facit / agreement-optimering smyger tillbaka | **Kritisk** | schemakontrakt + `label-auditor` + bevarade tester; skills förbjuder |
| Promotion utan Validate-evidens | **Hög** | `promotion-gatekeeper` (read-only) kräver ledger-länk + reflektion |
| Prompt-injection via issue/PR/CI-data | Hög | "untrusted external data"-regel; least-priv allowlist; sandbox |
| Sandbox-resultat läcker in i slutsatser | Hög | strikt isolering; reconciliera mot deterministiska ledgers |
| License-fällor (vectorbt Commons Clause, backtesting.py AGPL) | Medel | granska före adoption; sandbox/dev-only |
| Beroende-förfall (pandas-ta, empyrical) | Medel | undvik; pinna hash; välj underhållna alternativ |
| Komprometterad Action / överbehörig token | Medel | SHA-pin, least-priv token, Harden-Runner |
| Tooling-blobs bryter bounds | Låg | `check_repo_bounds.py` gäller även nya filer/skills |
| Review-verktyg auto-genererar facit | Hög | human anchor = sanning; output `source`-märkt; ingen auto-fib/ML |
| Branch-grounding ofullständig (overlay saknas) | Info | flaggat; verifiera mot PR #20 innan overlay-beslut |

## Verification checklist (innan någon adoption)
- [ ] Eget scoped issue + explicit order (`REPO_POLICY.md §13`).
- [ ] Liten diff, rollback-väg, before/after-verifiering.
- [ ] `uv run pytest -q` grön; coverage ≥60%; ruff check+format rena.
- [ ] `scripts/check_repo_bounds.py` grön (inkl. nya `.claude/`-filer).
- [ ] Bevarat: maskin skriver aldrig över human; maskin exkluderas från recall/agreement.
- [ ] Ingen agreement-optimering mot human labels.
- [ ] Inga promotion-rekommendationer utan Validate-evidens i `experiments/results/*`.
- [ ] Externa licenser granskade (särskilt vectorbt Commons Clause, backtesting.py AGPL).
- [ ] Versioner pinnade i `uv.lock`; pip-audit/gitleaks grön.
- [ ] Sandbox-verktyg isolerade från canonical ledgers.
- [ ] Reflektion i `premortem/reflections/` (≤80 rader/8 KiB).
- [ ] Ingen Genesis V2-integration eller trading-logik berörd.
