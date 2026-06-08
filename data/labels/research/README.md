# Research labels (not used by motor)

Facit som **inte** lÃ¤ses av `experiment`, `pivot_recall`, eller `evaluate`.

| Fil | Schema |
|-----|--------|
| *(legacy Bitfinex/BTC-USD behavior file removed in cleanup)* | [BEHAVIOR_FACIT.md](../../docs/labeling/BEHAVIOR_FACIT.md) |

Parent swing legs (arkiv): Bitfinex/BTC-USD-exemplet Ã¤r borttaget i cleanup-rundan.

**Policy (schema v3):** HTF/daily leg = fib **grid** (`derived_prices`). Varje **daily touch** = rad i `levels[ratio].events[]` med `human_label` = facit. `auto_candidate` = fÃ¶rslag endast.
Aktiv exchange Ã¤r Bitfinex; Bitfinex-filen ovan Ã¤r arkiverad historik.

**Legacy v2** (ett `human_label` per nivÃ¥) lÃ¤ses in som ett event; sparas som v3.

Tmp-sandbox: [tmp/README.md](../tmp/README.md).

**Research finding (2026-05-29):** Samma fib-nivÃ¥ â†’ flera beteenden Ã¶ver tid (`events[]`).  
**Scope (2026-05-31, [#12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)):** PrimÃ¤r hypotes **A** = maskin fÃ¶reslÃ¥r events, mÃ¤nniska **spot-checkar** â€” inte mass-manuell labeling. Start: [docs/research/RESEARCH_HANDOFF.md](../../docs/research/RESEARCH_HANDOFF.md).

