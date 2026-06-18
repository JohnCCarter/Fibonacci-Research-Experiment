# Karpathy LLM Wiki

Source: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

## Useful Pattern

The source describes a persistent wiki maintained by an LLM agent. Raw sources
stay immutable. The wiki accumulates summaries, links, contradictions, and
decisions so future sessions do not rediscover everything from scratch.

## Mapping To This Repo

- Raw sources: existing docs, code, GitHub issues, labels, experiment outputs.
- Wiki: `docs/research_wiki/`.
- Index: [index.md](../index.md).
- Log: [log.md](../log.md).
- Maintenance contract: [README.md](../README.md).

## What We Adopt

- `index.md` as the content map.
- `log.md` as the chronological trail.
- `handoff.md` as current agent context.
- `.cursor/rules/research-wiki-maintenance.mdc` as persistent agent discipline.
- Small pages with source links.
- Concepts and decisions as durable artifacts.

## Update (2026-06-17): accumulation loop now adopted

[decisions/2026-06-17-wiki-is-agent-native.md](../decisions/2026-06-17-wiki-is-agent-native.md)
extends this pattern: the wiki is **agent-native warm context** for ms-orientation, **the agent
curates** (the human queries), and the **accumulation loop is now live** — external methodology gets
concept/source pages so agents query instead of re-derive (it had been frozen out by an empty
`sources/`). Size caps were relaxed to "anti-runaway only" so knowledge is never buried by archiving.

## What We Still Do Not Adopt

- Search tooling beyond `.rgignore` scoping + the `index.md` content map (sufficient at this scale).
- Heavy automation scripts.
- Obsidian-specific setup.
- Any behavior that changes runtime research results.
