"""Label-täckning / worklist: vad återstår att labela mot målet?

Premortem-koppling (`premortem/PREMORTEM.md`): vikter ska inte låsas mot ett för
tunt facit — målet är minst 20–30 labelade setups. Den här hjälpredan gör gapen
mellan nuvarande labels och målet explicita och skriver ut färdiga
`labeling.tool`-kommandon för det som saknas, så att utökningen blir konkret.

Kör:
    uv run python -m fibengine.labeling.worklist
    uv run python -m fibengine.labeling.worklist --symbols BTC/USDT,ETH/USDT \
        --timeframes 1h,4h,1d
"""

from __future__ import annotations

import argparse

from fibengine.labeling.store import list_labels

# Mål per PREMORTEM.md: "Samla minst 20–30 labelade setups innan vikter låses".
LABEL_TARGET = 25
DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
DEFAULT_TIMEFRAMES = ["15m", "30m", "1h", "4h", "1d", "1w", "1M"]


def labeled_combos() -> set[tuple[str, str, str]]:
    """(exchange, symbol, timeframe) för varje sparad label."""
    return {(lbl.exchange.lower(), lbl.symbol, lbl.timeframe) for lbl in list_labels()}


def target_combos(
    exchange: str, symbols: list[str], timeframes: list[str]
) -> list[tuple[str, str, str]]:
    return [(exchange.lower(), symbol, tf) for symbol in symbols for tf in timeframes]


def coverage_report(
    exchange: str = "binance",
    symbols: list[str] | None = None,
    timeframes: list[str] | None = None,
    target: int = LABEL_TARGET,
) -> dict:
    """Sammanfatta hur långt facit-korpusen kommit mot målet + vad som saknas."""
    symbols = symbols or DEFAULT_SYMBOLS
    timeframes = timeframes or DEFAULT_TIMEFRAMES
    have = labeled_combos()
    targets = target_combos(exchange, symbols, timeframes)
    missing = [combo for combo in targets if combo not in have]
    n_labeled = len(have)
    return {
        "n_labeled": n_labeled,
        "target": target,
        "remaining_to_target": max(0, target - n_labeled),
        "target_reached": n_labeled >= target,
        "n_target_combos": len(targets),
        "n_covered_combos": len(targets) - len(missing),
        "missing_combos": missing,
    }


def format_report(report: dict) -> str:
    progress = (
        "mål uppnått"
        if report["target_reached"]
        else f"{report['remaining_to_target']} kvar till mål"
    )
    lines = [
        f"Labels: {report['n_labeled']} / {report['target']} ({progress})",
        f"Target-matris: {report['n_covered_combos']}/{report['n_target_combos']} "
        "kombinationer täckta",
    ]
    if report["missing_combos"]:
        lines.append("\nNästa att labela (kör kommandot, klicka high/low, tryck 's'):")
        for exchange, symbol, timeframe in report["missing_combos"]:
            lines.append(
                "  uv run python -m fibengine.labeling.tool "
                f"--exchange {exchange} --symbol {symbol} --timeframe {timeframe}"
            )
    else:
        lines.append("\nAlla target-kombinationer täckta.")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label coverage / worklist mot 20–30-setup-målet.")
    parser.add_argument("--exchange", default="binance", help="CCXT exchange id (default: binance)")
    parser.add_argument("--symbols", help="Comma-separated symbols, e.g. BTC/USDT,ETH/USDT")
    parser.add_argument("--timeframes", help="Comma-separated timeframes, e.g. 15m,1h,4h,1d")
    parser.add_argument(
        "--target", type=int, default=LABEL_TARGET, help=f"Label-mål (default: {LABEL_TARGET})"
    )
    return parser.parse_args()


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    args = _parse_args()
    report = coverage_report(
        exchange=args.exchange,
        symbols=_split_csv(args.symbols),
        timeframes=_split_csv(args.timeframes),
        target=args.target,
    )
    print(format_report(report))


if __name__ == "__main__":
    main()
