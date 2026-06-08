# 2026-05-29 â€” MTF + daily fib research (weekly VAD / daily HUR)

**Typ:** decision + run  
**Taggar:** labeling, MTF, 1w, 1d, fib, research

## VarfÃ¶r det strulade frÃ¥n bÃ¶rjan

1. **Labeling tool:** En swing per `1d.json` â€” varje `s` skrev Ã¶ver fÃ¶rra fib. Du ritade ned + upp i UI; repot sÃ¥g bara sista paret. Inte TV-problem â€” **persistens-design**.
2. **FÃ¶rsta multi-leg-fix rÃ¤ckte inte:** `a` fanns men `s` uppdaterade fortfarande aktiv leg om man inte tryckte `a`; terminalen visade inte tydligt flera legs.
3. **MTF â€œfelâ€ mot TV:** Ofta olika ankare + vi mÃ¤ter steg 1â€“2 (swing/nivÃ¥), inte steg 3â€“4 (reaktion vid 0.618). Inte samma som overwrite-buggen.

## Hur vi lÃ¶ste det

| Problem | LÃ¶sning |
|---------|---------|
| Flera daily-fibs fÃ¶rsvinner | `LegLabel` + `"legs"` i JSON; `p` push; `s` auto-appendar ny leg om endpoints skiljer sig |
| SvÃ¥rt att se att det fungerar | `Saved N legs`, startup-hjÃ¤lp, alla legs synliga i chart |
| Same-candle 1w | `same_candle_mtf_resolution` + MTF Disambiguation (research flag) |
| Olika veckor 1w | Fraktal: daily extreme per endpoint-vecka |

## Beslut

1. **Weekly** fÃ¶rblir HTF-facit (*vilken* swing, vilken range).
2. **Daily** Ã¤r *hur* priset rÃ¶r sig â€” **flera fib-legs** per fil, inte overwrite.
3. **Fas 3:** research-fynd â€” [fib-multi-behavior-per-level](2026-05-29-fib-multi-behavior-per-level.md); schema v3 `events[]`. Ingen motor.
4. `mtf_disambiguation` och `mtf_leg_daily_fib` fÃ¶rblir **research OFF by default** i prod-spÃ¥r.

## Vad som byggdes denna dag

| Del | Var |
|-----|-----|
| Fraktal MTF (olika veckor â†’ 1d per endpoint) | `mtf_disambiguation.py` |
| Daily touch/rejection-scan | `mtf_leg_research.py`, `scripts/mtf_leg_daily_fib.py` |
| Multi-leg save (`p`, auto-append pÃ¥ `s`) | `store.py` (`LegLabel`), `tool.py` |
| Dokumentation | `docs/MTF_DAILY_RESEARCH.md`, `LABELING_TOOL.md` Â§3Aâ€“3D, Â§5B |

## Golden set

- **BTC 1w:** 97â€¯924 â†’ 60â€¯000 (ofÃ¶rÃ¤ndrat HTF).
- **BTC 1d:** 30 legs i `data/labels/Bitfinex/BTC-USD/1d.json` (2026-05-29T11:25) â€” fÃ¶rsta fulla daily-HUR-facit.

## LÃ¤rdom (flaskhals)

> Motorn rÃ¤knar fib. MÃ¤nniskan lÃ¤ser **reaktion** vid 0.382 / 0.5 / 0.618.  
> Det Ã¤r **inte** samma problem. Facit fÃ¶r reaktion ligger nu i **research** (`human_label`), inte i motorn.

## Ej gjort / medvetet skjutet

- Fas 5 `report` (agreement auto vs human) â€” nÃ¤sta rena steg, ingen kod Ã¤n.
- Fas 4 heuristik-fÃ¶rbÃ¤ttring â€” efter report.
- Motor eller experiment som lÃ¤ser `legs[]` eller behavior-JSON.
- `role` / `note` per leg i labeling tool.

**Djupare guide:** [docs/MTF_DAILY_RESEARCH.md](../../docs/MTF_DAILY_RESEARCH.md)

