"""Market data repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from stock_ma_tracker.market_data.models import PriceBar


class MarketDataRepository(ABC):
    """Interface for persisting historical market data."""

    @abstractmethod
    def load(self, symbol: str) -> list[PriceBar]:
        """Load all stored price bars for a symbol."""

    @abstractmethod
    def save(self, symbol: str, bars: list[PriceBar]) -> None:
        """Persist price bars for a symbol."""
