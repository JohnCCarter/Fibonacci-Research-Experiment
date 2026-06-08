# docs

Djupare styrning och ramverk utöver snabbstart. Använd den här sidan som
innehållsförteckning — börja här i stället för att grep:a brett.

## Börja här (agenter)
- `RESEARCH_HANDOFF.md` — **start för agenter:** aktuellt läge och nästa steg
- `research_wiki/` — persistent research-wiki: `index.md` (ingång), `log.md`,
  koncept, beslut, reviews, glossary, reference (inkl. `module-map.md`,
  `cli-commands.md`)
- `TRACKS.md` — officiell 3-spårsmodell: Research / Validate / Promotion

## Agent & workflow
- `AGENT_RESPONSE_STYLE.md` — **agent-svar:** kort som standard; utökad förklaring
  först när användaren ber om mer
- `CONTRIBUTING.md` — lint, test, pre-commit, CI före commit/push
- `REPO_AWARE_AGENT.md` — repo-aware agent-setup (Cursor Chat + Qwen)
- `MODEL_COLLABORATION.md` — modellsamarbete (GLM lead + Qwen implement)
- `CURSOR_WORKSPACE_AGENT.md` — konfigurera Cursor workspace: Qwen som coding-agent
- `VSCODE_COPILOT_NVIDIA_MODELS.md` — VS Code Copilot med NVIDIA GLM/Qwen (BYOK)
- `prompts/qwen-chat-starter.md` — startprompt för Qwen-chat

## Research & metodik (MTF + nivåer)
- `MTF_DAILY_RESEARCH.md` — **MTF-ursprung (läs först):** samma H/L på 1w vs 1d →
  fler nivåträffar på daily; weekly = VAD, daily = HUR
- `HTF_LTF_RESEARCH_ALIGNMENT.md` — top-down fib: 1w → 1d → 4h → 1h (protocol)
- `MTF_FIB_LEVEL_PROJECTION.md` — MTF fib-nivåprojektion
- `LEVEL_EVENTS.md` — Fibonacci-nivå-interaktionshändelser (research-only)
- `LEVEL_EVENT_HUMAN_REVIEW.md` — human review av level-events (v1)
- `FIB_LEVEL_FINGERPRINTS.md` — fib-nivå-interaktions-fingerprints (#23)
- `FIB_CANDIDATE_OUTCOMES.md` — kandidat → forward-outcome-analys (#22)
- `FIB_FINGERPRINT_OUTCOMES.md` — fingerprint × outcome-join (#22 + #23)
- `BEHAVIOR_FACIT.md` — behavior-facit (Fas 3, research-only)
- `FIB_BACKTEST_PLAN.md` — backtest-roadmap (faser, status, kommandon, gate)

## Labeling & ground truth
- `HUMAN_FIB_ANNOTATION.md` — **manuell fib som ground truth** (`w` / CLI):
  nivå-beräkning, candle-interaktion (`above/below/touch/cross`) och
  behavior-candidates (`human_fib_events`); ingen auto-fib
- `MACHINE_LABELING.md` — maskin-kandidater: motor-swing vs chartfönster
- `LABELING_TOOL.md` — labeling-GUI: begränsningar, redraw, säkra UI-ändringar

## Verktyg & validering
- `TOOLING_RECOMMENDATION_REPORT.md` — read-only verktygsstrategi (issue #25);
  tabeller i `TOOLING_RECOMMENDATION_TOOLS.md`
- `FIB_AWARE_TOOLING_SPIKE.md` — spike: fib-aware annotation/review-tooling
- `GENESIS_BITFINEX_VALIDATE.md` — Genesis-Core / Bitfinex validate-pass

## Aktiva label-ytor
- Swing-facit (aktiv): `data/labels/bitfinex/`
- Human-fib ground truth (aktiv): `data/labels/human_fib/bitfinex/`
