"""Yahoo Finance market data provider."""

from __future__ import annotations

from datetime import date, timedelta

import yfinance as yf

from stock_ma_tracker.market_data.models import PriceBar
from stock_ma_tracker.market_data.provider import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Retrieve historical market data from Yahoo Finance."""

    def __init__(self, *, auto_adjust: bool = True) -> None:
        self._auto_adjust = auto_adjust

    def get_daily_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[PriceBar]:
        """Return daily historical prices for a ticker."""

        if not symbol.strip():
            raise ValueError("symbol must not be empty")

        if start_date > end_date:
            raise ValueError("start_date must not be later than end_date")

        ticker = yf.Ticker(symbol.strip().upper())

        # yfinance treats end as exclusive, so add one calendar day.
        history = ticker.history(
            start=start_date.isoformat(),
            end=(end_date + timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=self._auto_adjust,
            actions=False,
        )

        if history.empty:
            return []

        bars: list[PriceBar] = []

        for timestamp, row in history.iterrows():
            bars.append(
                PriceBar(
                    trading_date=timestamp.date(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )

        return bars
