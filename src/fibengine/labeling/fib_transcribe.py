"""Screenshot fib transcription helper — recover anchor *times* from anchor *prices*.

The human draws a fib on a chart (e.g. TradingView) and reads the two anchor **prices**
off the on-chart level labels (the ``0`` and ``1`` levels). This module recovers the
matching anchor **times** by matching each price to the candle whose extreme equals it,
then builds a **candidate** annotation for human review.

This is **transcription, not auto-fib**:

- The human supplies both anchor prices (from their own drawing). No detector picks them.
- The tool only recovers the *timestamp* of a supplied price by matching it to a candle
  high/low, and grades the match confidence (``exact`` / ``near`` / ``flag``).
- Output is a **candidate** (``created_by="vision_poc"``, ``_candidate=True``), printed or
  written to an explicit path. It is **never** facit and must never be written into
  ``human_fib/`` — the human reviews, fine-tunes, and promotes it via the labeling tool.

Level geometry, direction, and serialization are reused verbatim from
:mod:`fibengine.labeling.human_fib` so a candidate is structurally identical to facit.

Disambiguation & the ``n_within_near`` flag: when a price repeats on several candles the bar
is *guessed* by heuristic — the swing origin takes the earliest occurrence, the recent extreme
the first occurrence after the origin. Each match reports ``n_within_near`` (candles within
``NEAR_TOL``); **``n_within_near > 1`` means the bar was disambiguated by heuristic — verify it**.
Validated against the 71 daily facit fibs (price+time known): 95.8% both-anchor time match,
96.6% on repeated-price anchors; the few misses all carry ``n_within_near > 1``. The proper fix
for those is the vision step's rough x-position (deferred), which price+direction alone cannot
supply.

Run (CLI, no network — needs cached candles):
    uv run python -m fibengine.labeling.fib_transcribe \\
        --symbol BTC/USD --timeframe 1d --direction down \\
        --high-price 97850 --low-price 60096.6 \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.human_fib import FibAnchor, HumanFibAnnotation, make_annotation

# Match-confidence thresholds, as a fraction of the anchor price (|extreme - price| / price).
# exact: snapped to the candle extreme (sub-tick float noise only).
# near:  ~one candle's worth off — likely a finer-TF wick or a small read error; confirm.
# flag:  no candle extreme is close — projected/off-candle anchor; confirm manually.
EXACT_TOL = 2e-4  # 0.02 %
NEAR_TOL = 1e-3  # 0.10 %

CANDIDATE_CREATED_BY = "vision_poc"
CANDIDATE_SOURCE = "screenshot_vision_extraction"

_CONF_ORDER = {"exact": 0, "near": 1, "flag": 2}


@dataclass
class AnchorMatch:
    """One anchor price matched (or not) to a candle extreme."""

    price: float  # human-supplied price (kept verbatim in the annotation)
    role: str  # "high" or "low" — which candle column to match against
    time: str | None  # recovered candle timestamp (ISO-8601), or None if unmatched
    matched_extreme: float | None  # the candle high/low we matched to
    rel_delta: float | None  # |extreme - price| / price
    confidence: str  # exact / near / flag
    n_within_near: int  # how many candles sit within NEAR_TOL (ambiguity hint)


@dataclass
class TranscribeResult:
    annotation: HumanFibAnnotation | None  # None if either time could not be recovered
    matches: list[AnchorMatch]
    confidence: str  # worst of the per-anchor confidences


def match_anchor_time(
    df: pd.DataFrame,
    price: float,
    role: str,
    *,
    after: str | None = None,
    exact_tol: float = EXACT_TOL,
    near_tol: float = NEAR_TOL,
) -> AnchorMatch:
    """Match an anchor ``price`` to the candle whose ``role`` extreme is closest.

    ``role`` is ``"high"`` or ``"low"`` (which OHLC column to compare). ``after`` restricts
    the search to candles strictly after that timestamp — this disambiguates a price that
    occurs on several candles by enforcing the move's time order (the recent extreme comes
    after the swing origin).
    """
    if role not in ("high", "low"):
        raise ValueError(f"role must be 'high' or 'low', got {role!r}")
    sub = df
    if after is not None:
        sub = df[df.index > pd.to_datetime(after, utc=True)]
    if sub.empty:
        return AnchorMatch(price, role, None, None, None, "flag", 0)
    deltas = (sub[role] - price).abs() / price
    best_ts = deltas.idxmin()
    rel = float(deltas.loc[best_ts])
    confidence = "exact" if rel <= exact_tol else "near" if rel <= near_tol else "flag"
    return AnchorMatch(
        price=float(price),
        role=role,
        time=best_ts.isoformat(),
        matched_extreme=float(sub[role].loc[best_ts]),
        rel_delta=rel,
        confidence=confidence,
        n_within_near=int((deltas <= near_tol).sum()),
    )


def _worst(matches: list[AnchorMatch]) -> str:
    return max((m.confidence for m in matches), key=lambda c: _CONF_ORDER[c])


def transcribe_fib(
    df: pd.DataFrame,
    *,
    high_price: float,
    low_price: float,
    direction: str,
    symbol: str,
    timeframe: str,
    exchange: str = "bitfinex",
    exact_tol: float = EXACT_TOL,
    near_tol: float = NEAR_TOL,
) -> TranscribeResult:
    """Build a candidate annotation from two human-supplied anchor prices.

    The higher price matches a candle high, the lower a candle low. ``direction`` fixes the
    time order (down: high is the swing origin, low the recent extreme; up: vice versa) so
    the later anchor is searched only after the earlier one — resolving repeated prices.
    """
    direction = direction.lower()
    if direction not in ("up", "down"):
        raise ValueError(f"direction must be 'up' or 'down', got {direction!r}")
    if high_price < low_price:
        raise ValueError(f"high_price {high_price} must be >= low_price {low_price}")

    tol = {"exact_tol": exact_tol, "near_tol": near_tol}
    if direction == "down":
        # swing origin = high (earlier), recent extreme = low (later)
        origin = match_anchor_time(df, high_price, "high", **tol)
        extreme = match_anchor_time(df, low_price, "low", after=origin.time, **tol)
    else:
        # swing origin = low (earlier), recent extreme = high (later)
        origin = match_anchor_time(df, low_price, "low", **tol)
        extreme = match_anchor_time(df, high_price, "high", after=origin.time, **tol)

    matches = [origin, extreme]
    annotation: HumanFibAnnotation | None = None
    if origin.time is not None and extreme.time is not None:
        # anchor_a = swing origin (ratio 1.0), anchor_b = recent extreme (ratio 0.0)
        annotation = make_annotation(
            symbol=symbol,
            timeframe=timeframe,
            exchange=exchange,
            anchor_a=FibAnchor(time=origin.time, price=origin.price),
            anchor_b=FibAnchor(time=extreme.time, price=extreme.price),
            scale_mode="log",
        )
        annotation.created_by = CANDIDATE_CREATED_BY
        annotation.source = CANDIDATE_SOURCE
    return TranscribeResult(annotation=annotation, matches=matches, confidence=_worst(matches))


def candidate_dict(result: TranscribeResult) -> dict:
    """Serialize a candidate: the facit-shaped annotation plus a transcription audit block."""
    base = result.annotation.to_dict() if result.annotation else {}
    return {
        "_candidate": True,
        "_transcription": {
            "confidence": result.confidence,
            "matches": [
                {
                    "role": m.role,
                    "price": m.price,
                    "recovered_time": m.time,
                    "matched_extreme": m.matched_extreme,
                    "rel_delta": m.rel_delta,
                    "confidence": m.confidence,
                    "n_within_near": m.n_within_near,
                }
                for m in result.matches
            ],
        },
        **base,
    }


def _refuse_facit_path(path: Path) -> None:
    if "human_fib" in path.as_posix():
        raise SystemExit(
            f"refusing to write a candidate into a human_fib/ path ({path}); that surface is "
            "facit. Write the candidate elsewhere and promote via the labeling tool."
        )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Transcribe a screenshot fib: recover anchor times from supplied "
        "anchor prices (candidate output, never facit)."
    )
    p.add_argument("--symbol", required=True)
    p.add_argument("--timeframe", required=True)
    p.add_argument("--exchange", default=None)
    p.add_argument("--high-price", dest="high_price", type=float, required=True)
    p.add_argument("--low-price", dest="low_price", type=float, required=True)
    p.add_argument("--direction", choices=["up", "down"], required=True)
    p.add_argument("--config", default=None, help="Settings YAML (e.g. settings.expansion.yaml).")
    p.add_argument("--out", type=Path, default=None, help="Candidate output path (else print).")
    p.add_argument("--exact-tol", dest="exact_tol", type=float, default=EXACT_TOL)
    p.add_argument("--near-tol", dest="near_tol", type=float, default=NEAR_TOL)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    settings = load_settings(args.config)
    exchange = args.exchange or settings.data.exchange
    cfg = settings.data.model_copy(
        update={"exchange": exchange, "symbol": args.symbol, "timeframe": args.timeframe}
    )
    df = load_candles(cfg, fetch_if_missing=False)

    result = transcribe_fib(
        df,
        high_price=args.high_price,
        low_price=args.low_price,
        direction=args.direction,
        symbol=args.symbol,
        timeframe=args.timeframe,
        exchange=exchange,
        exact_tol=args.exact_tol,
        near_tol=args.near_tol,
    )

    for m in result.matches:
        delta = f"{m.rel_delta:.4%}" if m.rel_delta is not None else "n/a"
        print(
            f"  {m.role:>4} {m.price:>12.2f} -> {m.time or 'UNMATCHED':<28} "
            f"[{m.confidence}] delta={delta} near_candidates={m.n_within_near}"
        )
    print(f"  overall confidence: {result.confidence}")
    if result.annotation is None:
        raise SystemExit("could not recover both anchor times — no candidate emitted.")

    payload = json.dumps(candidate_dict(result), indent=2)
    if args.out:
        _refuse_facit_path(args.out)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
        print(f"  wrote candidate -> {args.out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
