# 2026-05-29 — MTF + daily fib research (weekly VAD / daily HUR)

**Typ:** decision + run  
**Taggar:** labeling, MTF, 1w, 1d, fib, research

## Varför det strulade från början

1. **Labeling tool:** En swing per `1d.json` — varje `s` skrev över förra fib. Du ritade ned + upp i UI; repot såg bara sista paret. Inte TV-problem — **persistens-design**.
2. **Första multi-leg-fix räckte inte:** `a` fanns men `s` uppdaterade fortfarande aktiv leg om man inte tryckte `a`; terminalen visade inte tydligt flera legs.
3. **MTF “fel” mot TV:** Ofta olika ankare + vi mäter steg 1–2 (swing/nivå), inte steg 3–4 (reaktion vid 0.618). Inte samma som overwrite-buggen.

## Hur vi löste det

| Problem | Lösning |
|---------|---------|
| Flera daily-fibs försvinner | `LegLabel` + `"legs"` i JSON; `p` push; `s` auto-appendar ny leg om endpoints skiljer sig |
| Svårt att se att det fungerar | `Saved N legs`, startup-hjälp, alla legs synliga i chart |
| Same-candle 1w | `same_candle_mtf_resolution` + MTF Disambiguation (research flag) |
| Olika veckor 1w | Fraktal: daily extreme per endpoint-vecka |

## Beslut

1. **Weekly** förblir HTF-facit (*vilken* swing, vilken range).
2. **Daily** är *hur* priset rör sig — **flera fib-legs** per fil, inte overwrite.
3. **Fas 3:** research-fynd — [fib-multi-behavior-per-level](2026-05-29-fib-multi-behavior-per-level.md); schema v3 `events[]`. Ingen motor.
4. `mtf_disambiguation` och `mtf_leg_daily_fib` förblir **research OFF by default** i prod-spår.

## Vad som byggdes denna dag

| Del | Var |
|-----|-----|
| Fraktal MTF (olika veckor → 1d per endpoint) | `mtf_disambiguation.py` |
| Daily touch/rejection-scan | `mtf_leg_research.py`, `scripts/mtf_leg_daily_fib.py` |
| Multi-leg save (`p`, auto-append på `s`) | `store.py` (`LegLabel`), `tool.py` |
| Dokumentation | `docs/MTF_DAILY_RESEARCH.md`, `LABELING_TOOL.md` §3A–3D, §5B |

## Golden set

- **BTC 1w:** 97 924 → 60 000 (oförändrat HTF).
- **BTC 1d:** 30 legs i `data/labels/binance/BTC-USDT/1d.json` (2026-05-29T11:25) — första fulla daily-HUR-facit.

## Lärdom (flaskhals)

> Motorn räknar fib. Människan läser **reaktion** vid 0.382 / 0.5 / 0.618.  
> Det är **inte** samma problem. Facit för reaktion ligger nu i **research** (`human_label`), inte i motorn.

## Ej gjort / medvetet skjutet

- Fas 5 `report` (agreement auto vs human) — nästa rena steg, ingen kod än.
- Fas 4 heuristik-förbättring — efter report.
- Motor eller experiment som läser `legs[]` eller behavior-JSON.
- `role` / `note` per leg i labeling tool.

**Djupare guide:** [docs/MTF_DAILY_RESEARCH.md](../../docs/MTF_DAILY_RESEARCH.md)
