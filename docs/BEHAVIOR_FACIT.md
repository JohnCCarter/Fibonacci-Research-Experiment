# Behavior facit (Fas 3, research only)

Manuellt facit för **vad som hände vid fib-nivåer** på redan sparade **daily multi-legs**.  
**Ingen** motor, experiment, recall eller scoring läser denna fil än.

Relaterat: [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md), [premortem finding](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md)

---

## Research finding (2026-05-29)

> **A fib level may exhibit multiple behaviors over time on Daily, especially when derived from a Weekly leg.**  
> Behavior should be modeled as **events** over time, not a single label per level.

| Lager | Roll |
|-------|------|
| **Weekly / HTF leg** | Fib **grid** — `derived_prices` (var nivåerna sitter) |
| **Daily** | **Events** — varje gång priset interagerar med en nivå (`events[]`) |

Samma 0.618 kan vara `rejection` en dag och `continuation` veckor senare. Det motiverar **schema v3** (`events[]` per ratio).  
**Ingen motorlogik, ingen promotion** — endast research-facit under `data/labels/research/`.

---

## Principer

| Regel | Varför |
|-------|--------|
| **Separat fil** från `1d.json` | `SwingLabel` / `load_label` påverkas inte; golden swing oförändrad |
| **Referens via `leg_id`** | Koppling till multi-leg utan att duplicera H/L-priser |
| **Weekly = grid, Daily = events** | HTF-leg definierar nivå/pris; varje **daily** touch är ett event |
| **`events[]` per nivå** | Samma 0.618 kan ha rejection i mars och continuation i april |
| **`human_label` på event = facit** | Endast det du sätter per event räknas som ground truth |
| **`auto_candidate` = förslag** | `annotate` fyller högst ett förslag-slot; kopieras **aldrig** till `human_label` |
| **Liten golden subset först** | t.ex. 5–8 legs (impuls, retracement, rejection) — inte alla 30 direkt |

---

## Beteenden (enum)

| Värde | Kort mening (för facit-rutin) |
|-------|-------------------------------|
| `reaction` | Tydlig respons vid nivån (stud/sakta av), utan ren genombrottsfortsättning |
| `rejection` | Test genom nivån, **stopp** och vändning tillbaka (wick/close mot trend) |
| `continuation` | **Genombrott** och fortsättning i legens riktning efter nivån |
| `failure` | Nivån *skulle* hålla men höll inte (false support/resistance i kontext) |
| `not_reached` | Fib-priset inom leg-range men priset kom aldrig dit |
| `unknown` | Osäker — ska vara sällsynt i golden subset |

**Viktigt:** `rejection` vs `continuation` är **efter** kontakt med nivån, i **legens** riktning (upp-leg vs ned-leg). Se “Läsa en leg” nedan.

---

## Nivåer (nycklar)

Fasta ratios som strängnycklar (matchar motor/config):

`0.382`, `0.5`, `0.618`, `0.786`

Pris per nivå **härleds** vid analys från legens H/L (samma formel som `fib_from_prices`) — sparas valfritt under `derived_prices` för reproducerbarhet.

---

## Filplats och namn

```
data/labels/research/binance/BTC-USDT/1d-behavior.json
```

Alternativ per studie: `1d-behavior-v1.json`.  
**Inte** i samma fil som `1d.json`.

---

## Schema (version 3) — events per level

```json
{
  "schema_version": 3,
  "facit_model": "events_per_level",
  "weekly_role": "grid",
  "daily_role": "events",
  "parent_label_path": "data/labels/binance/BTC-USDT/1d.json",
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
              "note": "Second touch — wick and stall"
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
| **Daily** | Varje rad i `events[]` = en interaktion vid den nivån |

### Event-fält

| Fält | Facit? | Beskrivning |
|------|--------|-------------|
| `event_bar` | ja | ISO-dag (eller `date`: `YYYY-MM-DD` vid import) |
| `level` | ja | Ratio-sträng, t.ex. `0.618` |
| `price` | nej | Grid-pris (default från `derived_prices`) |
| `human_label` | **ja** | `reaction` \| `rejection` \| `continuation` \| `failure` \| `not_reached` |
| `auto_candidate` | **nej** | Heuristik-förslag |
| `note` | nej | Fri text |

### Legacy v2 (läsning)

Filer med ett `human_label` per nivå (utan `events`) laddas som **ett** event. Vid `save` skrivs schema v3.

### Fält (leg)

| Fält | Krav | Beskrivning |
|------|------|-------------|
| `schema_version` | ja | `3` |
| `parent_label_path` | ja | Vilken multi-leg-fil detta annoterar |
| `leg_id` | ja | Måste finnas i parent `legs[].id` |
| `leg_direction` | ja | `up` eller `down` |
| `derived_prices` | nej | Fib-grid från leg H/L |
| `levels[ratio].events` | ja* | Lista daily-interaktioner |

\* `validate`: varje **ifylld** `events[]`-lista — varje event behöver `human_label` + `event_bar`. Tom `events` = nivå ej påbörjad (OK).

---

## Läsa en leg (upp vs ned)

| `leg_direction` | `rejection` vid motstånd (pris kommer underifrån) | `continuation` |
|-----------------|-----------------------------------------------------|----------------|
| **up** | Test av nivå uppifrån, **fall tillbaka** | Bryter **upp** genom nivån och fortsätter |
| **down** | Rally till nivå, **vänder ner** | Bryter **ner** genom nivån och fortsätter |

`reaction` = tydlig interaktion utan att du vill klassificera som ren rejection eller continuation än.

`failure` = du förväntade dig att nivån skulle hålla som S/R enligt din trading-tolkning, men den gjorde det inte.

---

## Golden subset (förslag att börja med)

| leg_id | Varför |
|--------|--------|
| `leg_1` | Huvud ned — weekly-ankare |
| `leg_8` eller `leg_10` | Retracement upp |
| `leg_20` | Mot ~0.618 / golden pocket |
| `leg_24` | Pullback efter topp |
| `leg_4`–`leg_6` | Kortare struktur (valfritt) |

Annotera **bara** dessa i första filen; resten av 30 legs kan vänta.

---

## Två lager (research — inte motor)

| Lager | Fil / fält | Betyder |
|-------|------------|---------|
| **Leg / weekly** | `1d.json` / `1w.json` H/L | Fib **grid** (`derived_prices`) |
| **Daily** | `events[]` per nivå | Varje interaktion över tid |
| **Auto** | `auto_candidate` på event | Förslag — aldrig facit |

**Ingen motor, ingen promotion.**

---

## Status

| Fas | Status |
|-----|--------|
| Schema v3 `events[]` | ✅ validate + docs |
| Fas 4 / 5 | ⏸ efter event-facit |

---

## Fas 5 — Mät `auto_candidate` vs `human_label` (nästa steg)

**Syfte:** Besvara om heuristiken är värd att förbättra (Fas 4) eller om fler legs ska labelas först.

**Per nivå (20 observationer i piloten):**

1. Strikt match: `auto_candidate.removesuffix("_candidate") == human_label`
2. Confusion matrix: särskilt `rejection` ↔ `continuation`
3. Breakdown per ratio: `0.382`, `0.5`, `0.618`, `0.786` — missar den oftast **0.618**?
4. Per `leg_id`: vilka ben driver flest fel?
5. `not_reached` / `reaction` — hur ofta förekommer de i human vs auto?

**Tolkning:**

| Agreement | Åtgärd |
|-----------|--------|
| **Svag** (< ~60–70 % strikt, hög rejection/continuation-blandning) | Förbättra heuristik i `behavior_candidates.py`, kör `annotate` om — **ändra inte** `human_label` automatiskt |
| **Stark** | Labela fler legs (`scaffold --legs …`), utöka golden subset |

**Planerat kommando (ej implementerat än):**

```powershell
uv run python scripts/behavior_facit.py report --symbol BTC/USDT --timeframe 1d
```

Ska skriva match rate, confusion per nivå, lista missar — **läser bara** research-JSON.

**Ingen** koppling till `evaluate()` / `experiment` förrän explicit beslut.

---

## Manuell workflow (tills UI finns)

### 1. Skapa mall från dina sparade legs

```powershell
uv run python scripts/behavior_facit.py scaffold --symbol BTC/USDT --timeframe 1d
```

Skapar `data/labels/research/binance/BTC-USDT/1d-behavior.json` med golden subset  
(`leg_1`, `leg_8`, `leg_10`, `leg_20`, `leg_24`) + `derived_prices` ifyllda.

Andra legs: `--legs leg_3,leg_4,leg_5`

### 2. Auto-förslag (valfritt)

```powershell
uv run python scripts/behavior_facit.py annotate --symbol BTC/USDT --timeframe 1d
```

Fyller **endast** `auto_candidate` + `event_bar`. Sätter **aldrig** `human_label`.

### 3. Godkänn facit

```powershell
uv run python scripts/behavior_facit.py print
```

Redigera JSON: lägg till rader i `levels[ratio].events[]` med `event_bar` + `human_label` (flera per nivå tillåtna).

### 4. Validera

```powershell
uv run python scripts/behavior_facit.py validate
```

Kräver `human_label` på varje **event**. Tom `events[]` eller bara `auto_candidate` ger **inte** OK.

`validate --allow-auto-only` finns bara för att kolla filstruktur — **inte** giltigt facit för Fas 5.

### 4. Chart

Öppna `1d.json` + TV/labeling tool vid sidan av `print`-utskriften.
