"""Konfiguration: ladda och validera settings.yaml via pydantic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "settings.yaml"


class DataConfig(BaseModel):
    exchange: str = "binance"
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    limit: int = Field(default=500, ge=1)
    # Per-timeframe limit-override. Långa timeframes (1d/1w/1M) behöver fler
    # candles för att täcka äldre labels — annars hamnar facit utanför fönstret
    # (out-of-window) och tystas ur måtten. Saknad nyckel → faller tillbaka på
    # `limit`. Obs: en enskild CCXT-hämtning kan vara börs-kapad (ofta ~1000).
    timeframe_limits: dict[str, int] = Field(default_factory=dict)

    def effective_limit(self) -> int:
        """Antal candles att ladda för aktuell timeframe (override eller `limit`)."""
        return self.timeframe_limits.get(self.timeframe, self.limit)


class PivotConfig(BaseModel):
    lookback: int = Field(default=5, ge=1)
    atr_period: int = Field(default=14, ge=1)
    min_prominence_atr: float = Field(default=0.5, ge=0.0)
    mode: str = "window"  # "window" (lokala extrema) eller "fractal" (strikt Williams)
    fractal_n: int = Field(default=2, ge=1)  # barer på varje sida i fraktal-läge


class ScoringConfig(BaseModel):
    weights: dict[str, float] = Field(default_factory=dict)
    duration_target: int = Field(default=20, ge=1)
    max_candidate_legs: int = Field(default=50, ge=1)
    magnitude_scale_atr: float = Field(default=10.0, gt=0.0)
    structure_window: int = Field(default=6, ge=1)
    confluence_degrees: list[int] = Field(default_factory=lambda: [5, 12])
    confluence_tol_bars: int = Field(default=3, ge=0)
    confirm_min_retrace: float = Field(default=0.1, ge=0.0)


class FibConfig(BaseModel):
    levels: list[float] = Field(default_factory=lambda: [0.236, 0.382, 0.5, 0.618, 0.786])


class EvaluationConfig(BaseModel):
    price_tol_atr: float = Field(default=0.5, gt=0.0)
    time_tol_bars: int = Field(default=3, ge=1)
    fib_level_tol: float = Field(default=0.02, gt=0.0)


class SizingConfig(BaseModel):
    # Lager B: positionsskalning. Frikopplad från swing-urvalet.
    enabled: bool = False
    entry_levels: list[float] = Field(default_factory=lambda: [0.382, 0.5, 0.618])
    sizes: list[float] = Field(default_factory=lambda: [1.0, 2.0, 3.0])

    @model_validator(mode="after")
    def validate_lengths(self) -> SizingConfig:
        if len(self.entry_levels) != len(self.sizes):
            raise ValueError("entry_levels and sizes must have the same length")
        return self


class BacktestConfig(BaseModel):
    # Kausalt walk-forward: mät hur stabilt urvalet är över tid (Lager A).
    warmup_bars: int = Field(default=60, ge=0)
    step: int = Field(default=1, ge=1)
    extension_tol_bars: int = Field(default=5, ge=0)
    # Stabilitets-gate (Validate-spåret). Drift är en FÖRSTKLASSIG kriterie vid
    # sidan av flip/confirmed — en swing vars endpunkt vandrar långt vid hopp är
    # instabil även om flip_rate ser låg ut. Trösklarna är principsatta start-
    # värden, tunbara i Research; ändra en sak i taget och spåra i leaderboard.
    gate_max_flip_rate: float = Field(default=0.35, ge=0.0)
    gate_min_confirmed_rate: float = Field(default=0.5, ge=0.0)
    gate_min_direction_consistency: float = Field(default=0.8, ge=0.0)
    gate_max_endpoint_drift_bars: float = Field(default=40.0, ge=0.0)


class Settings(BaseModel):
    seed: int = 42
    data: DataConfig = Field(default_factory=DataConfig)
    pivots: PivotConfig = Field(default_factory=PivotConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    fib: FibConfig = Field(default_factory=FibConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    sizing: SizingConfig = Field(default_factory=SizingConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)

    def config_hash(self) -> str:
        """Stabil hash av hela konfigurationen — används i audit-loggar."""
        payload = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:12]


def load_settings(path: str | Path | None = None) -> Settings:
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw = yaml.safe_load(path.read_text()) or {}
    return Settings(**raw)
