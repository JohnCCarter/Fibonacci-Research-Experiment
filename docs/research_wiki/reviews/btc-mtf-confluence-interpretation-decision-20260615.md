# BTC/USD MTF Confluence — Interpretation & Decision Note (2026-06-15)

Docs-only synthesis of the MTF-confluence track (CP1 → CP2 → CP3). Answers two questions:
**what did CP1–CP3 actually establish, and what should the next research decision be?** No new
code, charts, cards, atlas expansion, or claims.

Inputs: [CP1 table](btc-mtf-confluence-table-20260615.md) ·
[CP2 sensitivity](btc-mtf-confluence-sensitivity-20260615.md) ·
[CP3 capstone](btc-mtf-confluence-atlas-cp3-20260615.md) ·
[corpus integrity](btc-source-fib-corpus-integrity-20260615.md).

## Observed (facts only)

- **Corpus:** 462 active source fibs → 2772 level rows (1M=9, 1w=21, 1d=67, 4h=365);
  superseded `20250506` absent. Corpus declared clean (integrity capstone).
- **CP1 (single-linkage, ε=0.005):** 222 cross-TF clusters — 2×4-TF, 24×3-TF, 196×2-TF.
  Dense TFs dominate (`1d,4h` = 143/222, 64%). 30/222 exceed ε (chaining). span_log median
  0.00199, max 0.01643.
- **CP2 (sensitivity, predeclared ε 0.0025/0.005/0.01):** single-linkage count 173→222→266;
  chaining 7%→14%→26%. **Fixed-band** (complete-linkage in price) removes all over-ε clusters
  by construction → 144/188/242; 4-TF under fixed-band 1/1/0. At primary ε, 192/222 clusters
  intact. **c001** (~29 274) survives as a tight 4-TF under both methods (span 0.00123).
  **c002** (~21 167) does **not**: its 4-TF status exists only under single-linkage and is
  itself chained (span 0.00627 > ε); under fixed-band it dissolves into 2-TF fragments.
- **CP3 (visual atlas, first pack):** 5 cards across 3 archetypes — c001 robust fixed-band
  4-TF; c002 chaining-dependent single-linkage contrast (never labelled tight); c004/c006/c007
  zero-span exact-price 3-TF (~$64 829/$13 764/$9 085). **All human-approved 2026-06-15.**
- **Caveats on record:** cluster ids are positional (signature-resolved selection); dense-TF
  bias by construction; every card asserts geometry only — **no** edge/signal/support-resistance.

## Inferred (cautious)

- MTF confluence **exists as geometry** in the human corpus — not rare, not a chaining
  artifact (188 fixed-band clusters survive at primary ε).
- **c001** shows a tight, epsilon- and method-stable multi-TF confluence *can* exist.
- **c002** shows single-linkage **can overstate strength**: a region of loose 2-TF pairings
  chained into an apparent 4-TF point. Definition choice materially changes the headline.
- **Zero-span** clusters show some human-drawn levels coincide at the *exact* price across
  3 TFs — immune to epsilon and chaining.
- None of this demonstrates **edge, support/resistance, or predictive value**. These are
  coincidences of human-drawn endpoints, measured structurally.

## Unverified (open)

- Whether confluence has any **price-behaviour effect** (reaction, hold, reversal).
- Whether fixed-band clusters are more useful than **random/naïve** price levels (no baseline).
- Whether the pattern **generalises to ETH/USD** or is BTC-corpus-specific.
- Whether **more visual cards** add information or only repeat the three known archetypes.
- Whether a **behaviour study** around clusters is worth its scope/over-interpretation risk.

## Decision options

| # | Option | Value | Risk | Scope-creep | Smallest safe slice | Rec |
|---|--------|-------|------|-------------|---------------------|-----|
| 1 | **Stop CP3 here, pause MTF track** | Locks a clean, honest result; zero new risk | Momentum loss (low — work is durable) | None | — (already at a closed capstone) | **YES** |
| 2 | Expand atlas with more fixed-band cards | More coverage | Confirmation-only; the 3 archetypes are known | Medium — "one more card" creep | 1 card, fixed-band, signature-resolved, explicit pick | **NO** (now) |
| 3 | Behaviour study around robust clusters | First step toward an actual edge question | High — needs a baseline + invites signal/edge framing the protocol forbids | High — reaction-review/auto-fib pull | Pre-register ONE falsifiable question + naïve-level control, read-only | **LATER** (only with a written question) |
| 4 | Start ETH/USD source-facit | Tests generalisation; new corpus | Large labeling effort; protocol blocks ETH until BTC sign-off | High | Defer; gated on BTC protocol approval | **LATER** |
| 5 | Pause Fib, return to Genesis/other | Spends effort where ROI may be higher | Context switch cost | None here | A scoped task in the other track | **CANDIDATE** |

## Recommendation

**Stop the MTF-confluence track here (Option 1).** CP1–CP3 answered their structural
question cleanly: multi-timeframe Fibonacci confluence **exists as geometry** in the BTC
corpus, a tight method-stable case exists (c001), single-linkage can overstate strength
(c002), and some levels coincide exactly (zero-span). That is a complete, honest finding —
and explicitly **not** evidence of edge.

- **Do not** expand the atlas now (Option 2) — more cards confirm, they do not inform.
- **Do not** start a behaviour study yet (Option 3). It is the only path to an *edge*
  question, but it carries real scope and over-interpretation risk and must not begin without
  a pre-registered, falsifiable question **and** a naïve-level baseline. Park it as a written
  candidate, not active work.
- **ETH/USD (Option 4)** stays gated on BTC protocol sign-off.

**Next active decision is a fork, not more atlas work:** either (a) **pause the Fib research
track** with this note as the closing summary, or (b) **open a new research track with one
clearly-stated, falsifiable question** — the strongest candidate being a behaviour study with
a naïve-level control (Option 3), but only once that question is written down. Recommend
surfacing this fork to the human rather than defaulting into either.

## Non-goals honoured

No new claims, trading, ML, tuning, atlas, 1H, reaction-review, or auto-fib. Docs-only;
counts quoted from CP1/CP2/CP3 committed outputs.
