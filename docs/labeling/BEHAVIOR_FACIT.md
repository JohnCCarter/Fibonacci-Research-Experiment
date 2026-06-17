# Behavior facit (Fas 3, research only)

Manuellt facit fÃ¶r **vad som hÃ¤nde vid fib-nivÃ¥er** pÃ¥ redan sparade **daily multi-legs**.  
**Ingen** motor, experiment, recall eller scoring lÃ¤ser denna fil Ã¤n.

Relaterat: [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md), [premortem finding](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md)

---

## Research finding (2026-05-29)

> **A fib level may exhibit multiple behaviors over time on Daily, especially when derived from a Weekly leg.**  
> Behavior should be modeled as **events** over time, not a single label per level.

| Lager | Roll |
|-------|------|
| **Weekly / HTF leg** | Fib **grid** â€” `derived_prices` (var nivÃ¥erna sitter) |
| **Daily** | **Events** â€” varje gÃ¥ng priset interagerar med en nivÃ¥ (`events[]`) |

Samma 0.618 kan vara `rejection` en dag och `continuation` veckor senare. Det motiverar **schema v3** (`events[]` per ratio).  
**Ingen motorlogik, ingen promotion** â€” endast research-facit under `data/labels/research/`.

---

## Principer

| Regel | VarfÃ¶r |
|-------|--------|
| **Separat fil** frÃ¥n `1d.json` | `SwingLabel` / `load_label` pÃ¥verkas inte; golden swing ofÃ¶rÃ¤ndrad |
| **Referens via `leg_id`** | Koppling till multi-leg utan att duplicera H/L-priser |
| **Weekly = grid, Daily = events** | HTF-leg definierar nivÃ¥/pris; varje **daily** touch Ã¤r ett event |
| **`events[]` per nivÃ¥** | Samma 0.618 kan ha rejection i mars och continuation i april |
| **`human_label` pÃ¥ event = facit** | Endast det du sÃ¤tter per event rÃ¤knas som ground truth |
| **`auto_candidate` = fÃ¶rslag** | `annotate` fyller hÃ¶gst ett fÃ¶rslag-slot; kopieras **aldrig** till `human_label` |
| **Liten golden subset fÃ¶rst** | t.ex. 5â€“8 legs (impuls, retracement, rejection) â€” inte alla 30 direkt |

---

## Beteenden (enum)

| VÃ¤rde | Kort mening (fÃ¶r facit-rutin) |
|-------|-------------------------------|
| `reaction` | Tydlig respons vid nivÃ¥n (stud/sakta av), utan ren genombrottsfortsÃ¤ttning |
| `rejection` | Test genom nivÃ¥n, **stopp** och vÃ¤ndning tillbaka (wick/close mot trend) |
| `continuation` | **Genombrott** och fortsÃ¤ttning i legens riktning efter nivÃ¥n |
| `failure` | NivÃ¥n *skulle* hÃ¥lla men hÃ¶ll inte (false support/resistance i kontext) |
| `not_reached` | Fib-priset inom leg-range men priset kom aldrig dit |
| `unknown` | OsÃ¤ker â€” ska vara sÃ¤llsynt i golden subset |

**Viktigt:** `rejection` vs `continuation` Ã¤r **efter** kontakt med nivÃ¥n, i **legens** riktning (upp-leg vs ned-leg). Se â€œLÃ¤sa en legâ€ nedan.

---

## NivÃ¥er (nycklar)

Fasta ratios som strÃ¤ngnycklar (matchar motor/config):

`0.382`, `0.5`, `0.618`, `0.786`

Pris per nivÃ¥ **hÃ¤rleds** vid analys frÃ¥n legens H/L (samma formel som `fib_from_prices`) â€” sparas valfritt under `derived_prices` fÃ¶r reproducerbarhet.

---

## Filplats och namn

```
data/labels/research/bitfinex/BTC-USD/1d-behavior.json
```

Alternativ per studie: `1d-behavior-v1.json`.  
**Inte** i samma fil som `1d.json`.

---

## Schema (version 3) â€” events per level

```json
{
  "schema_version": 3,
  "facit_model": "events_per_level",
  "weekly_role": "grid",
  "daily_role": "events",
  "parent_label_path": "data/labels/bitfinex/BTC-USD/1d.json",
  "legs": [
    {
      "leg_id": "leg_1",
      "leg_direction": "down",
      "derived_prices": { "0.618": 83437.33 },
      "levels": {
        "0.618": {
          "level": "0.618",
          "price": 83437.33,
          "events": [
            {
              "event_bar": "2026-03-10T00:00:00+00:00",
              "level": "0.618",
              "price": 83437.33,
              "human_label": "continuation",
              "auto_candidate": null,
              "note": "Break up through level"
            },
            {
              "event_bar": "2026-04-20T00:00:00+00:00",
              "level": "0.618",
              "price": 83437.33,
              "human_label": "rejection",
              "note": "Second touch â€” wick and stall"
            }
          ]
        }
      }
    }
  ]
}
```

| Lager | Roll |
|-------|------|
| **Weekly / HTF leg** (`1w` eller daily leg som range) | `derived_prices` = fib **grid** |
| **Daily** | Varje rad i `events[]` = en interaktion vid den nivÃ¥n |

### Event-fÃ¤lt

| FÃ¤lt | Facit? | Beskrivning |
|------|--------|-------------|
| `event_bar` | ja | ISO-dag (eller `date`: `YYYY-MM-DD` vid import) |
| `level` | ja | Ratio-strÃ¤ng, t.ex. `0.618` |
| `price` | nej | Grid-pris (default frÃ¥n `derived_prices`) |
| `human_label` | **ja** | `reaction` \| `rejection` \| `continuation` \| `failure` \| `not_reached` |
| `auto_candidate` | **nej** | Heuristik-fÃ¶rslag |
| `note` | nej | Fri text |

### Legacy v2 (lÃ¤sning)

Filer med ett `human_label` per nivÃ¥ (utan `events`) laddas som **ett** event. Vid `save` skrivs schema v3.

### FÃ¤lt (leg)

| FÃ¤lt | Krav | Beskrivning |
|------|------|-------------|
| `schema_version` | ja | `3` |
| `parent_label_path` | ja | Vilken multi-leg-fil detta annoterar |
| `leg_id` | ja | MÃ¥ste finnas i parent `legs[].id` |
| `leg_direction` | ja | `up` eller `down` |
| `derived_prices` | nej | Fib-grid frÃ¥n leg H/L |
| `levels[ratio].events` | ja* | Lista daily-interaktioner |

\* `validate`: varje **ifylld** `events[]`-lista â€” varje event behÃ¶ver `human_label` + `event_bar`. Tom `events` = nivÃ¥ ej pÃ¥bÃ¶rjad (OK).

---

## LÃ¤sa en leg (upp vs ned)

| `leg_direction` | `rejection` vid motstÃ¥nd (pris kommer underifrÃ¥n) | `continuation` |
|-----------------|-----------------------------------------------------|----------------|
| **up** | Test av nivÃ¥ uppifrÃ¥n, **fall tillbaka** | Bryter **upp** genom nivÃ¥n och fortsÃ¤tter |
| **down** | Rally till nivÃ¥, **vÃ¤nder ner** | Bryter **ner** genom nivÃ¥n och fortsÃ¤tter |

`reaction` = tydlig interaktion utan att du vill klassificera som ren rejection eller continuation Ã¤n.

`failure` = du fÃ¶rvÃ¤ntade dig att nivÃ¥n skulle hÃ¥lla som S/R enligt din trading-tolkning, men den gjorde det inte.

---

## Golden subset (fÃ¶rslag att bÃ¶rja med)

| leg_id | VarfÃ¶r |
|--------|--------|
| `leg_1` | Huvud ned â€” weekly-ankare |
| `leg_8` eller `leg_10` | Retracement upp |
| `leg_20` | Mot ~0.618 / golden pocket |
| `leg_24` | Pullback efter topp |
| `leg_4`â€“`leg_6` | Kortare struktur (valfritt) |

Annotera **bara** dessa i fÃ¶rsta filen; resten av 30 legs kan vÃ¤nta.

---

## TvÃ¥ lager (research â€” inte motor)

| Lager | Fil / fÃ¤lt | Betyder |
|-------|------------|---------|
| **Leg / weekly** | `1d.json` / `1w.json` H/L | Fib **grid** (`derived_prices`) |
| **Daily** | `events[]` per nivÃ¥ | Varje interaktion Ã¶ver tid |
| **Auto** | `auto_candidate` pÃ¥ event | FÃ¶rslag â€” aldrig facit |

**Ingen motor, ingen promotion.**

---

## Status

| Fas | Status |
|-----|--------|
| Schema v3 `events[]` | âœ… validate + docs |
| Fas 4 / 5 | â¸ efter event-facit |

---

## Fas 5 â€” MÃ¤t `auto_candidate` vs `human_label` (nÃ¤sta steg)

**Syfte:** Besvara om heuristiken Ã¤r vÃ¤rd att fÃ¶rbÃ¤ttra (Fas 4) eller om fler legs ska labelas fÃ¶rst.

**Per nivÃ¥ (20 observationer i piloten):**

1. Strikt match: `auto_candidate.removesuffix("_candidate") == human_label`
2. Confusion matrix: sÃ¤rskilt `rejection` â†” `continuation`
3. Breakdown per ratio: `0.382`, `0.5`, `0.618`, `0.786` â€” missar den oftast **0.618**?
4. Per `leg_id`: vilka ben driver flest fel?
5. `not_reached` / `reaction` â€” hur ofta fÃ¶rekommer de i human vs auto?

**Tolkning:**

| Agreement | Ã…tgÃ¤rd |
|-----------|--------|
| **Svag** (< ~60â€“70 % strikt, hÃ¶g rejection/continuation-blandning) | FÃ¶rbÃ¤ttra heuristik i `behavior_candidates.py`, kÃ¶r `annotate` om â€” **Ã¤ndra inte** `human_label` automatiskt |
| **Stark** | Labela fler legs (`scaffold --legs â€¦`), utÃ¶ka golden subset |

**Planerat kommando (ej implementerat Ã¤n):**

```powershell
uv run python scripts/behavior_facit.py report --symbol BTC/USD --timeframe 1d
```

Ska skriva match rate, confusion per nivÃ¥, lista missar â€” **lÃ¤ser bara** research-JSON.

**Ingen** koppling till `evaluate()` / `experiment` fÃ¶rrÃ¤n explicit beslut.

---

## Manuell workflow (tills UI finns)

### 1. Skapa mall frÃ¥n dina sparade legs

```powershell
uv run python scripts/behavior_facit.py scaffold --symbol BTC/USD --timeframe 1d
```

Skapar `data/labels/research/bitfinex/BTC-USD/1d-behavior.json` med golden subset
(`leg_1`, `leg_8`, `leg_10`, `leg_20`, `leg_24`) + `derived_prices` ifyllda.

Andra legs: `--legs leg_3,leg_4,leg_5`

### 2. Auto-fÃ¶rslag (valfritt)

```powershell
uv run python scripts/behavior_facit.py annotate --symbol BTC/USD --timeframe 1d
```

Fyller **endast** `auto_candidate` + `event_bar`. SÃ¤tter **aldrig** `human_label`.

### 3. GodkÃ¤nn facit

```powershell
uv run python scripts/behavior_facit.py print
```

Redigera JSON: lÃ¤gg till rader i `levels[ratio].events[]` med `event_bar` + `human_label` (flera per nivÃ¥ tillÃ¥tna).

### 4. Validera

```powershell
uv run python scripts/behavior_facit.py validate
```

KrÃ¤ver `human_label` pÃ¥ varje **event**. Tom `events[]` eller bara `auto_candidate` ger **inte** OK.

`validate --allow-auto-only` finns bara fÃ¶r att kolla filstruktur â€” **inte** giltigt facit fÃ¶r Fas 5.

### 4. Chart

Ã–ppna `1d.json` + TV/labeling tool vid sidan av `print`-utskriften.

