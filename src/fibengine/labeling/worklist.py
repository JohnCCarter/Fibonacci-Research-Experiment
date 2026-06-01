"""Label-täckning / worklist: vad återstår att labela mot målet?

Premortem-koppling (`premortem/PREMORTEM.md`): vikter ska inte låsas mot ett för
tunt facit — målet är minst 20–30 labelade setups. Den här hjälpredan gör gapen
mellan nuvarande labels och målet explicita och skriver ut färdiga
`labeling.tool`-kommandon för det som saknas, så att utökningen blir konkret.

Kör:
    uv run python -m fibengine.labeling.worklist
    uv run python -m fibengine.labeling.worklist --symbols BTC/USD,ETH/USD \
        --timeframes 1h,4h,1d
"""

from __future__ import annotations

import argparse

from fibengine.labeling.store import list_labels

# Mål per PREMORTEM.md: "Samla minst 20–30 labelade setups innan vikter låses".
LABEL_TARGET = 25
DEFAULT_SYMBOLS = ["BTC/USD", "ETH/USD", "SOL/USD"]
DEFAULT_TIMEFRAMES = ["15m", "30m", "1h", "4h", "1d", "1w", "1M"]


def labeled_combos(source: str | None = None) -> set[tuple[str, str, str]]:
    """(exchange, symbol, timeframe) för varje sparad label (ev. filtrerad på source)."""
    return {(lbl.exchange.lower(), lbl.symbol, lbl.timeframe) for lbl in list_labels(source)}


def target_combos(
    exchange: str, symbols: list[str], timeframes: list[str]
) -> list[tuple[str, str, str]]:
    return [(exchange.lower(), symbol, tf) for symbol in symbols for tf in timeframes]


def coverage_report(
    exchange: str = "bitfinex",
    symbols: list[str] | None = None,
    timeframes: list[str] | None = None,
    target: int = LABEL_TARGET,
) -> dict:
    """Sammanfatta hur långt facit-korpusen kommit mot målet + vad som saknas."""
    symbols = symbols or DEFAULT_SYMBOLS
    timeframes = timeframes or DEFAULT_TIMEFRAMES
    # Bara mänskligt facit räknas mot målet. Maskin-labels är kandidater att granska.
    human = labeled_combos(source="human")
    machine = labeled_combos(source="machine")
    targets = target_combos(exchange, symbols, timeframes)
    # "Saknar facit" = ingen MÄNSKLIG label (även om en maskin-kandidat finns).
    missing = [combo for combo in targets if combo not in human]
    machine_to_review = [combo for combo in targets if combo in machine and combo not in human]
    n_labeled = len(human)
    return {
        "n_labeled": n_labeled,
        "target": target,
        "remaining_to_target": max(0, target - n_labeled),
        "target_reached": n_labeled >= target,
        "n_target_combos": len(targets),
        "n_covered_combos": len(targets) - len(missing),
        "n_machine_to_review": len(machine_to_review),
        "machine_to_review": machine_to_review,
        "missing_combos": missing,
    }


def format_report(report: dict) -> str:
    progress = (
        "mål uppnått"
        if report["target_reached"]
        else f"{report['remaining_to_target']} kvar till mål"
    )
    lines = [
        f"Human-facit: {report['n_labeled']} / {report['target']} ({progress})",
        f"Target-matris: {report['n_covered_combos']}/{report['n_target_combos']} "
        "kombinationer täckta (mänskliga)",
    ]
    if report.get("machine_to_review"):
        lines.append(
            f"\nMaskin-kandidater att granska ({report['n_machine_to_review']}) — "
            "öppna i labeling.tool, justera, tryck 's' för att befordra till human:"
        )
        for exchange, symbol, timeframe in report["machine_to_review"]:
            lines.append(
                "  uv run python -m fibengine.labeling.tool "
                f"--exchange {exchange} --symbol {symbol} --timeframe {timeframe}"
            )
    # Helt olabelade = saknar både human-facit och maskin-kandidat.
    machine_set = set(report.get("machine_to_review", []))
    empty = [combo for combo in report["missing_combos"] if combo not in machine_set]
    if empty:
        lines.append("\nHelt olabelade — labela för hand (klicka high/low, tryck 's'):")
        for exchange, symbol, timeframe in empty:
            lines.append(
                "  uv run python -m fibengine.labeling.tool "
                f"--exchange {exchange} --symbol {symbol} --timeframe {timeframe}"
            )
    if not report["missing_combos"]:
        lines.append("\nAlla target-kombinationer har human-facit.")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label coverage / worklist mot 20–30-setup-målet.")
    parser.add_argument(
        "--exchange", default="bitfinex", help="CCXT exchange id (default: bitfinex)"
    )
    parser.add_argument("--symbols", help="Comma-separated symbols, e.g. BTC/USD,ETH/USD")
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
