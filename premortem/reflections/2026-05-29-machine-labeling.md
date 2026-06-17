# 2026-05-29 Maskin-labeling (kandidater, inte facit)

Uppföljning: jag avböjde att generera facit (cirkulärt — maskinen skulle valideras
mot sin egen output). Kompromissen blev maskin-labeling med tydlig `source`-stämpel
och hårda integritetsregler, så kandidater kan sänka tröskeln utan att bli domare.

Hypotes:
- Provisoriska maskin-kandidater gör det billigare för en människa att fylla
  facit-gapen — UTAN att korrumpera golden set — om de (a) är tydligt märkta,
  (b) exkluderas från all label-baserad evaluering, och (c) aldrig skriver över
  mänskligt facit.

Scope:
- Delsystem: `labeling/` (ny `autolabel.py`, `source` i `store.py`, worklist-split),
  `evaluation/pivot_recall.py` + `experiment.py` (exkludering).
- Ingen nät/GUI i tester (syntetiska data + mockad `select_swing`/`load_candles`).

Observationer:
- `SwingLabel.source` ("human"/"machine"), default "human" → befintliga JSON-labels
  förblir human. `list_labels(source=...)` filtrerar.
- `pivot_recall` och `experiment` evaluerar nu **bara** `source="human"`; antal
  hoppade maskin-labels loggas. Test låser exkluderingen.
- `autolabel.py` bygger kandidat från motorns `select_swing`, märker `source="machine"`
  + not, och **vägrar** skriva över en mänsklig label (`status="skipped_human"`).
- `worklist`: bara human räknas mot målet; maskin-kandidater listas separat som
  "att granska". Nuläge oförändrat: 15/25 human, 6 helt olabelade.
- Befordran: öppnas kandidaten i `labeling.tool` och sparas → `source="human"`
  (verktygets save bygger en label utan source = default human).
- Tester: 78 → 85 gröna; coverage ~76%; lint rent.

Beslut:
- Maskin-labels är scaffolding/Research, aldrig facit eller optimeringsmål. Den
  uttalade filosofin ("labels = referens, inte domare") står kvar oförändrad.

Nästa steg (kräver nät/människa):
- Kör `autolabel` på de 6 saknade kombinationerna när nät finns; granska var och en
  i `labeling.tool` och befordra de rimliga till human.
- Kör därefter `pivot_recall` + `matrix` och kalibrera `gate_*`.

Uppföljning 2026-05-29 (BTC 1w): se `docs/labeling/MACHINE_LABELING.md` och
`2026-05-29-btc-1w-machine-approved.md` — fråga A vs chartfönster (fråga B).
