# Kategori-findings A (kat. 1–8)

> Del av `TOOLING_ECOSYSTEM_REVIEW.md`. Per kategori: Problem · Behöver · Etablerade ·
> Kopiera · Importera EJ · Repo-native · ROI-först · Risker · Verifiering · Skjut upp.
> Externa fakta = webb-verifierade juni 2026 (*UV* = ej pinnad version/licens).

## 1. Skills
- **Problem:** återkommande procedurer (labela, experiment, reflektion, gate-check) görs ad hoc → drift.
- **Behöver:** deterministiska, versionshanterade procedurminnen som kodar repo-reglerna.
- **Etablerade:** Claude Agent Skills (öppen standard 2025-12-18, `anthropics/skills`, Apache-2.0); `SKILL.md` = YAML-frontmatter (`name`,`description` krävs) + markdown, progressive disclosure, kropp <~500 rader.
- **Kopiera:** filbaserad SKILL.md; progressive disclosure; `description` som trigger; bryt ut overflow (matchar anti-blob).
- **Importera EJ:** tredjeparts-skills rakt av (kan bryta fib-filosofin) — extrahera pattern, skriv repo-native.
- **Repo-native:** `.claude/skills/{fib-label-integrity,promotion-gate-check,research-reflection,experiment-run,ecosystem-scan}` med file:line-referenser till policy.
- **ROI-först:** `promotion-gate-check` + `fib-label-integrity` (hårdaste reglerna).
- **Risker:** skills som tyst uppmuntrar agreement-optimering / maskin-som-facit; storleksdrift.
- **Verifiering:** citera policy-rad; respektera bounds; granska mot PREMORTEM före commit.
- **Skjut upp:** skills för trading/Genesis eller auto-labeling i skala.

## 2. Subagents
- **Problem:** stora multi-steg-uppgifter belamrar huvudkontext och blandar roller.
- **Behöver:** isolerade, read-only-default sub-roller med verktygsrestriktion.
- **Etablerade:** Claude Code subagents (`.claude/agents/*.md`, frontmatter `name`/`description`/`tools`/`model`, egen kontext).
- **Kopiera:** verktygsrestriktion som disciplin; separat kontext; explicit trigger-`description`.
- **Importera EJ:** subagents med skrivrätt mot canonical-ytor (`config/settings.yaml`, `src/core/`) utan gate.
- **Repo-native:** `explore` (read-only), `label-auditor`, `validate-runner`, `promotion-gatekeeper` — minimal tool-allowlist.
- **ROI-först:** `explore` + `label-auditor` (låg risk, hög återanvändning).
- **Risker:** auto-delegering som muterar canonical state; kontextläckage maskin→facit.
- **Verifiering:** allowlist granskad; gatekeeper aldrig skrivrätt; testa att subagent ej kan editera baseline.
- **Skjut upp:** skriv-kapabla subagents tills gate-disciplinen är kodad i skills.

## 3. Agent orchestration
- **Problem:** frestelse att bygga multi-agent-pipelines för research.
- **Behöver:** i praktiken nästan inget — single-dev, deterministiskt, CLI-drivet.
- **Etablerade:** LangGraph 1.0 (MIT), CrewAI (MIT), AutoGen (**maintenance mode**), AG2, MAF, OpenAI Agents SDK, Google ADK, Claude Agent SDK (alpha).
- **Kopiera:** LangGraphs *idé* om durabel, checkpointad, auditbar state — som mönster, ej beroende.
- **Importera EJ:** hela multi-agent-ramverk (fel modell för single-dev determinism).
- **Repo-native:** befintliga CLI-moduler + append-only ledgers + plan/todo-fil ÄR redan deterministisk orchestration.
- **ROI-först:** ingen adoption; dokumentera att ramverk avvisas.
- **Risker:** black-box-loopar bryter determinism/auditbarhet; tung maintenance.
- **Verifiering:** — (reject).
- **Skjut upp:** allt; ompröva endast om projektet blir multi-surface.

## 4. Prompt engineering
- **Problem:** agent-instruktioner oversionerade → icke-reproducerbara.
- **Behöver:** git-checkade prompt-filer + diff, ej hostad magi.
- **Etablerade:** DSPy 3.2.1 (MIT, metric-driven), Anthropic prompt-improver (SaaS), priompt (stale, TS-only).
- **Kopiera:** "prompts som versionerade filer + snapshot-test"; DSPy:s signatur/metric-tänk som mental modell.
- **Importera EJ:** DSPy som beroende nu (tung; risk för agreement-optimering); hostade improvers som källa-till-sanning.
- **Repo-native:** prompts/skills-instruktioner i `.claude/`, diffbara, anti-blob-bundna.
- **ROI-först:** konvention att alla agent-instruktioner är filer i git (noll beroende).
- **Risker:** optimerare mot human labels = **förbjuden** agreement-optimering.
- **Verifiering:** inga optimerare kopplade mot label-agreement; granska mot filosofin.
- **Skjut upp:** DSPy tills label-oberoende optimeringsbehov finns.

## 5. Context engineering
- **Problem:** långa sessioner spiller kontext; agenter tappar repo-regler.
- **Behöver:** lättviktiga, repo-native context-maps + just-in-time-hämtning.
- **Etablerade:** Anthropics "Effective context engineering" (2025-09): compaction, structured note-taking, sub-agent-isolation, JIT-retrieval — mest patterns, inte paket.
- **Kopiera:** alla fyra patterns; särskilt note-taking (plan/reflektion finns) och sub-agent-isolation.
- **Importera EJ:** tunga RAG/memory-ramverk för ett litet repo.
- **Repo-native:** `docs/CONTEXT_MAP.md` + glossary; reflektioner = episodiskt minne; skills = procedurminne.
- **ROI-först:** CONTEXT_MAP + glossary (kodifierar VAD/HUR/Lager A/B/facit/kandidat).
- **Risker:** kontextfiler som blir blobs eller divergerar från policy.
- **Verifiering:** context-map länkar (kopierar ej) canonical docs; anti-blob-bounds.
- **Skjut upp:** vektor-retrieval/embeddings tills datavolym kräver.

## 6. Planning / persistent working memory
- **Problem:** multi-steg-arbete saknar spårbart arbetsminne mellan steg.
- **Behöver:** deterministisk, inspekterbar, versionsbar arbetsminnesfil.
- **Etablerade:** Letta/MemGPT v0.16.8 (Apache-2.0, tungt: server/DB); CoALA-taxonomi (arXiv 2023); plan-fil/`todo.md`-pattern + Claude Code plan-mode/TodoWrite.
- **Kopiera:** CoALA-mappning (procedurellt=skills, semantiskt=docs, episodiskt=reflections/ledgers); plan-fil-patternet.
- **Importera EJ:** Letta-ramverket (server/DB = overkill, bryter lättvikts-disciplin).
- **Repo-native:** plan-/scratchpad-fil per större arbete; befintliga reflektioner som episodiskt minne.
- **ROI-först:** formalisera plan-fil-konventionen (noll beroende).
- **Risker:** persistent minne som tyst blir "fakta" utan validate-evidens.
- **Verifiering:** arbetsminne = förslag/anteckningar, aldrig promotion-grund utan gate.
- **Skjut upp:** Letta/MemFS tills behov av delat långtidsminne uppstår.

## 7. Research artifact management
- **Problem:** artefakter (ledgers/plots/batches) växer; provenance måste hålla.
- **Behöver:** typade, frågbara, reproducerbara artefakter utan att förlora git-läsbarhet.
- **Etablerade:** PyArrow/Parquet 21 (Apache-2.0), DuckDB 1.5.x (MIT), SQLite (stdlib), jsonlines.
- **Kopiera:** DuckDB-SQL över befintliga JSONL/Parquet som incheckade report-queries; Parquet för stora körningar; JSONL kvar för små/git-vänliga ledgers.
- **Importera EJ:** MLflow/DVC/SQLite-som-primär nu (tung yta; JSONL räcker i MVP).
- **Repo-native:** `scripts/query/*.sql` mot `experiments/results/*.jsonl`; behåll immutabla run-mappar + manifest+sha256.
- **ROI-först:** DuckDB-frågelager över befintliga ledgers.
- **Risker:** Parquet minskar human-läsbarhet; binära artefakter i git.
- **Verifiering:** queries deterministiska & incheckade; ingen ledger skrivs över; append-only behålls.
- **Skjut upp:** DVC/MLflow tills dataset/run-volym blir ohanterlig.

## 8. Label integrity / human-vs-machine separation (KÄRNA)
- **Problem:** viktigaste integritetsrisken — maskin-labels kontaminerar facit / driver agreement-optimering.
- **Behöver:** hård, testad separation + schema-validering av label-filer.
- **Etablerade:** pandera 0.31.1 (MIT), pydantic v2.13.4 (redan i repot), jsonschema 4.26.
- **Kopiera:** schema-validering som fail-fast-grind (high≥low, priser >0, `source∈{human,machine}`, level∈godkänd Fib-mängd, event-ts i candle-index).
- **Importera EJ:** något verktyg/skill som behandlar maskin som facit eller optimerar mot agreement.
- **Repo-native:** pandera/pydantic-scheman som *upprätthåller* befintlig `source`-separation; `label-auditor`-subagent.
- **ROI-först:** **högst i hela rapporten** — kontrakt på label-/ledger-scheman (skyddar primärkällan).
- **Risker:** schema som tillåter `source`-default-glidning; tyst promotion maskin→human.
- **Verifiering:** bevara/utöka `test_autolabel_never_overwrites_human`; maskin exkluderad från recall/agreement.
- **Skjut upp:** multi-user annotation-plattformar tills volym kräver.
