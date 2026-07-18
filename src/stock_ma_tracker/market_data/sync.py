"""Market data synchronization service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from stock_ma_tracker.market_data.models import PriceBar
from stock_ma_tracker.market_data.provider import MarketDataProvider
from stock_ma_tracker.market_data.repository import MarketDataRepository


@dataclass(frozen=True)
class MarketDataSyncResult:
    """Summary of one market data synchronization."""

    symbol: str
    requested_start_date: date
    requested_end_date: date
    downloaded_count: int
    stored_count: int
    latest_trading_date: date | None


class MarketDataSyncService:
    """Synchronize remote market data with local storage."""

    def __init__(
        self,
        provider: MarketDataProvider,
        repository: MarketDataRepository,
        *,
        overlap_calendar_days: int = 7,
        max_stored_rows: int = 400,
    ) -> None:
        if overlap_calendar_days < 0:
            raise ValueError("overlap_calendar_days must not be negative")

        if max_stored_rows <= 0:
            raise ValueError("max_stored_rows must be greater than zero")

        self._provider = provider
        self._repository = repository
        self._overlap_calendar_days = overlap_calendar_days
        self._max_stored_rows = max_stored_rows

    def sync(
        self,
        symbol: str,
        *,
        end_date: date,
        initial_start_date: date,
    ) -> MarketDataSyncResult:
        """Synchronize market data for one symbol."""

        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("symbol must not be empty")

        if initial_start_date > end_date:
            raise ValueError("initial_start_date must not be later than end_date")

        stored_bars = self._repository.load(normalized_symbol)

        request_start_date = self._determine_start_date(
            stored_bars=stored_bars,
            initial_start_date=initial_start_date,
        )

        downloaded_bars = self._provider.get_daily_prices(
            symbol=normalized_symbol,
            start_date=request_start_date,
            end_date=end_date,
        )

        merged_bars = self._merge_bars(
            stored_bars=stored_bars,
            downloaded_bars=downloaded_bars,
        )

        retained_bars = merged_bars[-self._max_stored_rows :]

        self._repository.save(
            normalized_symbol,
            retained_bars,
        )

        latest_trading_date = retained_bars[-1].trading_date if retained_bars else None

        return MarketDataSyncResult(
            symbol=normalized_symbol,
            requested_start_date=request_start_date,
            requested_end_date=end_date,
            downloaded_count=len(downloaded_bars),
            stored_count=len(retained_bars),
            latest_trading_date=latest_trading_date,
        )

    def _determine_start_date(
        self,
        *,
        stored_bars: list[PriceBar],
        initial_start_date: date,
    ) -> date:
        if not stored_bars:
            return initial_start_date

        latest_stored_date = max(bar.trading_date for bar in stored_bars)

        overlap_start_date = latest_stored_date - timedelta(days=self._overlap_calendar_days)

        return max(
            initial_start_date,
            overlap_start_date,
        )

    @staticmethod
    def _merge_bars(
        *,
        stored_bars: list[PriceBar],
        downloaded_bars: list[PriceBar],
    ) -> list[PriceBar]:
        bars_by_date = {bar.trading_date: bar for bar in stored_bars}

        for bar in downloaded_bars:
            bars_by_date[bar.trading_date] = bar

        return sorted(
            bars_by_date.values(),
            key=lambda bar: bar.trading_date,
        )
