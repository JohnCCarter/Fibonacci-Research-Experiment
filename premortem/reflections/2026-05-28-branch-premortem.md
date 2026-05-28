# 2026-05-28 Branch-premortem (`claude/branch-premortem-OViqi`)

Premortem över hela branchens nuläge: tänk dig att projektet har misslyckats om
sex månader — vad gick fel, och vad förankrar vi i koden redan nu? Nya
failure modes är inlagda i `PREMORTEM.md`; den här reflektionen sammanfattar
branch-genomgången.

Hypotes:
- Branchen upplevs "klar nog" att gå mot Validate/Promotion. Premortemen prövar
  vad som realistiskt skulle få det att misslyckas innan vi tar det steget.

Scope:
- Branch: `claude/branch-premortem-OViqi` (hela projektets nuläge, t.o.m. commit
  `a3186b4` "Address PR review feedback (out-of-window edge cases)").
- Exchange/symboler: Binance spot — `BTC/USDT`, `ETH/USDT`, `SOL/USDT`.
- Timeframes: `15m`–`1M`.
- Datamängd: 15 manuella labels totalt (≈ 1 high/low-par per symbol/timeframe);
  limit 500 candles per marknad/timeframe.
- Körningar i fokus: stabilitetsmatris `matrix_20260528T072357Z`, trade-matris
  `trade_matrix_20260528T075650Z`.

Observationer:
- **Bekräftat säkert (behåll disciplinen):**
  - *Kausalitet håller.* Walk-forward slicar `df.iloc[: t + 1]`
    (`backtest/stability.py:24`); features/structure/scale filtrerar konsekvent på
    `index <= end_index` (`core/features.py:41`, `core/structure.py:20`,
    `core/scale.py:20`). Testas av `test_walk_forward_is_causal()`.
  - *Lager A/B är frikopplat.* `sizing/solros.py` och `backtest/trade.py`
    konsumerar swing-output enkelriktat; `core/scoring.py` importerar aldrig
    sizing/trade.
  - *Out-of-window är fixat.* `evaluation/metrics.py:26-42` flaggar `in_window`;
    `pivot_recall.py:59-65` och `experiment.py:75-101` exkluderar och loggar.
    Testas av `test_out_of_window_label_does_not_count_as_recall_hit()`.
- **Kvarstående HIGH-risk:**
  - *Tunt underlag.* 15 labels och 8 handsatta vikter (`config/settings.yaml:19-27`)
    räcker inte för att hävda generalisering.
  - *Per-marknad-varians döljs i aggregat.* Enligt
    `reflections/2026-05-28-real-data-matrix.md` var BTC 15m svagast, och SOL 1h
    hade hög endpoint-drift (~52 barer) trots bra flip-rate.
  - *Drift mäts men gatas inte.* `flip_rate` ensamt kan ge falsk stabilitetsbild.
- **Medvetet avvisat:** att "lära" vikter mot agreement/labels. Det bryter mot
  filosofin och mot lärdomen i `reflections/2026-05-28-optuna-rollback.md`.
  Mitigering är bredare stabilitet/recall-validering — aldrig label-optimering.

Beslut:
- Håll motorn i spåren *Research/Validate*. Promota inget (t.ex. till
  `config/settings.yaml`) förrän promotion-gaten i `REPO_POLICY.md §13` är
  uppfylld.
- Vikter förblir principsatta; matris-/backtest-resultat är Research-evidens, inte
  Validate i sig.
- Rapportera alltid per symbol/timeframe, inte bara aggregerat.

Nästa steg:
- Mät pivot-recall mot ett större labelset *innan* scoring/detektering ändras.
- Lyft `drift` till en förstklassig gate-metric vid sidan av flip/confirmed-rate.
- Utöka labelkorpusen (mot tröskeln 20–30+ per relevant marknad/timeframe) och
  åtgärda out-of-window-källan för långa timeframes (1M/1w/1d) med längre fönster.
- Lägg adversariella/invariant-tester (t.ex. assert att vald swing-endpunkt
  aldrig ligger efter cursorn) i stället för att luta sig mot coverage-gaten.
