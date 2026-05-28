import pytest
from pydantic import ValidationError

from fibengine.core.config import BacktestConfig, EvaluationConfig, PivotConfig, SizingConfig


def test_rejects_invalid_window_and_tolerance_values():
    with pytest.raises(ValidationError):
        PivotConfig(lookback=0)
    with pytest.raises(ValidationError):
        EvaluationConfig(price_tol_atr=0)
    with pytest.raises(ValidationError):
        BacktestConfig(step=0)


def test_sizing_requires_matching_level_and_size_counts():
    with pytest.raises(ValidationError):
        SizingConfig(entry_levels=[0.382, 0.5], sizes=[1.0])
