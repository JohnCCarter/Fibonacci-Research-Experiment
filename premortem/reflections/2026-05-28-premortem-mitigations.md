# 2026-05-28 Premortem-mitigeringar implementerade

Uppföljning på `2026-05-28-branch-premortem.md`: åtgärdspunkterna från premortemen
omsatta i kod/config/tester. Additivt och bakåtkompatibelt — ingen ändring av
scoring-vikter eller swing-urvalets logik (det rörs först när recall mätts mot fler
labels).

Hypotes:
- Premortem-riskerna blir verkningslösa om de bara står som text. Genom att göra
  drift till en hård gate, exkludering explicit och look-ahead till ett regressions-
  test förvandlas riskerna till mekanismer som faktiskt larmar.

Scope:
- Delsystem: Lager A-diagnostik (backtest-stabilitet, pivot-recall), data-laddning,
  config.
- Inga nätverksberoenden i tester (gate/recall/limit testas på syntetiska data).

Observationer (vad som ändrades):
- **Drift som förstklassig gate-metric.** Ny `stability_gate()`
  (`backtest/stability.py`) med tröskel `gate_max_endpoint_drift_bars` vid sidan av
  flip/confirmed/direction. Wired in i `backtest/runner.py` och `backtest/matrix.py`
  (`gate_passed`/`gate_checks` i ledger + varning vid fail). Trösklar i
  `config/settings.yaml` (`backtest.gate_*`). Test: `test_stability_gate.py` visar att
  enbart drift (52 barer, jfr SOL/USDT 1h) underkänner gaten.
- **Tyst exkludering gjord explicit.** Ny `summarize_recall()`
  (`evaluation/pivot_recall.py`) räknar `n_excluded_out_of_window` och mäter recall
  *bara* på in-window-samplet; varnar i logg när labels exkluderas. Test täcker
  aggregat + "allt exkluderat".
- **Look-ahead-regressionstest.** `test_future_bars_do_not_change_past_selection`:
  att lägga till framtida barer får inte ändra ett redan fattat kausalt val.
- **Per-marknad-rapportering** finns redan radvis i matris-ledgern; gaten gör nu varje
  rad pass/fail så svaga rader inte göms i ett snitt.
- **Out-of-window-källa.** `data.timeframe_limits` + `DataConfig.effective_limit()`
  låter långa TF (1d/1w/1M/4h) ladda mer historik; `fetch.py` cache-väg och hämtning
  använder effektiv limit. Caveat dokumenterad: en CCXT-hämtning är ofta börs-kapad
  (~1000) → riktigt djup historik kräver paginering (ej gjort här).
- Tester: 68 → 74 gröna; ruff lint+format rena; coverage 76% (gate 60%).

Beslut:
- Behåll motorn i Research/Validate. Gaten är **principsatta startvärden**, tunbara i
  Research, aldrig auto-tunade mot labels.
- Vikter/urval orörda tills pivot-recall körts mot ett större labelset.

Nästa steg (kvarstår — kräver människa/nät):
- **Utöka labelkorpusen till 20–30+ per relevant marknad/timeframe.** Kräver manuell
  chart-läsning (TradingView) — medvetet INTE auto-genererat (facit = referens).
- Kör `pivot_recall` + `matrix` på riktiga data när nät finns; kalibrera `gate_*` mot
  utfallet och dokumentera i en ny reflektion.
- Överväg paginerad hämtning om 1d/1w-labels fortfarande klipps vid ~1000 candles.
