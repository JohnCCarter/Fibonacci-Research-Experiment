# Data Conventions

Common data paths and meanings. Source docs remain authoritative.

## Swing Labels

```text
data/labels/{exchange}/{symbol}/{timeframe}.json
```

Used for swing facit and machine/human label workflows. `symbol` uses dash form
such as `BTC-USD`.

## Human Fib

```text
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}.json
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}_events.json
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}_interactions.csv
```

The annotation JSON stores anchors and levels (versioned facit). The events
JSON and interactions CSV are regenerable (`human_fib_events` / `--classify`) and
are gitignored under `data/labels/human_fib/`.

## Research Behavior Facit

```text
data/labels/research/
```

This is schema v3 behavior research data. `human_label` is facit; `auto_candidate`
is only a proposal.

## Experiment Outputs

```text
experiments/results/*.jsonl
experiments/runs/{kind}/{date}/{run_id}/
experiments/review/fib_level_events/{run_id}/
```

Review packs contain `review_sample.csv`, `review_sample.jsonl`,
`REVIEW_INDEX.md`, and chart PNGs.

## Superseded research archive

```text
archive/research_superseded/{reset_id}/
```

Pre-reset experiments, labels, caches, and review packs live here **on disk**.
Git tracks only each reset's `MANIFEST.md` (see `archive/INDEX.md`).

Legacy May 2026 runs under `archive/experiments/` follow the same rule: local
blobs only; `README.md` / `INDEX.md` stubs stay in git.

**Agent rule:** do not commit archive blobs unless the user explicitly asks —
[repository-layout-policy.md](../../../repository-layout-policy.md) §7.

## Source Links

- [Human fib annotation](../../labeling/HUMAN_FIB_ANNOTATION.md)
- [Behavior facit](../../labeling/BEHAVIOR_FACIT.md)
- [Level event human review](../../research/LEVEL_EVENT_HUMAN_REVIEW.md)
- [data labels README](../../../data/labels/README.md)
