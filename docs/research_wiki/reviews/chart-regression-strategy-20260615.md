# Chart Regression Strategy (2026-06-15)

Research / design spike (Issue #32 evaluate-later). **Docs-only — no code, no deps, no
artifacts, no binary baselines.** Goal: a lightweight, repo-native way to catch accidental
changes in chart rendering without breaking the anti-blob policy or committing PNG
baselines.

Scope guards honored: no 1H, no reaction-review, no auto-fib, no source-label changes, no
heavy deps, no web dashboards.

---

## Observed

- The repo **already does structural contract testing extensively**: ~170 structural
  assertions across 22 test files under `tests/research/` assert rendered/skipped counts,
  output filenames (`4h_clean.png` / `4h_levels.png`), path/scope structure, fib_id
  selection, level endpoint values, and (for the gallery) relative-link strings + layout
  grouping. Examples: `test_fourh_source_fib_zoom.py` (counts, filenames, parent==scope,
  file exists + size>1000), `test_fourh_source_fib_map.py` (group split, skip surfacing),
  `test_artifact_gallery.py` (relative links, map/zoom layouts), `test_overlap_detector.py`,
  `test_review_ledger.py`.
- Render flows in play: 4H source fib map, 4H source fib zoom, weekly/monthly map/zoom/
  projection, static HTML gallery, correction preview flow, single-fib declutter edit-mode.
- Generated PNGs are gitignored under `experiments/review/**`; `check_repo_bounds.py`
  fails the build if a binary/blob is tracked (anti-blob policy is enforced, not advisory).
- Render dataclasses already carry the contract data: `FourhSourceFibZoom`
  (scope, artifacts, fib_count, rendered, skipped), `GroupArtifacts`/`FourhSourceFibMap`
  (label, fib_count, drawn, clean/levels paths, window_start/end, skipped). The map module
  also writes a **text** index (`fourh_source_fib_map_index.md`).
- `matplotlib` is already a dependency (so `matplotlib.testing.compare.compare_images` is
  available transitively); `pytest-mpl` is **not** installed.

## Inferred

- The cheapest, highest-value regression layer is **the one we already use** — assert on
  the structured return values and text outputs, not on pixels. The render dataclasses are
  effectively a render *contract*; we should test them deliberately and consistently.
- Pixel regression answers a question we are not currently asking ("did a pixel move?").
  Our real risks are *structural*: wrong counts, wrong anchors/levels, wrong filenames,
  broken pairing/links, wrong scope/grouping — all observable from the contract data and
  text outputs **without** rendering pixels.
- Binary baselines (any flavor) collide with the anti-blob policy and `check_repo_bounds`.
  Local-only baselines aren't shareable and rot across machines/matplotlib versions.

## Unverified

- Exact cross-version stability of `compare_images` / `pytest-mpl` on this Windows +
  matplotlib stack (assumed flaky from general experience; not benchmarked here).
- Whether any flow needs *true pixel* fidelity (e.g. a future presentation export). None
  identified today.

---

## Alternatives compared

| Approach | Catches | Deps | Blob risk | Flaky | Verdict |
|----------|---------|------|-----------|-------|---------|
| **Structural contract tests** (assert dataclass counts/ids/levels/filenames/paths) | counts, skip, anchors via levels, filenames, pairing, scope/grouping | none | none | no | **Adopt now (extend existing)** |
| **Text/metadata snapshots** (golden JSON/markdown of a render summary) | drift in any contract field; index/gallery content | none (stdlib `json`) | none (text, git-diffable) | no | **Adopt now** |
| **PNG dimension check** (parse PNG IHDR width/height, stdlib) | chart dimensions only | none | none | low | Optional add-on |
| **`matplotlib.testing.compare`** | pixel drift | none new (transitive) | **needs committed PNG baselines** | yes (AA/fonts/backends) | **Defer** |
| **`pytest-mpl`** | pixel drift | **new dep** | needs baselines | yes | **Defer** |
| **Image / perceptual hash** | gross pixel drift | **new dep (imagehash)** | hash files small, but value low | version-sensitive | **Reject** |
| **Manual visual** (HTML gallery + ledger + correction reports) | anything a human sees | none | none (gitignored PNGs) | n/a | **Already in place — keep as the visual layer** |

## Risks

- **Snapshot churn:** golden snapshots that include volatile fields (timestamps,
  full-precision floats, absolute paths) produce noisy diffs. Mitigate: snapshot only
  stable contract fields, round level prices, store repo-relative paths.
- **False confidence:** structural tests do not catch a genuinely visual regression (e.g.
  a color/marker change). That is exactly what the HTML gallery + manual review covers —
  the two layers are complementary, not redundant.
- **Scope creep into pixel testing** without a real pixel bug would import flakiness and
  the blob problem for little gain.

---

## Recommendation

1. **Now — structural chart-contract tests (extend the existing pattern).** Make the
   render dataclasses the explicit contract: per flow, assert rendered/skipped counts,
   the full fib_id list, output filenames, clean/levels pairing, scope/grouping, and level
   endpoint values. Most of this exists; the gap is *consistency* across all flows.
2. **Now — text/metadata snapshots.** Add a small, stable `render summary` (dict →
   committed golden JSON, or reuse the existing markdown index) and golden-test its
   content. Text, git-diffable, no blobs. Round floats, repo-relative paths, drop
   timestamps.
3. **Keep — manual visual regression** via the static HTML gallery + review-ledger +
   correction reports. This is the visual layer; it already caught and tracked the
   20171228 case end-to-end.
4. **Defer — pixel regression** (`pytest-mpl` / `matplotlib.testing.compare`) until a
   concrete pixel-fidelity need appears. Revisit only with an explicit decision on where
   baselines live (and they must not be committed blobs).
5. **Reject — image/perceptual hashing** (new dep, version-sensitive, lower value than
   structural for our risks).
6. **No binary baselines committed now.**

### Do now vs defer

- **Do now:** nothing in code yet (this is a spike). The concrete next step is a small,
  well-scoped implementation issue (below) — kept separate so this stays docs-only.
- **Defer:** all pixel-diff tooling and any baseline storage decision.

---

## Suggested follow-up issue

**#F — Structural chart-contract + metadata-snapshot tests (stdlib).**
- Define a `render_summary()` (or reuse the dataclasses) emitting a stable dict per flow:
  `{flow, scope, fib_count, rendered, skipped, fib_ids, filenames, levels?, window}`.
- Add golden-JSON snapshot tests (committed text) for map + zoom + gallery, plus a golden
  test of the markdown index content.
- Optional: stdlib PNG-IHDR dimension assertion for one representative chart per flow.
- Acceptance: no new deps, no committed PNGs, deterministic, git-diffable snapshots.

---

## Conclusion

We land on **structural regression first, not pixel regression** — which matches both the
repo's existing testing style (170 structural assertions already) and the anti-blob policy.
Pixel/baseline approaches are deferred until a real pixel need is demonstrated. This report
adds no code, no dependencies, no artifacts, and no source-label changes.
