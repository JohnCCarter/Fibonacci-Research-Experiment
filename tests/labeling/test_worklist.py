from fibengine.labeling import worklist
from fibengine.labeling.store import Point, SwingLabel


def _label(
    symbol: str, timeframe: str, exchange: str = "bitfinex", source: str = "human"
) -> SwingLabel:
    return SwingLabel(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        high=Point("2026-01-02T00:00:00+00:00", 110.0),
        low=Point("2026-01-01T00:00:00+00:00", 100.0),
        source=source,
    )


def _patch_labels(monkeypatch, labels: list[SwingLabel]) -> None:
    """Spegla store.list_labels(source=...) i worklist-namespacet."""

    def fake_list_labels(source=None):
        if source is None:
            return labels
        return [lbl for lbl in labels if lbl.source == source]

    monkeypatch.setattr(worklist, "list_labels", fake_list_labels)


def test_coverage_report_lists_missing_combos(monkeypatch):
    _patch_labels(monkeypatch, [_label("BTC/USDT", "1h"), _label("ETH/USDT", "1h")])

    report = worklist.coverage_report(
        symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        timeframes=["1h", "4h"],
    )

    assert report["n_labeled"] == 2
    assert report["n_target_combos"] == 6
    assert report["n_covered_combos"] == 2
    # Missing = allt utom de två labelade 1h-kombinationerna.
    assert ("bitfinex", "SOL/USDT", "1h") in report["missing_combos"]
    assert ("bitfinex", "BTC/USDT", "4h") in report["missing_combos"]
    assert ("bitfinex", "BTC/USDT", "1h") not in report["missing_combos"]
    assert len(report["missing_combos"]) == 4


def test_machine_labels_do_not_count_toward_target(monkeypatch):
    # En human + en maskin-kandidat på samma timeframe, olika symboler.
    _patch_labels(
        monkeypatch,
        [_label("BTC/USDT", "1h"), _label("ETH/USDT", "1h", source="machine")],
    )

    report = worklist.coverage_report(
        symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        timeframes=["1h"],
    )

    # Bara den mänskliga räknas mot målet.
    assert report["n_labeled"] == 1
    # ETH 1h saknar human-facit men har en maskin-kandidat att granska.
    assert ("bitfinex", "ETH/USDT", "1h") in report["missing_combos"]
    assert ("bitfinex", "ETH/USDT", "1h") in report["machine_to_review"]
    assert report["n_machine_to_review"] == 1

    text = worklist.format_report(report)
    assert "Maskin-kandidater att granska" in text
    # ETH listas under granskning, inte under "helt olabelade".
    assert "ETH/USDT --timeframe 1h" in text


def test_target_progress(monkeypatch):
    _patch_labels(monkeypatch, [_label("BTC/USDT", "1h")])
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is False
    assert report["remaining_to_target"] == 24


def test_target_reached(monkeypatch):
    _patch_labels(monkeypatch, [_label("BTC/USDT", str(i)) for i in range(25)])
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is True
    assert report["remaining_to_target"] == 0


def test_format_report_emits_runnable_commands(monkeypatch):
    _patch_labels(monkeypatch, [])
    report = worklist.coverage_report(symbols=["BTC/USDT"], timeframes=["30m"])
    text = worklist.format_report(report)
    assert "fibengine.labeling.tool" in text
    assert "--symbol BTC/USDT --timeframe 30m" in text
