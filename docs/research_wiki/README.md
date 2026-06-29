# Research Wiki

This directory is the **agent-native warm context** for the Fibonacci experiment
([Karpathy LLM wiki](sources/karpathy-llm-wiki.md) pattern, extended — see
[decisions/2026-06-17-wiki-is-agent-native.md](decisions/2026-06-17-wiki-is-agent-native.md)).
It exists so an agent **orients in milliseconds across sessions** ("as if the session
never ended") instead of re-searching the repo or re-deriving methodology. Operating
model: **the agent curates, the human asks questions, the agent does the rest.**

**This layer is:** the agent's persistent memory — navigation **and** accumulated
knowledge (summaries, concepts, decisions, contradictions, links).
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
- **Query the wiki before re-deriving methodology** (check [concepts/](concepts/) and
  [reference/closed-questions.md](reference/closed-questions.md) first).
- Prefer small pages with links over long reports.
- Update `index.md` whenever adding, moving, or retiring a page.
- Append to `log.md` for ingests, decisions, review sessions, and maintenance.
- **Search surface vs knowledge corpus:** keep the always-read fast path (`index.md`,
  `handoff.md`) lean for cheap orientation; the query-on-demand corpus (concepts, reference,
  reviews, decisions, sources, log) may grow freely — bounds are anti-runaway only, not a reason
  to bury knowledge by archiving. Keep noisy raw surfaces out of search via
  [`.rgignore`](../../.rgignore), not by capping pages.

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

The agent curates this — it is self-interest, not a chore: persist now so the next agent (or
future-you) orients in milliseconds. Use this loop after meaningful research work:

1. Add or update the smallest relevant wiki page.
2. Link it from `index.md`.
3. Add one `log.md` entry with type `ingest`, `decision`, `review`, `question`, or
   `maintenance`.
4. Update `handoff.md` when current state, next action, or blockers change.
5. If a page starts duplicating a source doc, replace duplicated detail with links.
6. Run the **Lint** operation periodically (below).

## Lint (keep the memory consistent)

Karpathy's third operation (Ingest / Query / **Lint**). Split by what is deterministic vs what
needs judgment:

- **Mechanical (automated, enforced):** [`scripts/wiki_lint.py`](../../scripts/wiki_lint.py) runs in
  **pre-commit** (and on demand) and fails on **dead internal links** and **orphan pages** (any wiki
  `.md` not reachable from `index.md`/`log.md`). Frozen `log-archive-*.md` are excluded as sources
  (still traversed for reachability), and links into local-only roots (`archive/`, `data/`,
  `experiments/`) are skipped so the check is environment-independent. Pre-commit — not CI — is the
  home: it runs in the same environment that authors the links, where the agent fixes them in
  context; a CI gate on docs links would false-fail on local-only paths and is disproportionate for
  an agent-maintained repo. Its unit tests ([`tests/test_wiki_lint.py`](../../tests/test_wiki_lint.py))
  exercise the dead-link/orphan logic on **synthetic `tmp_path` fixtures** — they verify the *script*,
  not the live wiki, so pytest (and CI via pytest) does **not** catch real link/orphan drift; the
  pre-commit hook is the only path that validates the actual corpus. The exit code hard-gates **both**
  checks together (`dead_links + orphans`; no warn-only split, no `--strict` flag). This is the
  tedious bookkeeping — never left to discipline.
- **Semantic (agent judgment, run periodically / when the corpus shifts):** scan for **stale
  claims** (counts/state that no longer match source), **contradictions vs source** (layers 1–4),
  **missing concept pages** (methodology re-derived in chat instead of read), **wrong section/textual
  refs** (e.g. a stale "§6" — the mechanical check sees the file exists, not that the section ref is
  wrong), and **superseded pages not marked**. Fix in place or flag inline with
  `> CONFLICT: …` (per [source-authority.md](reference/source-authority.md)), then log a
  `maintenance` entry.

Discipline alone does not keep memory consistent (the vestigial "periodically scan" line let a stale
`§6` ref rot until 2026-06-17) — hence the mechanical half is enforced, not suggested.
