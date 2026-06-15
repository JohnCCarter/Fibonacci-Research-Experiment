---
type: decision
topics: [MTF, confluence, genesis-v2, governance, leakage]
related: [docs/research_wiki/reviews/btc-mtf-confluence-interpretation-decision-20260615.md, docs/research_wiki/reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md]
status: active
---

# 2026-06-15 — MTF-confluence stängd + Genesis V2-gate

**Typ:** decision (finding + governance) · **Taggar:** MTF, confluence, genesis-v2, governance
Stänger MTF-confluence-spåret och registrerar Fib → Genesis V2 Phase 0/1.

## Hypotes (testad)

- Multi-timeframe Fib-**confluence** (samma nivå över 1M/1w/1d/4h) skulle kunna vara edge.

## Scope

- BTC/USD, låst korpus (462 fibs). Read-only research, inga charts som signal, inga trades.

## Observationer

1. **CP1** — 222 cross-TF-kluster @ε_log=0.005 (188 fixed-band). **CP2** — ε-sensitivitet:
   `c001` robust tight 4-TF (span 0.00123 ≤ ε); `c002` chaining-dependent (span 0.00627 > ε,
   löses upp under fixed-band); chaining 14%→26%. **CP3** — 5 kort, 3 arketyper, **alla
   human-approved 2026-06-15**.
2. **Fynd:** MTF-confluence finns som **geometri, inte edge** — c001 visar att tight metod-stabil
   confluence kan finnas, c002 att single-linkage kan överdriva styrka, zero-span att exakt
   pris-sammanfall finns; **inget** bevisar stöd/motstånd eller prediktivt värde.

## Beslut

1. **STOPP för MTF-spåret** — ingen kortexpansion eller beteendestudie utan en pre-registrerad
   falsifierbar fråga + naiv-nivå-baseline.
2. **Phase 0** (prereg, docs-only): en falsifierbar beteendefråga (reaktion vid kausala
   confluence-zoner vs placebo/naiva nivåer, OOS); anchor-recognition avvisad som
   **selection leakage**; kausal feature-regel; ≥3 baselines.
3. **Phase 1** (feature-export-spec, docs-only): **PASS / stängd som kontrakt** — zon-registry +
   bar-feature-tabell, bindande `known_after_ts = max(anchor_b)+buffer` + per-rad
   `known_after_ts ≤ timestamp`, 9 kausala invarianter, do-not-export-lista.
4. **Phase 2 (dummy-file-test) kräver explicit GO** — bygger inget innan dess.

## Risk / öppen fråga

- Den enda risk specen **inte** kan lösa på papper: är kausala features **non-empty** i praktiken
  (Phase 0 §8 stop)? Empiriskt — tillhör Phase 2.

## Nästa steg

- Fork (ej startad): **pausa Fib**, eller Phase 2 efter **explicit GO**. Ingen kod, ingen
  Genesis-touch, ingen ETH före BTC-sign-off.

## Referenser

- [MTF tolknings- & beslutsnota](../../docs/research_wiki/reviews/btc-mtf-confluence-interpretation-decision-20260615.md)
- [Phase 0 prereg](../../docs/research_wiki/reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md) ·
  [Phase 1 spec](../../docs/research_wiki/reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md)
