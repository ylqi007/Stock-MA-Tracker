"""Configuration file loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from stock_ma_tracker.config.models import (
    AppConfig,
    MarketDataConfig,
    NotificationConfig,
    ProjectConfig,
    StorageConfig,
    StrategyConfig,
)
from stock_ma_tracker.config.validator import ConfigurationError, validate_config


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
    except KeyError as error:
        raise ConfigurationError(
            f"Missing required configuration value: {error.args[0]}"
        ) from error
    except (TypeError, ValueError) as error:
        raise ConfigurationError("Configuration contains an invalid value.") from error

    validate_config(config)
    return config
