# Closed questions — do NOT re-run on the same data

**Query this before proposing a behaviour/level-reaction study.** These questions are closed NULL
on the current BTC corpus. The binding rule: **do not re-run a closed study on the same data with
tweaked parameters** — any re-test must be a **new prereg on fresh data** (post-2026-06-05 bars or a
new symbol after sign-off) or a **materially different question**, and a re-look at the same window
requires [anytime-valid inference](../concepts/anytime-valid-evalues.md), not a fresh permutation.

| Question | Verdict | Why | Result doc |
|----------|---------|-----|-----------|
| Do fib retracement levels repel BTC more than placebo/swing? | **NULL / closed** | fib ≈ placebo ≈ swing; ~0.8 reject across all = generic mean-reversion | [behaviour results](../reviews/btc-fib-behaviour-event-study-results-20260616.md) |
| Do fib levels react differently **within trend/deep-retracement contexts**? | **NULL / no candidate** | nominal only, fails Holm, never beats swing | [context-conditioned results](../reviews/btc-fib-context-conditioned-study-results-20260616.md) |
| Does **generic** horizontal structure (swing / 1-2-5 round / prior-extreme) beat a **random-walk null**? | **NULL / closed** | `any_robust=False` on all 12 cells; only swing edges the null (e=1.70, not even marginal); low power for subtle effects | [B-1 results](../reviews/btc-horizontal-structure-event-study-results-20260617.md) |

**Cumulative read:** at this resolution, on this corpus, BTC's reaction to horizontal levels behaves
like a random walk. The repo's real strength is the rigorous null-hypothesis methodology, not a
confirmed level edge.

## Still open (not closed)

- **Fib selection-learning** — can a model reproduce *how the human selects swings/ranges*?
  Pre-registered, gated, **not run**:
  [prereg](../reviews/btc-fib-selection-learning-prereg-20260617.md). This is selection learning, a
  different question from the behaviour nulls — no edge claim.

> [Source authority](../reference/source-authority.md): the linked results docs + `log.md` are the
> evidence; this is the fast-path index into them.
