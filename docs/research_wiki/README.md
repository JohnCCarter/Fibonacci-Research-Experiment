# Research Wiki

This directory is the persistent **LLM-maintained wiki** for the Fibonacci
experiment ([Karpathy LLM wiki](sources/karpathy-llm-wiki.md) pattern). It exists
for navigation, synthesis, decisions, concepts, handoff, and links between raw
sources and future work.

**This layer is:** memory and synthesis for agents and humans.
**This layer is not:** raw evidence, and not executable truth.

Every page must be grounded in a source: human fib labels, the active protocol
docs, code, tests, GitHub issues, or generated artifacts. When the wiki conflicts
with that evidence, **fix the wiki or flag the conflict** — the source wins. See
[reference/source-authority.md](reference/source-authority.md) for the full rule.

## Read First

1. Start with [index.md](index.md).
2. Check [log.md](log.md) for recent ingests, decisions, and reviews.
3. Check [handoff.md](handoff.md) for current working context.
4. Use [source-authority.md](reference/source-authority.md) to resolve any
   evidence-vs-wiki conflict; use wiki pages for synthesis only.

## Rules

- Keep this research-only. Do not promote behavior from wiki notes.
- Link to source docs instead of copying them.
- Keep candidates separate from facts: `*_candidate` is a hypothesis until a
  human review label exists.
- Do not add auto-fib, trading signals, edge claims, ML behavior, or optimization
  loops here.
- Prefer small pages with links over long reports.
- Update `index.md` whenever adding, moving, or retiring a page.
- Append to `log.md` for ingests, decisions, review sessions, and maintenance.
- Keep every page within the repo doc bounds.

## Page Types

- `glossary.md` — compact canonical definitions.
- `handoff.md` — current working context for the next agent or human.
- `concepts/<name>.md` — stable synthesis such as VAD/HUR, guardrails, human fib.
- `reference/<name>.md` — module maps, data schemas, CLI commands.
- `decisions/<date>-<slug>.md` — decisions and why they were made.
- `reviews/<date>-<slug>.md` — findings from generated review packs.
- `sources/<slug>.md` — short notes about external sources or GitHub issues.
- `templates/<name>.md` — reusable skeletons for wiki-maintained workflows.

## Maintenance Loop

Use this loop after meaningful research work:

1. Add or update the smallest relevant wiki page.
2. Link it from `index.md`.
3. Add one `log.md` entry with type `ingest`, `decision`, `review`, `question`, or
   `maintenance`.
4. Update `handoff.md` when current state, next action, or blockers change.
5. If a page starts duplicating a source doc, replace duplicated detail with links.
6. Periodically scan for stale claims, dead links, missing concept pages, and
   contradictions.
