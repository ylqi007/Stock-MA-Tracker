"""Application configuration validation."""

from __future__ import annotations

from stock_ma_tracker.config.models import AppConfig


class ConfigurationError(ValueError):
    """Raised when application configuration is invalid."""


def validate_config(config: AppConfig) -> None:
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

    if config.strategy.risk_off_multiplier >= config.strategy.risk_on_multiplier:
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
