"""Market data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from stock_ma_tracker.market_data.models import PriceBar


class MarketDataProvider(ABC):
    """Interface for retrieving historical market data."""

    @abstractmethod
    def get_daily_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[PriceBar]:
        """Return daily price bars within the requested date range."""
