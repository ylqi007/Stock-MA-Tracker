"""Typed application configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    """Project metadata configuration."""

    name: str
    version: str


@dataclass(frozen=True)
class MarketDataConfig:
    """Market data retrieval and retention configuration."""

    provider: str
    signal_symbol: str
    trade_symbol: str
    interval: str
    auto_adjust: bool
    overlap_calendar_days: int
    max_stored_rows: int


@dataclass(frozen=True)
class StrategyConfig:
    """Moving-average strategy configuration."""

    name: str
    version: int
    sma_window: int
    risk_on_multiplier: float
    risk_off_multiplier: float
    threshold_inclusive: bool
    neutral_behavior: str
    initial_state: str


@dataclass(frozen=True)
class NotificationConfig:
    """Notification delivery configuration."""

    provider: str
    mode: str
    include_chart: bool


@dataclass(frozen=True)
class StorageConfig:
    """Local storage path configuration."""

    data_directory: Path
    state_directory: Path
    history_directory: Path
    chart_directory: Path


@dataclass(frozen=True)
class AppConfig:
    """Complete application configuration."""

    project: ProjectConfig
    market_data: MarketDataConfig
    strategy: StrategyConfig
    notification: NotificationConfig
    storage: StorageConfig
