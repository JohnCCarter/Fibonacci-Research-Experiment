# docs

Djupare styrning och ramverk utöver snabbstart.

- `AGENT_RESPONSE_STYLE.md` — **agent-svar:** kort som standard; utökad förklaring först när användaren säger ok / ber om mer
- `TRACKS.md` — officiell 3-spårsmodell:
  - Research / Experiment
  - Validate
  - Promotion
- `FIB_BACKTEST_PLAN.md` — backtest-roadmap (faser, status, kommandon, promotion gate)
- `MTF_DAILY_RESEARCH.md` — **MTF-ursprung (läs först):** samma H/L på 1w vs 1d → fler nivåträffar på daily; weekly = VAD, daily = HUR
- `HTF_LTF_RESEARCH_ALIGNMENT.md` — top-down fib: 1w → 1d → 4h → 1h (research protocol)
- `CONTRIBUTING.md` — lint, test, pre-commit, CI före commit/push
- `MACHINE_LABELING.md` — maskin-kandidater: motor-swing vs chartfönster (båda giltiga)
- `LABELING_TOOL.md` — labeling GUI: begränsningar, redraw, säkra UI-ändringar
- `HUMAN_FIB_ANNOTATION.md` — **manuell fib som ground truth** (`w` / CLI): nivå-beräkning, candle-interaktion (`above/below/touch/cross`), och behavior-candidates (`human_fib_events`: `rejection/continuation/failure/reaction`); ingen auto-fib
- `research_wiki/` — persistent research-wiki: index, logg, koncept, beslut och review-insikter

## Aktiva label-ytor

- Swing-facit (aktiv): `data/labels/bitfinex/`
- Human-fib ground truth (aktiv): `data/labels/human_fib/bitfinex/`
