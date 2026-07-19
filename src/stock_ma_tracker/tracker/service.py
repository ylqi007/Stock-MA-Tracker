from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from stock_ma_tracker.analysis.moving_average import (
    MovingAverageAnalysis,
    MovingAverageAnalysisError,
    analyze_moving_average,
)


class TrackerError(RuntimeError):
    """Raised when a symbol cannot be tracked."""


class MarketDataProvider(Protocol):
    """Provide historical market data for a symbol."""

    def fetch_history(
        self,
        symbol: str,
        period: str,
    ) -> pd.DataFrame:
        """Fetch historical market data."""
        ...


@dataclass(frozen=True)
class TrackerSettings:
    moving_average_window: int
    history_period: str

    def __post_init__(self) -> None:
        if self.moving_average_window < 1:
            raise ValueError(
                "moving_average_window must be greater than or equal to 1",
            )

        if not self.history_period.strip():
            raise ValueError("history_period must not be empty")


class TrackerService:
    """Track symbols using moving-average analysis."""

    def __init__(
        self,
        market_data_provider: MarketDataProvider,
        settings: TrackerSettings,
    ) -> None:
        self._market_data_provider = market_data_provider
        self._settings = settings

    def track(
        self,
        symbol: str,
    ) -> MovingAverageAnalysis:
        """Track one symbol and return its latest moving-average analysis."""
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise TrackerError("symbol must not be empty")

        market_data = self._market_data_provider.fetch_history(
            symbol=normalized_symbol,
            period=self._settings.history_period,
        )

        close_prices = self._extract_close_prices(
            symbol=normalized_symbol,
            market_data=market_data,
        )

        try:
            return analyze_moving_average(
                symbol=normalized_symbol,
                close_prices=close_prices,
                window=self._settings.moving_average_window,
            )
        except MovingAverageAnalysisError as error:
            raise TrackerError(
                f"failed to analyze {normalized_symbol}: {error}",
            ) from error

    def track_many(
        self,
        symbols: list[str],
    ) -> list[MovingAverageAnalysis]:
        return [self.track(symbol) for symbol in symbols]

    @staticmethod
    def _extract_close_prices(
        symbol: str,
        market_data: pd.DataFrame,
    ) -> pd.Series:
        if market_data.empty:
            raise TrackerError(
                f"no market data returned for {symbol}",
            )

        if "Close" not in market_data.columns:
            raise TrackerError(
                f"market data for {symbol} does not contain a Close column",
            )

        close_prices = market_data["Close"].dropna()

        if close_prices.empty:
            raise TrackerError(
                f"market data for {symbol} does not contain valid close prices",
            )

        return close_prices
