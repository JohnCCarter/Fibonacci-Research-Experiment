"""Maskin-labeling: generera provisoriska swing-kandidater fÃ¶r granskning.

TvÃ¥ giltiga frÃ¥gor (bÃ¥da kan vara rÃ¤tt â€” blanda inte ihop dem):
- **A Motor-swing:** `autolabel` = bÃ¤sta leg pÃ¥ tillgÃ¤nglig historik (standard CLI).
- **B ChartfÃ¶nster:** endpoints inom ett synligt datumintervall (ej standard Ã¤n;
  se docs/MACHINE_LABELING.md).

VIKTIGT â€” integritet:
- Maskin-labels (`source="machine"`) Ã¤r KANDIDATER, inte facit. De skrivs sÃ¥ att de
  kan Ã¶ppnas i `labeling.tool`, granskas och justeras av en mÃ¤nniska. Sparar du dem
  i verktyget blir de `source="human"` (befordran).
- De EXKLUDERAS frÃ¥n recall/agreement (`evaluation/pivot_recall`, `experiment`) â€”
  annars mÃ¤ter vi motorn mot sin egen output (cirkulÃ¤rt). De rÃ¤knas INTE mot
  20â€“30-facit-mÃ¥let i `labeling.worklist`.
- En befintlig MÃ„NSKLIG label skrivs aldrig Ã¶ver (skyddar golden set).

KÃ¶r:
    uv run python -m fibengine.labeling.autolabel
    uv run python -m fibengine.labeling.autolabel --symbols SOL/USD --timeframes 4h,1d
"""

from __future__ import annotations

import argparse

from fibengine.core.config import Settings, load_settings
from fibengine.core.logging_conf import setup_logging
from fibengine.core.models import Swing
from fibengine.core.scoring import select_swing
from fibengine.data.loader import load_candles
from fibengine.labeling.store import Point, SwingLabel, find_label, save_label
from fibengine.labeling.worklist import DEFAULT_SYMBOLS, DEFAULT_TIMEFRAMES

MACHINE_NOTE = "maskin-labeling: provisorisk kandidat â€” granska och justera i labeling.tool"


def label_from_swing(swing: Swing, exchange: str, symbol: str, timeframe: str) -> SwingLabel:
    """Bygg en maskin-label frÃ¥n motorns valda swing (high/low-endpunkter)."""
    high = swing.start if swing.start.kind == "high" else swing.end
    low = swing.start if swing.start.kind == "low" else swing.end
    return SwingLabel(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        high=Point(high.timestamp.isoformat(), high.price),
        low=Point(low.timestamp.isoformat(), low.price),
        note=MACHINE_NOTE,
        source="machine",
    )


def autolabel_one(
    settings: Settings, exchange: str, symbol: str, timeframe: str, overwrite: bool = False
) -> dict:
    """Generera (eller hoppa Ã¶ver) en maskin-label fÃ¶r en kombination."""
    existing = find_label(exchange, symbol, timeframe)
    if existing is not None and existing.source == "human":
        return {"symbol": symbol, "timeframe": timeframe, "status": "skipped_human"}
    if existing is not None and not overwrite:
        return {"symbol": symbol, "timeframe": timeframe, "status": "skipped_exists"}

    data_cfg = settings.data.model_copy(
        update={"exchange": exchange, "symbol": symbol, "timeframe": timeframe}
    )
    df = load_candles(data_cfg)
    swing = select_swing(df, settings.pivots, settings.scoring)
    if swing is None:
        return {"symbol": symbol, "timeframe": timeframe, "status": "no_swing"}

    label = label_from_swing(swing, exchange, symbol, timeframe)
    path = save_label(label)
    return {"symbol": symbol, "timeframe": timeframe, "status": "written", "path": str(path)}


def run_autolabel(
    settings: Settings | None = None,
    exchange: str = "bitfinex",
    symbols: list[str] | None = None,
    timeframes: list[str] | None = None,
    overwrite: bool = False,
) -> list[dict]:
    settings = settings or load_settings()
    symbols = symbols or DEFAULT_SYMBOLS
    timeframes = timeframes or DEFAULT_TIMEFRAMES
    log = setup_logging("autolabel", settings.config_hash())

    results: list[dict] = []
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                result = autolabel_one(settings, exchange, symbol, timeframe, overwrite)
            except Exception as exc:  # noqa: BLE001 - rapportera per kombination.
                result = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "status": "error",
                    "error": str(exc),
                }
            log.info("{} {} -> {}", symbol, timeframe, result["status"])
            results.append(result)

    written = sum(1 for r in results if r["status"] == "written")
    log.info("Maskin-labeling klar: {} skrivna av {} kombinationer", written, len(results))
    return results


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generera provisoriska maskin-labels (kandidater) fÃ¶r granskning."
    )
    parser.add_argument(
        "--exchange", default="bitfinex", help="CCXT exchange id (default: bitfinex)"
    )
    parser.add_argument("--symbols", help="Comma-separated symbols, e.g. SOL/USD")
    parser.add_argument("--timeframes", help="Comma-separated timeframes, e.g. 4h,1d")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Skriv Ã¶ver befintliga MASKIN-labels (mÃ¤nskliga rÃ¶rs aldrig)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    results = run_autolabel(
        exchange=args.exchange,
        symbols=_split_csv(args.symbols),
        timeframes=_split_csv(args.timeframes),
        overwrite=args.overwrite,
    )
    written = [r for r in results if r["status"] == "written"]
    print(f"Skrev {len(written)} maskin-labels (source=machine).")
    print("Granska dem i labeling.tool och tryck 's' fÃ¶r att befordra till human-facit.")


if __name__ == "__main__":
    main()
