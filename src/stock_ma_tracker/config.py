"""Application configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when application configuration is invalid."""


@dataclass(frozen=True)
class ProjectConfig:
    """Project metadata."""

    name: str
    version: str


@dataclass(frozen=True)
class MarketDataConfig:
    """Market data configuration."""

    provider: str
    signal_symbol: str
    trade_symbol: str
    interval: str
    auto_adjust: bool
    overlap_calendar_days: int
    max_stored_rows: int


@dataclass(frozen=True)
class StrategyConfig:
    """Trading strategy configuration."""

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
    """Notification configuration."""

    provider: str
    mode: str
    include_chart: bool


@dataclass(frozen=True)
class StorageConfig:
    """File storage configuration."""

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


def load_config(config_path: str | Path) -> AppConfig:
    """Load and validate application configuration from a YAML file."""

    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Configuration file does not exist: {path}")

    try:
        with path.open("r", encoding="utf-8") as config_file:
            raw_config = yaml.safe_load(config_file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML configuration file: {path}") from error

    if not isinstance(raw_config, dict):
        raise ConfigurationError("Configuration root must be a mapping.")

    return _parse_config(raw_config)


def _parse_config(raw: dict[str, Any]) -> AppConfig:
    """Convert raw YAML values into validated configuration objects."""
    try:
        project_raw = raw["project"]
        market_raw = raw["market_data"]
        strategy_raw = raw["strategy"]
        notification_raw = raw["notification"]
        storage_raw = raw["storage"]
    except KeyError as error:
        raise ConfigurationError(
            f"Missing required configuration section: {error.args[0]}"
        ) from error

    config = AppConfig(
        project=ProjectConfig(
            name=str(project_raw["name"]),
            version=str(project_raw["version"]),
        ),
        market_data=MarketDataConfig(
            provider=str(market_raw["provider"]),
            signal_symbol=str(market_raw["signal_symbol"]).upper(),
            trade_symbol=str(market_raw["trade_symbol"]).upper(),
            interval=str(market_raw["interval"]),
            auto_adjust=bool(market_raw["auto_adjust"]),
            overlap_calendar_days=int(market_raw["overlap_calendar_days"]),
            max_stored_rows=int(market_raw["max_stored_rows"]),
        ),
        strategy=StrategyConfig(
            name=str(strategy_raw["name"]),
            version=int(strategy_raw["version"]),
            sma_window=int(strategy_raw["sma_window"]),
            risk_on_multiplier=float(strategy_raw["risk_on_multiplier"]),
            risk_off_multiplier=float(strategy_raw["risk_off_multiplier"]),
            threshold_inclusive=bool(strategy_raw["threshold_inclusive"]),
            neutral_behavior=str(strategy_raw["neutral_behavior"]),
            initial_state=str(strategy_raw["initial_state"]).upper(),
        ),
        notification=NotificationConfig(
            provider=str(notification_raw["provider"]),
            mode=str(notification_raw["mode"]),
            include_chart=bool(notification_raw["include_chart"]),
        ),
        storage=StorageConfig(
            data_directory=Path(storage_raw["data_directory"]),
            state_directory=Path(storage_raw["state_directory"]),
            history_directory=Path(storage_raw["history_directory"]),
            chart_directory=Path(storage_raw["chart_directory"]),
        ),
    )

    _validate_config(config)
    return config


def _validate_config(config: AppConfig) -> None:
    """Validate configuration values."""

    if config.market_data.overlap_calendar_days < 0:
        raise ConfigurationError("overlap_calendar_days must be greater than or equal to 0.")

    if config.market_data.max_stored_rows < config.strategy.sma_window:
        raise ConfigurationError("max_stored_rows must be greater than or equal to sma_window.")

    if config.strategy.sma_window <= 0:
        raise ConfigurationError("sma_window must be greater than 0.")

    if config.strategy.risk_on_multiplier <= 1:
        raise ConfigurationError("risk_on_multiplier must be greater than 1.")

    if not 0 < config.strategy.risk_off_multiplier < 1:
        raise ConfigurationError("risk_off_multiplier must be between 0 and 1.")

    if config.strategy.risk_off_multiplier >= (config.strategy.risk_on_multiplier):
        raise ConfigurationError("risk_off_multiplier must be less than risk_on_multiplier.")

    if config.strategy.initial_state not in {
        "UNKNOWN",
        "RISK_ON",
        "RISK_OFF",
    }:
        raise ConfigurationError("initial_state must be UNKNOWN, RISK_ON, or RISK_OFF.")

    if config.notification.mode not in {
        "signal_only",
        "daily_summary",
    }:
        raise ConfigurationError("notification mode must be signal_only or daily_summary.")
