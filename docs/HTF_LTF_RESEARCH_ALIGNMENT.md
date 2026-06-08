# HTF → LTF: jobba oss ner med fiben (research protocol)

**Status:** policy / facit-rutin (inte motor-promotion). Issue [#14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14) closed 2026-06-08 (minimal close).  
**Relaterat:** [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) (§0 — ursprung), [RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md), [MTF_FIB_LEVEL_PROJECTION.md](MTF_FIB_LEVEL_PROJECTION.md)

---

## Idén i en mening

Vi mäter **samma rörelse** top-down: först *var* stor swing och fib-grid (HTF), sedan *hur* priset beter sig vid nivåerna när vi zoomar in (LTF) — **inte** oberoende fibs per timeframe utan sammanhang.

| Kort | Betydelse |
|------|-----------|
| **VAD** | Weekly (1w): vilken impuls/range ska fib sitter på? |
| **HUR** | Daily (1d): hur rör sig priset i segment och vid nivåer? |
| **Neråt** | 4h → 1h: finare timing — se **två spår** nedan (facit vs projection) |

---

## Två spår — blanda inte ihop dem

### A. Facit chain (labeling / ground truth)

Facit-JSON och labeling-rutin. Detta är **källan till sanning** för vad som ritats och vad som hände.

```text
1w   VAD  — swing + fib-grid (facit-range, source-of-truth)
 ↓
1d   HUR  — multi-leg (`legs[]`) + behavior `events[]` vid nivåer
 ↓
4h   legs[] i samma `leg_id`-träd   →  DEFERRED (ej byggt)
 ↓
1h   inom valt 4h-segment            →  DEFERRED (ej byggt)
```

| TF | Facit-fil | Fib ankare | Beteende |
|----|-----------|------------|----------|
| **1w** | `{exchange}/…/1w.json` | Veckans H/L (facit-range) | — |
| **1d** | `…/1d.json` (`legs[]`) | **Egna** H/L per leg | `…/1d-behavior.json` (`events[]`) |
| **4h** | — | — | — |
| **1h** | — | — | — |

**Facit-regler (oförändrade):**

- **Weekly-grid ≠ daily-ankare:** daily-legs har egna endpoints; weekly ger **kontext**, inte copy-paste av H/L.
- **Same-candle 1w→1d:** `same_candle_mtf_resolution` — se [LABELING_TOOL.md](LABELING_TOOL.md) §3A.
- **Maskin:** `level_events` + human review = spot-check på **events**, inte mass-manuell labeling ([#12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)).
- **4h/1h facit:** `legs[]` i samma träd och **1d→4h disambiguation** är **inte** implementerat och **inte** planerat nu.

### B. MTF projection research (mätning, inte facit)

Separat research-runner: låsta **HTF human fib-nivåpriser** projiceras ned på **LTF-candles**; beteende mäts runt dessa priser. Detta **ersätter inte** 4h facit `legs[]`.

| Vad | Var |
|-----|-----|
| Runner | `fibengine.research.mtf_fib_level_projection` |
| Design + CLI | [MTF_FIB_LEVEL_PROJECTION.md](MTF_FIB_LEVEL_PROJECTION.md) |
| Checkpoint (1W→1D) | [wiki: MTF projection checkpoint](research_wiki/reviews/2026-06-05-mtf-fib-projection-checkpoint.md) |
| Clean-forward n≥20 read | [wiki: MTF clean-forward](research_wiki/reviews/2026-06-05-mtf-clean-forward-n20-review.md) |

**Implementerat och testat (research-only):**

- **1W → 1D** — end-to-end smoke (fingerprints + outcomes + toplist)
- **1W → 4H** — högre upplösning, ingen stabil evidens än
- **1D → 4H** — samma mönster

**Vad projection gör:** mäter candle-beteende (relation, fingerprint, forward outcome) vid **exakta HTF-nivåpriser** på lägre TF. Human fib förblir locked map; `auto_candidate` är aldrig facit. Ingen trading-logik, ingen edge-claim.

**Vad projection inte gör:** skapa 4h/1h `legs[]`, behavior-facit JSON, eller `leg_id`-träd under 1d.

---

## Beslut (2026-06-08, issue #14 close)

| Fråga | Beslut |
|-------|--------|
| 4h `legs[]` JSON i facit-trädet? | **Nej för nu** — deferred |
| 1d→4h disambiguation (som 1w→1d)? | **Nej för nu** — deferred |
| Aktiv LTF-research-väg? | **MTF projection** (spår B) |
| 1h projection / facit? | **Deferred** tills 4h clean-forward-sample är starkare |

Protokollet är **uppfyllt för 1w→1d facit-kedjan**. 4h/1h facit-expansion och 1h-projection öppnas via **nya scoped issues** om behov uppstår.

---

## Byggt vs plan (repo)

| Steg | Spår | Status |
|------|------|--------|
| 1w facit | A | ✅ labeling tool, `1w.json` |
| 1w → 1d ordning | A | ✅ `mtf_disambiguation`, `same_candle_mtf_resolution` |
| 1d multi-leg + events | A | ✅ `legs[]`, behavior facit v3 (PR #13) |
| 1d scan mot 1w grid | A | ✅ `mtf_leg_daily_fib.py` (heuristik, ej facit) |
| 4h / 1h facit `legs[]` | A | ❌ deferred |
| 1d→4h disambiguation | A | ❌ deferred |
| HTF fib → LTF candles | B | ✅ `mtf_fib_level_projection` (1W→1D, 1W→4H, 1D→4H) |

---

## Vanliga misstag

1. **Bara `s` på 1d** utan flera legs → overwrite (löst med `p` / auto-append) — se [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) §0A.
2. **Rita 1d-fib på weekly-priser** som om det vore samma leg.
3. **Börja på 1h** och tro att det är samma facit som weekly-impulsen.
4. **Auto-scan = facit** — `mtf_leg_daily_fib` och `auto_candidate` är förslag.
5. **MTF projection = facit** — projection mäter beteende; den skapar inte 4h `legs[]` eller ersätter human labels.

---

## Nästa (efter #14)

1. Fortsätt **MTF projection** på clean-forward-kohort (anchor_b ≥ `history_start`); håll cross-era separat.
2. Väx per-symbol clean-forward N på 4h innan 1h öppnas.
3. Nytt issue endast om facit-behov för 4h `legs[]` eller 1d→4h disambiguation återuppstår.
