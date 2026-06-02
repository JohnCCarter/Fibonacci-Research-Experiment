# 2026-06-02 — MTF-ursprung: samma H/L på 1w och 1d

**Typ:** finding (chart observation)  
**Taggar:** MTF, 1w, 1d, labeling, fib, origin

## Hypotes

- **Weekly** svarar på *vilken* stor swing och *vilken* fib-range som är relevant (VAD).
- **Daily** med **samma** H/L-priser / samma fib-grid svarar på *hur* priset rör sig vid nivåerna (HUR) — med fler candles syns **fler** nivåinteraktioner än på 1w ensam.

## Scope

- Exchange: Bitfinex (senare BTC/ETH/SOL i korpus)
- Start-TF: **1w** (H→L, fib på range)
- Zoom: **1d** med samma facit-range i labeling tool
- Data: manuell chart-läsning, inte motor/experiment

## Observationer

1. På **1w** såg vi att candles **ibland** når vissa fib-nivåer (0.382, 0.5, 0.618, …) — användbart men grovt (få bars).
2. När vi lade **samma H och L** (samma range, samma grid) på **1d** syntes **plötsligt fler** tillfällen där priset touch:ar, korsar eller reagerar vid nivåerna.
3. Det förklarar varför projektet inte stannade på “en swing per TF”: daily behöver **egen upplösning** (legs, events, human-fib), inte bara en kopia av weekly-endpoints.
4. Same-candle weekly (H+L på samma vecka) är ett **separat** tekniskt problem (1d-dagar inom veckan) — se `same_candle_mtf_resolution` i labeling tool.

## Beslut

1. Dokumentera ursprunget som **§0** i [MTF_DAILY_RESEARCH.md](../../docs/MTF_DAILY_RESEARCH.md) och i [RESEARCH_HANDOFF.md](../../docs/RESEARCH_HANDOFF.md).
2. Hålla fast vid **weekly = VAD**, **daily = HUR** i all facit-design (se även [HTF_LTF_RESEARCH_ALIGNMENT.md](../../docs/HTF_LTF_RESEARCH_ALIGNMENT.md)).
3. Räkna inte `experiment` (en motor-swing vs leg_1) som validering av denna insikt.

## Nästa steg

- Fortsätt human-fib + `*_events.json` på 1d som research-spår (Hypothesis A / spot-check).
- Vid behov: bounded review av kandidat-events mot chart, inte mass-hand-label utan maskinförslag först.

## Referenser

- [MTF_DAILY_RESEARCH.md](../../docs/MTF_DAILY_RESEARCH.md) §0
- [2026-05-29-mtf-daily-fib-research](2026-05-29-mtf-daily-fib-research.md) — multi-leg, overwrite-fix, teknisk uppföljning
