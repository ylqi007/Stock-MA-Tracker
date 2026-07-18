from datetime import date

from stock_ma_tracker.market_data import (
    MarketDataSyncService,
    PriceBar,
)


class FakeMarketDataProvider:
    def __init__(self, bars: list[PriceBar]) -> None:
        self._bars = bars
        self.requests: list[tuple[str, date, date]] = []

    def get_daily_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[PriceBar]:
        self.requests.append((symbol, start_date, end_date))
        return self._bars


class InMemoryMarketDataRepository:
    def __init__(
        self,
        bars: list[PriceBar] | None = None,
    ) -> None:
        self.bars = bars or []
        self.saved_symbol: str | None = None

    def load(self, symbol: str) -> list[PriceBar]:
        return list(self.bars)

    def save(
        self,
        symbol: str,
        bars: list[PriceBar],
    ) -> None:
        self.saved_symbol = symbol
        self.bars = list(bars)


def make_bar(
    year: int,
    month: int,
    day: int,
    close: float,
) -> PriceBar:
    return PriceBar(
        trading_date=date(year, month, day),
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1_000,
    )


def test_initial_sync_uses_initial_start_date():
    provider = FakeMarketDataProvider(
        [
            make_bar(2026, 7, 1, 550.0),
            make_bar(2026, 7, 2, 551.0),
        ]
    )
    repository = InMemoryMarketDataRepository()

    service = MarketDataSyncService(
        provider=provider,
        repository=repository,
        overlap_calendar_days=7,
        max_stored_rows=400,
    )

    result = service.sync(
        symbol="qqq",
        initial_start_date=date(2025, 1, 1),
        end_date=date(2026, 7, 18),
    )

    assert provider.requests == [
        (
            "QQQ",
            date(2025, 1, 1),
            date(2026, 7, 18),
        )
    ]
    assert result.downloaded_count == 2
    assert result.stored_count == 2
    assert repository.saved_symbol == "QQQ"


def test_incremental_sync_uses_overlap():
    repository = InMemoryMarketDataRepository(
        [
            make_bar(2026, 7, 8, 548.0),
            make_bar(2026, 7, 10, 550.0),
        ]
    )
    provider = FakeMarketDataProvider([])

    service = MarketDataSyncService(
        provider=provider,
        repository=repository,
        overlap_calendar_days=7,
        max_stored_rows=400,
    )

    service.sync(
        symbol="QQQ",
        initial_start_date=date(2025, 1, 1),
        end_date=date(2026, 7, 18),
    )

    assert provider.requests == [
        (
            "QQQ",
            date(2026, 7, 3),
            date(2026, 7, 18),
        )
    ]


def test_downloaded_bar_replaces_existing_same_date():
    repository = InMemoryMarketDataRepository(
        [
            make_bar(2026, 7, 10, 550.0),
        ]
    )
    provider = FakeMarketDataProvider(
        [
            make_bar(2026, 7, 10, 555.0),
            make_bar(2026, 7, 11, 556.0),
        ]
    )

    service = MarketDataSyncService(
        provider=provider,
        repository=repository,
    )

    service.sync(
        symbol="QQQ",
        initial_start_date=date(2025, 1, 1),
        end_date=date(2026, 7, 11),
    )

    assert len(repository.bars) == 2
    assert repository.bars[0].trading_date == date(2026, 7, 10)
    assert repository.bars[0].close == 555.0
    assert repository.bars[1].trading_date == date(2026, 7, 11)


def test_sync_retains_only_max_rows():
    provider = FakeMarketDataProvider(
        [
            make_bar(2026, 7, 1, 501.0),
            make_bar(2026, 7, 2, 502.0),
            make_bar(2026, 7, 3, 503.0),
            make_bar(2026, 7, 4, 504.0),
        ]
    )
    repository = InMemoryMarketDataRepository()

    service = MarketDataSyncService(
        provider=provider,
        repository=repository,
        max_stored_rows=2,
    )

    service.sync(
        symbol="QQQ",
        initial_start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 4),
    )

    assert [bar.trading_date for bar in repository.bars] == [
        date(2026, 7, 3),
        date(2026, 7, 4),
    ]


def test_sync_returns_latest_trading_date():
    provider = FakeMarketDataProvider(
        [
            make_bar(2026, 7, 16, 550.0),
            make_bar(2026, 7, 17, 552.0),
        ]
    )
    repository = InMemoryMarketDataRepository()

    service = MarketDataSyncService(
        provider=provider,
        repository=repository,
    )

    result = service.sync(
        symbol="QQQ",
        initial_start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 18),
    )

    assert result.latest_trading_date == date(2026, 7, 17)
