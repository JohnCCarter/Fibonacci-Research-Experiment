"""Human Fib Annotation Layer — manual fib ranges as ground truth.

The **human draws** a fib range (two anchors); we store the exact anchors and
the derived fib levels. Machine logic here only *reads, stores, calculates
levels, and classifies* candle interaction with those saved levels.

Design rules (deliberate):

- **No auto-fib detection.** Anchors are always supplied by a human. This module
  exposes no detector and never guesses a range.
- **No tuning / no edge claims.** Pure, deterministic geometry + classification.
- **Research-only.** Not read by the motor / evaluation / promotion path.

Level convention (matches the labeling tool's fib): ``anchor_b`` is ratio 0.0 and
``anchor_a`` is ratio 1.0, so ``price(r) = b.price + r * (a.price - b.price)``.

Run (CLI, no network — needs cached candles for --classify):
    uv run python -m fibengine.labeling.human_fib \\
        --symbol BTC/USD --timeframe 1d \\
        --anchor-a-time 2026-01-14T00:00:00Z --anchor-a-price 97924 \\
        --anchor-b-time 2026-02-06T00:00:00Z --anchor-b-price 60000
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.store import get_labels_dir

# Active fib profile for BTC monthly-first protocol (TradingView log-scale).
# 0.0 = recent extreme (anchor_b), 1.0 = swing origin (anchor_a). No 0.236.
DEFAULT_FIB_RATIOS: tuple[float, ...] = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)

# Round derived level prices to clean up float noise (e.g. 426.17895999999996).
# 8 decimals keeps satoshi-level precision for any asset.
PRICE_DECIMALS = 8

HUMAN_FIB_DIRNAME = "human_fib"

# Candle-vs-level relation labels (geometry only; NOT behaviour like rejection).
ABOVE = "above"
BELOW = "below"
TOUCH = "touch"
CROSS = "cross"
RELATIONS = (ABOVE, BELOW, TOUCH, CROSS)


def _symbol_dir(symbol: str) -> str:
    return symbol.replace("/", "-")


@dataclass
class FibAnchor:
    """A human-picked anchor point (exact, not snapped by any detector)."""

    time: str  # ISO-8601 UTC
    price: float

    def __post_init__(self) -> None:
        self.price = float(self.price)


@dataclass
class FibLevel:
    ratio: float
    price: float


@dataclass
class HumanFibAnnotation:
    symbol: str
    timeframe: str
    anchor_a: FibAnchor
    anchor_b: FibAnchor
    direction: str
    levels: list[FibLevel]
    exchange: str = "bitfinex"
    fib_id: str = ""
    created_by: str = "human"
    source: str = "manual_labeling_tool"
    created_at: str = ""
    scale_mode: str = "log"
    levels_profile: str = "tradingview_log_chamoun"
    # Presentation/review-only annotations (e.g. a zone from 0.5 to 0.618). They may
    # drive filtering/visual focus in review tools but must never affect event
    # detection, outcome logic, sampling, or level importance (issue #30, Addendum 2).
    human_highlights: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.anchor_a, dict):
            self.anchor_a = FibAnchor(**self.anchor_a)
        if isinstance(self.anchor_b, dict):
            self.anchor_b = FibAnchor(**self.anchor_b)
        self.levels = [lvl if isinstance(lvl, FibLevel) else FibLevel(**lvl) for lvl in self.levels]
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.fib_id:
            self.fib_id = _default_fib_id(self.symbol, self.timeframe, self.anchor_a)

    def to_dict(self) -> dict:
        return {
            "fib_id": self.fib_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "exchange": self.exchange,
            "created_by": self.created_by,
            "source": self.source,
            "scale_mode": self.scale_mode,
            "levels_profile": self.levels_profile,
            "human_highlights": self.human_highlights,
            "anchor_a": asdict(self.anchor_a),
            "anchor_b": asdict(self.anchor_b),
            "direction": self.direction,
            "created_at": self.created_at,
            "levels": [asdict(lvl) for lvl in self.levels],
        }


def _default_fib_id(symbol: str, timeframe: str, anchor_a: FibAnchor) -> str:
    stamp = anchor_a.time.replace(":", "").replace("-", "").replace("+0000", "").replace("Z", "")
    return f"fib_{_symbol_dir(symbol)}_{timeframe}_{stamp}".rstrip("T_")


def infer_direction(anchor_a: FibAnchor, anchor_b: FibAnchor) -> str:
    """Down if the move from anchor_a to anchor_b is downward in price, else up."""
    return "down" if anchor_a.price >= anchor_b.price else "up"


def compute_levels(
    anchor_a: FibAnchor,
    anchor_b: FibAnchor,
    ratios: tuple[float, ...] = DEFAULT_FIB_RATIOS,
    decimals: int = PRICE_DECIMALS,
    scale_mode: str = "linear",
) -> list[FibLevel]:
    """Derive fib level prices from two human anchors.

    ``anchor_b`` is ratio 0.0, ``anchor_a`` is ratio 1.0.

    Linear: ``price(r) = b + r * (a - b)``
    Log:    ``price(r) = exp(log(b) + r * (log(a) - log(b)))``
    """
    if scale_mode == "log":
        log_b = math.log(anchor_b.price)
        log_a = math.log(anchor_a.price)
        return [
            FibLevel(ratio=r, price=round(math.exp(log_b + r * (log_a - log_b)), decimals))
            for r in ratios
        ]
    span = anchor_a.price - anchor_b.price
    return [FibLevel(ratio=r, price=round(anchor_b.price + r * span, decimals)) for r in ratios]


def make_annotation(
    *,
    symbol: str,
    timeframe: str,
    anchor_a: FibAnchor,
    anchor_b: FibAnchor,
    exchange: str = "bitfinex",
    fib_id: str = "",
    direction: str | None = None,
    ratios: tuple[float, ...] = DEFAULT_FIB_RATIOS,
    decimals: int = PRICE_DECIMALS,
    created_at: str = "",
    scale_mode: str = "log",
    levels_profile: str = "tradingview_log_chamoun",
) -> HumanFibAnnotation:
    """Build an annotation from explicit human anchors (never auto-detected)."""
    return HumanFibAnnotation(
        symbol=symbol,
        timeframe=timeframe,
        anchor_a=anchor_a,
        anchor_b=anchor_b,
        direction=direction or infer_direction(anchor_a, anchor_b),
        levels=compute_levels(anchor_a, anchor_b, ratios, decimals, scale_mode=scale_mode),
        exchange=exchange,
        fib_id=fib_id,
        created_at=created_at,
        scale_mode=scale_mode,
        levels_profile=levels_profile,
    )


def anchors_from_picks(
    df: pd.DataFrame,
    high_idx: int,
    high_price: float,
    low_idx: int,
    low_price: float,
) -> tuple[FibAnchor, FibAnchor]:
    """Map a labeling-tool high/low pick to (anchor_a, anchor_b) in time order.

    anchor_a is the earlier point, anchor_b the later one. Direction then falls
    out of the prices (down if the earlier point is the high).
    """
    high = FibAnchor(time=df.index[high_idx].isoformat(), price=float(high_price))
    low = FibAnchor(time=df.index[low_idx].isoformat(), price=float(low_price))
    if high_idx <= low_idx:
        return high, low
    return low, high


def classify_candle(open_: float, high: float, low: float, close: float, level: float) -> str:
    """Deterministic relation of one candle to one fib level price.

    Precedence keeps the four labels mutually exclusive:
    - ``below``: whole candle below the level (``high < level``)
    - ``above``: whole candle above the level (``low > level``)
    - otherwise the level is within [low, high]:
        - ``cross``: open and close are on strictly opposite sides
        - ``touch``: anything else within range
    """
    if high < level:
        return BELOW
    if low > level:
        return ABOVE
    if (open_ < level < close) or (close < level < open_):
        return CROSS
    return TOUCH


def classify_candles(
    df: pd.DataFrame,
    annotation: HumanFibAnnotation,
    *,
    start_time: str | None = None,
    end_time: str | None = None,
) -> list[dict]:
    """Per-candle interaction record for every fib level (one row per candle×level)."""
    start = pd.to_datetime(start_time, utc=True) if start_time else None
    end = pd.to_datetime(end_time, utc=True) if end_time else None
    rows: list[dict] = []
    for ts, bar in df.iterrows():
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        o, h, low_p, c = (
            float(bar["open"]),
            float(bar["high"]),
            float(bar["low"]),
            float(bar["close"]),
        )
        for lvl in annotation.levels:
            rows.append(
                {
                    "time": ts.isoformat(),
                    "ratio": lvl.ratio,
                    "level_price": lvl.price,
                    "relation": classify_candle(o, h, low_p, c, lvl.price),
                    "open": o,
                    "high": h,
                    "low": low_p,
                    "close": c,
                }
            )
    return rows


def human_fib_dir() -> Path:
    return get_labels_dir() / HUMAN_FIB_DIRNAME


def annotation_path(annotation: HumanFibAnnotation) -> Path:
    return (
        human_fib_dir()
        / annotation.exchange.lower()
        / _symbol_dir(annotation.symbol)
        / annotation.timeframe
        / f"{annotation.fib_id}.json"
    )


def save_annotation(annotation: HumanFibAnnotation, path: Path | None = None) -> Path:
    path = path or annotation_path(annotation)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(annotation.to_dict(), indent=2), encoding="utf-8")
    return path


def load_annotation(path: str | Path) -> HumanFibAnnotation:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return HumanFibAnnotation(
        symbol=data["symbol"],
        timeframe=data["timeframe"],
        anchor_a=FibAnchor(**data["anchor_a"]),
        anchor_b=FibAnchor(**data["anchor_b"]),
        direction=data["direction"],
        levels=[FibLevel(**lvl) for lvl in data["levels"]],
        exchange=data.get("exchange", "bitfinex"),
        fib_id=data.get("fib_id", ""),
        created_by=data.get("created_by", "human"),
        source=data.get("source", "manual_labeling_tool"),
        created_at=data.get("created_at", ""),
        scale_mode=data.get("scale_mode", "linear"),
        levels_profile=data.get("levels_profile", ""),
        human_highlights=data.get("human_highlights", []),
    )


def find_annotation(
    fib_id: str,
    *,
    exchange: str,
    symbol: str,
    timeframe: str,
    root: Path | None = None,
) -> HumanFibAnnotation:
    """Load exactly one human fib by ``fib_id``, fail-closed for the single-fib tools.

    Read-only — never mutates any label file. Raises with a clear message when the id is
    missing, ambiguous (same filename under multiple dirs), or when the loaded fib does
    not match the active ``symbol`` / ``timeframe`` / ``exchange``. Symbol is checked
    before timeframe so a mismatch surfaces the most specific cause first.
    """
    base = Path(root) if root is not None else human_fib_dir()
    matches = sorted(base.rglob(f"{fib_id}.json"))
    if not matches:
        raise FileNotFoundError(f"human fib {fib_id!r} not found under {base}")
    if len(matches) > 1:
        joined = ", ".join(str(m) for m in matches)
        raise ValueError(f"human fib {fib_id!r} is ambiguous ({len(matches)} files): {joined}")
    ann = load_annotation(matches[0])
    if ann.symbol != symbol:
        raise ValueError(f"{fib_id}: symbol {ann.symbol!r} != active {symbol!r}")
    if ann.timeframe != timeframe:
        raise ValueError(f"{fib_id}: timeframe {ann.timeframe!r} != active {timeframe!r}")
    if ann.exchange.lower() != exchange.lower():
        raise ValueError(f"{fib_id}: exchange {ann.exchange!r} != active {exchange!r}")
    return ann


def write_interactions_csv(rows: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["time", "ratio", "level_price", "relation", "open", "high", "low", "close"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create/inspect a human fib annotation (manual ground truth, no auto-fib)."
    )
    p.add_argument("--symbol", default=None)
    p.add_argument("--timeframe", default=None)
    p.add_argument("--exchange", default=None)
    p.add_argument("--anchor-a-time", dest="a_time")
    p.add_argument("--anchor-a-price", dest="a_price", type=float)
    p.add_argument("--anchor-b-time", dest="b_time")
    p.add_argument("--anchor-b-price", dest="b_price", type=float)
    p.add_argument("--fib-id", dest="fib_id", default="")
    p.add_argument("--direction", default=None, choices=[None, "up", "down"])
    p.add_argument("--show", type=Path, default=None, help="Load and print an annotation JSON.")
    p.add_argument(
        "--classify",
        action="store_true",
        help="Also classify cached candles and write <fib_id>_interactions.csv.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.show:
        ann = load_annotation(args.show)
        print(json.dumps(ann.to_dict(), indent=2))
        return

    settings = load_settings()
    symbol = args.symbol or settings.data.symbol
    timeframe = args.timeframe or settings.data.timeframe
    exchange = args.exchange or settings.data.exchange
    missing = [
        name
        for name, val in {
            "--anchor-a-time": args.a_time,
            "--anchor-a-price": args.a_price,
            "--anchor-b-time": args.b_time,
            "--anchor-b-price": args.b_price,
        }.items()
        if val is None
    ]
    if missing:
        raise SystemExit(f"Missing required anchor args: {', '.join(missing)} (no auto-fib).")

    annotation = make_annotation(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange,
        anchor_a=FibAnchor(time=args.a_time, price=args.a_price),
        anchor_b=FibAnchor(time=args.b_time, price=args.b_price),
        fib_id=args.fib_id,
        direction=args.direction,
    )
    path = save_annotation(annotation)
    print(f"Saved human fib annotation -> {path}")
    for lvl in annotation.levels:
        print(f"  {lvl.ratio:>5}: {lvl.price:.4f}")

    if args.classify:
        cfg = settings.data.model_copy(
            update={"exchange": exchange, "symbol": symbol, "timeframe": timeframe}
        )
        try:
            df = load_candles(cfg, fetch_if_missing=False)
        except FileNotFoundError as exc:
            print(f"Skipped --classify: {exc}")
            return
        rows = classify_candles(df, annotation)
        csv_name = f"{annotation.fib_id}_interactions.csv"
        csv_path = write_interactions_csv(rows, path.with_name(csv_name))
        print(f"Wrote {len(rows)} interaction rows -> {csv_path}")


if __name__ == "__main__":
    main()
