"""Adapters for analyzing locally stored market data."""

from __future__ import annotations

import pandas as pd

from stock_ma_tracker.market_data import MarketDataRepository
from stock_ma_tracker.tracker.service import TrackerError


class StoredHistoryProvider:
    """Adapt stored price bars to the tracker history interface."""

    def __init__(self, repository: MarketDataRepository) -> None:
        self._repository = repository

    def fetch_history(
        self,
        symbol: str,
        period: str,
    ) -> pd.DataFrame:
        """Load locally stored price bars as a pandas DataFrame.

        The period argument is accepted to satisfy the existing
        MarketDataProvider protocol. Data retention is currently controlled
        by the market-data synchronization configuration.
        """
        del period

        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise TrackerError("symbol must not be empty")

        bars = self._repository.load(normalized_symbol)

        if not bars:
            raise TrackerError(
                f"no stored market data found for {normalized_symbol}; "
                "run 'stock-ma-tracker sync-data' first"
            )

        return pd.DataFrame(
            {
                "Open": [bar.open for bar in bars],
                "High": [bar.high for bar in bars],
                "Low": [bar.low for bar in bars],
                "Close": [bar.close for bar in bars],
                "Volume": [bar.volume for bar in bars],
            },
            index=pd.DatetimeIndex(
                [bar.trading_date for bar in bars],
                name="Date",
            ),
        )
