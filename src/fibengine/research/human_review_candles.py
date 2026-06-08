"""Shared mplfinance candle rendering for Fib review charts (PNG + interactive)."""

from __future__ import annotations

import mplfinance as mpf
import pandas as pd

# Match labeling.tool / review palette (single source for up/down bodies).
CANDLE_UP = "#26a69a"
CANDLE_DOWN = "#ef5350"
CANDLE_WICK_LIGHT = "#c7cedb"
FACE_LIGHT = "white"
FACE_DARK = "#0f1117"


def review_mpf_style(*, dark_theme: bool = False) -> mpf.MPFStyle:
    face = FACE_DARK if dark_theme else FACE_LIGHT
    wick = CANDLE_WICK_LIGHT if dark_theme else "inherit"
    return mpf.make_mpf_style(
        marketcolors=mpf.make_marketcolors(
            up=CANDLE_UP,
            down=CANDLE_DOWN,
            edge="inherit",
            wick=wick,
        ),
        facecolor=face,
        edgecolor=face,
        gridcolor="#3a4150" if dark_theme else "#e0e0e0",
        rc={"axes.labelcolor": "#9aa3b2" if dark_theme else "black"},
    )


def _ohlcv_frame(df: pd.DataFrame) -> pd.DataFrame:
    plot_df = df[["open", "high", "low", "close", "volume"]].copy()
    if not isinstance(plot_df.index, pd.DatetimeIndex):
        plot_df.index = pd.to_datetime(plot_df.index, utc=True)
    return plot_df


def draw_mplfinance_candles(ax, df: pd.DataFrame, *, dark_theme: bool = False) -> None:
    """Draw OHLCV candles on ``ax``; x positions are ``0 .. len(df)-1``.

    Callers using absolute bar indices for fib overlays should pass the same
    ``df`` slice (full series or window) and set overlay ``x_shift`` when the
    window does not start at bar 0.
    """
    plot_df = _ohlcv_frame(df)
    mpf.plot(
        plot_df,
        type="candle",
        ax=ax,
        volume=False,
        style=review_mpf_style(dark_theme=dark_theme),
        datetime_format="",
        xrotation=0,
        warn_too_much_data=max(99999, len(plot_df)),
    )


def draw_review_candles(
    ax,
    df: pd.DataFrame,
    *,
    candlestick: bool = True,
    dark_theme: bool = False,
) -> None:
    """Shared entry: mplfinance candles or close-line fallback (``--line``)."""
    if candlestick:
        draw_mplfinance_candles(ax, df, dark_theme=dark_theme)
        return
    close_color = "#d6d9e0" if dark_theme else "black"
    ax.plot(range(len(df)), df["close"].to_numpy(), color=close_color, lw=1.0)
