# Atomic Runnable Artifacts

An atomic runnable artifact is a small, self-contained research artifact that
shows one idea end-to-end. It can be a script, notebook-free CLI flow, generated
review pack, or short doc with exact commands.

## Why It Fits

This repo is research-heavy and will grow. Atomic artifacts keep experiments
understandable by making each idea runnable, inspectable, and easy to retire.

The style is inspired by small educational programs such as Karpathy's
`microgpt.py` and `min-char-rnn.py`: the point is not the ML code, but the shape:
one file or page that explains the whole idea without hiding the important path.

## Rules

- One artifact, one question.
- Include the command to run it.
- Include expected inputs and outputs.
- Log where outputs are written.
- Link source docs instead of restating them.
- Stay within repo bounds: scripts are small, docs are small.
- Do not optimize toward labels, edge, or trading outcomes.
- Do not add dependencies unless the research question truly requires them.

## Good Uses

- Human-fib smoke review commands.
- Sensitivity checks over principled config variants.
- Small comparisons of review output shape.
- Reproducible examples for relation vs candidate behavior.

## Bad Uses

- Auto-tuning weights against agreement.
- Searching for profitable settings.
- Long notebooks that hide state.
- Monolithic scripts that mix fetch, analysis, plotting, and decision write-up.

## Template

Use [atomic-artifact.md](../templates/atomic-artifact.md) when adding a new
research artifact note.

## Source Links

- [Guardrails](guardrails.md)
- [CLI commands](../reference/cli-commands.md)
- [Repository layout policy](../../../repository-layout-policy.md)
