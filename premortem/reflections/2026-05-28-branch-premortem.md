# 2026-05-28 Branch-premortem (`claude/branch-premortem-OViqi`)

Premortem Ã¶ver hela branchens nulÃ¤ge: tÃ¤nk dig att projektet har misslyckats om
sex mÃ¥nader â€” vad gick fel, och vad fÃ¶rankrar vi i koden redan nu? Nya
failure modes Ã¤r inlagda i `PREMORTEM.md`; den hÃ¤r reflektionen sammanfattar
branch-genomgÃ¥ngen.

Hypotes:
- Branchen upplevs "klar nog" att gÃ¥ mot Validate/Promotion. Premortemen prÃ¶var
  vad som realistiskt skulle fÃ¥ det att misslyckas innan vi tar det steget.

Scope:
- Branch: `claude/branch-premortem-OViqi` (hela projektets nulÃ¤ge, t.o.m. commit
  `a3186b4` "Address PR review feedback (out-of-window edge cases)").
- Exchange/symboler: Bitfinex spot â€” `BTC/USD`, `ETH/USD`, `SOL/USD`.
- Timeframes: `15m`â€“`1M`.
- DatamÃ¤ngd: 15 manuella labels totalt (â‰ˆ 1 high/low-par per symbol/timeframe);
  limit 500 candles per marknad/timeframe.
- KÃ¶rningar i fokus: stabilitetsmatris `matrix_20260528T072357Z`, trade-matris
  `trade_matrix_20260528T075650Z`.

Observationer:
- **BekrÃ¤ftat sÃ¤kert (behÃ¥ll disciplinen):**
  - *Kausalitet hÃ¥ller.* Walk-forward slicar `df.iloc[: t + 1]`
    (`backtest/stability.py:24`); features/structure/scale filtrerar konsekvent pÃ¥
    `index <= end_index` (`core/features.py:41`, `core/structure.py:20`,
    `core/scale.py:20`). Testas av `test_walk_forward_is_causal()`.
  - *Lager A/B Ã¤r frikopplat.* `sizing/solros.py` och `backtest/trade.py`
    konsumerar swing-output enkelriktat; `core/scoring.py` importerar aldrig
    sizing/trade.
  - *Out-of-window Ã¤r fixat.* `evaluation/metrics.py:26-42` flaggar `in_window`;
    `pivot_recall.py:59-65` och `experiment.py:75-101` exkluderar och loggar.
    Testas av `test_out_of_window_label_does_not_count_as_recall_hit()`.
- **KvarstÃ¥ende HIGH-risk:**
  - *Tunt underlag.* 15 labels och 8 handsatta vikter (`config/settings.yaml:19-27`)
    rÃ¤cker inte fÃ¶r att hÃ¤vda generalisering.
  - *Per-marknad-varians dÃ¶ljs i aggregat.* Enligt
    `reflections/2026-05-28-real-data-matrix.md` var BTC 15m svagast, och SOL 1h
    hade hÃ¶g endpoint-drift (~52 barer) trots bra flip-rate.
  - *Drift mÃ¤ts men gatas inte.* `flip_rate` ensamt kan ge falsk stabilitetsbild.
- **Medvetet avvisat:** att "lÃ¤ra" vikter mot agreement/labels. Det bryter mot
  filosofin och mot principen att labels bara Ã¤r referens.
  Mitigering Ã¤r bredare stabilitet/recall-validering â€” aldrig label-optimering.

Beslut:
- HÃ¥ll motorn i spÃ¥ren *Research/Validate*. Promota inget (t.ex. till
  `config/settings.yaml`) fÃ¶rrÃ¤n promotion-gaten i `repository-layout-policy.md Â§13` Ã¤r
  uppfylld.
- Vikter fÃ¶rblir principsatta; matris-/backtest-resultat Ã¤r Research-evidens, inte
  Validate i sig.
- Rapportera alltid per symbol/timeframe, inte bara aggregerat.

NÃ¤sta steg:
- MÃ¤t pivot-recall mot ett stÃ¶rre labelset *innan* scoring/detektering Ã¤ndras.
- Lyft `drift` till en fÃ¶rstklassig gate-metric vid sidan av flip/confirmed-rate.
- UtÃ¶ka labelkorpusen (mot trÃ¶skeln 20â€“30+ per relevant marknad/timeframe) och
  Ã¥tgÃ¤rda out-of-window-kÃ¤llan fÃ¶r lÃ¥nga timeframes (1M/1w/1d) med lÃ¤ngre fÃ¶nster.
- LÃ¤gg adversariella/invariant-tester (t.ex. assert att vald swing-endpunkt
  aldrig ligger efter cursorn) i stÃ¤llet fÃ¶r att luta sig mot coverage-gaten.

