# Fib-aware Annotation/Review Tooling Spike

## Decision Question

What is the smallest tool we can build that lets Chamoun review human fib anchors,
fib levels, level events, and behavior candidates without fighting the current
labeling tool?

## Current Baseline

The repo already has the important data boundary:

- Human-drawn fib anchors are saved as JSON by `fibengine.labeling.human_fib`.
- Candidate events are saved as JSON by `fibengine.labeling.human_fib_events`.
- The review package in `fibengine.research.human_review_level_events` can render
  PNG charts and review sheets.
- The interactive reviewer in `fibengine.research.level_event_review_tool` gives
  pan/zoom and keyboard labels, but it is still Matplotlib-bound.

The missing piece is not new trading logic. It is a clearer and faster review
surface over the saved JSON data.

## Evaluation

| Option | Candles | Fib overlays and labels | JSON import/export | Review speed | Maintenance fit |
|--------|---------|-------------------------|--------------------|--------------|-----------------|
| Extend current Matplotlib review | Good enough, already present | Good for labels and PNGs | Excellent, already JSON-first | Acceptable for bounded review, slower for heavy pan/zoom | Best short-term fit, no new stack |
| Static HTML export with embedded data | Good if using a small JS chart lib | Good, can draw custom labels | Good, write one HTML per review pack | Fast enough for review, no server | Good next prototype if Matplotlib remains sluggish |
| Python + Plotly/Dash | Good | Good annotations | Good | Usually good, but server adds friction | Adds heavier deps and a web app shape |
| Python + Bokeh/Panel | Good | Good annotations | Good | Usually good | Adds heavier deps and server/runtime choices |
| React + chart library | Excellent with the right library | Excellent | Good | Fast | Adds Node/frontend toolchain to a Python research repo |
| TradingView Lightweight Charts | Excellent | Good, but custom fib/event labels need glue | Good | Fast | Viable library choice, not a product requirement |

## Recommendation

Do not replace the labeling tool yet.

The smallest safe path is:

1. Keep human-drawn fib JSON as the source of truth.
2. Improve the existing review package so it renders H/L anchors, all fib levels,
   raw relations, and `*_candidate` labels from saved human-fib event JSON.
3. Use the improved PNG/index workflow for near-term review.
4. If pan/zoom remains the bottleneck, prototype a static HTML review artifact
   that reads the same JSON shape and writes the same review rows.

This keeps the research workflow inside the current repo and avoids committing
to Dash, Panel, React, or TradingView before the review schema is stable.

## Minimal Prototype Proposal

Build a generated review artifact, not a platform:

- Input: cached candles, `<fib_id>.json`, and `<fib_id>_events.json`.
- View: candlesticks, H/L anchor labels, all fib levels, and event labels like
  `0.618 touch -> rejection_candidate`.
- Output: the existing `review_sample.csv` / `review_sample.jsonl` pattern, with
  optional human review fields left blank.
- Scope: one or more saved fib event files, offline-first, no network fetch.

The prototype should be disposable if the current Matplotlib flow becomes good
enough after the fib-aware label improvements.

## Do Not Build Yet

- No auto-fib detection.
- No buy/sell signals, alerts, PnL, or edge claims.
- No ML/AI behavior classifier.
- No replacement for `fibengine.labeling.tool`.
- No database, hosted web service, login, or multi-user workflow.
- No broad frontend stack until the JSON review contract proves useful.

## Recommended Next Step

Use the updated review renderer as the first implementation path. Reassess only
after a manual smoke review of several saved human-fib event files shows whether
Matplotlib pan/zoom is still the main blocker.

## Smoke outcome (2026-06-05)

First smoke: `human_fib_review_20260605T064610Z` from
`fib_ETH-USD_1d_20170618T000000_events.json` (10 events). PNG charts meet #15
acceptance (H/L anchors, fib levels, relation vs candidate, `fib_id`). **Matplotlib
PNG workflow is sufficient for bounded review**; no new UI stack yet. Distilled
notes: [research wiki smoke page](research_wiki/reviews/2026-06-05-eth-1d-human-fib-smoke.md).
