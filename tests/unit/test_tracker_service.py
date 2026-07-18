from datetime import date

import pandas as pd
import pytest

from stock_ma_tracker.strategy.signals import CrossSignal, PricePosition
from stock_ma_tracker.tracker.service import (
    TrackerError,
    TrackerService,
    TrackerSettings,
)


class FakeMarketDataProvider:
    def __init__(
        self,
        market_data: pd.DataFrame,
    ) -> None:
        self._market_data = market_data
        self.requested_symbol: str | None = None
        self.requested_period: str | None = None

    def fetch_history(
        self,
        symbol: str,
        period: str,
    ) -> pd.DataFrame:
        self.requested_symbol = symbol
        self.requested_period = period

        return self._market_data


def test_track_returns_moving_average_analysis() -> None:
    market_data = pd.DataFrame(
        {
            "Open": [9.5, 10.5, 11.5, 12.5],
            "Close": [10.0, 11.0, 12.0, 13.0],
            "Volume": [100, 110, 120, 130],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    result = tracker.track("qqq")

    assert provider.requested_symbol == "QQQ"
    assert provider.requested_period == "1mo"

    assert result.symbol == "QQQ"
    assert result.date == date(2026, 7, 17)
    assert result.close == 13.0
    assert result.moving_average == 12.0
    assert result.position is PricePosition.ABOVE
    assert result.cross_signal is CrossSignal.NONE
    assert result.distance_percentage == pytest.approx(8.333333)


@pytest.mark.parametrize("symbol", ["", " ", "   "])
def test_track_rejects_empty_symbol(
    symbol: str,
) -> None:
    provider = FakeMarketDataProvider(pd.DataFrame())
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    with pytest.raises(
        TrackerError,
        match="symbol must not be empty",
    ):
        tracker.track(symbol)


def test_track_rejects_empty_market_data() -> None:
    provider = FakeMarketDataProvider(pd.DataFrame())
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    with pytest.raises(
        TrackerError,
        match="no market data returned for QQQ",
    ):
        tracker.track("QQQ")


def test_track_rejects_market_data_without_close_column() -> None:
    market_data = pd.DataFrame(
        {
            "Open": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    with pytest.raises(
        TrackerError,
        match="market data for QQQ does not contain a Close column",
    ):
        tracker.track("QQQ")


def test_track_rejects_market_data_without_valid_close_prices() -> None:
    market_data = pd.DataFrame(
        {
            "Close": [
                float("nan"),
                float("nan"),
            ],
        },
        index=pd.date_range(
            start="2026-07-16",
            periods=2,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=1,
            history_period="1mo",
        ),
    )

    with pytest.raises(
        TrackerError,
        match="market data for QQQ does not contain valid close prices",
    ):
        tracker.track("QQQ")


def test_track_wraps_analysis_errors() -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0],
        },
        index=pd.date_range(
            start="2026-07-15",
            periods=3,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    with pytest.raises(
        TrackerError,
        match=("failed to analyze QQQ: at least 4 close prices are required"),
    ):
        tracker.track("QQQ")


def test_track_drops_missing_close_prices() -> None:
    market_data = pd.DataFrame(
        {
            "Close": [
                10.0,
                float("nan"),
                11.0,
                12.0,
                13.0,
            ],
        },
        index=pd.date_range(
            start="2026-07-13",
            periods=5,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)
    tracker = TrackerService(
        market_data_provider=provider,
        settings=TrackerSettings(
            moving_average_window=3,
            history_period="1mo",
        ),
    )

    result = tracker.track("QQQ")

    assert result.date == date(2026, 7, 17)
    assert result.close == 13.0
    assert result.moving_average == 12.0


@pytest.mark.parametrize(
    "window",
    [0, -1, -100],
)
def test_tracker_settings_rejects_invalid_window(
    window: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=("moving_average_window must be greater than or equal to 1"),
    ):
        TrackerSettings(
            moving_average_window=window,
            history_period="1mo",
        )


@pytest.mark.parametrize(
    "history_period",
    ["", " ", "   "],
)
def test_tracker_settings_rejects_empty_history_period(
    history_period: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="history_period must not be empty",
    ):
        TrackerSettings(
            moving_average_window=200,
            history_period=history_period,
        )
