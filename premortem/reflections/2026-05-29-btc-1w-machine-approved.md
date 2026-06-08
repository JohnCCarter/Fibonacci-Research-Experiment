# 2026-05-29 BTC/USD 1w â€” godkÃ¤nd maskin-kandidat

Observation:
- FÃ¶rsta maskin-labeling (select_swing pÃ¥ weekly med warmup, ej strikt chartfÃ¶nster):
  high 2025-10-27 @ 116400, low 2026-02-02 @ 60000 â€” **godkÃ¤nd** som human-facit.
- Senare omkÃ¶rning med endpoints lÃ¥sta till chartfÃ¶nster 2026-03-23â€“2026-05-04 gav
  low 65000 / high 82850; TradingView pÃ¥ samma fÃ¶nster visade ~65019 / 82807 (vecko-OHLC vs exakt wick).

Beslut:
- `data/labels/Bitfinex/BTC-USD/1w.json` uppdaterad till godkÃ¤nd swing, `source=human`.
- ChartfÃ¶nster-specifik omkÃ¶rning Ã¤r **inte** facit; skillnad TV vs cache Ã¤r fÃ¶rvÃ¤ntad pÃ¥ veckonivÃ¥.

NÃ¤sta:
- Vid behov: finjustera pris i `labeling.tool` mot TV-wicks och spara igen.

AllmÃ¤n modell (bÃ¥da giltiga): `docs/labeling/MACHINE_LABELING.md`.

