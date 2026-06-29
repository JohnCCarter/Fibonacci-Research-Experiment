"""#38 B-closure: run the pivot CONTROL coverage under BOTH window and fractal mode,
holding everything else fixed (expansion config, k=3, same causal cut, same facit), to:
  (1) determine which mode the recorded N=71 run actually used (reproduce both_hit=0.90), and
  (2) get the fractal-control coverage that postlock A4 only *assumed* (< 0.90, > wick 0.08).

Read-only over frozen daily facit; no --refresh, no edge claim. Reuses the locked harness's
own adapter + metric (evaluate_label_recall with injected producer) — mode is the only knob.
"""

import glob
import json

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.evaluation.pivot_recall import evaluate_label_recall
from fibengine.pivots.detect import detect_pivots
from fibengine.research.chamoun_wick_pair_accuracy import FACIT_GLOB, _facit_to_label

CONFIG = "config/settings.expansion.yaml"  # the config covering all 71 facit (start 2016)
K = 3
MODES = ("window", "fractal")

settings = load_settings(CONFIG)
print(
    f"config={CONFIG}  pivots.mode={settings.pivots.mode}  fractal_n={settings.pivots.fractal_n}  "
    f"lookback={settings.pivots.lookback}"
)

files = sorted(glob.glob(FACIT_GLOB))
hits = {m: [] for m in MODES}
n_cands = {m: [] for m in MODES}

for path in files:
    payload = json.loads(open(path).read())
    label = _facit_to_label(payload)
    data_cfg = settings.data.model_copy(
        update={"exchange": label.exchange, "symbol": label.symbol, "timeframe": label.timeframe}
    )
    df = load_candles(data_cfg)
    hi_bar, hi_ok = bar_of_timestamp(df, label.high.timestamp)
    lo_bar, lo_ok = bar_of_timestamp(df, label.low.timestamp)
    if not (hi_ok and lo_ok):
        continue
    cut = min(len(df), max(hi_bar, lo_bar) + K + 1)
    for mode in MODES:
        pcfg = settings.pivots.model_copy(update={"mode": mode})

        def producer(frame, _cut=cut, _pcfg=pcfg):
            return detect_pivots(frame.iloc[:_cut], _pcfg)

        cov = evaluate_label_recall(settings, label, pivot_producer=producer)
        hits[mode].append(1 if cov["both_hit"] else 0)
        n_cands[mode].append(cov["n_pivots"])

print(
    f"\nin-window facit: N={len(hits['window'])}  (wick-pair both_hit was 0.08 in the recorded run)"
)
for mode in MODES:
    xs = hits[mode]
    n = len(xs)
    rate = sum(xs) / n if n else float("nan")
    cands = n_cands[mode]
    med_c = sorted(cands)[len(cands) // 2] if cands else 0
    print(f"  control[{mode:7s}]  both_hit_rate={rate:.4f}  median_candidates={med_c}")
