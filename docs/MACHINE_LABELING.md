# Maskin-labeling â€” tvÃ¥ giltiga frÃ¥gor

Provisoriska kandidater (`source="machine"`). FullstÃ¤ndiga integritetsregler: README Â§ Maskin-labeling,
`premortem/reflections/2026-05-29-machine-labeling.md`.

**LÃ¤rdom (2026-05-29, BTC/USD 1w):** Ett *chartfÃ¶nster* du beskriver Ã¤r inte alltid samma frÃ¥ga som
*vilken swing motorn vÃ¤ljer pÃ¥ full historik*. **BÃ¥da svaren kan vara giltiga** â€” dokumentera vilket
du menar innan du jÃ¤mfÃ¶r eller befordrar till facit.

---

## FrÃ¥ga A â€” Motorns swing (standard `autolabel`)

**Vad det svarar pÃ¥:** Vilken swing-leg skulle motorn vÃ¤lja som **bÃ¤sta** leg pÃ¥ tillgÃ¤nglig
weekly-historik (med warmup fÃ¶r pivots/ATR)?

**Kommando:**

```bash
uv run python -m fibengine.labeling.autolabel --symbols BTC/USD --timeframes 1w
```

**Typiskt beteende:** Endpoints kan ligga **utanfÃ¶r** det synliga fÃ¶nster du har pÃ¥ TradingView just nu,
om en Ã¤ldre/nyligare leg poÃ¤ngsÃ¤tter hÃ¶gre.

**NÃ¤r det Ã¤r rÃ¤tt:** Du vill ha **facit fÃ¶r â€œvilken swing gÃ¤ller pÃ¥ denna TFâ€** (golden set) efter
mÃ¤nsklig granskning â†’ spara som `source="human"` i `labeling.tool`.

**Exempel (godkÃ¤nt facit, legacy):** BTC/USD 1w â€” high **2025-10-27** @ 116â€¯400, low **2026-02-02** @ 60â€¯000.
Se reflektion
`premortem/reflections/2026-05-29-btc-1w-machine-approved.md`.

---

## FrÃ¥ga B â€” Synligt chartfÃ¶nster (lokal vy)

**Vad det svarar pÃ¥:** Vilken swing **syns** mellan tvÃ¥ datum du anger (t.ex. â€œmÃ¥ndag 23 mar â€“ mÃ¥ndag 4 maj 2026â€
pÃ¥ weekly)?

**Status i kod:** Standard-`autolabel` gÃ¶r **inte** detta automatiskt. Det krÃ¤ver att endpoints filtreras
till fÃ¶nstret (kommande flagga `--chart-window-start` / `--chart-window-end`, eller manuell omkÃ¶rning
med `rank_swings` + filter). Tills dess: beskriv fÃ¶nstret i chat/issue sÃ¥ vi inte blandar ihop med frÃ¥ga A.

**Typiskt beteende:** Low/high nÃ¤ra **fÃ¶rsta/sista veckan** i fÃ¶nstret; pris frÃ¥n **vecko-OHLC** (Bitfinex-cache),
inte nÃ¶dvÃ¤ndigtvis exakt samma som en manuell wick-klick i TradingView.

**NÃ¤r det Ã¤r rÃ¤tt:** Du vill validera â€œvad motorn ser i **den hÃ¤r rutan**â€ â€” bra maskin-kandidat eller
jÃ¤mfÃ¶relse mot screenshot, **inte** automatiskt samma som facit fÃ¶r hela TF.

**Exempel (BTC/USD 1w, fÃ¶nster 2026-03-23 â€“ 2026-05-04):**

| KÃ¤lla | Low | High |
|--------|-----|------|
| Motor (endpoints i fÃ¶nster) | 65â€¯000 (vecko 23 mar) | 82â€¯850 (vecko 4 maj) |
| TradingView (anvÃ¤ndare) | 65â€¯019 | 82â€¯807 |
| Skillnad | ~19 USDT | ~43 USDT |

Liten marginal = **bra resultat** fÃ¶r frÃ¥ga B; det **ersÃ¤tter inte** godkÃ¤nd frÃ¥ga A om de skiljer sig.

Artefakt frÃ¥n omkÃ¶rning: `experiments/runs/experiment/2026-05-29/btc_1w_machine_window/candidate.json`.

---

## Kommunikationsfallgropar

| Du sÃ¤ger | Risk om vi tolkar fel | RÃ¤tt tolkning |
|----------|------------------------|---------------|
| â€œKÃ¶r maskin pÃ¥ weekly 23 mar â€“ 4 majâ€ | Endpoints mÃ¥ste ligga i datumintervallet | Antingen **frÃ¥ga B** (fÃ¶nster) eller **frÃ¥ga A** (bÃ¤sta leg) â€” **frÃ¥ga explicit** |
| â€œDet blev fel datumâ€ | Vi byter facit till fÃ¶nster-swing | FÃ¶nster-swing kan vara **rÃ¤tt fÃ¶r B** medan **A fortfarande Ã¤r facit** |
| â€œTV visar andra priserâ€ | Bug i motorn | Ofta **OHLC vs wick**; jÃ¤mfÃ¶r apples-to-apples |

**Regel:** Innan befordran till `source="human"`, skriv i not/reflektion: **A (motor-swing)** eller **B (chartfÃ¶nster)**.

---

## Facit och evaluering (ofÃ¶rÃ¤ndrat)

- Endast `source="human"` rÃ¤knas i `pivot_recall`, `experiment`, och 20â€“30-mÃ¥let (`worklist`).
- Maskin-labels skriver **aldrig** Ã¶ver human (`skipped_human`).
- Befordran: `labeling.tool` â†’ justera â†’ `s` â†’ `human`.

---

## Relaterat

| Fil | InnehÃ¥ll |
|-----|----------|
| `premortem/reflections/2026-05-29-machine-labeling.md` | InfÃ¶rande av maskin-labeling |
| `premortem/reflections/2026-05-29-btc-1w-machine-approved.md` | BTC 1w: A godkÃ¤nd som facit |
| `data/labels/README.md` | `source`-fÃ¤lt |

**Planerat:** `--chart-window-start` / `--chart-window-end` pÃ¥ `labeling.autolabel` fÃ¶r frÃ¥ga B i CLI.

