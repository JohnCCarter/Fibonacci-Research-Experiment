# Glossary

Compact definitions for terms that recur across the repo. Link to source docs for
details.

## Terms

- **Anchor** — a human-selected high or low point used to draw a fib range.
- **Atomic runnable artifact** — a small self-contained research artifact with
  question, command, inputs, outputs, and interpretation.
- **Candidate** — a machine-proposed behavior label ending in `_candidate`.
  Candidates are hypotheses, not facts.
- **Facit** — human truth data. In this repo, facit must come from explicit human
  labels or saved human-drawn anchors.
- **Fib level** — a derived price at a ratio such as `0.382`, `0.5`, or `0.618`.
- **HUR** — how price behaves around a fib range at a lower timeframe, especially
  daily candles after a weekly range is selected.
- **Handoff** — current working context for future agents and humans.
- **Human fib** — manually drawn anchors plus derived levels saved under
  `data/labels/human_fib/`.
- **Layer A** — swing selection and fib research, the core project surface.
- **Layer B** — trade/sizing experiments, decoupled from swing selection.
- **Leg** — a labeled move between high and low anchors.
- **Promotion** — moving behavior into trusted canonical surfaces after validation.
- **Relation** — deterministic candle geometry against a level:
  `above/below/touch/cross`.
- **Review pack** — generated charts and sheets for bounded human review.
- **VAD** — what range is being measured, usually the higher-timeframe fib range.

## Source Links

- [Research handoff](../RESEARCH_HANDOFF.md)
- [Human fib annotation](../HUMAN_FIB_ANNOTATION.md)
- [Level events](../LEVEL_EVENTS.md)
- [Repo tracks](../TRACKS.md)
