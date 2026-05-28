# 2026-05-28 Labeling-worklist (täckning mot facit-målet)

Uppföljning på premortem-mitigeringarna: den kvarstående åtgärdspunkten "utöka
labelkorpusen till 20–30 setups" kräver mänsklig chart-läsning. För att göra den
tractable lade jag till en täcknings-worklist i stället för att fabricera facit.

Hypotes:
- Om gapen mot facit-målet är osynliga blir korpusen aldrig utökad. Gör gapen och
  nästa-steg-kommandona explicita → lättare att faktiskt labela.

Scope:
- Delsystem: `labeling/` (diagnostik, ingen ändring av tool-interaktionen).
- Ingen nät/GUI i tester (worklist läser sparade JSON-labels).

Observationer:
- `labeling/tool.py` var redan välutrustat (CLI `--exchange/--symbol/--timeframe`,
  kö över symbol×timeframe, 'n' = nästa olabelade). Det som saknades var att *veta
  vad* som återstår.
- Ny `labeling/worklist.py`: `coverage_report()` + `format_report()` jämför sparade
  labels mot en target-matris (default BTC/ETH/SOL × 7 TF = 21 kombinationer) och
  mot `LABEL_TARGET = 25`, och skriver ut färdiga `labeling.tool`-kommandon för det
  som saknas.
- Körning nu: **15/25 labels, 15/21 kombinationer täckta.** Saknas: BTC 30m, ETH 1h,
  SOL 4h/1d/1w/1M.
- Tester: 74 → 78 gröna; coverage ~76%; lint rent.

Beslut:
- Worklist är ren diagnostik/Research — den genererar inga labels, bara nästa-steg.
- Facit ritas alltid manuellt via `labeling.tool` (referens, inte domare).

Nästa steg (människa):
- Labela de 6 saknade kombinationerna (kommandona finns i worklist-utskriften) tills
  ≥ 20–30 setups. Kör därefter `pivot_recall` + `matrix` och kalibrera `gate_*`.
