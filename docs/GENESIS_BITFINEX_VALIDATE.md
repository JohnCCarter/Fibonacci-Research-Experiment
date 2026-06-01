# Genesis-Core / Bitfinex validate-pass

Fib-repot utvecklar **Lager A** (swing-urval) mot OHLCV. **Genesis-Core** kör er algo-plattform mot **Bitfinex** (subaccount / paper). Binance i det här repot är ett **research-fönster** — inte produktionssign-off.

Innan Fib importeras i Genesis: repetera **Validate** på Bitfinex-data med samma motor och gates som baseline, jämför mot Binance-matrisen, och (vid behov) bygg **nytt human-facit** under `data/labels/bitfinex/`.

| Doc | Roll |
|-----|------|
| [FIB_BACKTEST_PLAN.md](FIB_BACKTEST_PLAN.md) | Faser 1–6 (Binance-matris m.m.) |
| [TRACKS.md](TRACKS.md) | Research / Validate / Promotion |
| `config/settings.yaml` | Promotion-baseline (oförändrad) |
| `config/settings.bitfinex.yaml` | Bitfinex validate-profil (denna pass) |

---

## Spelar Binance roll?

| Del | Binance nu | Bitfinex / Genesis |
|-----|------------|-------------------|
| Pivot/scoring/Fib-kod | Börs-oberoende | Samma kod |
| Candles | CCXT `binance` → `data/raw/binance/` | CCXT `bitfinex` → `data/raw/bitfinex/` |
| Labels (facit) | `data/labels/binance/` | Nytt: `data/labels/bitfinex/` för Bitfinex-specifikt facit |
| Stabilitetsmatris | `exchange: binance` i ledger | Kör med `--config settings.bitfinex.yaml` |
| Agreement / recall | Bara `source=human`; Binance-labels är referens | Bitfinex-labels när ni ritat mot Bitfinex-chart |

**Slutsats:** Fortsätt på Binance för snabb iteration. **Produktionsklar** = Bitfinex-matris + dokumenterad jämförelse, inte bara Binance-rader i `backtest_matrix.jsonl`.

---

## Symbol- och timeframe-mappning

Justera tabellen mot er **faktiska Genesis-paper-konfiguration** (tickers, margin, spot vs derivat).

| Genesis / Bitfinex (CCXT) | Binance research (jämförelse) | Kommentar |
|---------------------------|-------------------------------|-----------|
| `BTC/USD` | `BTC/USDT` | Närmaste likvärdiga BTC — **inte** identiska serier |
| `ETH/USD` | `ETH/USDT` | Samma |
| `SOL/USD` | `SOL/USDT` | Verifiera att SOL finns på ert Bitfinex-konto |
| *(lägg till)* | *(lägg till)* | t.ex. LTC, XRP om ni handlar dem i Genesis |

**Rekommenderad validate-matris** (samma TFs som Phase 1 på Binance):

- Symboler: `BTC/USD`, `ETH/USD`, `SOL/USD`
- Timeframes: `15m`, `1h`, `4h`

Om Genesis använder andra par: ändra bara `--symbols` vid matrix/fetch (se nedan), uppdatera denna tabell i samma commit.

---

## Konfiguration

- **Baseline (rör ej):** `config/settings.yaml` → `exchange: binance`
- **Bitfinex-pass:** `config/settings.bitfinex.yaml` → `exchange: bitfinex`, default `BTC/USD`

Laddas med `--config config/settings.bitfinex.yaml` på moduler som stödjer flaggan.

---

## Körordning (Validate)

Kräver nät för första CCXT-hämtning (cachas sedan under `data/raw/bitfinex/`).

### 1. Hämta candles

```bash
# En symbol/TF (default i settings.bitfinex.yaml: BTC/USD 1h)
uv run python -m fibengine.data.fetch --config config/settings.bitfinex.yaml

# Fler kombinationer: kör fetch med overrides via kort Python eller upprepa
# med ändrad symbol i en kopia — matrix hämtar per case automatiskt vid körning.
```

### 2. Stabilitetsmatris (Lager A)

```bash
uv run python -m fibengine.backtest.matrix \
  --config config/settings.bitfinex.yaml \
  --symbols BTC/USD,ETH/USD,SOL/USD \
  --timeframes 15m,1h,4h
```

Resultat appendas till `experiments/results/backtest_matrix.jsonl` med `"exchange": "bitfinex"`.

### 3. Enstaka marknad (snabb check)

```bash
uv run python -m fibengine.backtest.runner --config config/settings.bitfinex.yaml
```

### 4. Facit och recall (valfritt men rekommenderat)

- **Human-facit:** `uv run python -m fibengine.labeling.tool` med data som pekar på Bitfinex-candles (sätt exchange i label-JSON till `bitfinex` vid save — sparas under `data/labels/bitfinex/...`).
- **Maskin-kandidater:** `uv run python -m fibengine.labeling.autolabel --exchange bitfinex --config config/settings.bitfinex.yaml`
- **Recall (endast human):** `uv run python -m fibengine.evaluation.pivot_recall` — filtrera ledger på Bitfinex-labels eller utöka verktyget med `--config` i senare iteration.

Binance-labels i `data/labels/binance/` ska **inte** tolkas som Bitfinex-ground-truth utan ny human-granskning eller tydlig trade-off i reflektion.

### 5. Jämför mot Binance-baseline

- Phase 2 triage: rangordna rader där `exchange == bitfinex` separat från `binance`.
- Gate: `gate_passed` ska hålla på **båda** (eller dokumentera varför Bitfinex är svagare).
- Kort reflektion i `premortem/reflections/YYYY-MM-DD-bitfinex-validate.md`.

---

## Inport till Genesis-Core (senare)

Fib-modulen i Genesis bör ta:

1. **OHLCV** från Genesis datafeed (Bitfinex paper), samma kolumner som här (`open/high/low/close/volume`, UTC-index).
2. **Settings** motsvarande `settings.yaml` / bevisad Bitfinex-validate (hash i loggar).
3. **Ingen** hårdkodning av `binance` — exchange och symbol kommer från Genesis runtime.

Det här repot fortsätter använda CCXT för research-cache; Genesis äger auth, subaccount och orderflöde (Lager B).

---

## Checklista innan “production ready”

- [ ] `settings.bitfinex.yaml` speglar er Genesis symbol-lista
- [ ] `backtest_matrix` körd med `exchange: bitfinex` för alla planerade par/TF
- [ ] Jämförelse mot Binance-matris dokumenterad (gate + drift + flip)
- [ ] Human-facit under `data/labels/bitfinex/` för kritiska par (eller medvetet undantag)
- [ ] Reflektion + beslut i `premortem/reflections/`
- [ ] PR till Genesis-Core med config-hash och validate-run-id
