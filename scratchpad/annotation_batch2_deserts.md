# Contrastive annotation — batch 2: FACIT DESERTS (from the 2026-07-21 negative-audit)

Complement to [batch 1](annotation_batch1.md) (which targets structures you know). This batch
targets the **coverage holes** the
[implicit-negative audit](../docs/research_wiki/reviews/btc-fib-track-a-implicit-negative-audit-20260721.md)
found: 75 % of 4h implicit negatives sit in regions with no facit endpoint nearby, so the model
never learns what you *reject* there — and the deserts silently weaken every study's negative
set. One honest window in a desert is worth several in already-dense 2017.

Same workflow/keys as batch 1 (`--annotate-selection`, `h`/`l`, `1`/`2`/`3`, `t`, `e`, `v`).
**In each window:** if there IS a leg you'd draw — draw it accepted + 1–2 rejected neighbours
(normal contrast). If there is genuinely NOTHING you'd draw — mark the tempting candidates as
**rejected** with a reason (`no_clean_impulse`? use whatever tag fits): an explicit
"nothing here" is exactly the negative evidence the corpus lacks. Both outcomes are wins.

## Desert windows (ranked by audit desert size × era diversity)

| # | TF | window-start | window-end | why (audit) |
|---|----|--------------|------------|-------------|
| D1 | 4h | 2018-03-01 | 2018-11-30 | **Biggest desert: 1 652 bars, zero endpoints** (the 2018 bear grind — chop or drawable?) |
| D2 | 4h | 2022-06-15 | 2022-09-20 | 548-bar desert (post-Luna summer range) |
| D3 | 4h | 2023-03-15 | 2023-06-20 | 588-bar desert (2023 = thinnest year, 17 fibs) |
| D4 | 4h | 2019-12-15 | 2020-03-10 | 511-bar desert ending AT the COVID crash — where does the pre-crash structure end for you? |
| D5 | 4h | 2026-03-01 | 2026-06-05 | 570-bar desert, freshest era (recency check on your style) |
| D6 | 1d | 2025-01-01 | 2025-10-01 | 1d's biggest desert (294 bars) — also feeds the 1d context cells |
| D7 | 1d | 2018-04-01 | 2018-12-10 | 1d mirror of D1 (268 bars) — cross-TF read on the same hole |

Launch (one per TF, pan/zoom between D-windows):

```bash
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 4h --limit 8000 \
  --annotate-selection --config config/settings.expansion.yaml
uv run --no-sync python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1d --limit 3500 \
  --annotate-selection --config config/settings.expansion.yaml
```

Notes:
- These windows double as **grow-facit** candidates: if D-windows yield accepted legs you'd
  stand behind as source fibs, they can be drawn as normal facit too (separate pass, `w`) —
  that directly shrinks the desert metric.
- Batch 1's ~10-window consistency checkpoint still applies to the combined stream.
- Do NOT let this batch push total windows past the ≥30 goal alone — deserts are the
  *diversity* axis, batch 1 is the *known-structure* axis; the mix is the point.
