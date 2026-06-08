# Reflections index

Kurerad översikt. Nya reflektioner: `YYYY-MM-DD-<kort-beskrivning>.md` (se [README](README.md)).

**Sök:** `rg` i denna mapp, eller filtrera på taggar i tabellen.

| Datum | Fil | Typ | Ämnen | Beslut / status |
|-------|-----|-----|-------|-----------------|
| 2026-05-28 | [branch-premortem](2026-05-28-branch-premortem.md) | premortem | risk, process | Branch-risker dokumenterade |
| 2026-05-28 | [premortem-mitigations](2026-05-28-premortem-mitigations.md) | decision | validate, drift | Mitigationer införda |
| 2026-05-28 | [labeling-worklist](2026-05-28-labeling-worklist.md) | decision | labeling | Worklist + 20–30-mål |
| 2026-05-28 | [real-data-matrix](2026-05-28-real-data-matrix.md) | run | validate, backtest | Fas 1 matris klar |
| 2026-05-29 | [machine-labeling](2026-05-29-machine-labeling.md) | decision | labeling | `source` human/machine infört |
| 2026-05-29 | [btc-1w-machine-approved](2026-05-29-btc-1w-machine-approved.md) | decision | labeling, BTC | Facit 1w godkänd (motor-swing) |
| 2026-05-29 | [mtf-daily-fib-research](2026-05-29-mtf-daily-fib-research.md) | decision | MTF, 1w, 1d, fib | Weekly VAD / daily HUR; multi-leg; 30× BTC 1d |
| 2026-05-29 | [fib-multi-behavior-per-level](2026-05-29-fib-multi-behavior-per-level.md) | **finding** | behavior, events, #12 | Samma nivå → flera events; v3; realign → Hypothesis A spot-check |
| 2026-06-01 | [hypothesis-a-spot-check-pilot](2026-06-01-hypothesis-a-spot-check-pilot.md) | run | #12, level_events, review | BTC 1d review_20260601T152524Z (40 events); labels pending |
| 2026-06-01 | [human-fib-annotation-layer](2026-06-01-human-fib-annotation-layer.md) | decision | labeling, fib, behavior | Human-fib ground truth + candidates (emit-only); atoms vs path |
| 2026-06-02 | [mtf-origin-1w-to-1d](2026-06-02-mtf-origin-1w-to-1d.md) | **finding** | MTF, 1w, 1d, origin | Chart-ursprung: samma H/L på 1d → fler nivåträffar; VAD vs HUR |

**Djupare guider:**

- **[docs/research/RESEARCH_HANDOFF.md](../../docs/research/RESEARCH_HANDOFF.md)** — scope + Hypothesis A ([GitHub #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12))
- [docs/labeling/MACHINE_LABELING.md](../../docs/labeling/MACHINE_LABELING.md) (fråga A vs chartfönster)
- [docs/research/MTF_DAILY_RESEARCH.md](../../docs/research/MTF_DAILY_RESEARCH.md) (MTF-lager, multi-leg, roadmap steg 1–4)

## Ämnesindex (snabbnavigering)

- **labeling:** worklist, machine-labeling, btc-1w-machine-approved, mtf-daily-fib-research → [MACHINE_LABELING.md](../../docs/labeling/MACHINE_LABELING.md), [MTF_DAILY_RESEARCH.md](../../docs/research/MTF_DAILY_RESEARCH.md)
- **MTF / 1w / 1d:** mtf-origin-1w-to-1d, mtf-daily-fib-research, fib-multi-behavior-per-level → [MTF_DAILY_RESEARCH.md](../../docs/research/MTF_DAILY_RESEARCH.md) §0, [BEHAVIOR_FACIT.md](../../docs/labeling/BEHAVIOR_FACIT.md)
- **behavior / events:** fib-multi-behavior-per-level, human-fib-annotation-layer → [HUMAN_FIB_ANNOTATION.md](../../docs/labeling/HUMAN_FIB_ANNOTATION.md)
- **validate / backtest:** real-data-matrix, premortem-mitigations
- **process / risk:** branch-premortem
