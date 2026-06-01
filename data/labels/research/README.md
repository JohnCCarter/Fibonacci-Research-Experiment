# Research labels (not used by motor)

Facit som **inte** läses av `experiment`, `pivot_recall`, eller `evaluate`.

| Fil | Schema |
|-----|--------|
| `binance/BTC-USDT/1d-behavior.json` | [BEHAVIOR_FACIT.md](../../docs/BEHAVIOR_FACIT.md) |

Parent swing legs: `../binance/BTC-USDT/1d.json`.

**Policy (schema v3):** HTF/daily leg = fib **grid** (`derived_prices`). Varje **daily touch** = rad i `levels[ratio].events[]` med `human_label` = facit. `auto_candidate` = förslag endast.

**Legacy v2** (ett `human_label` per nivå) läses in som ett event; sparas som v3.

Tmp-sandbox: [tmp/README.md](../tmp/README.md).

**Research finding (2026-05-29):** Samma fib-nivå → flera beteenden över tid (`events[]`).  
**Scope (2026-05-31, [#12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)):** Primär hypotes **A** = maskin föreslår events, människa **spot-checkar** — inte mass-manuell labeling. Start: [docs/RESEARCH_HANDOFF.md](../../docs/RESEARCH_HANDOFF.md).
