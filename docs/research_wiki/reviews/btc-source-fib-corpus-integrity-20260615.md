# BTC/USD Source-Fib Corpus Integrity Report (2026-06-15)

Read-only **capstone**. Locks the BTC/USD source-fib corpus as a clean research base
before the next analytical pass (MTF confluence atlas). This is Alternativ #2 from
[btc-source-fib-next-research-plan-20260615.md](btc-source-fib-next-research-plan-20260615.md).

**Docs-only — no source-label changes, no code changes, no deps, no committed artifacts,
no new tooling.** All numbers below were re-derived from disk on 2026-06-15 (commands in
[Verification](#verification)). Scope guards honored: no 1H, no reaction-review, no
auto-fib, no trading conclusions, no ML/tuning.

---

## Observed

- Active corpus on disk (base `fib_*.json`, `*_events.json`/`*_interactions.csv` sidecars
  excluded): **1M=9, 1w=21, 1d=67, 4h=365**. Up/down splits match
  [INDEX.md](../../../data/labels/INDEX.md) exactly.
- 4H is post-cleanup: `20171228` corrected, `20250506` deduped/superseded (366→365), ledger
  validates (10 rows), INDEX reconciled, log archived under bound.
- Ladder conventions identical across all four TFs (log scale, `tradingview_log_chamoun`,
  no 0.236, human/manual).
- The 4H `20250506T080000` source file is **absent** from disk (superseded) — confirmed.

## Inferred

- The corpus is internally consistent and traceable: every verdict in the ledger ties to a
  committed `fib_*.json` via `source_hash`; the one removed fib retains provenance only.
- Coverage is **anchor-derived** (from label anchor timestamps), not an independent metadata
  claim — see the explicit note in [Coverage](#coverage).
- The corpus is ready to serve as a stable read-only input to the MTF confluence atlas; no
  open source-quality items remain.

## Unverified

- Whether 1M coverage "should" extend before 2020-10 (earliest 1M anchor is 2020-10-01).
  This reflects how the monthly anchors were drawn, not a gap claim — not investigated here.
- Per-fib visual correctness beyond the Tier 2 *sample* (8 fibs) — Tier 1 map-OK covers all
  groups, but full per-fib Tier 2 was not exhaustively run (by design).
- Cross-version float stability of stored level prices (not relevant to integrity; noted).

---

## Corpus counts

Base `fib_*.json` only; `*_events.json` / `*_interactions.csv` sidecars excluded.

| Timeframe | Count | Up | Down |
|-----------|------:|---:|-----:|
| 1M | 9 | 5 | 4 |
| 1w | 21 | 13 | 8 |
| 1d | 67 | 33 | 34 |
| 4h | **365** | 168 | 197 |
| **Total** | **462** | 219 | 243 |

All `direction` fields resolved to `up`/`down` (0 other). Matches INDEX.md.

## Coverage

Span = earliest/latest anchor timestamp across `anchor_a` + `anchor_b` per TF. **This is
label-anchor-derived**, not an independent candle-cache metadata claim.

| Timeframe | Earliest anchor | Latest anchor |
|-----------|-----------------|---------------|
| 1M | 2020-10-01 | 2026-02-01 |
| 1w | 2016-12-29 | 2026-06-04 |
| 1d | 2017-01-05 | 2024-12-20 |
| 4h | 2017-01-05 04:00 | 2026-06-07 20:00 |

**Total BTC/USD source-fib coverage (union): 2016-12-29 → 2026-06-07** (anchor-derived).
1M anchors begin 2020-10 (reflects how monthly anchors were drawn — see Unverified).

## Ladder conventions

Identical for every BTC/USD source fib (all TFs):

- **scale:** log
- **profile:** `tradingview_log_chamoun`
- **levels:** `[0, 0.382, 0.5, 0.618, 0.786, 1.0]` — **no 0.236**
- **endpoint mapping:** ratio `0.0 = anchor_b`, `1.0 = anchor_a`
- **origin:** human / manual only (no auto-fib)

Schema: [HUMAN_FIB_ANNOTATION.md](../../labeling/HUMAN_FIB_ANNOTATION.md).

## Source-quality state

- **4H Tier 1 (annual map):** 11 annual groups, 366/366 drawn, 9/11 map-OK; 2017_h2 and
  2021 flagged for Tier 2 (local density).
  [Tier 1 review](btc-4h-tier1-map-review-20260615.md).
- **4H Tier 2 (per-fib zoom):** sample-pass of 8 fibs (4 per flagged scope); no suspicious
  labels in the sample; resolves Tier 1 readability.
  [Tier 2 review](btc-4h-tier2-sample-review-20260615.md).
- **20171228 correction:** anchor_a moved 2017-12-28T20:00 @ 13611 → 2017-12-28T08:00 @
  13145 (candidate_1, preview-first flow); only anchor_a + dependent levels changed;
  guard PASS; ledger `suspicious/correction-candidate → ok-with-note/corrected`.
  [Report](btc-4h-fib-20171228-correction-20260615.md).
- **20250506 dedup:** fib A (`08:00`) **superseded** in favour of fib B (`12:00`, structural
  bottom @ 93663); A deleted from active facit, B unchanged.
  [Report](btc-4h-fib-20250506-dedup-20260615.md).
- **Ledger:** [btc-4h-source-quality-ledger.csv](ledgers/btc-4h-source-quality-ledger.csv)
  — 10 rows, validates clean. By status: accepted 6, corrected 1, noted 1, superseded 1
  (+ the dedup-retained `accepted` B). **Superseded count: 1.**
- **Active 4H count now: 365** (366 drawn − 1 superseded).

## Known caveats

- **body/close vs wick convention** is undocumented in some anchors — watchlisted (e.g.
  `20210110T200000` anchor_b uses body/close ~$30,500, not wick ~$28,500). Convention noted
  in `HUMAN_FIB_ANNOTATION.md`; not a defect, but a consistency item.
- **20171228** corrected via preview-first flow (machine renders candidates → human picks →
  machine edits JSON). fib_id kept stable as identifier.
- **20250506** fib A superseded, fib B retained — these were the same up-leg, not
  complementary sub-legs.
- **1H paused** — cache not fetched; 4H is the lowest active timeframe.
- **ETH/USD deferred** until the BTC protocol is signed off.
- **No trading conclusions** — this corpus is a source-fib research base, not a signal set.

## Verification

All re-derived on disk 2026-06-15.

Counts + up/down + coverage (sidecar-excluded), one-shot stdlib rollup (not committed):

```
1M: n=9  up=5   down=4   | 2020-10-01        .. 2026-02-01
1w: n=21 up=13  down=8   | 2016-12-29        .. 2026-06-04
1d: n=67 up=33  down=34  | 2017-01-05        .. 2024-12-20
4h: n=365 up=168 down=197 | 2017-01-05 04:00 .. 2026-06-07 20:00
```

Sidecar sanity (4H): `base=365 all_json=365` — no `*_events`/`*_interactions` counted.

```bash
ls -1 data/labels/human_fib/bitfinex/BTC-USD/4h/fib_*.json \
  | grep -vE '_events|_interactions' | wc -l        # → 365
```

Ledger validation:

```bash
uv run --no-sync python -m fibengine.research.review_ledger \
  --validate docs/research_wiki/reviews/ledgers/btc-4h-source-quality-ledger.csv
# → ledger OK: 10 row(s) validated
```

Superseded sanity: `fib_BTC-USD_4h_20250506T080000.json` → **No such file** (correctly
removed from active facit). No source labels changed by this report; no artifacts committed.

## Links / authorities

- [INDEX.md](../../../data/labels/INDEX.md) — on-disk label index
- [handoff.md](../handoff.md) — phase-status authority
- [source-quality ledger](ledgers/btc-4h-source-quality-ledger.csv) · [ledger README](ledgers/README.md)
- [20171228 correction](btc-4h-fib-20171228-correction-20260615.md)
- [20250506 dedup](btc-4h-fib-20250506-dedup-20260615.md)
- [next-research-plan](btc-source-fib-next-research-plan-20260615.md)
- [reviews README](README.md)

## Final corpus declaration

- **Active facit (BTC/USD source fibs):** 1M=9, 1w=21, 1d=67, 4h=365 — **462 total**, log
  scale, `tradingview_log_chamoun`, no 0.236, human/manual. Coverage (anchor-derived)
  2016-12-29 → 2026-06-07.
- **Superseded:** `fib_BTC-USD_4h_20250506T080000` (1 fib, provenance in ledger only).
- **Deferred:** 1H source labeling (cache not fetched); ETH/USD (blocked until BTC sign-off);
  full exhaustive per-fib Tier 2 (sample-pass done).
- **Next analytical pass:** MTF confluence atlas (#1), first slice a read-only confluence
  table (no chart, no trading conclusions).

The BTC/USD source-fib corpus is **declared clean and locked as the research base.**

## Next pass recommendation

**#1 — MTF confluence atlas.** First slice: a **read-only confluence table** (no chart) —
for fixed log-price bands, list which TFs (1M/1W/1D/4H) have a level within ε over a shared
time window; counts only. Reuse `overlap_detector.py` (extend beyond 4H),
`monthly_fib_map.py` primitives, `render_summary.py` for verification. **No trading
conclusions, no auto-fib, no signal interpretation of clusters.** Full design + non-goals in
[next-research-plan](btc-source-fib-next-research-plan-20260615.md).
