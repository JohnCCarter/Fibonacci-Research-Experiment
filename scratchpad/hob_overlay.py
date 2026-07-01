"""Render HO-B on the 1h chart: Chamoun's drawing vs engine proposal.

Time axis + labels in Europe/Stockholm local time (matches Chamoun's TradingView);
candle lookup stays on the UTC cache. Saves a PNG to scratchpad.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles

TZ = "Europe/Stockholm"
settings = load_settings("config/variants/settings.1h_recent.yaml")
df = load_candles(settings.data, fetch_if_missing=False)

lo = pd.Timestamp("2026-06-16", tz="UTC")
hi = pd.Timestamp("2026-06-30 14:00", tz="UTC")
w = df[(df.index >= lo) & (df.index <= hi)].copy()
local = w.index.tz_convert(TZ)  # display labels
idx = {t: k for k, t in enumerate(w.index)}  # lookup by UTC ts


def lt(utc_str: str) -> str:
    return str(pd.Timestamp(utc_str, tz="UTC").tz_convert(TZ))[:16]


fig, ax = plt.subplots(figsize=(15, 8))
for k, (_, r) in enumerate(w.iterrows()):
    up = r["close"] >= r["open"]
    col = "#26a69a" if up else "#ef5350"
    ax.plot([k, k], [r["low"], r["high"]], color=col, lw=0.6, zorder=1)
    ax.add_patch(
        plt.Rectangle(
            (k - 0.3, min(r["open"], r["close"])),
            0.6,
            abs(r["close"] - r["open"]) or 1,
            color=col,
            zorder=2,
        )
    )


def mark(utc_ts, price, color, label, dy):
    k = idx.get(pd.Timestamp(utc_ts, tz="UTC"))
    if k is None:
        return
    ax.scatter([k], [price], s=90, color=color, zorder=5, edgecolors="white")
    ax.annotate(
        label,
        (k, price),
        textcoords="offset points",
        xytext=(6, dy),
        color=color,
        fontsize=9,
        fontweight="bold",
    )


# Chamoun's drawing (172932): origin 61,773 @ 25 jun 14:00 local -> reached ~58,134
ax.axhline(61773, color="#42a5f5", ls="--", lw=1, alpha=0.8)
ax.axhline(58134, color="#42a5f5", ls=":", lw=1, alpha=0.8)
mark("2026-06-25 12:00", 61773, "#42a5f5", "CHAMOUN origin 61,773 (25 jun 14:00)", 8)
ax.annotate(
    "CHAMOUN 0 = 58,134",
    (len(w) - 1, 58134),
    textcoords="offset points",
    xytext=(-160, -14),
    color="#42a5f5",
    fontsize=9,
    fontweight="bold",
)

# Engine proposal: origin 63,229 @ 24 jun 13:00 local -> reached 58,136 @ 25 jun 15:00 local
ax.axhline(63229, color="#ffa726", ls="--", lw=1, alpha=0.8)
mark("2026-06-24 11:00", 63229, "#ffa726", "ENGINE origin 63,229 (24 jun 13:00)", 10)
mark("2026-06-25 13:00", 58136, "#ffa726", "ENGINE 0 = 58,136 (25 jun 15:00)", -16)
mark("2026-06-17 16:00", 66279, "#ab47bc", "ENGINE parent 66,279 (17 jun 18:00)", 8)

ticks = [k for k, t in enumerate(local) if t.hour == 0]
ax.set_xticks(ticks)
ax.set_xticklabels([str(local[k])[5:10] for k in ticks])
ax.set_title(
    "HO-B on 1h (times = Europe/Stockholm): Chamoun (blue) vs engine (orange), parent (purple)"
)
ax.set_ylabel("price")
ax.grid(True, alpha=0.15)
out = "scratchpad/hob_overlay.png"
fig.tight_layout()
fig.savefig(out, dpi=110)
print(f"saved {out}  local range {local[0]} .. {local[-1]}")
