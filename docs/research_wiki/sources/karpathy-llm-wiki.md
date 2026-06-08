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

## What We Do Not Adopt Yet

- Search tooling.
- Heavy automation scripts.
- Obsidian-specific setup.
- Any behavior that changes runtime research results.
