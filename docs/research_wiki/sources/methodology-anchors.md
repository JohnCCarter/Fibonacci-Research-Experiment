# Methodology anchors (external sources we rely on)

Peer-reviewed / primary sources the repo's methods are anchored to. Cite these for provenance
instead of re-deriving. Each links to the concept page where we apply it.

| Source | What it gives us | Applied in |
|--------|------------------|-----------|
| **Lo, Mamaysky & Wang (2000)**, "Foundations of Technical Analysis…", *Journal of Finance* 55(4):1705–1765 | Support/resistance + chart formations arise spontaneously in random walks → a level-reaction claim must beat a random-walk null | [random-walk-null.md](../concepts/random-walk-null.md) (NU-1) |
| **Johari, Pekelis & Walsh**, "Always Valid Inference: Continuous Monitoring of A/B Tests," arXiv:1512.04922 | Anytime-valid inference lineage (always-valid p-values / confidence sequences) for re-looks at a peeked window | [anytime-valid-evalues.md](../concepts/anytime-valid-evalues.md) (NU-2) |
| **Grünwald, de Heide & Koolen (2024)**, *Safe Testing* | e-value / test-by-betting framework; `E[E] ≤ 1` under H0 as the defining property | [anytime-valid-evalues.md](../concepts/anytime-valid-evalues.md) |
| **Turner, Ly & Grünwald**, two-sample / 2×2 safe tests | The conditional 2×2 e-value construction (exact at every N) we pinned over mSPRT | [anytime-valid-evalues.md](../concepts/anytime-valid-evalues.md) |
| **López de Prado (2018)**, *Advances in Financial Machine Learning*, Ch. 12 | Purging / embargo / combinatorial purged CV vocabulary + leakage-safe OOS split | [purged-embargoed-cv.md](../concepts/purged-embargoed-cv.md) (NU-3) |

NU-1..NU-3 are the standing requirements in the
[horizontal-structure prereg addendum](../reviews/horizontal-structure-prereg-addendum-20260617.md).

> [Source authority](../reference/source-authority.md): these are external anchors; the repo's own
> code/preregs are the operative truth for what we actually run.
