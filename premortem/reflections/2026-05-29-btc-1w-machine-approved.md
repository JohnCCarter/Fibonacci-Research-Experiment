# 2026-05-29 BTC/USDT 1w — godkänd maskin-kandidat

Observation:
- Första maskin-labeling (select_swing på weekly med warmup, ej strikt chartfönster):
  high 2025-10-27 @ 116400, low 2026-02-02 @ 60000 — **godkänd** som human-facit.
- Senare omkörning med endpoints låsta till chartfönster 2026-03-23–2026-05-04 gav
  low 65000 / high 82850; TradingView på samma fönster visade ~65019 / 82807 (vecko-OHLC vs exakt wick).

Beslut:
- `data/labels/binance/BTC-USDT/1w.json` uppdaterad till godkänd swing, `source=human`.
- Chartfönster-specifik omkörning är **inte** facit; skillnad TV vs cache är förväntad på veckonivå.

Nästa:
- Vid behov: finjustera pris i `labeling.tool` mot TV-wicks och spara igen.

Allmän modell (båda giltiga): `docs/MACHINE_LABELING.md`.
