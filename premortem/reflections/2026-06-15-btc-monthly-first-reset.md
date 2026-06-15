---
type: decision
topics: [process, reset, BTC, protocol, corpus]
related: [docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md, docs/research_wiki/reviews/btc-source-fib-corpus-integrity-20260615.md]
supersedes: 2026-06-02-mtf-origin-1w-to-1d
status: active
---

# 2026-06-15 — Research reset: BTC monthly-first-protokoll

**Typ:** decision (scope/process) · **Taggar:** reset, BTC, protocol, corpus
Retroaktiv reflektion för 2026-06-08/06-09-besluten (reflektionsplikt §11).

## Hypotes / motiv

- Mixed-symbol + pre-monthly-spåret (BTC/ETH/SOL, lösa 1w→1d-fynd) gav **tunn evidens**:
  generalisering hävdad från en mager matris (jfr [PREMORTEM.md](../PREMORTEM.md) "tunn matris").
- Disciplinerad **top-down BTC-first** (1M→1w→1d→4h→1h) ger ett kontrollerat facit innan
  bredd, istället för aggregat som döljer svaga rader.

## Scope

- Endast **BTC/USD** tills monthly→weekly→daily är godkänt; ETH/SOL pausade.
- Exchange Bitfinex; facit-källa `tradingview_log_chamoun`.

## Observationer

1. **2026-06-08** — 480 genererade filer arkiverade till
   `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`; **kod, tester, facit behållna**.
2. **2026-06-09** — facit-konvention bytt: **log-scale** (`scale_mode: log`), golden-zone
   `[0.5, 0.618]` leder sampling, nivåstege `[0, 0.382, 0.5, 0.618, 0.786, 1]` — **ingen 0.236**.
3. **2026-06-15** — korpus byggd och **låst**: 1M=9, 1w=21, 1d=67, 4h=365 aktiv (366 ritade,
   1 superseded) = **462**; coverage 2017-01-05 → 2026-06-05. Korpus förklarad ren.
4. **Arkivblobs committas inte** (layout-policy §7) — bara stubs/manifest; facit ligger i
   `data/labels/human_fib/.../fib_*.json`.

## Beslut

1. **Human fib = facit**; `*_candidate` ≠ facit; ingen auto-fib som sanning.
2. Äldre mixed-symbol/MTF-resultat = `archive/`, **inte** aktuell evidens (gör därför
   [2026-06-02 mtf-origin](2026-06-02-mtf-origin-1w-to-1d.md) `historical`).
3. Ingen ETH-promotion före BTC monthly→daily-sign-off.

## Nästa steg

- MTF-confluence-atlas på den låsta korpusen → se
  [2026-06-15 MTF-close + Genesis V2-gate](2026-06-15-mtf-confluence-genesis-v2-gate.md).

## Referenser

- [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [log-archive part 3 (2026-06-08/09)](../../docs/research_wiki/log-archive-pre-btc-reset-part3.md)
- [Korpus-integritet (capstone)](../../docs/research_wiki/reviews/btc-source-fib-corpus-integrity-20260615.md)
