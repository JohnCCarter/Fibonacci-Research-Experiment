# Research handoff (start here for agents)

**Last updated:** 2026-05-31  
**Scope anchor:** [GitHub issue #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12) — research direction, not an implementation ticket.

---

## Active hypothesis (project decision)

**Hypothesis A (primary):**

```text
Can machine-generated fib-level event candidates approximate human review,
so the human only spot-checks/corrects — not labels every interaction from scratch?
```

**Not primary right now:** predictive edge (C), full outcome-mapping research (B as product), or large HTF/LTF architecture redesign (D in #12).

Document closure of #12 when: hypothesis chosen ✅, spot-check plan written ✅, drift boundaries recorded ✅.

---

## Original plan vs where we drifted

### Original track (issues #7, #8, PR #9, PR #11)

```text
HTF/leg fib grid  →  machine proposes level interactions (candidates + evidence)
                 →  human spot-check / correct a bounded sample
```

- **Issue #8:** same fib level visited multiple times → **event stream**, auto-detect, research-only.
- **PR #9 (intent):** `detect_level_events()`-style detector, walk-forward, candidate labels.
- **PR #11 (intent):** review pack (PNG/CSV) for **20–40 sampled events** — mobile spot-check, not a labeling campaign.
- **`auto_candidate` ≠ facit** (PR #7 semantics) — still valid.

### What we did in late May (useful but drifted)

| Activity | Verdict |
|----------|---------|
| Schema v3 `events[]` per level | ✅ **Keeps** — answers #8 (“not one label per level”) |
| Research finding: multiple behaviors per level over time | ✅ **Keeps** — same as #8 problem statement |
| Tmp sandbox + manual `human_label` in JSON from chart | ⚠️ **Drift Track A** — valid as pilot, not the main workflow |
| Treating `annotate` + bulk-approve as facit | ⚠️ Risk — machine must propose first; human **corrects** |
| Golden `1d-behavior.json` bulk human_label = auto | ⚠️ Not evidence for Hypothesis A (100% agreement by construction) |

**Realignment:** tmp/manual JSON = **exploratory** (learn the event model). **Primary path** = detector/candidates → bounded spot-check → then refine rules.

---

## One-minute context (data model)

| Layer | Role | Where |
|-------|------|--------|
| **Weekly / HTF** | Swing + fib **grid** (VAD / range) | `1w.json`, leg H/L → `derived_prices` |
| **Daily** | **Events** at grid lines (HUR over time) | `1d-behavior.json` → `levels[ratio].events[]` |
| **Machine** | Proposes interactions | `auto_candidate`, detector (PR #9 track), `behavior_facit annotate` (first-touch heuristic only) |
| **Human** | Facit on each reviewed event | `human_label` on event rows only |

**Motor / `evaluate()` / recall do NOT read behavior JSON or all `legs[]`. No promotion.**

---

## Top-down fib (VAD → HUR, neråt)

**Policy:** [HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md) · tracking: [GitHub #14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14)

```text
1w  VAD  — swing + fib-grid (facit-range)
 ↓
1d  HUR  — multi-leg + events[] at levels (facit today)
 ↓
4h  (plan) — finer structure inside a chosen 1d leg
 ↓
1h  (plan) — timing; never start here
```

**Built:** 1w + 1d (+ 1w→1d MTF). **Not built:** 4h/1h chain in code.

---

## Key research finding (still valid)

**Same fib level → multiple behaviors over time on Daily** (especially grid from a Weekly/longer leg).

→ **Schema v3** (`events[]`) is the right container.  
→ **Wrong workflow** = filling every event by hand before inspecting machine quality.

**Read:** [premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md)

---

## Correct workflow (going forward)

### 1. Structure (already have or tmp)

- Legs: `data/labels/binance/BTC-USDT/1d.json` (30 legs) **or** tmp subset.
- Do **not** restart mass manual labeling unless correcting machine output.

### 2. Machine first

- Run fib-level **event detection** on a **small** real sample (issue #8 / PR #9 track).
- If detector CLI is not on current branch, use interim heuristics:
  - `uv run python scripts/behavior_facit.py annotate ...` → one `auto_candidate` per level (weak; not multi-touch).
  - `uv run python scripts/mtf_leg_daily_fib.py` → descriptive touches (research scan, not facit).
- Prefer full detector when available on branch.

### 3. Human = spot-check only

- Target: **20–40 events total**, balanced across candidate types / levels where possible.
- Use review artifacts (PR #11 style) when present under `experiments/label_review/`.
- Human sets `human_label` only on sampled/corrected rows — not every bar on every leg.

### 4. Record observations (close #12)

Short note (premortem or issue comment):

- labels that look correct / wrong type / noisy / missing / unclear
- whether rules need refinement
- **Do not** open outcome-mapping, edge, or trading issues until this exists

---

## Docs (read order)

1. **This file** + [GitHub #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)
2. [HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md) — top-down 1w → 1d → 4h → 1h ([#14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14))
3. [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) — weekly VAD / daily HUR, multi-leg
4. [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md) — schema v3, validate, `auto_candidate` rules
5. [LABELING_TOOL.md](LABELING_TOOL.md) — legs only; `--labels-dir tmp`; fib on active leg only
6. [data/labels/tmp/README.md](../data/labels/tmp/README.md) — sandbox reset

**Index:** [premortem/reflections/INDEX.md](../premortem/reflections/INDEX.md)

---

## CLI cheat sheet

```powershell
# Leg structure (only if adding/changing H/L — not the main behavior workflow)
uv run python -m fibengine.labeling.tool --symbol BTC/USDT --timeframe 1d --labels-dir data/labels/tmp

# Behavior file (grid + event slots)
uv run python scripts/behavior_facit.py scaffold --labels-subdir tmp --research-subdir tmp --legs leg_1,leg_2 --symbol BTC/USDT --timeframe 1d
uv run python scripts/behavior_facit.py annotate --research-subdir tmp --symbol BTC/USDT --timeframe 1d
uv run python scripts/behavior_facit.py print --research-subdir tmp --symbol BTC/USDT --timeframe 1d

# Descriptive scan (not facit)
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USDT --timeframe 1w

# Hypothesis A spot-check (interactive chart, then summarize)
uv run python -m fibengine.research.human_review_level_events --symbol BTC/USD --timeframe 1d --max-events 40 --seed 7 --line
uv run python -m fibengine.research.level_event_review_tool --run-dir experiments/review/fib_level_events/<run_id>
uv run python scripts/summarize_human_review.py experiments/review/fib_level_events/<run_id>
```

**Rules:**

- `auto_candidate` ≠ facit — never bulk-copy to `human_label`.
- `scaffold` **replaces** the behavior file — list every `leg_id` you need.
- **Adding events:** append to `events[]` in JSON (multiple per level allowed); use `event_bar` + `human_label`.

---

## Current disk state (verify before work)

| Path | Note |
|------|------|
| `data/labels/tmp/.../1d.json` | Sandbox legs (e.g. leg_1, leg_2) |
| `data/labels/research/tmp/.../1d-behavior.json` | Schema 3; mostly `auto_candidate`, human pending |
| `data/labels/research/binance/.../1d-behavior.json` | Older pilot; v2-style bulk labels — **not** Hypothesis A evidence |
| `data/labels/binance/.../1d.json` | 30 production legs (structure) |

---

## Explicitly NOT started (do not open without new issue)

- Large-scale manual labeling (“mark every rejection/continuation on every leg”)
- Fas 5 agreement report (auto vs human **per event**) — after spot-check sample exists
- Outcome mapping after each event (Drift B)
- Predictive value / edge claims (Drift C)
- Motor reading `events[]` or prod promotion
- Trading / Genesis integration

---

## Drift boundaries (from #12)

| Track | Question | When |
|-------|----------|------|
| **A (active)** | Machine candidates ≈ human? | **Now** — spot-check 20–40 events |
| B | Event stream vs single label? | **Answered** — use `events[]`; validate with sample |
| C | Predictive value? | After A has evidence |
| D | HTF/LTF architecture | After detector output inspected |

---

## User prompt hint (next session)

```text
Read docs/RESEARCH_HANDOFF.md and GitHub issue #12.
Primary hypothesis A: machine fib-level event candidates, human spot-check only.
Continue schema v3 events[] — do not expand manual labeling or motor without explicit ask.
```
