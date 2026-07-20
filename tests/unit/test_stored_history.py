from datetime import date

import pandas as pd
import pytest

from stock_ma_tracker.application.stored_history import StoredHistoryProvider
from stock_ma_tracker.market_data import PriceBar
from stock_ma_tracker.tracker import TrackerError


class FakeMarketDataRepository:
    def __init__(self, bars: list[PriceBar]) -> None:
        self._bars = bars
        self.loaded_symbol: str | None = None

    def load(self, symbol: str) -> list[PriceBar]:
        self.loaded_symbol = symbol
        return self._bars

    def save(
        self,
        symbol: str,
        bars: list[PriceBar],
    ) -> None:
        raise NotImplementedError


def test_fetch_history_converts_price_bars_to_dataframe() -> None:
    repository = FakeMarketDataRepository(
        [
            PriceBar(
                trading_date=date(2026, 7, 16),
                open=600.0,
                high=605.0,
                low=598.0,
                close=603.0,
                volume=40_000_000,
            ),
            PriceBar(
                trading_date=date(2026, 7, 17),
                open=604.0,
                high=610.0,
                low=602.0,
                close=608.0,
                volume=42_000_000,
            ),
        ]
    )

    provider = StoredHistoryProvider(repository)

    result = provider.fetch_history(" qqq ", "400d")

    assert repository.loaded_symbol == "QQQ"
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]
    assert result.index.name == "Date"
    assert result.iloc[-1]["Close"] == 608.0


def test_fetch_history_rejects_missing_stored_data() -> None:
    provider = StoredHistoryProvider(
        FakeMarketDataRepository([]),
    )

    with pytest.raises(
        TrackerError,
        match="run 'stock-ma-tracker sync-data' first",
    ):
        provider.fetch_history("QQQ", "400d")


def test_fetch_history_rejects_empty_symbol() -> None:
    provider = StoredHistoryProvider(
        FakeMarketDataRepository([]),
    )

    with pytest.raises(
        TrackerError,
        match="symbol must not be empty",
    ):
        provider.fetch_history("   ", "400d")
