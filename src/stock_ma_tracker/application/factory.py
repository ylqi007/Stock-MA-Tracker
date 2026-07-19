from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from stock_ma_tracker.config.models import AppConfig
from stock_ma_tracker.market_data.yahoo import YahooFinanceProvider
from stock_ma_tracker.tracker.service import (
    MarketDataProvider,
    TrackerService,
    TrackerSettings,
)


class YahooHistoryProvider:
    """Adapt daily price bars to the tracker service history interface."""

    def __init__(self, provider: YahooFinanceProvider) -> None:
        self._provider = provider

    def fetch_history(
        self,
        symbol: str,
        period: str,
    ) -> pd.DataFrame:
        end_date = date.today()
        start_date = end_date - _parse_history_period(period)

        bars = self._provider.get_daily_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        return pd.DataFrame(
            [
                {
                    "Open": bar.open,
                    "High": bar.high,
                    "Low": bar.low,
                    "Close": bar.close,
                    "Volume": bar.volume,
                }
                for bar in bars
            ],
            index=pd.DatetimeIndex([bar.trading_date for bar in bars]),
        )


def create_tracker_service(
    config: AppConfig,
    market_data_provider: MarketDataProvider | None = None,
) -> TrackerService:
    provider = market_data_provider or YahooHistoryProvider(
        YahooFinanceProvider(
            auto_adjust=config.market_data.auto_adjust,
        )
    )

    settings = TrackerSettings(
        moving_average_window=config.strategy.sma_window,
        history_period=f"{config.market_data.max_stored_rows}d",
    )

    return TrackerService(
        market_data_provider=provider,
        settings=settings,
    )


def _parse_history_period(period: str) -> timedelta:
    normalized_period = period.strip().lower()

    if normalized_period.endswith("d"):
        return timedelta(days=int(normalized_period[:-1]))

    if normalized_period.endswith("mo"):
        return timedelta(days=int(normalized_period[:-2]) * 30)

    raise ValueError(f"Unsupported history period: {period}")
