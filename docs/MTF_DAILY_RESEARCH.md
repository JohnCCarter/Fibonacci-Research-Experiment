# MTF + daily fib research (2026-05-29)

Sammanfattning av forskningsriktningen: **weekly = VAD**, **daily = HUR**.  
Detta dokument Ã¤r kÃ¤llan fÃ¶r vad som Ã¤r byggt, vad som saknas, och hur det hÃ¤nger ihop.

Relaterat:

- **[HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md)** â€” **jobba oss ner:** 1w â†’ 1d â†’ 4h â†’ 1h ([GitHub #14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14))
- **[RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md)** â€” aktiv scope + [GitHub #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12) (Hypothesis A: maskin â†’ spot-check)
- [LABELING_TOOL.md](LABELING_TOOL.md) â€” verktyg, tangenter, begrÃ¤nsningar
- [MACHINE_LABELING.md](MACHINE_LABELING.md) â€” motor-swing vs chartfÃ¶nster
- `config/settings.yaml` â€” `labeling.*` flags

---

## 0. VarfÃ¶r det inte gick frÃ¥n bÃ¶rjan â€” och hur vi lÃ¶ste det

### A. Flera fibs pÃ¥ daily syntes inte i repot (labeling tool)

**Vad du gjorde (korrekt i UI):**  
Rita fib fÃ¶r **nedgÃ¥ng**, sedan fib fÃ¶r **uppgÃ¥ng** (och fler segment) i labeling tool pÃ¥ 1d â€” samma symbol/TF.

**Vad som hÃ¤nde pÃ¥ disk:**  
Varje **`s`** skrev om **samma fil** (dÃ¥varande Bitfinex/BTC-USD 1d) med **ett** par `high` + `low`. FÃ¶rra leg fÃ¶rsvann. I JSON fanns bara **sista** paret (t.ex. maj-pullback 82kâ†’79k), inte janâ€“apr-kedjan du ritat.

**VarfÃ¶r (design frÃ¥n start):**  
Golden set var modellerat som **en swing per symbol + timeframe** â€” som weekly. Verktyget kunde visa fib pÃ¥ skÃ¤rmen (`g`), men **persistens** = en `SwingLabel`, inte en lista. Inget fel i din metod; **schemat matchade inte** â€œdaily = mÃ¥nga HUR-legsâ€.

**Symptom vi sÃ¥g:**  
- Du: â€œjag ritade flera fibsâ€  
- Granskning: bara en leg i filen  
- Risk fÃ¶r missfÃ¶rstÃ¥nd (â€œbilder?â€) â€” det var **JSON-overwrite**, inte TV

**FÃ¶rsta fÃ¶rsÃ¶k (ofullstÃ¤ndigt):**  
Multi-leg i kod + tangent **`a`** (append leg). Funkade i teorin, men:

1. MÃ¥nga tryckte bara **`s`** igen (vana) â†’ fortfarande en leg, eller overwrite av aktiv leg i sessionen.  
2. Terminalen sa `Saved label` â€” inte `Saved 2 legs` / `Stored leg_2` â†’ svÃ¥rt att se att multi-leg aktiverades.  
3. **`s` utan `a`:** om du redan hade leg_1 laddad och satte nya endpoints uppdaterades **leg_1** i stÃ¤llet fÃ¶r att leg_2 lades till.

**LÃ¶sning (nu):**

| Del | Ã„ndring |
|-----|---------|
| **Schema** | `LegLabel` + `"legs": [...]` i JSON nÃ¤r â‰¥2 legs (`store.py`) |
| **Tangent `p`** | Push leg explicit (alias `a`) |
| **Smart `s`** | Om nya picks **inte** matchar aktiv legs barer â†’ **ny leg appendas automatiskt**, sedan sparas alla |
| **UI** | Alla legs ritas (svagare inaktiva); titel visar `legs=N` |
| **Startup** | Rad i terminal: multi-leg-instruktion |
| **BekrÃ¤ftelse** | `Saved 2 legs -> ...` och `"legs": [` i filen |

**Resultat:** BTC `1d.json` med **30 legs** (2026-05-29T11:25) â€” fÃ¶rsta riktiga daily-HUR-facit.

**Workflow nu:**

1. H+L â†’ **`p`** (eller H+L â†’ **`s`** â†’ H+L â†’ **`s`** med auto-append)  
2. Upprepa fÃ¶r fler segment  
3. Sista **`s`** â†’ alla legs till disk  

---

### B. â€œMTF / fib stÃ¤mmer inte mot TVâ€ (annat problem)

**Vad det sÃ¥g ut som:**  
Weekly-facit OK, men 0.618 pÃ¥ daily i auto-scan (~83k) vs ~81k pÃ¥ TV â€” â€œmotorn failarâ€.

**VarfÃ¶r det inte var samma bugg:**  
- **Olika ankare** (Bitfinex snap 60â€¯000 vs TV 60â€¯091) â†’ annan fib-grid.  
- **Halva pipelinen:** MTF Disambiguation ger **ordning + tid** (1d-dagar inom veckor), inte **reaktion vid nivÃ¥**.  
- `mtf_leg_daily_fib` Ã¤r **heuristik** (touch/rejection), inte ditt facit fÃ¶r accept/reject/inâ€“ut.

**LÃ¶sning (begreppsmÃ¤ssig, inte en knapp):**  
Separera steg 1â€“2 (swing + nivÃ¥er) frÃ¥n steg 3â€“4 (beteende + beslut). Daily multi-leg **Ã¤r** steg 3-facit under uppbyggnad; motor ska inte â€œgissaâ€ steg 4 utan labels.

---

### C. Same-candle weekly (tidigare delproblem)

**Problem:** H+L pÃ¥ **samma** 1w-candle â†’ verktyget vÃ¤grade spara (regel fÃ¶r distinct endpoints).

**LÃ¶sning:** `same_candle_mtf_resolution` vid save (1D max-high / min-low-dag i veckan) + MTF Disambiguation i motor nÃ¤r flagga ON. HTF-priser ofÃ¶rÃ¤ndrade.

**Fraktal (senare):** H+L pÃ¥ **olika** veckor â†’ tvÃ¥ veckofÃ¶nster pÃ¥ 1D (en gÃ¥ng per endpoint), samma princip.

---

## 1. Mental modell (facit, inte motor-sanning)

| Lager | Tidsram | FrÃ¥ga | Exempel BTC |
|-------|---------|-------|-------------|
| **HTF** | 1w | Vilken **stor swing** ska mÃ¤tas? | 97â€¯924 â†’ 60â€¯000 |
| **LTF** | 1d | **Hur** rÃ¶rde sig priset (del-legs, nivÃ¥er, reaktioner)? | 30 fib-segment janâ€“maj 2026 |

- Weekly-priser = **facit-range** (snap till veckans H/L i labeling tool).
- Daily = **egna legs** inuti/efter samma berÃ¤ttelse â€” inte samma endpoints som weekly.
- Fib pÃ¥ daily ritas pÃ¥ **varje legs** egna ankare, inte automatiskt weekly-grid.

**Formulering vi anvÃ¤nder:** motorn hittar fib-nivÃ¥er; den har **Ã¤nnu inte facit** fÃ¶r *mÃ¤nskligt beteende vid* nivÃ¥erna (reject / accept / failure / inâ€“ut).

**Top-down (hela kedjan):** vi jobbar oss **ner** med fiben â€” weekly grid fÃ¶rst, daily legs/events, sedan (plan) 4h och 1h. Se [HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md).

---

## 2. Fyra steg (research-roadmap)

| Steg | InnehÃ¥ll | Repo-status |
|------|----------|-------------|
| **1** | Vilken swing? | âœ… weekly labels + motor-swing |
| **2** | Vilka fib-nivÃ¥er? | âœ… `fib_from_prices`, verktyg `g` |
| **3** | Beteende vid nivÃ¥? | âš ï¸ human facit (events); heuristik `annotate` / `mtf_leg_daily_fib` |
| **4** | MÃ¤nskligt beslut (in/ut) | âŒ ej kopplat till motor Ã¤n |

**Fas 3 (research finding, 2026-05-29):**  
Samma fib-nivÃ¥ (sÃ¤rskilt frÃ¥n **weekly grid**) kan ge **flera beteenden Ã¶ver tid** pÃ¥ daily â€” t.ex. `rejection` vid en touch och `continuation` vid en senare.  
â†’ Modell: **events[]** per nivÃ¥, inte ett enda label. Se [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md), [premortem finding](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md).

- **Weekly / HTF leg** = grid (`derived_prices`)  
- **Daily** = `events[]` med `event_bar` + `human_label`  
- Fil: `data/labels/research/.../1d-behavior.json` (tmp-sandbox: `research/tmp/`)  
- **Ingen motor, ingen promotion**

**Workflow (2026-05-31, #12):** maskin fÃ¶reslÃ¥r events â†’ mÃ¤nniska **spot-checkar** 20â€“40 st. Tmp/manual JSON = pilot fÃ¶r `events[]`, inte huvudspÃ¥r.

---

## 3. Kod: tre lager + multi-leg save

### 3A. Same-candle MTF (verktyg â†’ JSON)

NÃ¤r **H+L pÃ¥ samma 1w-bar** men olika **1d-dagar**:

- `labeling.enable_same_candle_mtf_resolution: true`
- Sparas som `same_candle_mtf_resolution` pÃ¥ label (eller pÃ¥ leg).
- Weekly H/L-priser Ã¤ndras **inte**.

### 3B. MTF Disambiguation Layer (motor, research)

- `labeling.mtf_disambiguation: false` (default) / `true` (research)
- **1w â†’ 1d:** ordning + tid; HTF-priser ofÃ¶rÃ¤ndrade.
- **Samma vecka:** sparad metadata eller hÃ¤rled max-high / min-low-dag i veckan.
- **Olika veckor (fraktal):** varje endpoint â†’ daily extreme i **sin** vecka (`fractal_endpoints`).
- Ã–vriga TF: ingen effekt (fallback som OFF).
- Same-candle utan metadata + OFF â†’ mjukt skip (`skipped_mtf`).

```bash
uv run python scripts/compare_mtf_disambiguation.py --summary
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USD --timeframe 1w
```

### 3C. Daily fib inom HTF-leg (beskrivande scan)

- Modul: `src/fibengine/labeling/mtf_leg_research.py`
- Script: `scripts/mtf_leg_daily_fib.py`
- HTF-range frÃ¥n weekly-facit; skannar 1d fÃ¶r touch/rejection vid 0.382 / 0.5 / 0.618 (impulse + retrace).
- **Inte** samma som TV-manuell tolkning; ankare kan skilja nÃ¥got i pris.

```bash
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USD --timeframe 1w
uv run python scripts/mtf_leg_daily_fib.py --all-1w
```

### 3D. Multi-leg save (labeling tool)

Se **Â§0A** fÃ¶r full historia (varfÃ¶r / hur). Kort: en `s` = en fil med ett par H+L â†’ overwrite; nu `legs[]` + `p` + smart `s`.

**Nu:**

| Tangent | Funktion |
|---------|----------|
| `p` / `a` | Push: spara nuvarande H+L som ny leg i sessionen |
| `j` / `k` | Byt aktiv leg |
| `s` | Spara **alla** legs; om nya picks â‰  aktiv leg â†’ **auto-ny leg** |

JSON med 2+ legs:

```json
{
  "exchange": "bitfinex",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "high": { "...": "leg_1 high (bakÃ¥tkompat)" },
  "low": { "...": "leg_1 low" },
  "legs": [
    { "id": "leg_1", "high": { ... }, "low": { ... } },
    { "id": "leg_2", "high": { ... }, "low": { ... } }
  ],
  "source": "human"
}
```

- **En leg:** gammalt format (utan `legs`-array).
- **Motor / recall / agreement:** anvÃ¤nder fortfarande top-level `high`/`low` (= leg_1) tills steg 3â€“4 finns.

Typer: `LegLabel`, `SwingLabel.all_legs()` i `src/fibengine/labeling/store.py`.

---

## 4. Golden set BTC (2026-05-29)

| Fil | InnehÃ¥ll |
|-----|----------|
| `data/labels/bitfinex/BTC-USD/1d.json` | Aktiv labels-yta pÃ¥ Bitfinex (nuvarande workflow) |
| *(legacy Bitfinex/BTC-USD labels removed in cleanup)* | Historisk referens finns i reflektioner/dokumentation |

**leg_1** matchar weekly-impuls (och fractal 1d-ankare 14 jan / 6 feb).  
**leg_20** (exempel): upp 20 apr â†’ 22 apr ~79.5k (golden-pocket-zon i research).  
Ordning i `legs[]` = sparningsordning, inte alltid kronologi.

---

## 5. KÃ¤nda begrÃ¤nsningar

1. **TV vs Bitfinex snap** â€” smÃ¥ prisskillnader â†’ fib-nivÃ¥er kan skilja mellan datakÃ¤llor.
2. **Auto-scan â‰  facit** â€” `mtf_leg_daily_fib` Ã¤r heuristik (touch/rejection), inte rejection/accept facit.
3. **Multi-leg ej i motor** â€” 30 legs Ã¤r research-data; experiment mÃ¤ter inte dem Ã¤n.
4. **ETH 1w fractal** â€” krÃ¤ver tillrÃ¤cklig **1d-cache** fÃ¶r label-Ã¥r (annars `unresolved`).
5. **`tool.py` stor** â€” fortfarande grandfather enfil (REPO_POLICY Â§2B).

---

## 6. NÃ¤sta fas (ej implementerat)

1. **Steg 3 (pÃ¥gÃ¥r, #12):** Hypothesis A â€” maskin-kandidater + bounded human review; schema v3 `events[]`. Se [RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md), [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md).
2. **Koppla multi-leg â†’ analys** â€” script som lÃ¤ser alla `legs` och jÃ¤mfÃ¶r med `mtf_leg_daily_fib`.
3. **Motorn** â€” endast efter facit; inte optimera mot labels.
4. Ev. **lÃ¤nka leg till parent** `1w` label-id / `htf_leg_ref`.

---

## 7. Kommandon (snabbreferens)

```powershell
# Labeling
uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1d --symbols BTC/USD

# MTF compare (weekly)
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USD --timeframe 1w --summary

# Daily fib scan mot weekly facit
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USD --timeframe 1w
```

Config (research):

```yaml
labeling:
  enable_same_candle_mtf_resolution: true
  mtf_disambiguation: false   # true endast vid medveten MTF-kÃ¶rning
```

