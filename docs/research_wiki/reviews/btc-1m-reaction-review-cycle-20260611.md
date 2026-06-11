# BTC/USD 1M — Reaction-Review Cycle Summary

**Date:** 2026-06-11
**Protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
**Scope:** All 9 human-drawn BTC/USD 1M source fibs, reaction review after anchor B, 1D + 4H.

---

## Protocol Confirmations

- Source fibs remain **human-drawn 1M truth** — no anchor, level price, or ratio was modified.
- Reaction review scope: **anchor_b.time → review_end_time** (no pre-B history).
- `full_history=False` in all runs — review windows enforced via `review_windows.yaml`.
- No auto-fib promoted to facit.
- No nested fibs introduced.
- No trading edge is claimed; candidates are detection labels only.
- Pipeline used exclusively: `source_fib_projection_review` + `source_fib_projection_chart`.
- Profile: `tradingview_log_chamoun` · Scale: `log` · Levels: `0 · 0.382 · 0.5 · 0.618 · 0.786 · 1.0`.

---

## Per-Fib Summary

### fib_BTC-USD_1M_20201001T000000
| Field | Value |
|-------|-------|
| Direction | up |
| Anchor A → B | 2020-10-01 $10,391 → 2021-04-01 $64,829 |
| Review window | 2021-04-01 → 2021-06-01 |
| 1D events | 3 |
| 4H events | 3 |

**Observed pattern:** Narrow 2-month post-B window. Single 0.0 touch (Apr 14). Twin 0.382 touches (May 19 + 23). All three classified rejection. 1D and 4H counts identical — no additional granularity from 4H. Sparse, clean reaction zone.

---

### fib_BTC-USD_1M_20210401T000000
| Field | Value |
|-------|-------|
| Direction | down |
| Anchor A → B | 2021-04-01 $64,829 → 2021-06-01 $29,247 |
| Review window | 2021-06-01 → 2021-11-01 |
| 1D events | 18 |
| 4H events | 34 |

**Observed pattern:** Dense 5-month window. 0.382 active early (held below × 2) and late (held above). 0.618 was the most contested zone — 6 crosses on 1D, 13 events on 4H — highly volatile back-and-forth. 0.786 and 1.0 each crossed once late in the window. Levels successively engaged from 0.382 upward.

---

### fib_BTC-USD_1M_20211101T000000
| Field | Value |
|-------|-------|
| Direction | down |
| Anchor A → B | 2021-11-01 $68,958 → 2022-01-01 $32,937 |
| Review window | 2021-11-01 → 2022-11-01 |
| 1D events | 12 |
| 4H events | 20 |

**Observed pattern:** 12-month window. 0.382 dominant — multiple crosses and failures across Jan–Apr 2022, functioning as a repeatedly contested boundary. 0.5 engaged at window open and again late (Mar–Apr). 0.0 touched Jan 24 then decisively crossed May 9. Progressively deeper retracement across the full window.

---

### fib_BTC-USD_1M_20220401T000000
| Field | Value |
|-------|-------|
| Direction | down |
| Anchor A → B | 2022-04-01 $47,600 → 2022-11-01 $15,487 |
| Review window | 2022-11-01 → 2023-01-01 |
| 1D events | 1 |
| 4H events | 1 |

**Observed pattern:** Very narrow 2-month window. Single event: 0.0 touch Nov 21. No retracement levels engaged. Minimal post-B reaction observed within the defined scope.

---

### fib_BTC-USD_1M_20230101T000000
| Field | Value |
|-------|-------|
| Direction | up |
| Anchor A → B | 2023-01-01 $16,517 → 2023-07-01 $31,845 |
| Review window | 2023-07-01 → 2023-10-01 |
| 1D events | 2 |
| 4H events | 2 |

**Observed pattern:** 3-month window. 0.0 single touch Jul 13 (rejection). 0.382 single touch Aug 17 (reaction). Sparse. 1D and 4H counts identical. Two isolated level contacts; no cluster activity.

---

### fib_BTC-USD_1M_20231001T000000
| Field | Value |
|-------|-------|
| Direction | up |
| Anchor A → B | 2023-10-01 $26,562 → 2024-03-01 $73,666 |
| Review window | 2024-03-01 → 2024-08-01 |
| 1D events | 1 |
| 4H events | 2 |

**Observed pattern:** 5-month window. Minimal activity: 0.0 held-below on 1D (Mar 13); 4H resolves this as a held-below followed by a close touch the next session (Mar 14). Price remained well above retracement levels throughout.

---

### fib_BTC-USD_1M_20240801T000000
| Field | Value |
|-------|-------|
| Direction | up |
| Anchor A → B | 2024-08-01 $49,130 → 2024-12-01 $108,100 |
| Review window | 2024-12-01 → 2025-04-01 |
| 1D events | 4 |
| 4H events | 5 |

**Observed pattern:** 4-month window. 0.0 tested twice (Dec 17, Jan 20). 0.382 showed a 1D touch (Feb 28) which on 4H resolves as a cross — level briefly breached intraday — followed by a held-above sequence (touch Mar 10, above Mar 13). 4H adds one extra event and sharpens the 0.382 interaction from touch to cross+recovery.

---

### fib_BTC-USD_1M_20250401T000000
| Field | Value |
|-------|-------|
| Direction | up |
| Anchor A → B | 2025-04-01 $74,501 → 2025-08-01 $123,640 |
| Review window | 2025-08-01 → 2026-01-01 |
| 1D events | 9 |
| 4H events | 28 |

**Observed pattern:** 5-month window, highest event density in the cycle. 0.0 re-approached in Oct via a 7-event 4H cluster (cross/touch sequence Oct 3–9). 0.382 and 0.5 each saw brief engagement (Nov). 0.618 was the dominant zone — 13 4H events spanning Nov 18 → Dec 29 — including repeated crosses, touches, and holds. 0.786 touched once (Nov 21). Deepest multi-level retracement in the dataset.

---

### fib_BTC-USD_1M_20260101T000000
| Field | Value |
|-------|-------|
| Direction | down |
| Anchor A → B | 2026-01-01 $97,850 → 2026-02-01 $60,100 |
| Review window | 2026-02-01 → 2026-06-08 (latest cache) |
| 1D events | 12 |
| 4H events | 32 |

**Observed pattern:** Final fib; window extends to latest available 1D cache (2026-06-08). 0.382 ($72,400) and 0.5 ($76,686) were both heavily active — 13 and 12 4H events respectively — with extended oscillation between the two levels from Feb through late May. 0.618 engaged in May (4 events). 0.0 touched at window open (Feb 6) and again near end (Jun 5). Window remains open; no forward inference made.

---

## Event Count Overview

| Fib ID | Dir | A→B | Review Window | 1D | 4H |
|--------|-----|-----|---------------|----|----|
| 20201001 | up | $10,391→$64,829 | 2021-04-01 → 2021-06-01 | 3 | 3 |
| 20210401 | down | $64,829→$29,247 | 2021-06-01 → 2021-11-01 | 18 | 34 |
| 20211101 | down | $68,958→$32,937 | 2021-11-01 → 2022-11-01 | 12 | 20 |
| 20220401 | down | $47,600→$15,487 | 2022-11-01 → 2023-01-01 | 1 | 1 |
| 20230101 | up | $16,517→$31,845 | 2023-07-01 → 2023-10-01 | 2 | 2 |
| 20231001 | up | $26,562→$73,666 | 2024-03-01 → 2024-08-01 | 1 | 2 |
| 20240801 | up | $49,130→$108,100 | 2024-12-01 → 2025-04-01 | 4 | 5 |
| 20250401 | up | $74,501→$123,640 | 2025-08-01 → 2026-01-01 | 9 | 28 |
| 20260101 | down | $97,850→$60,100 | 2026-02-01 → 2026-06-08† | 12 | 32 |
| **Total** | | | | **62** | **127** |

† Window open; ends at latest available cache candle, not a macro boundary.

---

## Review Artifacts

All artifacts under `experiments/review/source_fib_projection/<fib_id>/`:
- `REVIEW_INDEX.md` — levels + event list per TF
- `review_sample.csv` / `review_sample.jsonl` — structured event rows
- `summary.json` — run metadata
- `charts/human_fib/` — clean candle + fib charts (1d, 4h)
- `charts/events/` — event-marker overlay charts (1d, 4h)
- `charts/zoom/` — anchor zoom + event cluster zooms (1d, 4h)
