"""Konfiguration: ladda och validera settings.yaml via pydantic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "settings.yaml"


class DataConfig(BaseModel):
    exchange: str = "binance"
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    limit: int = 500


class PivotConfig(BaseModel):
    lookback: int = 5
    atr_period: int = 14
    min_prominence_atr: float = 0.5
    mode: str = "window"   # "window" (lokala extrema) eller "fractal" (strikt Williams)
    fractal_n: int = 2     # barer på varje sida i fraktal-läge (2 = 5-stapelsmönster)


class ScoringConfig(BaseModel):
    weights: dict[str, float] = Field(default_factory=dict)
    duration_target: int = 20
    max_candidate_legs: int = 50
    magnitude_scale_atr: float = 10.0  # ATR-skala där magnitude-featuren mättas
    structure_window: int = 6          # antal färska pivots som väger in i HH/HL
    confluence_degrees: list[int] = Field(default_factory=lambda: [5, 12])  # större fraktal-grader
    confluence_tol_bars: int = 3       # hur nära en större-grads-pivot måste ligga


class FibConfig(BaseModel):
    levels: list[float] = Field(default_factory=lambda: [0.236, 0.382, 0.5, 0.618, 0.786])


class EvaluationConfig(BaseModel):
    price_tol_atr: float = 0.5
    time_tol_bars: int = 3
    fib_level_tol: float = 0.02


class SizingConfig(BaseModel):
    # Lager B: positionsskalning. Frikopplad från swing-urvalet.
    enabled: bool = False
    entry_levels: list[float] = Field(default_factory=lambda: [0.382, 0.5, 0.618])
    sizes: list[float] = Field(default_factory=lambda: [1.0, 2.0, 3.0])


class Settings(BaseModel):
    seed: int = 42
    data: DataConfig = Field(default_factory=DataConfig)
    pivots: PivotConfig = Field(default_factory=PivotConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    fib: FibConfig = Field(default_factory=FibConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    sizing: SizingConfig = Field(default_factory=SizingConfig)

    def config_hash(self) -> str:
        """Stabil hash av hela konfigurationen — används i audit-loggar."""
        payload = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:12]


def load_settings(path: str | Path | None = None) -> Settings:
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw = yaml.safe_load(path.read_text()) or {}
    return Settings(**raw)
