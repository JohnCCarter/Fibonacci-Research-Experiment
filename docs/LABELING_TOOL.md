# Labeling tool (`fibengine.labeling.tool`)

Interaktiv matplotlib-workspace för manuellt facit. Maskin-kandidater granskas här innan `source=human`.

Kör: `uv run python -m fibengine.labeling.tool`

---

## Vad verktyget är (och inte är)

| Är | Är inte |
|----|---------|
| Golden-set-editor (human facit) | Auto-optimering eller “sanning” från motorn |
| Snap till **candle high/low** per klick | Fri handritning på godtyckligt pris |
| Lokal desktop-GUI | TradingView-klon eller headless CI för musinteraktion |
| En fil (`labeling/tool.py`, ~595 rader) | Modulärt uppdelad ännu (känd skuld, `REPO_POLICY.md` §2B) |

---

## Tekniska begränsningar (läs innan du ändrar UI)

### 1. Matplotlib + full `redraw()`

- Chart ritas om med `ax.clear()` vid nästan varje ändring (drag, klick, tangent).
- **Konsekvens:** nya UI-element (crosshair, hover-text) försvinner vid `redraw()` om de inte skapas om eller hålls utanför `clear()`.
- **Risk vid ändring:** hover som ritar i `on_motion` utan plan → flicker, eller försvinner vid drag.

**Säkert mönster:** en `ax.text` / `ax.axhline` med `set_visible(False)` uppdateras i `on_motion`; **ingen** `redraw()` på ren hover — bara `fig.canvas.draw_idle()`. Full `redraw()` endast vid pick/drag/marknadbyte.

### 2. Klick = snap, inte musens Y

```text
set_pick / move_pick → pris = df["high"|"low"] på vald bar, inte event.ydata
```

- Du kan **inte** sätta ett pris mellan high/low på samma candle via klick.
- Hover/crosshair-pris (om vi lägger till det) är **visning only** — ändrar inte facit förrän du klickar/draggar (fortfarande snap).

### 3. Spar-validering (`_label_warnings`)

Spara (`s`) blockeras om:

- high och low på **samma bar** — **undantag (research):** se §3A;
- endpoint inom **kantmarginal** (`lookback` / `fractal_n`) från vänster/höger kant — för lite historik i fönstret.

Varningar är **råd**, inte facit-regler från motorn — men sparar dig från uppenbart dåliga labels.

### 3A. `same_candle_mtf_resolution` (research, 1W → 1D)

När H och L ligger på **samma weekly candle** men du menar olika **dagliga** pivots (TV-MTF-resonemang):

1. Verktyget hämtar alla **1D**-bars i den veckan (Binance-cache, samma symbol/börs).
2. **Högsta daily high** och **lägsta daily low** — om de sitter på **olika** dagar → spar tillåts.
3. JSON får extra block `same_candle_mtf_resolution` (weekly H/L oförändrat + metadata).

Aktiveras i `config/settings.yaml`:

```yaml
labeling:
  enable_same_candle_mtf_resolution: true
```

**Används inte** av `pivot_recall`, `experiment` eller motorn — endast dokumentation i golden set tills vidare.

Exempel-metadata:

```json
"same_candle_mtf_resolution": {
  "timeframe": "1w",
  "resolved_by": "lower_timeframe",
  "resolution_timeframe": "1d",
  "high_daily_timestamp": "2026-03-25T00:00:00+00:00",
  "low_daily_timestamp": "2026-03-28T00:00:00+00:00",
  "order": "high_then_low"
}
```

Misslyckas om: flagga av, ingen 1D-cache i veckan, eller high/low kollapsar till **samma** daily bar.

### 3B. MTF Disambiguation Layer (motor, research)

`config/settings.yaml`:

```yaml
labeling:
  mtf_disambiguation: false   # baseline (default)
  # mtf_disambiguation: true  # research ON
```

**Princip:** HTF-priser = facit-range. LTF-metadata = **ordning** (och fib-riktning) — skriver **inte** över HTF-priser.

När `mtf_disambiguation: true` (1w → 1d idag):

| Fall | Beteende |
|------|----------|
| **Samma weekly candle** | Sparad metadata om den finns; annars härled max-high / min-low-dag i veckan |
| **Olika veckor (fraktal)** | Varje endpoint → **egen veckas** daily extreme-dag; HTF-pris oförändrat; tid/fib-ordning på 1D |

OFF: same-candle utan metadata → skip. Olika veckor → jämförelse på weekly (som tidigare).

Annars: `mtf_status: unresolved` → mjukt skip (inga falska anchors).

Jämför OFF vs ON:

```bash
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USDT --timeframe 1w
```

### 3C. Full MTF-leg (research) — daily Fib in/ut inom weekly-facit

**Halva pipelinen (3B):** HTF-priser + LTF-ordning/tid.  
**Hela pipelinen (3C):** samma ankare, sedan **1D-scan** mot Fib-nivåer ritade på **weekly-range** (inga nya HTF-priser).

| Fas | Daily-fönster | Vad vi letar efter |
|-----|---------------|-------------------|
| **impulse** | LTF high-dag → LTF low-dag | Nivåberöringar på vägen ner (ned-leg) |
| **retrace** | Efter LTF low → sista daily i cache | Touch / rejection vid 0,382 / 0,5 / 0,618 (upplevd in/ut-zon) |

Kör (tvingar `mtf_disambiguation` ON internt; ändrar inte `settings.yaml`):

```bash
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USDT --timeframe 1w
uv run python scripts/mtf_leg_daily_fib.py --all-1w
```

JSON: `experiments/results/mtf_leg_daily_fib_*.json`. Detta är **beskrivande research**, inte motor-score mot TV.

### 4. Befintlig label vs candle-fönster

- Laddad label: timestamp → **närmaste bar** i nu laddad `df`.
- Om `data.limit` / cache är för kort hamnar facit **out-of-window** (syns i `pivot_recall`, inte i verktyget).
- Långa TF: använd `timeframe_limits` i `config/settings.yaml` (samma som validate-spåret).

### 5. Zoom och pan

- **Zoom/pan:** matplotlib-verktygsraden (förstoringsglas / hand) — ingen mushjul-doc, standard backend-beteende.
- **Vy bevaras** över `redraw()` (drag, `f`/`g`, spara, hover påverkar inte): gränser sparas i `view_limits` före `ax.clear()` och återställs efter omritning.
- **`z`:** återställ hela charten (autoscale på all data).
- **Ny symbol/TF:** vy nollställs (ny `df`).
- Toolbar **home** = matplotlibs egen reset; **`z`** = verktygets reset efter omritning.

Toolbar kan fortfarande **konkurrera** med klick/drag — använd pan/zoom-läge medvetet, inte samtidigt som du drar markers.

### 5B. Flera fib-legs på samma TF (research, t.ex. 1d)

**Bakgrund:** Tidigare skrev varje `s` **över** samma fil — bara en fib i JSON trots flera i UI. Orsak och fix: [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) §0A.

En fil kan innehålla **flera** high/low-par (nedgång + uppgång) utan overwrite:

| Tangent | Funktion |
|---------|----------|
| **`p`** eller **`a`** | Push: spara nuvarande high/low som **ny leg** i sessionen, töm picks |
| **`j` / `k`** | Föregående / nästa leg (redigera, fib ritas svagare på inaktiva) |
| **`s`** | Spara **alla** legs till JSON. Om picks skiljer sig från aktiv leg → **ny leg läggs till automatiskt** (ingen overwrite av förra) |

**Vanligt misstag:** bara `s` två gånger utan `p` gav tidigare overwrite — nu lägger andra `s` till ny leg om endpoints skiljer sig. Bekräfta i terminal: `Saved 2 legs -> ...` och `"legs": [` i JSON.

Fil med 2+ legs får `"legs": [...]` i JSON. En leg = gammalt format (bara `high`/`low`).

Motor/recall använder fortfarande top-level `high`/`low` (första leg) tills daily-beteende-facit byggs.

### 6. Byta symbol / timeframe

- **Symbol:** `←` `→` eller **`[` `]`** eller **`,` `.`** (cyklar BTC, ETH, SOL om du inte angav `--symbols`).
- **Timeframe:** `↑` `↓` eller **`;`** / **`'`**.
- Starta med flera symboler: `--symbols BTC/USDT,ETH/USDT,SOL/USDT --timeframe 1w`.
- **Klicka i chart-fönstret** innan tangent — annars hamnar den i terminal/Cursor.
- Avaktivera toolbar **pan** (hand-ikon) om pilar bara flyttar bilden; använd `[` `]` istället.
- Vid byte skrivs `Market: ETH/USDT 1w` i terminalen.

### 7. Interaktionskonflikter

- **Drag** marker (≤18 px) vs **klick** ny punkt — samma musknapp.
- **Shift+drag** flyttar hela leg **horisontellt** (bar-index), inte vertikalt.
- Många tangenter avstängda i matplotlib (`_disable_matplotlib_keymap_conflicts`) så `h/l/s/…` fungerar.

### 8. Testning

- `tests/labeling/test_label_tool.py` testar **hjälpfunktioner och workspace**, inte GUI-events.
- `labeling/tool.py` är **exkluderad från coverage** (`pyproject.toml`) — medvetet.
- **Regression:** manuell röktest efter UI-ändring; automatisk test av hover kräver mock av canvas (ej värt komplexiteten än).

### 9. Prestanda

- Många candles + `redraw()` vid drag kan kännas segt.
- Hover ska vara **lätt** (uppdatera 1–2 textobjekt), inte rita om candles varje musrörelse.

---

## Säkra vs riskfyllda ändringar

| Relativt säker | Riskfyllt utan refaktor |
|---------------|------------------------|
| Hover/crosshair-pris (read-only) | Ny sparlogik eller annan snap-regel |
| Statusrad med OHLC för bar under mus | Ändra `set_pick` till fri Y |
| Tunn `fig.text` utanför axes | Stor omstruktur av `redraw()` |
| Dokumentation, tangenter | Fler saker i samma `on_motion` som anropar `redraw()` |

**Innan merge:** manuellt testa klick, drag, shift+drag, spara, byta symbol/TF, pan/zoom toolbar.

---

## Hover (implementerat)

Modul: `fibengine.labeling.hover` — kopplas in från `tool.py`.

| Läge | Visning |
|------|---------|
| **A** | Horisontell crosshair + pris vid musens Y (höger kant, `event.ydata`) |
| **B** | Vertikal linje vid närmaste bar + OHLC-rad överst till vänster |

- Uppdateras med `draw_idle()` — **ingen** full `redraw()` på hover.
- Döljs vid drag (high/low eller shift+leg).
- Facit oförändrat: klick/drag snappar fortfarande candle high/low.

**Röktest:** klick, drag, shift+drag, spara, byta symbol/TF, pan/zoom toolbar.

---

## Relaterat

- [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) — hela MTF/daily-fib-arbetet (VAD/HUR, steg 1–4, BTC-facit)
- [MACHINE_LABELING.md](MACHINE_LABELING.md) — fråga A (motor-swing) vs B (chartfönster)
- [data/labels/README.md](../data/labels/README.md) — `source` human/machine
- `REPO_POLICY.md` §2B — `tool.py` grandfather tills split
