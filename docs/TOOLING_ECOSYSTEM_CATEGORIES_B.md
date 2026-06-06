# Kategori-findings B (kat. 9–16)

> Del av `TOOLING_ECOSYSTEM_REVIEW.md`. Samma format som del A.
> Externa fakta = webb-verifierade juni 2026 (*UV* = ej pinnad version/licens).

## 9. Evals / regression testing för agentbeteende
- **Problem:** agent-/LLM-beteende (om/när det används) kan regrera tyst.
- **Behöver:** lokala, deterministiska, git-incheckade eval-suiter — inte hostad SaaS.
- **Etablerade:** promptfoo (MIT, deklarativ YAML, deterministiska asserts), DeepEval (MIT, "pytest för LLM"), Inspect (`inspect_ai`, MIT, 0.3.236); OpenAI Evals (hostad **deprekeras**), Braintrust/LangSmith (SaaS).
- **Kopiera:** deterministiska asserts framför LLM-judge; cases-som-filer i git; fail-on-regression i CI; pytest-native-mönstret.
- **Importera EJ:** SaaS-kopplade plattformar; LLM-judge som primär grind.
- **Repo-native:** om agent-i-loop införs: `tests/evals/` med promptfoo-YAML eller rena pytest-asserts; annars ingen adoption nu.
- **ROI-först:** vänta tills LLM-i-loop finns; då promptfoo eller DeepEval.
- **Risker:** eval-suite optimerad mot human labels = förbjuden agreement-optimering.
- **Verifiering:** deterministiska asserts; cases incheckade; ingen koppling till label-tuning.
- **Skjut upp:** hela kategorin tills agent-beteende ingår i flödet.

## 10. Observability / tracing / replay
- **Problem:** om agenter/LLM körs saknas spårning/replay för felsökning.
- **Behöver:** self-hostbar, lättviktig tracing; replay via dataset.
- **Etablerade:** Arize Phoenix (Elastic-2.0, local-first), Langfuse (self-host, replay + dataset-experiment), OpenLLMetry (Apache-2.0, OTel), OTel GenAI semconv.
- **Kopiera:** OTel GenAI-konventioner som mål; record/replay-via-dataset (VCR-stil) — matchar immutabla run-mappar.
- **Importera EJ:** SaaS-kopplad tracing (LangSmith); tung stack i en icke-serverande engine.
- **Repo-native:** befintlig Loguru run-context (`run_id`+`config_hash`) + immutabla run-mappar ÄR redan tracing/replay.
- **ROI-först:** ingen adoption nu; behåll Loguru+ledgers.
- **Risker:** dubbel tracing-yta; data-exfiltrering via hostad backend.
- **Verifiering:** endast self-host om något; ingen utgående telemetri default.
- **Skjut upp:** Phoenix/Langfuse tills agent-/LLM-tracing behövs.

## 11. Research → Validate → Promotion gates
- **Problem:** risk att kandidater promotas utan evidens (Goodhart, regression).
- **Behöver:** kodifierad gate-kontroll — finns redan som policy, kan stärkas som verktyg/skill.
- **Etablerade:** inget externt slår repots `TRACKS.md` + `stability_gate`; externa CI-gates kan upprätthålla mekaniskt.
- **Kopiera:** inget utifrån — intern modell starkare än generiska MLOps-gates.
- **Importera EJ:** tunga MLOps-promotion-pipelines (Kubeflow/MLflow-stages) — fel altitud.
- **Repo-native:** `promotion-gate-check`-skill + `promotion-gatekeeper`-subagent (read-only) som verifierar de 4 kraven.
- **ROI-först:** skill+subagent som mekaniskt kollar gate-kraven (hög skyddseffekt, låg risk).
- **Risker:** promotion-rekommendation utan Validate-evidens (förbjudet).
- **Verifiering:** gatekeeper kräver länk till `experiments/results/*` + reflektion; annars block.
- **Skjut upp:** automatisk promotion (ska förbli mänskligt beslut).

## 12. Security (skills/tools/prompt injection/repo-miljö)
- **Problem:** agenter + verktyg + extern data (issues/PR/CI-loggar) = injection & tool-misuse-yta.
- **Behöver:** least-privilege, sandbox, injection-medvetenhet, supply-chain-pinning.
- **Etablerade:** OWASP LLM Top 10 (2025, LLM01 injection), OWASP Agentic Top 10 (2025-12, ASI02 tool misuse), Anthropic Claude Code sandboxing; Semgrep 1.160, gitleaks, TruffleHog/pip-audit, GitHub push protection, Dependabot, `uv.lock`+hashes, Sigstore/PEP 740.
- **Kopiera:** OWASP LLM01/ASI02 som checklista; behandla extern textdata som otillförlitlig; least-priv tool-allowlist; sandbox med nät-allowlist.
- **Importera EJ:** LLM-guardrail-stacken (NeMo/Guardrails/Llama Guard/Rebuff/garak) — endast för exponerad LLM-endpoint.
- **Repo-native:** gitleaks i pre-commit; pip-audit i CI; `uv.lock`+hashes (finns); subagent-allowlists; regel "extern data = untrusted".
- **ROI-först:** push protection + gitleaks pre-commit + pip-audit (gratis, låg friktion, permanent).
- **Risker:** injektion via PR-/issue-innehåll; läckta secrets; beroende-kompromiss.
- **Verifiering:** secret-scan grön; deps pinnade+hashade; subagents kan ej skriva canonical-ytor.
- **Skjut upp:** modellbaserade injection-detektorer tills LLM-yta exponeras.

## 13. GitHub / CI / PR-review automation
- **Problem:** CI/PR-flödet kan stärkas (säkerhet, review) utan tung infrastruktur.
- **Behöver:** härdat CI, deterministisk linter-feedback, *en* AI-reviewer max.
- **Etablerade:** Actions-härdning (SHA-pin, least-priv `GITHUB_TOKEN`), Harden-Runner, OpenSSF Scorecard, CodeQL (gratis publikt), Dependabot; reviewdog, Danger, Claude Code GitHub Action (GA, kan ställas till `claude-opus-4-8`), CodeRabbit (gratis OSS).
- **Kopiera:** SHA-pinning + minimibehörighet; reviewdog för inline ruff/semgrep; *en* AI-reviewer.
- **Importera EJ:** dubbla AI-reviewers (brus); breda write-behörigheter i CI.
- **Repo-native:** utöka `ci.yml`: pin actions till SHA, `permissions: read-all` + per-job-grants, lägg pip-audit/gitleaks/CodeQL; ev. reviewdog/Claude Action.
- **ROI-först:** SHA-pin + least-priv token + CodeQL/push protection (permanent säkerhetsbas).
- **Risker:** komprometterad action (tag-hijack); överbehörig token; AI-reviewer som agerar på injicerat innehåll.
- **Verifiering:** inga otpinnade actions; token least-priv; AI-reviewer endast read + kommentar.
- **Skjut upp:** CodeRabbit om Claude Action väljs; tunga policy-bots.

## 14. Documentation / context maps / ADR / glossary
- **Problem:** beslut & domänspråk spridda (sv/en-mix); ADR implicit (daterade reflektioner).
- **Behöver:** lätt formalisering — inte en docs-plattform.
- **Etablerade:** mkdocs-material 9.7.6 (MIT), Quarto (binär), marimo, ADR-konventioner (MADR), glossary-workflows.
- **Kopiera:** ADR-light (reflektioner ÄR redan ADR:er — formalisera rubriker); glossary-pattern; context-map.
- **Importera EJ:** docs-site (mkdocs/Quarto) nu (för litet); Jupyter som källa-till-sanning (icke-deterministisk).
- **Repo-native:** `docs/CONTEXT_MAP.md` + `docs/GLOSSARY.md` (VAD/HUR/Lager A/B/facit/kandidat/confirmed); reflektioner som ADR-light (≤80-rader-bound); behåll `INDEX.md`.
- **ROI-först:** GLOSSARY + CONTEXT_MAP (billigt, minskar drift).
- **Risker:** docs som blir blobs eller divergerar från policy.
- **Verifiering:** anti-blob-bounds; context-map länkar canonical docs.
- **Skjut upp:** mkdocs/Quarto-site tills metodiken stabiliserats.

## 15. Visualization / annotation / review tooling (HÖGT BEHOV — issues #15–#21, #24)
- **Problem:** manuella close-line-plots är trubbiga för touch/rejection/continuation runt fib-nivåer; review är sliggish.
- **Behöver:** tydlig OHLC + fib-overlay + event-markörer; deterministiska review-bilder; snabbare review. Human-ritad fib = sanning.
- **Etablerade:** mplfinance (BSD, statiska candlesticks), plotly (MIT), streamlit 1.55 (Apache-2.0), bokeh/panel/dash; annotation: Label Studio (Apache, Docker), CVAT, doccano (**stale**).
- **Kopiera:** mplfinance för deterministiska review-PNG (kompletterar `viz/plot.py`); Streamlit+Plotly som *lätt* review-workbench med append-only JSONL (matchar #16).
- **Importera EJ:** Label Studio/CVAT nu (Docker, overkill, risk maskin-pre-labels→facit); doccano (stale); auto-fib/ML i verktyget (förbjudet enligt #16).
- **Finns redan (Observed, PR #20):** `research/human_review_level_events.py` har en context-first fib-overlay-renderare (`_draw_fib_context`): human-leg-pil, H/L-ankare, full fib-stack + aktiv nivå, vy vidgad till hela H/L-spannet (issue #21). Handrullad matplotlib.
- **Repo-native:** behåll/utöka den befintliga renderaren; mplfinance vore en *förenkling* (ej greenfield). Ev. liten Streamlit-app som läser candles+human-anchors+events, skriver `source`-märkt JSONL.
- **ROI-först:** stabilisera befintlig renderare; mplfinance-migrering endast om den minskar kod/maintenance (filen är grandfathered & växer → dela före tillväxt).
- **Risker:** interaktiv UI ökar maintenance; verktyg som auto-genererar facit; Streamlit bytte till Starlette/Uvicorn 2026 → pinna & retesta.
- **Verifiering:** output `source`-märkt; human anchor = sanning; deterministiska bilder; pinnade versioner.
- **Skjut upp:** Label Studio tills annotation-volym överstiger tröskel; full React/TradingView-UI.

## 16. Backtest / experiment validation tooling (issues #22, #24)
- **Problem:** behov av oberoende sanity-check + event-study (forward outcomes) utan att ersätta deterministiska ledgers.
- **Behöver:** lätt event-study (MFE/MAE, +5/+10/+20-candles, hit-before-invalidation) + benchmark.
- **Etablerade:** vectorbt 1.0 (Apache-2.0 **+ Commons Clause**), backtesting.py (**AGPL** *UV*), quantstats (Apache-2.0), **empyrical övergivet 2020 → empyrical-reloaded**, ruptures 1.1.10/stumpy 1.13/tsfresh (sandbox), scipy.find_peaks/ZigZag (baselines).
- **Kopiera:** minimal **custom event-study-layer** (aligned med fib-frågan); vectorbt enbart som isolerad sandbox/benchmark; scipy.find_peaks som transparent anchor-baseline.
- **Importera EJ:** vectorbt/backtesting.py som beslutsgrund (black-box + license); empyrical (övergivet); stock-indicators (.NET); pandas-ta (**arkiveringsrisk juli 2026** + paid-tier).
- **Repo-native:** event-study-modul i `research/` som läser human-fib-grid + daily-events, skriver append-only JSONL; valbar vectorbt-sandbox isolerad.
- **ROI-först:** custom event-study-layer (kärnan i hypotes A / #22) framför externa ramverk.
- **Risker:** sandbox-output läcker in i slutsatser; license; indikator-"feature soup" maskerar hypotesen.
- **Verifiering:** sandbox reconcilieras mot deterministiska ledgers; license granskad; ingen forward-looking läcka (causal).
- **Skjut upp:** vectorbt/ruptures/stumpy/tsfresh-sandboxar tills deterministisk event-study-bas finns.
