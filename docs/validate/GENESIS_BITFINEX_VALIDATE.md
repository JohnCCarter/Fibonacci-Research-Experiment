# Genesis-Core / Bitfinex validate-pass

Fib-repot utvecklar **Lager A** (swing-urval) mot OHLCV. **Genesis-Core** kÃ¶r er algo-plattform mot **Bitfinex** (subaccount / paper). Bitfinex i det hÃ¤r repot Ã¤r ett **research-fÃ¶nster** â€” inte produktionssign-off.

Innan Fib importeras i Genesis: repetera **Validate** pÃ¥ Bitfinex-data med samma motor och gates som baseline, jÃ¤mfÃ¶r mot Bitfinex-matrisen, och (vid behov) bygg **nytt human-facit** under `data/labels/bitfinex/`.

| Doc | Roll |
|-----|------|
| [FIB_BACKTEST_PLAN.md](FIB_BACKTEST_PLAN.md) | Faser 1â€“6 (Bitfinex-matris m.m.) |
| [TRACKS.md](TRACKS.md) | Research / Validate / Promotion |
| `config/settings.yaml` | Promotion-baseline (ofÃ¶rÃ¤ndrad) |
| `config/settings.bitfinex.yaml` | Bitfinex validate-profil (denna pass) |

---

## Spelar Bitfinex roll?

| Del | Legacy (arkiv) | Bitfinex / Genesis (aktivt) |
|-----|----------------|------------------------------|
| Pivot/scoring/Fib-kod | BÃ¶rs-oberoende | Samma kod |
| Candles | Tidigare `data/raw/Bitfinex/` | CCXT `bitfinex` â†’ `data/raw/bitfinex/` |
| Labels (facit) | `archive/data_labels_Bitfinex/labels/Bitfinex/` | `data/labels/bitfinex/` |
| Stabilitetsmatris | Historiska rader kan finnas | KÃ¶r med `--config settings.bitfinex.yaml` |
| Agreement / recall | Legacy-referens vid behov | Bitfinex-labels nÃ¤r ni ritat mot Bitfinex-chart |

**Slutsats:** Aktiv exchange Ã¤r Bitfinex. Bitfinex anvÃ¤nds endast som historik i `archive/`.

---

## Symbol- och timeframe-mappning

Justera tabellen mot er **faktiska Genesis-paper-konfiguration** (tickers, margin, spot vs derivat).

| Genesis / Bitfinex (CCXT) | Kommentar |
|---------------------------|-----------|
| `BTC/USD` | PrimÃ¤rt par i nuvarande setup |
| `ETH/USD` | LÃ¤gg till vid behov |
| `SOL/USD` | Verifiera att SOL finns pÃ¥ ert Bitfinex-konto |
| *(lÃ¤gg till)* | t.ex. LTC, XRP om ni handlar dem i Genesis |

**Rekommenderad validate-matris**:

- Symboler: `BTC/USD`, `ETH/USD`, `SOL/USD`
- Timeframes: `15m`, `1h`, `4h`

Om Genesis anvÃ¤nder andra par: Ã¤ndra `--symbols` vid matrix/fetch (se nedan) och uppdatera tabellen i samma commit.

---

## Konfiguration

- **Baseline (rÃ¶r ej):** `config/settings.yaml` â†’ `exchange: bitfinex`
- **Bitfinex-pass:** `config/settings.bitfinex.yaml` â†’ `exchange: bitfinex`, default `BTC/USD`

Laddas med `--config config/settings.bitfinex.yaml` pÃ¥ moduler som stÃ¶djer flaggan.

---

## KÃ¶rordning (Validate)

KrÃ¤ver nÃ¤t fÃ¶r fÃ¶rsta CCXT-hÃ¤mtning (cachas sedan under `data/raw/bitfinex/`).

### 1. HÃ¤mta candles

```bash
# En symbol/TF (default i settings.bitfinex.yaml: BTC/USD 1h)
uv run python -m fibengine.data.fetch --config config/settings.bitfinex.yaml

# Fler kombinationer: kÃ¶r fetch med overrides via kort Python eller upprepa
# med Ã¤ndrad symbol i en kopia â€” matrix hÃ¤mtar per case automatiskt vid kÃ¶rning.
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

- **Human-facit:** `uv run python -m fibengine.labeling.tool` med data som pekar pÃ¥ Bitfinex-candles (sÃ¤tt exchange i label-JSON till `bitfinex` vid save â€” sparas under `data/labels/bitfinex/...`).
- **Maskin-kandidater:** `uv run python -m fibengine.labeling.autolabel --exchange bitfinex --config config/settings.bitfinex.yaml`
- **Recall (endast human):** `uv run python -m fibengine.evaluation.pivot_recall` â€” filtrera ledger pÃ¥ Bitfinex-labels eller utÃ¶ka verktyget med `--config` i senare iteration.

Legacy Bitfinex-labels i `archive/data_labels_Bitfinex/labels/Bitfinex/` ska **inte** tolkas som Bitfinex-ground-truth utan ny human-granskning eller tydlig trade-off i reflektion.

### 5. JÃ¤mfÃ¶r mot Bitfinex-baseline

- Phase 2 triage: rangordna Bitfinex-rader separat frÃ¥n legacy-rader i arkivet.
- Gate: `gate_passed` ska hÃ¥lla pÃ¥ **bÃ¥da** (eller dokumentera varfÃ¶r Bitfinex Ã¤r svagare).
- Kort reflektion i `premortem/reflections/YYYY-MM-DD-bitfinex-validate.md`.

---

## Inport till Genesis-Core (senare)

Fib-modulen i Genesis bÃ¶r ta:

1. **OHLCV** frÃ¥n Genesis datafeed (Bitfinex paper), samma kolumner som hÃ¤r (`open/high/low/close/volume`, UTC-index).
2. **Settings** motsvarande `settings.yaml` / bevisad Bitfinex-validate (hash i loggar).
3. **Ingen** hÃ¥rdkodning av exchange-id â€” exchange och symbol kommer frÃ¥n Genesis runtime.

Det hÃ¤r repot fortsÃ¤tter anvÃ¤nda CCXT fÃ¶r research-cache; Genesis Ã¤ger auth, subaccount och orderflÃ¶de (Lager B).

---

## Checklista innan â€œproduction readyâ€

- [ ] `settings.bitfinex.yaml` speglar er Genesis symbol-lista
- [ ] `backtest_matrix` kÃ¶rd med `exchange: bitfinex` fÃ¶r alla planerade par/TF
- [ ] JÃ¤mfÃ¶relse mot Bitfinex-matris dokumenterad (gate + drift + flip)
- [ ] Human-facit under `data/labels/bitfinex/` fÃ¶r kritiska par (eller medvetet undantag)
- [ ] Reflektion + beslut i `premortem/reflections/`
- [ ] PR till Genesis-Core med config-hash och validate-run-id

