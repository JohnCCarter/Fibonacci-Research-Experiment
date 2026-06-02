# 2026-05-28 Premortem-mitigeringar implementerade

UppfÃ¶ljning pÃ¥ `2026-05-28-branch-premortem.md`: Ã¥tgÃ¤rdspunkterna frÃ¥n premortemen
omsatta i kod/config/tester. Additivt och bakÃ¥tkompatibelt â€” ingen Ã¤ndring av
scoring-vikter eller swing-urvalets logik (det rÃ¶rs fÃ¶rst nÃ¤r recall mÃ¤tts mot fler
labels).

Hypotes:
- Premortem-riskerna blir verkningslÃ¶sa om de bara stÃ¥r som text. Genom att gÃ¶ra
  drift till en hÃ¥rd gate, exkludering explicit och look-ahead till ett regressions-
  test fÃ¶rvandlas riskerna till mekanismer som faktiskt larmar.

Scope:
- Delsystem: Lager A-diagnostik (backtest-stabilitet, pivot-recall), data-laddning,
  config.
- Inga nÃ¤tverksberoenden i tester (gate/recall/limit testas pÃ¥ syntetiska data).

Observationer (vad som Ã¤ndrades):
- **Drift som fÃ¶rstklassig gate-metric.** Ny `stability_gate()`
  (`backtest/stability.py`) med trÃ¶skel `gate_max_endpoint_drift_bars` vid sidan av
  flip/confirmed/direction. Wired in i `backtest/runner.py` och `backtest/matrix.py`
  (`gate_passed`/`gate_checks` i ledger + varning vid fail). TrÃ¶sklar i
  `config/settings.yaml` (`backtest.gate_*`). Test: `test_stability_gate.py` visar att
  enbart drift (52 barer, jfr SOL/USD 1h) underkÃ¤nner gaten.
- **Tyst exkludering gjord explicit.** Ny `summarize_recall()`
  (`evaluation/pivot_recall.py`) rÃ¤knar `n_excluded_out_of_window` och mÃ¤ter recall
  *bara* pÃ¥ in-window-samplet; varnar i logg nÃ¤r labels exkluderas. Test tÃ¤cker
  aggregat + "allt exkluderat".
- **Look-ahead-regressionstest.** `test_future_bars_do_not_change_past_selection`:
  att lÃ¤gga till framtida barer fÃ¥r inte Ã¤ndra ett redan fattat kausalt val.
- **Per-marknad-rapportering** finns redan radvis i matris-ledgern; gaten gÃ¶r nu varje
  rad pass/fail sÃ¥ svaga rader inte gÃ¶ms i ett snitt.
- **Out-of-window-kÃ¤lla.** `data.timeframe_limits` + `DataConfig.effective_limit()`
  lÃ¥ter lÃ¥nga TF (1d/1w/1M/4h) ladda mer historik; `fetch.py` cache-vÃ¤g och hÃ¤mtning
  anvÃ¤nder effektiv limit. Caveat dokumenterad: en CCXT-hÃ¤mtning Ã¤r ofta bÃ¶rs-kapad
  (~1000) â†’ riktigt djup historik krÃ¤ver paginering (ej gjort hÃ¤r).
- Tester: 68 â†’ 74 grÃ¶na; ruff lint+format rena; coverage 76% (gate 60%).

Beslut:
- BehÃ¥ll motorn i Research/Validate. Gaten Ã¤r **principsatta startvÃ¤rden**, tunbara i
  Research, aldrig auto-tunade mot labels.
- Vikter/urval orÃ¶rda tills pivot-recall kÃ¶rts mot ett stÃ¶rre labelset.

NÃ¤sta steg (kvarstÃ¥r â€” krÃ¤ver mÃ¤nniska/nÃ¤t):
- **UtÃ¶ka labelkorpusen till 20â€“30+ per relevant marknad/timeframe.** KrÃ¤ver manuell
  chart-lÃ¤sning (TradingView) â€” medvetet INTE auto-genererat (facit = referens).
- KÃ¶r `pivot_recall` + `matrix` pÃ¥ riktiga data nÃ¤r nÃ¤t finns; kalibrera `gate_*` mot
  utfallet och dokumentera i en ny reflektion.
- Ã–vervÃ¤g paginerad hÃ¤mtning om 1d/1w-labels fortfarande klipps vid ~1000 candles.

