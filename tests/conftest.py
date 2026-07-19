from pathlib import Path

import pytest

from stock_ma_tracker.config import (
    AppConfig,
    MarketDataConfig,
    NotificationConfig,
    ProjectConfig,
    StorageConfig,
    StrategyConfig,
)


@pytest.fixture
def app_config() -> AppConfig:
    return AppConfig(
        project=ProjectConfig(
            name="stock-ma-tracker",
            version="0.1.0",
        ),
        market_data=MarketDataConfig(
            provider="yahoo",
            signal_symbol="QQQ",
            trade_symbol="TQQQ",
            interval="1d",
            auto_adjust=True,
            overlap_calendar_days=7,
            max_stored_rows=180,
        ),
        strategy=StrategyConfig(
            name="sma_buffer",
            version=1,
            sma_window=3,
            risk_on_multiplier=1.04,
            risk_off_multiplier=0.97,
            threshold_inclusive=True,
            neutral_behavior="keep_previous",
            initial_state="UNKNOWN",
        ),
        notification=NotificationConfig(
            provider="telegram",
            mode="signal_only",
            include_chart=True,
        ),
        storage=StorageConfig(
            data_directory=Path("data"),
            state_directory=Path("state"),
            history_directory=Path("history"),
            chart_directory=Path("charts"),
        ),
    )
