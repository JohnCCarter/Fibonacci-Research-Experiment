from fibengine.labeling import worklist
from fibengine.labeling.store import Point, SwingLabel


def _label(symbol: str, timeframe: str, exchange: str = "binance") -> SwingLabel:
    return SwingLabel(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        high=Point("2026-01-02T00:00:00+00:00", 110.0),
        low=Point("2026-01-01T00:00:00+00:00", 100.0),
    )


def test_coverage_report_lists_missing_combos(monkeypatch):
    labels = [_label("BTC/USDT", "1h"), _label("ETH/USDT", "1h")]
    monkeypatch.setattr(worklist, "list_labels", lambda: labels)

    report = worklist.coverage_report(
        symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        timeframes=["1h", "4h"],
    )

    assert report["n_labeled"] == 2
    assert report["n_target_combos"] == 6
    assert report["n_covered_combos"] == 2
    # Missing = allt utom de två labelade 1h-kombinationerna.
    assert ("binance", "SOL/USDT", "1h") in report["missing_combos"]
    assert ("binance", "BTC/USDT", "4h") in report["missing_combos"]
    assert ("binance", "BTC/USDT", "1h") not in report["missing_combos"]
    assert len(report["missing_combos"]) == 4


def test_target_progress(monkeypatch):
    monkeypatch.setattr(worklist, "list_labels", lambda: [_label("BTC/USDT", "1h")])
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is False
    assert report["remaining_to_target"] == 24


def test_target_reached(monkeypatch):
    labels = [_label("BTC/USDT", str(i)) for i in range(25)]
    monkeypatch.setattr(worklist, "list_labels", lambda: labels)
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is True
    assert report["remaining_to_target"] == 0


def test_format_report_emits_runnable_commands(monkeypatch):
    monkeypatch.setattr(worklist, "list_labels", lambda: [])
    report = worklist.coverage_report(symbols=["BTC/USDT"], timeframes=["30m"])
    text = worklist.format_report(report)
    assert "fibengine.labeling.tool" in text
    assert "--symbol BTC/USDT --timeframe 30m" in text
