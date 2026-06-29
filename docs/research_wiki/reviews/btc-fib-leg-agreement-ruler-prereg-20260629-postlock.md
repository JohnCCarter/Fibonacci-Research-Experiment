# Post-lock addenda — leg-agreement ruler prereg (2026-06-29)

Append-only companion to the **locked** prereg
[`btc-fib-leg-agreement-ruler-prereg-20260629.md`](btc-fib-leg-agreement-ruler-prereg-20260629.md).
The locked file is immutable; build notes, the run result, and sign-off status live here so the
registration is never edited against its result.

### A1 — Build authorized under the lock (2026-06-29)

`evaluation/leg_agreement.py` (locked knobs: `mean`, absolute, `W=2`; secondary `min` + IoU fields;
best-match assignment) + unit tests for the synthetic sanity table + the 4h scoring run. Pending.

### Run result

_Pending build + run. The pre-lock calibration already shows AUC 0.968 at the locked knobs; the build
re-confirms `ruler_usable` with the committed module before any selector work._

### Status

_Not yet signed off._
