# Tool recommendation tables (issue #25)

> Companion to [TOOLING_RECOMMENDATION_REPORT.md](TOOLING_RECOMMENDATION_REPORT.md).
> Columns: **Maint** / **Learn** = low/med/high. **Review** / **Annot** / **Repro** =
> impact on deterministic review, manual annotation, reproducibility (none/low/med/high).

## 1. Static visualization & review UI

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **matplotlib** (in repo) | Review PNG + labeling GUI | JSON-first, fib-aware overlay exists | Custom code growth (741-line file) | med | low | high | med | high | now | **In repo** |
| **mplfinance** | OHLC + overlays | Cleaner candles/volume vs hand-rolled | Another dep; may not map fib-context 1:1 | low | low | high | med | high | after split renderer | **Adopt Later** |
| **plotly** | Interactive OHLC | Pan/zoom/hover | Heavier dep; server optional | med | med | high | med | med | if matplotlib blocks | **Adopt Later** |
| **streamlit** | Light review app | Fast internal UI, JSONL output | Runtime + maintenance (#16) | med | med | high | high | med | if review volume grows | **Adopt Later** |
| **bokeh / panel / dash** | Alt dashboards | Rich interactivity | Heavier than Streamlit for this repo | high | med | med | med | med | only if Streamlit fails | **Reject** |

## 2. DataFrame & object validation

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **pandera** | DF schemas | Fail-fast OHLC/label/ledger invariants | Schema drift if not in CI | low | med | med | med | **high** | next scoped issue | **Adopt Now** |
| **pydantic** (in repo) | Object contracts | Config + models today | Not all JSON artefacts validated | low | low | low | med | high | extend schemas | **In repo** |
| **jsonschema** | JSON/JSONL outside Python | Language-agnostic validation | Duplication vs pydantic | low | med | low | med | high | if non-Python consumers | **Adopt Later** |
| **frictionless** | Dataset packages | Metadata for shared datasets | Heavy for current phase | med | med | low | low | med | external datasets only | **Reject** |

## 3. Annotation platforms

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **Label Studio** | Structured annotation | Queues, multi-user | Docker ops; TS chart glue; facit drift | high | high | med | **high** | med | high label volume | **Annotation Later** |
| **CVAT** | Image/video annotate | Strong if chart-as-image | Wrong model for candle semantics | high | high | low | med | low | image workflow only | **Reject** |
| **doccano** | Text annotate | NLP labels | Irrelevant to OHLC review | med | med | none | low | low | — | **Reject** |

## 4. Research acceleration & backtest reference

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **custom event-study** (in repo) | Forward outcomes #22 | Aligned MFE/MAE/horizons; causal | Must stay isolated from promotion | med | — | med | low | **high** | maintain | **In repo** |
| **vectorbt** | Matrix sweeps | Fast parameter grids | Commons Clause; black-box temptation | med | high | low | none | med | license OK + sandbox | **Research Sandbox Only** |
| **backtesting.py** | Reference backtest API | Metric sanity checks | **AGPL**; poor event-study fit | med | med | low | none | med | — | **Documentation/Reference Only** |
| **quantstats** | Return analytics | Report metrics | Not event-centric | low | med | low | none | med | optional reports | **Documentation/Reference Only** |
| **empyrical** | Metrics | Classic quant stats | **Abandoned** (2020) | — | — | — | — | — | — | **Reject** |

## 5. Indicators & swing/anchor baselines

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **ta / pandas-ta** | Indicator library | Fast side experiments | Feature soup; pandas-ta churn | med | low | low | none | med | — | **Research Sandbox Only** |
| **scipy.signal.find_peaks** | Swing baseline | Transparent peaks | Not human-like swings | low | low | low | none | high | diagnostics | **Research Sandbox Only** |
| **ZigZag / findpeaks** | Anchor candidates | Baseline compare | Silent facit risk | med | med | low | none | med | never as truth | **Research Sandbox Only** |

## 6. Changepoint, motif, feature extraction

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **ruptures** | Changepoint detect | Regime/leg diagnostics | Black-box segmentation | low | med | low | none | med | isolated reports | **Research Sandbox Only** |
| **stumpy** | Motif search | Pattern compare at levels | Exploratory only | med | high | low | none | med | isolated | **Research Sandbox Only** |
| **tsfresh** | Auto features | Compare event windows | Hypothesis drift / overfit | high | high | low | none | low | post-hoc only | **Research Sandbox Only** |

## 7. Storage, querying, artefacts

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **JSONL** (in repo) | Append-only ledgers | Git-friendly, simple | Scale limits | low | low | med | med | high | keep default | **In repo** |
| **duckdb** | Local SQL analytics | Fast agg over JSONL/Parquet | Extra dep | low | med | med | low | **high** | after schemas | **Adopt Now** |
| **PyArrow / Parquet** | Typed columnar files | Scale, dtypes | Less human-readable in git | low | med | low | low | high | large multi-run batches | **Adopt Later** |
| **SQLite** | Local metadata DB | Review status DB | Ops vs JSONL | med | med | low | med | med | if JSONL unwieldy | **Adopt Later** |

## 8. Reporting & docs

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **markdown + wiki** (in repo) | Evidence packs | Already used | Sprawl if unbounded | low | low | med | low | high | keep | **In repo** |
| **jupyter** | Scratch exploration | Familiar | Non-deterministic order | low | low | med | low | **low** | scratch only | **Documentation/Reference Only** |
| **marimo** | Repro notebooks | Dependency-aware cells | New toolchain | med | med | med | low | med | methodology stable | **Adopt Later** |
| **quarto** | HTML/PDF reports | Issue evidence packs | Build pipeline | med | med | med | low | high | larger reports | **Adopt Later** |
| **mkdocs-material** | Docs site | Methodology portal | Overkill now | med | med | low | low | med | many external readers | **Adopt Later** |

## 9. CI & dev environment

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **uv** (in repo) | Lockfile env | Fast reproducible installs | — | low | low | low | low | **high** | keep | **In repo** |
| **ruff** (in repo) | Lint/format | Fast, CI-aligned | — | low | low | low | low | high | keep | **In repo** |
| **pytest** (in repo) | Tests | Deterministic gates | — | low | low | med | low | **high** | keep | **In repo** |
| **pre-commit** (in repo) | Local fail-fast | Catches before CI | Hook drift | low | low | low | low | high | keep | **In repo** |
| **hypothesis** | Property tests | Fib invariants | Over-broad properties | low | med | med | low | **high** | with schema work | **Adopt Later** |
| **nox** | Task sessions | Standard sessions | vs simple scripts | med | med | low | low | med | scripts stabilize | **Adopt Later** |
| **tox** | Multi-env test | Matrix testing | Redundant with uv | med | med | low | low | med | — | **Reject** |

## 10. Data source & provenance

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **ccxt** (in repo) | Exchange OHLCV fetch | Already in data path | API drift, rate limits | med | med | low | low | med | keep; improve manifest | **In repo** |
| **exchange CSV dumps** | Fixed historical sets | Repro vs re-fetch | Storage, normalization | med | low | low | low | **high** | pinned research sets | **Adopt Later** |
| **cryptofeed** | Live multi-exchange | Streaming | Out of scope for static research | high | high | none | none | low | live phase | **Reject** |

## 11. MLOps (issue #25 “later”)

| Tool | Purpose | Benefit | Risks | Maint | Learn | Review | Annot | Repro | Timing | **Cat** |
|------|---------|---------|-------|-------|-------|--------|-------|-------|--------|---------|
| **MLflow** | Run tracking | Experiment registry | Heavy vs JSONL runs | high | med | low | low | med | run volume pain | **Adopt Later** |
| **DVC** | Data versioning | Large artefact sets | Git LFS complexity | high | med | low | low | med | dataset scale | **Adopt Later** |
