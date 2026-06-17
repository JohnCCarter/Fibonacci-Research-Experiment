# Labeling tool (`fibengine.labeling.tool`)

Interaktiv matplotlib-workspace fÃ¶r manuellt facit. Maskin-kandidater granskas hÃ¤r innan `source=human`.

KÃ¶r: `uv run python -m fibengine.labeling.tool`

---

## Vad verktyget Ã¤r (och inte Ã¤r)

| Ã„r | Ã„r inte |
|----|---------|
| Golden-set-editor (human facit) | Auto-optimering eller â€œsanningâ€ frÃ¥n motorn |
| Snap till **candle high/low** per klick | Fri handritning pÃ¥ godtyckligt pris |
| Lokal desktop-GUI | TradingView-klon eller headless CI fÃ¶r musinteraktion |
| En fil (`labeling/tool.py`, ~595 rader) | ModulÃ¤rt uppdelad Ã¤nnu (kÃ¤nd skuld, `repository-layout-policy.md` Â§2B) |

---

## Tekniska begrÃ¤nsningar (lÃ¤s innan du Ã¤ndrar UI)

### 1. Matplotlib + full `redraw()`

- Chart ritas om med `ax.clear()` vid nÃ¤stan varje Ã¤ndring (drag, klick, tangent).
- **Konsekvens:** nya UI-element (crosshair, hover-text) fÃ¶rsvinner vid `redraw()` om de inte skapas om eller hÃ¥lls utanfÃ¶r `clear()`.
- **Risk vid Ã¤ndring:** hover som ritar i `on_motion` utan plan â†’ flicker, eller fÃ¶rsvinner vid drag.

**SÃ¤kert mÃ¶nster:** en `ax.text` / `ax.axhline` med `set_visible(False)` uppdateras i `on_motion`; **ingen** `redraw()` pÃ¥ ren hover â€” bara `fig.canvas.draw_idle()`. Full `redraw()` endast vid pick/drag/marknadbyte.

### 2. Klick = snap, inte musens Y

```text
set_pick / move_pick â†’ pris = df["high"|"low"] pÃ¥ vald bar, inte event.ydata
```

- Du kan **inte** sÃ¤tta ett pris mellan high/low pÃ¥ samma candle via klick.
- Hover/crosshair-pris (om vi lÃ¤gger till det) Ã¤r **visning only** â€” Ã¤ndrar inte facit fÃ¶rrÃ¤n du klickar/draggar (fortfarande snap).

### 3. Spar-validering (`_label_warnings`)

Spara (`s`) blockeras om:

- high och low pÃ¥ **samma bar** â€” **undantag (research):** se Â§3A;
- endpoint inom **kantmarginal** (`lookback` / `fractal_n`) frÃ¥n vÃ¤nster/hÃ¶ger kant â€” fÃ¶r lite historik i fÃ¶nstret.

Varningar Ã¤r **rÃ¥d**, inte facit-regler frÃ¥n motorn â€” men sparar dig frÃ¥n uppenbart dÃ¥liga labels.

### 3A. `same_candle_mtf_resolution` (research, 1W â†’ 1D)

NÃ¤r H och L ligger pÃ¥ **samma weekly candle** men du menar olika **dagliga** pivots (TV-MTF-resonemang):

1. Verktyget hÃ¤mtar alla **1D**-bars i den veckan (Bitfinex-cache, samma symbol/bÃ¶rs).
2. **HÃ¶gsta daily high** och **lÃ¤gsta daily low** â€” om de sitter pÃ¥ **olika** dagar â†’ spar tillÃ¥ts.
3. JSON fÃ¥r extra block `same_candle_mtf_resolution` (weekly H/L ofÃ¶rÃ¤ndrat + metadata).

Aktiveras i `config/settings.yaml`:

```yaml
labeling:
  enable_same_candle_mtf_resolution: true
```

**AnvÃ¤nds inte** av `pivot_recall`, `experiment` eller motorn â€” endast dokumentation i golden set tills vidare.

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

**Princip:** HTF-priser = facit-range. LTF-metadata = **ordning** (och fib-riktning) â€” skriver **inte** Ã¶ver HTF-priser.

NÃ¤r `mtf_disambiguation: true` (1w â†’ 1d idag):

| Fall | Beteende |
|------|----------|
| **Samma weekly candle** | Sparad metadata om den finns; annars hÃ¤rled max-high / min-low-dag i veckan |
| **Olika veckor (fraktal)** | Varje endpoint â†’ **egen veckas** daily extreme-dag; HTF-pris ofÃ¶rÃ¤ndrat; tid/fib-ordning pÃ¥ 1D |

OFF: same-candle utan metadata â†’ skip. Olika veckor â†’ jÃ¤mfÃ¶relse pÃ¥ weekly (som tidigare).

Annars: `mtf_status: unresolved` â†’ mjukt skip (inga falska anchors).

JÃ¤mfÃ¶r OFF vs ON:

```bash
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USD --timeframe 1w
```

### 3C. Full MTF-leg (research) â€” daily Fib in/ut inom weekly-facit

**Halva pipelinen (3B):** HTF-priser + LTF-ordning/tid.  
**Hela pipelinen (3C):** samma ankare, sedan **1D-scan** mot Fib-nivÃ¥er ritade pÃ¥ **weekly-range** (inga nya HTF-priser).

| Fas | Daily-fÃ¶nster | Vad vi letar efter |
|-----|---------------|-------------------|
| **impulse** | LTF high-dag â†’ LTF low-dag | NivÃ¥berÃ¶ringar pÃ¥ vÃ¤gen ner (ned-leg) |
| **retrace** | Efter LTF low â†’ sista daily i cache | Touch / rejection vid 0,382 / 0,5 / 0,618 (upplevd in/ut-zon) |

KÃ¶r (tvingar `mtf_disambiguation` ON internt; Ã¤ndrar inte `settings.yaml`):

```bash
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USD --timeframe 1w
uv run python scripts/mtf_leg_daily_fib.py --all-1w
```

JSON: `experiments/results/mtf_leg_daily_fib_*.json`. Detta Ã¤r **beskrivande research**, inte motor-score mot TV.

### 4. Befintlig label vs candle-fÃ¶nster

- Laddad label: timestamp â†’ **nÃ¤rmaste bar** i nu laddad `df`.
- Om `data.limit` / cache Ã¤r fÃ¶r kort hamnar facit **out-of-window** (syns i `pivot_recall`, inte i verktyget).
- LÃ¥nga TF: anvÃ¤nd `timeframe_limits` i `config/settings.yaml` (samma som validate-spÃ¥ret).

### 5. Zoom och pan

- **Zoom/pan:** matplotlib-verktygsraden (fÃ¶rstoringsglas / hand) â€” ingen mushjul-doc, standard backend-beteende.
- **Vy bevaras** Ã¶ver `redraw()` (drag, `f`/`g`, spara, hover pÃ¥verkar inte): grÃ¤nser sparas i `view_limits` fÃ¶re `ax.clear()` och Ã¥terstÃ¤lls efter omritning.
- **`z`:** Ã¥terstÃ¤ll hela charten (autoscale pÃ¥ all data).
- **Ny symbol/TF:** vy nollstÃ¤lls (ny `df`).
- Toolbar **home** = matplotlibs egen reset; **`z`** = verktygets reset efter omritning.

Toolbar kan fortfarande **konkurrera** med klick/drag â€” anvÃ¤nd pan/zoom-lÃ¤ge medvetet, inte samtidigt som du drar markers.

### 5B. Flera fib-legs pÃ¥ samma TF (research, t.ex. 1d)

**Bakgrund:** Tidigare skrev varje `s` **Ã¶ver** samma fil â€” bara en fib i JSON trots flera i UI. Orsak och fix: [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) Â§0A.

En fil kan innehÃ¥lla **flera** high/low-par (nedgÃ¥ng + uppgÃ¥ng) utan overwrite:

| Tangent | Funktion |
|---------|----------|
| **`p`** eller **`a`** | Push: spara nuvarande high/low som **ny leg** i sessionen, tÃ¶m picks |
| **`j` / `k`** | FÃ¶regÃ¥ende / nÃ¤sta leg (redigera, fib ritas svagare pÃ¥ inaktiva) |
| **`s`** | Spara **alla** legs till JSON. Om picks skiljer sig frÃ¥n aktiv leg â†’ **ny leg lÃ¤ggs till automatiskt** (ingen overwrite av fÃ¶rra) |

**Vanligt misstag:** bara `s` tvÃ¥ gÃ¥nger utan `p` gav tidigare overwrite â€” nu lÃ¤gger andra `s` till ny leg om endpoints skiljer sig. BekrÃ¤fta i terminal: `Saved 2 legs -> ...` och `"legs": [` i JSON.

Fil med 2+ legs fÃ¥r `"legs": [...]` i JSON. En leg = gammalt format (bara `high`/`low`).

Motor/recall anvÃ¤nder fortfarande top-level `high`/`low` (fÃ¶rsta leg) tills daily-beteende-facit byggs.

### 6. Byta symbol / timeframe

- **Symbol:** `â†` `â†’` eller **`[` `]`** eller **`,` `.`** (cyklar BTC, ETH, SOL om du inte angav `--symbols`).
- **Timeframe:** `â†‘` `â†“` eller **`;`** / **`'`**.
- Starta med flera symboler: `--symbols BTC/USD,ETH/USD,SOL/USD --timeframe 1w`.
- **Klicka i chart-fÃ¶nstret** innan tangent â€” annars hamnar den i terminal/Cursor.
- Avaktivera toolbar **pan** (hand-ikon) om pilar bara flyttar bilden; anvÃ¤nd `[` `]` istÃ¤llet.
- Vid byte skrivs `Market: ETH/USD 1w` i terminalen.

### 7. Interaktionskonflikter

- **Drag** marker (â‰¤18 px) vs **klick** ny punkt â€” samma musknapp.
- **Shift+drag** flyttar hela leg **horisontellt** (bar-index), inte vertikalt.
- MÃ¥nga tangenter avstÃ¤ngda i matplotlib (`_disable_matplotlib_keymap_conflicts`) sÃ¥ `h/l/s/â€¦` fungerar.

### 8. Testning

- `tests/labeling/test_label_tool.py` testar **hjÃ¤lpfunktioner och workspace**, inte GUI-events.
- `labeling/tool.py` Ã¤r **exkluderad frÃ¥n coverage** (`pyproject.toml`) â€” medvetet.
- **Regression:** manuell rÃ¶ktest efter UI-Ã¤ndring; automatisk test av hover krÃ¤ver mock av canvas (ej vÃ¤rt komplexiteten Ã¤n).

### 9. Prestanda

- MÃ¥nga candles + `redraw()` vid drag kan kÃ¤nnas segt.
- Hover ska vara **lÃ¤tt** (uppdatera 1â€“2 textobjekt), inte rita om candles varje musrÃ¶relse.

---

## SÃ¤kra vs riskfyllda Ã¤ndringar

| Relativt sÃ¤ker | Riskfyllt utan refaktor |
|---------------|------------------------|
| Hover/crosshair-pris (read-only) | Ny sparlogik eller annan snap-regel |
| Statusrad med OHLC fÃ¶r bar under mus | Ã„ndra `set_pick` till fri Y |
| Tunn `fig.text` utanfÃ¶r axes | Stor omstruktur av `redraw()` |
| Dokumentation, tangenter | Fler saker i samma `on_motion` som anropar `redraw()` |

**Innan merge:** manuellt testa klick, drag, shift+drag, spara, byta symbol/TF, pan/zoom toolbar.

---

## Hover (implementerat)

Modul: `fibengine.labeling.hover` â€” kopplas in frÃ¥n `tool.py`.

| LÃ¤ge | Visning |
|------|---------|
| **A** | Horisontell crosshair + pris vid musens Y (hÃ¶ger kant, `event.ydata`) |
| **B** | Vertikal linje vid nÃ¤rmaste bar + OHLC-rad Ã¶verst till vÃ¤nster |

- Uppdateras med `draw_idle()` â€” **ingen** full `redraw()` pÃ¥ hover.
- DÃ¶ljs vid drag (high/low eller shift+leg).
- Facit ofÃ¶rÃ¤ndrat: klick/drag snappar fortfarande candle high/low.

**RÃ¶ktest:** klick, drag, shift+drag, spara, byta symbol/TF, pan/zoom toolbar.

---

## Relaterat

- [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) â€” hela MTF/daily-fib-arbetet (VAD/HUR, steg 1â€“4, BTC-facit)
- [MACHINE_LABELING.md](MACHINE_LABELING.md) â€” frÃ¥ga A (motor-swing) vs B (chartfÃ¶nster)
- [data/labels/README.md](../data/labels/README.md) â€” `source` human/machine
- `repository-layout-policy.md` Â§2B â€” `tool.py` grandfather tills split

