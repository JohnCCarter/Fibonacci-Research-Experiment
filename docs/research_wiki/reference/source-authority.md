# Source Authority

How to resolve disagreements between the LLM wiki and the things it summarizes.
This is the minimum model needed to keep the wiki from drifting away from reality
(see [Karpathy LLM wiki](../sources/karpathy-llm-wiki.md)).

The wiki (`docs/research_wiki/`) is **synthesis and navigation**. It never owns
truth. It points at the layers below and keeps them findable. When the wiki and a
source layer disagree, the **source wins** — fix the wiki or flag the conflict.

## Authority layers

Each layer is authoritative for a different question. Higher in this list beats
lower **for its own kind of claim**.

| # | Layer | Where | Authoritative for |
|---|-------|-------|-------------------|
| 1 | **Human-approved facit** | `data/labels/human_fib/.../fib_*.json`, signed-off review packs | The correct anchors / levels / labels. Ground truth. |
| 2 | **Executable behavior** | `src/`, `tests/`, verified CLI output | What the code actually does. |
| 3 | **Active protocol + handoff** | [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md), [handoff.md](../handoff.md) | What we are doing now and what is in/out of scope. |
| 4 | **Generated evidence** | `experiments/`, review artifacts, `*_events.json`, `*_interactions.csv` | What a run produced. Derived, not facit. |
| 5 | **Wiki synthesis** | `docs/research_wiki/` | Navigation, summaries, decisions, concepts, links. |
| 6 | **Archived / superseded** | `archive/**`, `*-archive-*`, "(superseded)" pages | History only. **Not** current evidence. |

## Conflict rule

When sources disagree:

1. **Source evidence beats wiki synthesis.** A wiki page may summarize evidence;
   it may never override it. If a page contradicts layers 1–4, the page is wrong.
2. **Fix or flag.** Correct the wiki page to match the source, or mark the
   contradiction inline (e.g. `> CONFLICT: page says X, source Y says Z`) so the
   next agent does not trust it silently.
3. **Candidates are not facit.** `*_candidate` events (layer 4) are hypotheses
   until a human promotes them to layer 1. Never restate a candidate as truth.
4. **Archived is not current.** Layer 6 explains how we got here; it is never
   cited as present-state evidence.

## What this prevents

- Stale counts and claims surviving in the wiki after a reset (see the BTC
  monthly-first reset: prior 1w/1d/4h labels were archived, not current).
- Machine candidates hardening into "facts" by repetition.
- Local tool config, caches, or scratch output (`.claude/settings.local.json`, `.venv/`, `.env`,
  `._*.png`, debug logs) leaking into wiki memory or source truth. These are
  local-only and are kept out of git (`.gitignore`,
  [check_repo_bounds.py](../../../scripts/check_repo_bounds.py)). Note: `.claude/`'s shared parts
  (`commands/`, `hooks/`, `settings.json`) **are** versioned-portable — only `settings.local.json`
  is machine-local.

## Enforcement

- [check_repo_bounds.py](../../../scripts/check_repo_bounds.py) fails CI if a
  required wiki/schema file is missing or a local/private artifact is tracked.
- [AGENTS.md](../../../AGENTS.md) §2 (source authority) + §3 (maintenance) and
  [CLAUDE.md](../../../CLAUDE.md) carry the short version of this rule.
