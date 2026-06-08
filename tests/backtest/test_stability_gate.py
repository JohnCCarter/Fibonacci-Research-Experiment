from fibengine.backtest.stability import stability_gate
from fibengine.core.config import BacktestConfig


def _good_metrics() -> dict:
    return {
        "flip_rate": 0.07,
        "confirmed_rate": 0.94,
        "direction_consistency": 0.98,
        "mean_endpoint_drift_bars": 5.0,
    }


def test_gate_passes_on_stable_metrics():
    gate = stability_gate(_good_metrics(), BacktestConfig())
    assert gate["passed"] is True
    assert all(gate["checks"].values())


def test_drift_is_first_class_and_can_fail_alone():
    # Allt ser stabilt ut UTOM driften â€” gaten ska Ã¤ndÃ¥ falla pÃ¥ endpoint-drift.
    metrics = _good_metrics()
    metrics["mean_endpoint_drift_bars"] = 52.0  # jfr SOL/USD 1h i reflektionen
    gate = stability_gate(metrics, BacktestConfig())
    assert gate["passed"] is False
    assert gate["checks"]["endpoint_drift_bars"] is False
    # Ã–vriga kriterier Ã¤r fortfarande grÃ¶na.
    assert gate["checks"]["flip_rate"] is True
    assert gate["checks"]["confirmed_rate"] is True


def test_each_threshold_can_fail_the_gate():
    failing = {
        "flip_rate": {"flip_rate": 0.9},
        "confirmed_rate": {"confirmed_rate": 0.1},
        "direction_consistency": {"direction_consistency": 0.2},
        "endpoint_drift_bars": {"mean_endpoint_drift_bars": 999.0},
    }
    for check_name, override in failing.items():
        metrics = {**_good_metrics(), **override}
        gate = stability_gate(metrics, BacktestConfig())
        assert gate["passed"] is False
        assert gate["checks"][check_name] is False
