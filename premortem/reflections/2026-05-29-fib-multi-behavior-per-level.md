# 2026-05-29 — Research finding: multiple behaviors per fib level

**Typ:** research finding  
**Taggar:** behavior, fib, MTF, 1w, 1d, events, Fas-3  
**Status:** Dokumenterat — schema v3; ingen motor/promotion

---

## Observation (EN)

> A fib level may exhibit multiple behaviors over time on Daily, especially when derived from a Weekly leg.  
> Future research may model behavior as **events** rather than a single label.

## Fynd (SV)

Vi har hittat en **begränsning** i den ursprungliga Fas-3-modellen (“ett `human_label` per nivå”) och ett **bra forskningsspår**:

**Samma fib-nivå (t.ex. 0.382 eller 0.618) kan ge flera olika signaler över tid på Daily** — t.ex. `rejection` vid ett tillfälle och `continuation` vid ett senare, när grid/range kommer från Weekly (eller ett längre HTF-ben) men interaktionerna sker på daily-barer.

Det är **inte** samma sak som att nivån “är” rejection eller continuation. Nivån är en **prislinje (grid)**; beteendet är **vad priset gjorde varje gång** det träffade linjen.

### Exempel (tmp leg_1, BTC 1d)

- Fib-grid från ned-ben ~97.9k → 60k (jan–feb 2026).
- Vid **0.382 (~74.5k)**:
  - Ett tillfälle: rally från low, **rejection** (stud vid zonen).
  - Senare: **continuation** (genombrott upp genom samma nivå mot 0.5).
  - Tidigare på huvudfallet: **continuation** ner genom nivån på väg mot 60k.

En enda etikett per nivå raderar denna information.

---

## Beslut (research only)

| Lager | Roll | Representation |
|-------|------|----------------|
| **Weekly / HTF leg** | Var finns fib-grid? | `1w.json`, daily leg H/L → `derived_prices` |
| **Daily** | Vad hände vid varje touch? | `1d-behavior.json` → `levels[ratio].events[]` |

- **Schema v3:** `events[]` med `event_bar`, `human_label`, `auto_candidate`, `note` per event.
- **Legacy v2** (ett label per nivå) läses in som ett event; sparas som v3.
- **Ingen** koppling till motor, `evaluate()`, recall, eller promotion till prod.
- **Tmp sandbox:** `data/labels/tmp` + `data/labels/research/tmp` för ren pilot.

---

## Konsekvenser

| Tidigare antagande | Ny insikt |
|--------------------|-----------|
| 0.618 = “golden pocket = rejection” | 0.618 kan vara rejection **och** senare continuation |
| Fas 3 = fyra labels per leg | Fas 3 = **N events** per nivå (valfritt per ratio) |
| `annotate` = facit | `annotate` = **ett förslag**; facit = `human_label` på events |
| Nästa steg: agreement en label | Nästa steg: agreement **per event** (Fas 5, ej påbörjad) |

---

## Scope realignment (2026-05-31, issue #12)

Tmp manuell JSON (Drift A) lärde `events[]`; **plan:** maskin → spot-check 20–40 ([#12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12), [RESEARCH_HANDOFF](../../docs/research/RESEARCH_HANDOFF.md)).

## Öppet (medvetet ej gjort)

- Full multi-touch auto-detect (PR #9 track) på bred sample — före spot-check-plan.
- Metrics: confusion per event (Fas 5) — efter bounded review.
- UI i labeling tool för events (idag: JSON).

---

## Referenser

- [docs/labeling/BEHAVIOR_FACIT.md](../../docs/labeling/BEHAVIOR_FACIT.md) — schema v3
- [docs/research/MTF_DAILY_RESEARCH.md](../../docs/research/MTF_DAILY_RESEARCH.md) — Weekly VAD / daily HUR
- [2026-05-29-mtf-daily-fib-research.md](2026-05-29-mtf-daily-fib-research.md) — multi-leg, tmp
