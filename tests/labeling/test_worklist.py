from types import SimpleNamespace

from fibengine.labeling import worklist
from fibengine.labeling.store import Point, SwingLabel


class _FakeData:
    def model_copy(self, update):
        return SimpleNamespace(**update)


def _fake_settings():
    return SimpleNamespace(data=_FakeData(), pivots=object(), scoring=object())


def _patch_uncertainty(monkeypatch, margins: dict, missing_cache: set):
    """Fake candle-load + margin so ordering is testable without a real corpus."""
    import fibengine.core.scoring as scoring
    import fibengine.data.loader as loader

    def fake_load_candles(data_cfg, fetch_if_missing=True):
        if data_cfg.symbol in missing_cache:
            raise FileNotFoundError("no cache")
        return data_cfg  # stand-in df carrying .symbol

    def fake_margin(df, pivot_cfg, scoring_cfg):
        return margins[df.symbol]

    monkeypatch.setattr(loader, "load_candles", fake_load_candles)
    monkeypatch.setattr(scoring, "swing_score_margin", fake_margin)


def _combo(symbol: str) -> tuple[str, str, str]:
    return ("bitfinex", symbol, "1d")


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
    _patch_labels(monkeypatch, [_label("BTC/USD", "1h"), _label("ETH/USD", "1h")])

    report = worklist.coverage_report(
        symbols=["BTC/USD", "ETH/USD", "SOL/USD"],
        timeframes=["1h", "4h"],
    )

    assert report["n_labeled"] == 2
    assert report["n_target_combos"] == 6
    assert report["n_covered_combos"] == 2
    # Missing = allt utom de tvÃ¥ labelade 1h-kombinationerna.
    assert ("bitfinex", "SOL/USD", "1h") in report["missing_combos"]
    assert ("bitfinex", "BTC/USD", "4h") in report["missing_combos"]
    assert ("bitfinex", "BTC/USD", "1h") not in report["missing_combos"]
    assert len(report["missing_combos"]) == 4


def test_machine_labels_do_not_count_toward_target(monkeypatch):
    # En human + en maskin-kandidat pÃ¥ samma timeframe, olika symboler.
    _patch_labels(
        monkeypatch,
        [_label("BTC/USD", "1h"), _label("ETH/USD", "1h", source="machine")],
    )

    report = worklist.coverage_report(
        symbols=["BTC/USD", "ETH/USD", "SOL/USD"],
        timeframes=["1h"],
    )

    # Bara den mÃ¤nskliga rÃ¤knas mot mÃ¥let.
    assert report["n_labeled"] == 1
    # ETH 1h saknar human-facit men har en maskin-kandidat att granska.
    assert ("bitfinex", "ETH/USD", "1h") in report["missing_combos"]
    assert ("bitfinex", "ETH/USD", "1h") in report["machine_to_review"]
    assert report["n_machine_to_review"] == 1

    text = worklist.format_report(report)
    assert "Maskin-kandidater att granska" in text
    # ETH listas under granskning, inte under "helt olabelade".
    assert "ETH/USD --timeframe 1h" in text


def test_target_progress(monkeypatch):
    _patch_labels(monkeypatch, [_label("BTC/USD", "1h")])
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is False
    assert report["remaining_to_target"] == 24


def test_target_reached(monkeypatch):
    _patch_labels(monkeypatch, [_label("BTC/USD", str(i)) for i in range(25)])
    report = worklist.coverage_report(target=25)
    assert report["target_reached"] is True
    assert report["remaining_to_target"] == 0


def test_format_report_emits_runnable_commands(monkeypatch):
    _patch_labels(monkeypatch, [])
    report = worklist.coverage_report(symbols=["BTC/USD"], timeframes=["30m"])
    text = worklist.format_report(report)
    assert "fibengine.labeling.tool" in text
    assert "--symbol BTC/USD --timeframe 30m" in text


def test_order_by_uncertainty_most_ambiguous_first(monkeypatch):
    # AAA margin 0.5, BBB 0.1 (more uncertain), CCC unscored (None), DDD no cache.
    _patch_uncertainty(
        monkeypatch,
        margins={"AAA": 0.5, "BBB": 0.1, "CCC": None, "DDD": 0.0},
        missing_cache={"DDD"},
    )
    missing = [_combo(s) for s in ("AAA", "BBB", "CCC", "DDD")]
    ordered = worklist.order_missing_by_uncertainty(missing, _fake_settings())
    # Scored ascending by margin first (BBB before AAA), then unscored in original order.
    assert ordered == [_combo("BBB"), _combo("AAA"), _combo("CCC"), _combo("DDD")]


def test_order_by_uncertainty_is_deterministic(monkeypatch):
    _patch_uncertainty(
        monkeypatch,
        margins={"AAA": 0.5, "BBB": 0.1, "CCC": None, "DDD": 0.0},
        missing_cache={"DDD"},
    )
    missing = [_combo(s) for s in ("AAA", "BBB", "CCC", "DDD")]
    first = worklist.order_missing_by_uncertainty(missing, _fake_settings())
    second = worklist.order_missing_by_uncertainty(missing, _fake_settings())
    assert first == second


def test_order_by_uncertainty_writes_no_labels(monkeypatch, tmp_path):
    from fibengine.labeling import store

    store.set_labels_dir(tmp_path)
    try:
        _patch_uncertainty(monkeypatch, margins={"AAA": 0.2}, missing_cache=set())
        worklist.order_missing_by_uncertainty([_combo("AAA")], _fake_settings())
        assert list(tmp_path.rglob("*.json")) == []  # ordering is read-only
    finally:
        store.set_labels_dir(None)
