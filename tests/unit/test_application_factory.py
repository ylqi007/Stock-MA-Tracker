from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from stock_ma_tracker.application.factory import create_tracker_service
from stock_ma_tracker.config.models import AppConfig
from stock_ma_tracker.tracker.service import TrackerService


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


def test_create_tracker_service_returns_tracker_service(
    app_config: AppConfig,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)

    tracker = create_tracker_service(
        config=app_config,
        market_data_provider=provider,
    )

    assert isinstance(tracker, TrackerService)


def test_create_tracker_service_uses_injected_market_data_provider(
    app_config: AppConfig,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)

    tracker = create_tracker_service(
        config=app_config,
        market_data_provider=provider,
    )

    result = tracker.track("qqq")

    assert provider.requested_symbol == "QQQ"
    assert result.symbol == "QQQ"


def test_create_tracker_service_maps_history_period_from_config(
    app_config: AppConfig,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)

    tracker = create_tracker_service(
        config=app_config,
        market_data_provider=provider,
    )

    tracker.track("QQQ")

    assert provider.requested_period == "180d"


def test_create_tracker_service_maps_moving_average_window_from_config(
    app_config: AppConfig,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)

    tracker = create_tracker_service(
        config=app_config,
        market_data_provider=provider,
    )

    result = tracker.track("QQQ")

    assert result.window == 3
    assert result.moving_average == 12.0
    assert result.date == date(2026, 7, 17)


def test_create_tracker_service_builds_service_from_config(
    app_config: AppConfig,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    provider = FakeMarketDataProvider(market_data)

    tracker = create_tracker_service(
        config=app_config,
        market_data_provider=provider,
    )

    result = tracker.track("qqq")

    assert isinstance(tracker, TrackerService)

    assert provider.requested_symbol == "QQQ"
    assert provider.requested_period == "180d"

    assert result.symbol == "QQQ"
    assert result.window == 3
    assert result.moving_average == 12.0
    assert result.date == date(2026, 7, 17)


def test_create_tracker_service_creates_default_yahoo_provider(
    app_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    market_data = pd.DataFrame(
        {
            "Close": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
    )
    fake_provider = FakeMarketDataProvider(market_data)

    def create_fake_provider() -> FakeMarketDataProvider:
        return fake_provider

    monkeypatch.setattr(
        "stock_ma_tracker.application.factory.YahooHistoryProvider",
        lambda provider: create_fake_provider(),
    )

    tracker = create_tracker_service(config=app_config)
    result = tracker.track("QQQ")

    assert fake_provider.requested_symbol == "QQQ"
    assert fake_provider.requested_period == "180d"
    assert result.symbol == "QQQ"
