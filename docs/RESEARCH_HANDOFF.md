# Research handoff (start here for agents)

**Last updated:** 2026-06-02
**Scope anchor:** [GitHub issue #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12) â€” research direction, not an implementation ticket.

---

## Active hypothesis (project decision)

**Hypothesis A (primary):**

```text
Can machine-generated fib-level event candidates approximate human review,
so the human only spot-checks/corrects â€” not labels every interaction from scratch?
```

**Not primary right now:** predictive edge (C), full outcome-mapping research (B as product), or large HTF/LTF architecture redesign (D in #12).

Document closure of #12 when: hypothesis chosen âœ…, spot-check plan written âœ…, drift boundaries recorded âœ….

---

## Original plan vs where we drifted

### Original track (issues #7, #8, PR #9, PR #11)

```text
HTF/leg fib grid  â†’  machine proposes level interactions (candidates + evidence)
                 â†’  human spot-check / correct a bounded sample
```

- **Issue #8:** same fib level visited multiple times â†’ **event stream**, auto-detect, research-only.
- **PR #9 (intent):** `detect_level_events()`-style detector, walk-forward, candidate labels.
- **PR #11 (intent):** review pack (PNG/CSV) for **20â€“40 sampled events** â€” mobile spot-check, not a labeling campaign.
- **`auto_candidate` â‰  facit** (PR #7 semantics) â€” still valid.

### What we did in late May (useful but drifted)

| Activity | Verdict |
|----------|---------|
| Schema v3 `events[]` per level | âœ… **Keeps** â€” answers #8 (â€œnot one label per levelâ€) |
| Research finding: multiple behaviors per level over time | âœ… **Keeps** â€” same as #8 problem statement |
| Tmp sandbox + manual `human_label` in JSON from chart | âš ï¸ **Drift Track A** â€” valid as pilot, not the main workflow |
| Treating `annotate` + bulk-approve as facit | âš ï¸ Risk â€” machine must propose first; human **corrects** |
| Golden `1d-behavior.json` bulk human_label = auto | âš ï¸ Not evidence for Hypothesis A (100% agreement by construction) |

**Realignment:** tmp/manual JSON = **exploratory** (learn the event model). **Primary path** = detector/candidates â†’ bounded spot-check â†’ then refine rules.

---

## One-minute context (data model)

| Layer | Role | Where |
|-------|------|--------|
| **Weekly / HTF** | Swing + fib **grid** (VAD / range) | `1w.json`, leg H/L â†’ `derived_prices` |
| **Daily** | **Events** at grid lines (HUR over time) | `1d-behavior.json` â†’ `levels[ratio].events[]` |
| **Machine** | Proposes interactions | `auto_candidate`, detector (PR #9 track), `behavior_facit annotate` (first-touch heuristic only) |
| **Human** | Facit on each reviewed event | `human_label` on event rows only |

**Motor / `evaluate()` / recall do NOT read behavior JSON or all `legs[]`. No promotion.**

---

## Human-fib ground truth (manuell fib â†’ candidates)

Komplement till maskin-spÃ¥ret: mÃ¤nniskan **ritar** fiben och den Ã¤r facit. TvÃ¥ lager,
bÃ¥da deterministiska och research-only (motorn lÃ¤ser dem inte):

| Lager | Modul | Vad |
|-------|-------|-----|
| Annotering | `fibengine.labeling.human_fib` | Spara ankare + nivÃ¥er; klassa per candle `above/below/touch/cross`. `w` i labeling-tool eller CLI. |
| Behavior-candidates | `fibengine.labeling.human_fib_events` | Mata human-fib in i `detect_level_events` â†’ `*_candidate` per nivÃ¥ (samma taxonomi som [LEVEL_EVENTS.md](LEVEL_EVENTS.md)). |

Bryggan: `swing.start = anchor_a` (1.0), `swing.end = anchor_b` (0.0) â†’ identiska nivÃ¥priser;
fÃ¶nstret skannas efter legens slut. **Candidates Ã¤r aldrig facit.** Lagras under
`data/labels/human_fib/.../`. Detaljer: [HUMAN_FIB_ANNOTATION.md](HUMAN_FIB_ANNOTATION.md).

---

## Origin: why MTF exists (1w H/L, same range on 1d)

**Read first:** [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) **§0** · reflection: [2026-06-02-mtf-origin-1w-to-1d](../premortem/reflections/2026-06-02-mtf-origin-1w-to-1d.md)

The project did **not** start as “label many timeframes in parallel.” It started on **1w**:

1. Draw **H → L** on the weekly chart and place fib on that range (**VAD** — which impulse to measure).
2. On 1w you see price reach **some** fib levels on **some** weekly candles (few bars per period).
3. Put the **same H/L range** (same fib grid) on **1d** in the labeling tool → you suddenly see **many more** daily candles touching, crossing, or reacting at those levels (**HUR** — how price moves in detail).

| TF | Question | What you see |
|----|----------|--------------|
| **1w** | **VAD** — which swing / range? | Coarse: which levels matter for the impulse |
| **1d** | **HUR** — how does price behave? | More bars → more level interactions and legs |

**Implications for agents:**

- Weekly `1w.json` = range/grid context, not a substitute for daily behavior facit.
- Daily needs its own resolution: `legs[]`, `human_fib` (`w`), `*_events.json` — not “copy weekly H/L once and done.”
- `experiment` / motor swing recall does **not** test this observation; it compares one global swing to `leg_1`.

**One-liner:** *Same fib-range on 1w shows VAD; on 1d it shows HUR — more candles, more level interactions.*

---

## Top-down fib (VAD â†’ HUR, nerÃ¥t)

**Policy:** [HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md) Â· tracking: [GitHub #14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14)

```text
1w  VAD  â€” swing + fib-grid (facit-range)
 â†“
1d  HUR  â€” multi-leg + events[] at levels (facit today)
 â†“
4h  (plan) â€” finer structure inside a chosen 1d leg
 â†“
1h  (plan) â€” timing; never start here
```

**Built:** 1w + 1d (+ 1wâ†’1d MTF). **Not built:** 4h/1h chain in code.

---

## Key research finding (still valid)

**Same fib level â†’ multiple behaviors over time on Daily** (especially grid from a Weekly/longer leg).

â†’ **Schema v3** (`events[]`) is the right container.  
â†’ **Wrong workflow** = filling every event by hand before inspecting machine quality.

**Read:** [premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md](../premortem/reflections/2026-05-29-fib-multi-behavior-per-level.md)

---

## Correct workflow (going forward)

### 1. Structure (already have or tmp)

- Legs: `data/labels/bitfinex/BTC-USD/1d.json` (active) **or** tmp subset.
- Do **not** restart mass manual labeling unless correcting machine output.

### 2. Machine first

- Run fib-level **event detection** on a **small** real sample (issue #8 / PR #9 track).
- If detector CLI is not on current branch, use interim heuristics:
  - `uv run python scripts/behavior_facit.py annotate ...` â†’ one `auto_candidate` per level (weak; not multi-touch).
  - `uv run python scripts/mtf_leg_daily_fib.py` â†’ descriptive touches (research scan, not facit).
- Prefer full detector when available on branch.

### 3. Human = spot-check only

- Target: **20â€“40 events total**, balanced across candidate types / levels where possible.
- Use review artifacts (PR #11 style) when present under `experiments/label_review/`.
- Human sets `human_label` only on sampled/corrected rows â€” not every bar on every leg.

### 4. Record observations (close #12)

Short note (premortem or issue comment):

- labels that look correct / wrong type / noisy / missing / unclear
- whether rules need refinement
- **Do not** open outcome-mapping, edge, or trading issues until this exists

---

## Docs (read order)

1. **This file** + [GitHub #12](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/12)
2. [HTF_LTF_RESEARCH_ALIGNMENT.md](HTF_LTF_RESEARCH_ALIGNMENT.md) â€” top-down 1w â†’ 1d â†’ 4h â†’ 1h ([#14](https://github.com/JohnCCarter/Fibonacci-Research-Experiment/issues/14))
3. [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) â€” weekly VAD / daily HUR, multi-leg
4. [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md) â€” schema v3, validate, `auto_candidate` rules
5. [LABELING_TOOL.md](LABELING_TOOL.md) â€” legs only; `--labels-dir tmp`; fib on active leg only
6. [data/labels/tmp/README.md](../data/labels/tmp/README.md) â€” sandbox reset

**Index:** [premortem/reflections/INDEX.md](../premortem/reflections/INDEX.md)

---

## CLI cheat sheet

```powershell
# Leg structure (only if adding/changing H/L â€” not the main behavior workflow)
uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1d --labels-dir data/labels/tmp

# Behavior file (grid + event slots)
uv run python scripts/behavior_facit.py scaffold --labels-subdir tmp --research-subdir tmp --legs leg_1,leg_2 --symbol BTC/USD --timeframe 1d
uv run python scripts/behavior_facit.py annotate --research-subdir tmp --symbol BTC/USD --timeframe 1d
uv run python scripts/behavior_facit.py print --research-subdir tmp --symbol BTC/USD --timeframe 1d

# Descriptive scan (not facit)
uv run python scripts/mtf_leg_daily_fib.py --symbol BTC/USD --timeframe 1w

# Hypothesis A spot-check (interactive chart, then summarize)
uv run python -m fibengine.research.human_review_level_events --symbol BTC/USD --timeframe 1d --max-events 40 --seed 7 --line
uv run python -m fibengine.research.level_event_review_tool --run-dir experiments/review/fib_level_events/<run_id>
uv run python scripts/summarize_human_review.py experiments/review/fib_level_events/<run_id>
```

**Rules:**

- `auto_candidate` â‰  facit â€” never bulk-copy to `human_label`.
- `scaffold` **replaces** the behavior file â€” list every `leg_id` you need.
- **Adding events:** append to `events[]` in JSON (multiple per level allowed); use `event_bar` + `human_label`.

---

## Current disk state (verify before work)

| Path | Note |
|------|------|
| `data/labels/tmp/.../1d.json` | Sandbox legs (e.g. leg_1, leg_2) |
| `data/labels/research/tmp/.../1d-behavior.json` | Schema 3; mostly `auto_candidate`, human pending |
| `archive/data_labels_Bitfinex/labels/research/Bitfinex/.../1d-behavior.json` | Older pilot; v2-style bulk labels â€” **not** Hypothesis A evidence |
| `archive/data_labels_Bitfinex/labels/Bitfinex/.../1d.json` | Legacy 30-leg structure (historik) |

---

## Explicitly NOT started (do not open without new issue)

- Large-scale manual labeling (â€œmark every rejection/continuation on every legâ€)
- Fas 5 agreement report (auto vs human **per event**) â€” after spot-check sample exists
- Outcome mapping after each event (Drift B)
- Predictive value / edge claims (Drift C)
- Motor reading `events[]` or prod promotion
- Trading / Genesis integration

---

## Drift boundaries (from #12)

| Track | Question | When |
|-------|----------|------|
| **A (active)** | Machine candidates â‰ˆ human? | **Now** â€” spot-check 20â€“40 events |
| B | Event stream vs single label? | **Answered** â€” use `events[]`; validate with sample |
| C | Predictive value? | After A has evidence |
| D | HTF/LTF architecture | After detector output inspected |

---

## User prompt hint (next session)

```text
Read docs/RESEARCH_HANDOFF.md and GitHub issue #12.
Primary hypothesis A: machine fib-level event candidates, human spot-check only.
Continue schema v3 events[] â€” do not expand manual labeling or motor without explicit ask.
```

