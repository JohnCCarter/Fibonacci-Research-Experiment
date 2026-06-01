# HTF → LTF: jobba oss ner med fiben (research protocol)

**Status:** policy / facit-rutin (inte motor-promotion).  
**Relaterat:** [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md), [RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md), [GitHub #14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14)

---

## Idén i en mening

Vi mäter **samma rörelse** top-down: först *var* stor swing och fib-grid (HTF), sedan *hur* priset beter sig vid nivåerna när vi zoomar in (LTF) — **inte** oberoende fibs per timeframe utan sammanhang.

| Kort | Betydelse |
|------|-----------|
| **VAD** | Weekly (1w): vilken impuls/range ska fib sitter på? |
| **HUR** | Daily (1d): hur rör sig priset i segment och vid nivåer? |
| **Neråt** | 4h → 1h (plan): samma berättelse, finare timing — **ej i motor än** |

---

## Rekommenderad ordning (facit)

```text
1w   range + fib-grid (HTF facit)
 ↓
1d   flera legs (HUR) + events vid nivåer (behavior facit)
 ↓
4h   (plan) legs / reaktioner inom redan valt 1d-segment
 ↓
1h   (plan) execution-timing — sista steget, inte först
```

**15m / 30m:** valfritt senare; används i validate-matris, inte i denna research-kedja än.

---

## Vad som gäller per steg

| TF | Facit-fil | Fib ankare | Beteende |
|----|-----------|------------|----------|
| **1w** | `{exchange}/…/1w.json` | Veckans H/L (facit-range) | — |
| **1d** | `…/1d.json` (`legs[]`) | **Egna** H/L per leg | `…/1d-behavior.json` (`events[]`) |
| **4h** | (plan) | Inom valt 1d-leg | (plan) |
| **1h** | (plan) | Inom valt 4h-segment | (plan) |

- **Weekly-grid ≠ daily-ankare:** daily-legs har egna endpoints; weekly ger **kontext**, inte copy-paste av H/L.
- **Same-candle 1w:** spara med `same_candle_mtf_resolution` (1d-dagar inom veckan) — se [LABELING_TOOL.md](LABELING_TOOL.md) §3A.
- **Maskin:** `level_events` + human review = spot-check på **events**, inte mass-manuell labeling ([#12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)).

---

## Byggt vs plan (repo)

| Steg | Dokumentation / kod |
|------|---------------------|
| 1w facit | ✅ labeling tool, `1w.json` |
| 1w → 1d ordning | ✅ `mtf_disambiguation`, `same_candle_mtf_resolution` |
| 1d multi-leg + events | ✅ `legs[]`, behavior facit v3, PR #13 |
| 1d scan mot 1w grid | ✅ `mtf_leg_daily_fib.py` (heuristik) |
| 4h / 1h i kedjan | ❌ policy only — inga scripts, ingen motor |

---

## Vanliga misstag

1. **Bara `s` på 1d** utan flera legs → overwrite (löst med `p` / auto-append) — se [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) §0A.
2. **Rita 1d-fib på weekly-priser** som om det vore samma leg.
3. **Börja på 1h** och tro att det är samma facit som weekly-impulsen.
4. **Auto-scan = facit** — `mtf_leg_daily_fib` och `auto_candidate` är förslag.

---

## Nästa (efter Hypothesis A spot-check)

1. Bounded review 20–40 events på 1d (PR #9/#11).
2. Beslut: behöver vi 4h-legs i JSON för samma `leg_id`-träd?
3. Ev. issue för 1d→4h disambiguation (samma mönster som 1w→1d).
