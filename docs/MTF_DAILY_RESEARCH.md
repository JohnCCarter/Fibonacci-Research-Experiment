# MTF + daily fib research (2026-05-29)

Sammanfattning av forskningsriktningen: **weekly = VAD**, **daily = HUR**.  
Detta dokument är källan för vad som är byggt, vad som saknas, och hur det hänger ihop.

Relaterat:

- **[RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md)** — aktiv scope + [GitHub #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12) (Hypothesis A: maskin → spot-check)
- [LABELING_TOOL.md](LABELING_TOOL.md) — verktyg, tangenter, begränsningar
- [MACHINE_LABELING.md](MACHINE_LABELING.md) — motor-swing vs chartfönster
- `config/settings.yaml` — `labeling.*` flags

---

## 0. Varför det inte gick från början — och hur vi löste det

### A. Flera fibs på daily syntes inte i repot (labeling tool)

**Vad du gjorde (korrekt i UI):**  
Rita fib för **nedgång**, sedan fib för **uppgång** (och fler segment) i labeling tool på 1d — samma symbol/TF.

**Vad som hände på disk:**  
Varje **`s`** skrev om **samma fil** (`binance/BTC-USDT/1d.json`) med **ett** par `high` + `low`. Förra leg försvann. I JSON fanns bara **sista** paret (t.ex. maj-pullback 82k→79k), inte jan–apr-kedjan du ritat.

**Varför (design från start):**  
Golden set var modellerat som **en swing per symbol + timeframe** — som weekly. Verktyget kunde visa fib på skärmen (`g`), men **persistens** = en `SwingLabel`, inte en lista. Inget fel i din metod; **schemat matchade inte** “daily = många HUR-legs”.

**Symptom vi såg:**  
- Du: “jag ritade flera fibs”  
- Granskning: bara en leg i filen  
- Risk för missförstånd (“bilder?”) — det var **JSON-overwrite**, inte TV

**Första försök (ofullständigt):**  
Multi-leg i kod + tangent **`a`** (append leg). Funkade i teorin, men:

1. Många tryckte bara **`s`** igen (vana) → fortfarande en leg, eller overwrite av aktiv leg i sessionen.  
2. Terminalen sa `Saved label` — inte `Saved 2 legs` / `Stored leg_2` → svårt att se att multi-leg aktiverades.  
3. **`s` utan `a`:** om du redan hade leg_1 laddad och satte nya endpoints uppdaterades **leg_1** i stället för att leg_2 lades till.

**Lösning (nu):**

| Del | Ändring |
|-----|---------|
| **Schema** | `LegLabel` + `"legs": [...]` i JSON när ≥2 legs (`store.py`) |
| **Tangent `p`** | Push leg explicit (alias `a`) |
| **Smart `s`** | Om nya picks **inte** matchar aktiv legs barer → **ny leg appendas automatiskt**, sedan sparas alla |
| **UI** | Alla legs ritas (svagare inaktiva); titel visar `legs=N` |
| **Startup** | Rad i terminal: multi-leg-instruktion |
| **Bekräftelse** | `Saved 2 legs -> ...` och `"legs": [` i filen |

**Resultat:** BTC `1d.json` med **30 legs** (2026-05-29T11:25) — första riktiga daily-HUR-facit.

**Workflow nu:**

1. H+L → **`p`** (eller H+L → **`s`** → H+L → **`s`** med auto-append)  
2. Upprepa för fler segment  
3. Sista **`s`** → alla legs till disk  

---

### B. “MTF / fib stämmer inte mot TV” (annat problem)

**Vad det såg ut som:**  
Weekly-facit OK, men 0.618 på daily i auto-scan (~83k) vs ~81k på TV — “motorn failar”.

**Varför det inte var samma bugg:**  
- **Olika ankare** (Binance snap 60 000 vs TV 60 091) → annan fib-grid.  
- **Halva pipelinen:** MTF Disambiguation ger **ordning + tid** (1d-dagar inom veckor), inte **reaktion vid nivå**.  
- `mtf_leg_daily_fib` är **heuristik** (touch/rejection), inte ditt facit för accept/reject/in–ut.

**Lösning (begreppsmässig, inte en knapp):**  
Separera steg 1–2 (swing + nivåer) från steg 3–4 (beteende + beslut). Daily multi-leg **är** steg 3-facit under uppbyggnad; motor ska inte “gissa” steg 4 utan labels.

---

### C. Same-candle weekly (tidigare delproblem)

**Problem:** H+L på **samma** 1w-candle → verktyget vägrade spara (regel för distinct endpoints).

**Lösning:** `same_candle_mtf_resolution` vid save (1D max-high / min-low-dag i veckan) + MTF Disambiguation i motor när flagga ON. HTF-priser oförändrade.

**Fraktal (senare):** H+L på **olika** veckor → två veckofönster på 1D (en gång per endpoint), samma princip.

---

## 1. Mental modell (facit, inte motor-sanning)

| Lager | Tidsram | Fråga | Exempel BTC |
|-------|---------|-------|-------------|
| **HTF** | 1w | Vilken **stor swing** ska mätas? | 97 924 → 60 000 |
| **LTF** | 1d | **Hur** rörde sig priset (del-legs, nivåer, reaktioner)? | 30 fib-segment jan–maj 2026 |

- Weekly-priser = **facit-range** (snap till veckans H/L i labeling tool).
- Daily = **egna legs** inuti/efter samma berättelse — inte samma endpoints som weekly.
- Fib på daily ritas på **varje legs** egna ankare, inte automatiskt weekly-grid.

**Formulering vi använder:** motorn hittar fib-nivåer; den har **ännu inte facit** för *mänskligt beteende vid* nivåerna (reject / accept / failure / in–ut).

---

## 2. Fyra steg (research-roadmap)

| Steg | Innehåll | Repo-status |
|------|----------|-------------|
| **1** | Vilken swing? | ✅ weekly labels + motor-swing |
| **2** | Vilka fib-nivåer? | ✅ `fib_from_prices`, verktyg `g` |
| **3** | Beteende vid nivå? | ⚠️ human facit (events); heuristik `annotate` / `mtf_leg_daily_fib` |
| **4** | Mänskligt beslut (in/ut) | ❌ ej kopplat till motor än |

**Fas 3 (research finding, 2026-05-29):**  
Samma fib-nivå (särskilt från **weekly grid**) kan ge **flera beteenden över tid** på daily — t.ex. `rejection` vid en touch och `continuation` vid en senare.  
→ Modell: **events[]** per nivå, inte ett enda label. Se [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md), [premortem finding](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md).

- **Weekly / HTF leg** = grid (`derived_prices`)  
- **Daily** = `events[]` med `event_bar` + `human_label`  
- Fil: `data/labels/research/.../1d-behavior.json` (tmp-sandbox: `research/tmp/`)  
- **Ingen motor, ingen promotion**

**Workflow (2026-05-31, #12):** maskin föreslår events → människa **spot-checkar** 20–40 st. Tmp/manual JSON = pilot för `events[]`, inte huvudspår.

---

## 3. Kod: tre lager + multi-leg save

### 3A. Same-candle MTF (verktyg → JSON)

När **H+L på samma 1w-bar** men olika **1d-dagar**:

- `labeling.enable_same_candle_mtf_resolution: true`
- Sparas som `same_candle_mtf_resolution` på label (eller på leg).
- Weekly H/L-priser ändras **inte**.

### 3B. MTF Disambiguation Layer (motor, research)

- `labeling.mtf_disambiguation: false` (default) / `true` (research)
- **1w → 1d:** ordning + tid; HTF-priser oförändrade.
- **Samma vecka:** sparad metadata eller härled max-high / min-low-dag i veckan.
- **Olika veckor (fraktal):** varje endpoint → daily extreme i **sin** vecka (`fractal_endpoints`).
- Övriga TF: ingen effekt (fallback som OFF).
- Same-candle utan metadata + OFF → mjukt skip (`skipped_mtf`).

```bash
uv run python scripts/compare_mtf_disambiguation.py --summary
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USDT --timeframe 1w
```

### 3C. Daily fib inom HTF-leg (beskrivande scan)

- Modul: `src/fibengine/labeling/mtf_leg_research.py`
- Script: `scripts/mtf_leg_daily_fib.py`
- HTF-range från weekly-facit; skannar 1d för touch/rejection vid 0.382 / 0.5 / 0.618 (impulse + retrace).
- **Inte** samma som TV-manuell tolkning; ankare kan skilja något i pris.

```bash
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USDT --timeframe 1w
uv run python scripts/mtf_leg_daily_fib.py --all-1w
```

### 3D. Multi-leg save (labeling tool)

Se **§0A** för full historia (varför / hur). Kort: en `s` = en fil med ett par H+L → overwrite; nu `legs[]` + `p` + smart `s`.

**Nu:**

| Tangent | Funktion |
|---------|----------|
| `p` / `a` | Push: spara nuvarande H+L som ny leg i sessionen |
| `j` / `k` | Byt aktiv leg |
| `s` | Spara **alla** legs; om nya picks ≠ aktiv leg → **auto-ny leg** |

JSON med 2+ legs:

```json
{
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "timeframe": "1d",
  "high": { "...": "leg_1 high (bakåtkompat)" },
  "low": { "...": "leg_1 low" },
  "legs": [
    { "id": "leg_1", "high": { ... }, "low": { ... } },
    { "id": "leg_2", "high": { ... }, "low": { ... } }
  ],
  "source": "human"
}
```

- **En leg:** gammalt format (utan `legs`-array).
- **Motor / recall / agreement:** använder fortfarande top-level `high`/`low` (= leg_1) tills steg 3–4 finns.

Typer: `LegLabel`, `SwingLabel.all_legs()` i `src/fibengine/labeling/store.py`.

---

## 4. Golden set BTC (2026-05-29)

| Fil | Innehåll |
|-----|----------|
| `data/labels/binance/BTC-USDT/1w.json` | HTF leg 97 924 (12 jan) → 60 000 (2 feb) |
| `data/labels/binance/BTC-USDT/1d.json` | **30 legs** (`leg_1` … `leg_30`), sparad 11:25 — kedja ned + retracement + jan-segment |

**leg_1** matchar weekly-impuls (och fractal 1d-ankare 14 jan / 6 feb).  
**leg_20** (exempel): upp 20 apr → 22 apr ~79.5k (golden-pocket-zon i research).  
Ordning i `legs[]` = sparningsordning, inte alltid kronologi.

---

## 5. Kända begränsningar

1. **TV vs Binance snap** — små prisskillnader → fib-nivåer kan skilja (t.ex. 0.618 ~81k vs ~83k).
2. **Auto-scan ≠ facit** — `mtf_leg_daily_fib` är heuristik (touch/rejection), inte rejection/accept facit.
3. **Multi-leg ej i motor** — 30 legs är research-data; experiment mäter inte dem än.
4. **ETH 1w fractal** — kräver tillräcklig **1d-cache** för label-år (annars `unresolved`).
5. **`tool.py` stor** — fortfarande grandfather enfil (REPO_POLICY §2B).

---

## 6. Nästa fas (ej implementerat)

1. **Steg 3 (pågår, #12):** Hypothesis A — maskin-kandidater + bounded human review; schema v3 `events[]`. Se [RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md), [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md).
2. **Koppla multi-leg → analys** — script som läser alla `legs` och jämför med `mtf_leg_daily_fib`.
3. **Motorn** — endast efter facit; inte optimera mot labels.
4. Ev. **länka leg till parent** `1w` label-id / `htf_leg_ref`.

---

## 7. Kommandon (snabbreferens)

```powershell
# Labeling
uv run python -m fibengine.labeling.tool --symbol BTC/USDT --timeframe 1d --symbols BTC/USDT

# MTF compare (weekly)
uv run python scripts/compare_mtf_disambiguation.py --symbol BTC/USDT --timeframe 1w --summary

# Daily fib scan mot weekly facit
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USDT --timeframe 1w
```

Config (research):

```yaml
labeling:
  enable_same_candle_mtf_resolution: true
  mtf_disambiguation: false   # true endast vid medveten MTF-körning
```
