# Source-quality review ledgers

Lightweight, machine-trackable record of **source-fib review verdicts** — so verdicts,
watchlist items, and correction-candidates live in a queryable CSV instead of only in
prose review docs. Not a database, not a heavy system: one flat CSV per review track.

Helper: [`research/review_ledger.py`](../../../../src/fibengine/research/review_ledger.py)
(stdlib-only, no new dependencies). Source-quality review only — it never edits source
labels, renders artifacts, or touches reaction-review / auto-fib.

## Files

| Ledger | Track |
|--------|-------|
| [btc-4h-source-quality-ledger.csv](btc-4h-source-quality-ledger.csv) | BTC/USD 4H Tier 2 zoom sample-pass (2026-06-15) |

## Schema (CSV columns, in order)

| Column | Meaning |
|--------|---------|
| `fib_id` | Full fib id (e.g. `fib_BTC-USD_4h_20171228T200000`) |
| `symbol` | Market, e.g. `BTC/USD` |
| `timeframe` | Source TF of the fib (`4h` here) |
| `scope` | Review scope/group (e.g. `2017_h2`, `2021_dec2020_mar2021`) |
| `review_type` | What kind of review produced the verdict (e.g. `tier2_zoom`) |
| `verdict` | Review outcome — controlled (see below) |
| `status` | Lifecycle state — controlled (see below) |
| `note` | Short free-text rationale |
| `source_fib_path` | Repo-relative path to the committed source `fib_*.json` |
| `artifact_path` | Repo-relative path to the (gitignored) zoom artifacts |
| `source_hash` | `sha256:<16 hex>` of the source fib JSON bytes — ties the verdict to the exact facit version |
| `reviewed_at` | ISO date of the review |
| `reviewer` | Origin of the verdict (`human` here) |

### Controlled vocabulary

- **verdict** ∈ `ok`, `ok-with-note`, `watchlist`, `suspicious`
- **status** ∈ `accepted`, `noted`, `open`, `correction-candidate`, `deferred`, `corrected`,
  `superseded`

`superseded` = the fib was retired from active facit (e.g. a near-duplicate removed in
favour of a better fib); its `source_fib_path`/`source_hash` are provenance and the file
may no longer exist on disk.

`verdict` is the judgement; `status` is the lifecycle. A `suspicious` fib that we decided
not to fix yet is `verdict=suspicious, status=correction-candidate` (e.g.
`fib_BTC-USD_4h_20171228T200000`).

## Determinism

`source_hash` is `sha256` of the raw `fib_*.json` bytes (truncated to 16 hex). The same
committed fib always hashes the same; any edit to the facit changes it, so a stale verdict
is detectable (hash no longer matches the current file). Re-compute by re-running the
helper against the current source fib.

## Usage

Validate a ledger (controlled-vocab + header check):

```bash
uv run --no-sync python -m fibengine.research.review_ledger \
  --validate docs/research_wiki/reviews/ledgers/btc-4h-source-quality-ledger.csv
```

Build/append rows programmatically (stdlib helper):

```python
from fibengine.research.review_ledger import row_for_source_fib, write_ledger

row = row_for_source_fib(
    "data/labels/human_fib/bitfinex/BTC-USD/4h/fib_BTC-USD_4h_20171228T200000.json",
    scope="2017_h2", review_type="tier2_zoom",
    verdict="suspicious", status="correction-candidate",
    note="better anchor_a adjacent to leg A; deferred",
    artifact_path="experiments/review/fourh_source_fib_zoom/2017_h2/fib_BTC-USD_4h_20171228T200000/",
    reviewed_at="2026-06-15",
)
write_ledger("docs/research_wiki/reviews/ledgers/btc-4h-source-quality-ledger.csv", [row])
```

## Constraints

- CSV is committed text under `docs/` (never under `experiments/review/**`).
- The ledger records verdicts; it does **not** change source labels or artifacts.
- Keep it flat and human-readable — no database, no migrations.
