"""One-off: machine swing candidate for BTC/USD 1w in a chart window (does not overwrite human)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fibengine.core.config import load_settings
from fibengine.core.scoring import select_swing
from fibengine.data.loader import load_candles
from fibengine.labeling.autolabel import MACHINE_NOTE, label_from_swing
from fibengine.labeling.store import find_label, save_label

WINDOW_START = pd.Timestamp("2026-03-23", tz="UTC")
WINDOW_END = pd.Timestamp("2026-05-04", tz="UTC")
WARMUP_WEEKS = 80


def main() -> None:
    settings = load_settings()
    cfg = settings.data.model_copy(update={"symbol": "BTC/USD", "timeframe": "1w"})
    df = load_candles(cfg)
    warmup = WINDOW_START - pd.Timedelta(weeks=WARMUP_WEEKS)
    slice_df = df.loc[(df.index >= warmup) & (df.index <= WINDOW_END)].copy()
    start_d = slice_df.index[0].date()
    end_d = slice_df.index[-1].date()
    print(f"Candles in slice: {len(slice_df)} ({start_d} .. {end_d})")

    existing = find_label("Bitfinex", "BTC/USD", "1w")
    if existing:
        src = getattr(existing, "source", "human")
        print(
            f"Existing canonical label: source={src} "
            f"high={existing.high.timestamp} low={existing.low.timestamp}"
        )

    swing = select_swing(slice_df, settings.pivots, settings.scoring)
    if swing is None:
        print("STATUS: no_swing")
        raise SystemExit(1)

    label = label_from_swing(swing, "Bitfinex", "BTC/USD", "1w")
    label.note = (
        f"{MACHINE_NOTE} | chartfÃ¶nster {WINDOW_START.date()}â€“{WINDOW_END.date()} (weekly)."
    )

    out_dir = Path("experiments/runs/experiment/2026-05-29/btc_1w_machine_window")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "written",
        "window_start": WINDOW_START.isoformat(),
        "window_end": WINDOW_END.isoformat(),
        "candles_used": len(slice_df),
        "label": {
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
            "high": {"timestamp": label.high.timestamp, "price": label.high.price},
            "low": {"timestamp": label.low.timestamp, "price": label.low.price},
            "note": label.note,
            "source": label.source,
        },
    }
    out_path = out_dir / "candidate.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["label"], indent=2))
    print(f"Review artifact -> {out_path}")

    if existing and getattr(existing, "source", "human") == "human":
        print(
            "Canonical data/labels/Bitfinex/BTC-USD/1w.json unchanged (human facit). "
            "Open labeling.tool to compare; press 's' to promote a revised human label."
        )
    else:
        path = save_label(label)
        print(f"Saved machine label -> {path}")


if __name__ == "__main__":
    main()
