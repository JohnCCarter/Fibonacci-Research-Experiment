# Maskin-labeling — två giltiga frågor

Provisoriska kandidater (`source="machine"`). Fullständiga integritetsregler: README § Maskin-labeling,
`premortem/reflections/2026-05-29-machine-labeling.md`.

**Lärdom (2026-05-29, BTC/USDT 1w):** Ett *chartfönster* du beskriver är inte alltid samma fråga som
*vilken swing motorn väljer på full historik*. **Båda svaren kan vara giltiga** — dokumentera vilket
du menar innan du jämför eller befordrar till facit.

---

## Fråga A — Motorns swing (standard `autolabel`)

**Vad det svarar på:** Vilken swing-leg skulle motorn välja som **bästa** leg på tillgänglig
weekly-historik (med warmup för pivots/ATR)?

**Kommando:**

```bash
uv run python -m fibengine.labeling.autolabel --symbols BTC/USDT --timeframes 1w
```

**Typiskt beteende:** Endpoints kan ligga **utanför** det synliga fönster du har på TradingView just nu,
om en äldre/nyligare leg poängsätter högre.

**När det är rätt:** Du vill ha **facit för “vilken swing gäller på denna TF”** (golden set) efter
mänsklig granskning → spara som `source="human"` i `labeling.tool`.

**Exempel (godkänt facit):** BTC/USDT 1w — high **2025-10-27** @ 116 400, low **2026-02-02** @ 60 000.
Se `data/labels/binance/BTC-USDT/1w.json`, reflektion
`premortem/reflections/2026-05-29-btc-1w-machine-approved.md`.

---

## Fråga B — Synligt chartfönster (lokal vy)

**Vad det svarar på:** Vilken swing **syns** mellan två datum du anger (t.ex. “måndag 23 mar – måndag 4 maj 2026”
på weekly)?

**Status i kod:** Standard-`autolabel` gör **inte** detta automatiskt. Det kräver att endpoints filtreras
till fönstret (kommande flagga `--chart-window-start` / `--chart-window-end`, eller manuell omkörning
med `rank_swings` + filter). Tills dess: beskriv fönstret i chat/issue så vi inte blandar ihop med fråga A.

**Typiskt beteende:** Low/high nära **första/sista veckan** i fönstret; pris från **vecko-OHLC** (Binance-cache),
inte nödvändigtvis exakt samma som en manuell wick-klick i TradingView.

**När det är rätt:** Du vill validera “vad motorn ser i **den här rutan**” — bra maskin-kandidat eller
jämförelse mot screenshot, **inte** automatiskt samma som facit för hela TF.

**Exempel (BTC/USDT 1w, fönster 2026-03-23 – 2026-05-04):**

| Källa | Low | High |
|--------|-----|------|
| Motor (endpoints i fönster) | 65 000 (vecko 23 mar) | 82 850 (vecko 4 maj) |
| TradingView (användare) | 65 019 | 82 807 |
| Skillnad | ~19 USDT | ~43 USDT |

Liten marginal = **bra resultat** för fråga B; det **ersätter inte** godkänd fråga A om de skiljer sig.

Artefakt från omkörning: `experiments/runs/experiment/2026-05-29/btc_1w_machine_window/candidate.json`.

---

## Kommunikationsfallgropar

| Du säger | Risk om vi tolkar fel | Rätt tolkning |
|----------|------------------------|---------------|
| “Kör maskin på weekly 23 mar – 4 maj” | Endpoints måste ligga i datumintervallet | Antingen **fråga B** (fönster) eller **fråga A** (bästa leg) — **fråga explicit** |
| “Det blev fel datum” | Vi byter facit till fönster-swing | Fönster-swing kan vara **rätt för B** medan **A fortfarande är facit** |
| “TV visar andra priser” | Bug i motorn | Ofta **OHLC vs wick**; jämför apples-to-apples |

**Regel:** Innan befordran till `source="human"`, skriv i not/reflektion: **A (motor-swing)** eller **B (chartfönster)**.

---

## Facit och evaluering (oförändrat)

- Endast `source="human"` räknas i `pivot_recall`, `experiment`, och 20–30-målet (`worklist`).
- Maskin-labels skriver **aldrig** över human (`skipped_human`).
- Befordran: `labeling.tool` → justera → `s` → `human`.

---

## Relaterat

| Fil | Innehåll |
|-----|----------|
| `premortem/reflections/2026-05-29-machine-labeling.md` | Införande av maskin-labeling |
| `premortem/reflections/2026-05-29-btc-1w-machine-approved.md` | BTC 1w: A godkänd som facit |
| `data/labels/README.md` | `source`-fält |

**Planerat:** `--chart-window-start` / `--chart-window-end` på `labeling.autolabel` för fråga B i CLI.
