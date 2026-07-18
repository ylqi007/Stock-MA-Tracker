from datetime import date

import pandas as pd
import pytest

from stock_ma_tracker.analysis.moving_average import analyze_moving_average
from stock_ma_tracker.strategy.signals import CrossSignal, PricePosition


def test_analyze_moving_average_returns_latest_analysis() -> None:
    close_prices = pd.Series(
        [10.0, 11.0, 12.0, 13.0],
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
        name="Close",
    )

    result = analyze_moving_average(
        symbol="qqq",
        close_prices=close_prices,
        window=3,
    )

    assert result.symbol == "QQQ"
    assert result.date == date(2026, 7, 17)
    assert result.close == 13.0
    assert result.moving_average == 12.0
    assert result.window == 3
    assert result.position is PricePosition.ABOVE
    assert result.cross_signal is CrossSignal.NONE
    assert result.distance_percentage == pytest.approx(8.333333)


def test_analyze_moving_average_detects_cross_up() -> None:
    close_prices = pd.Series(
        [10.0, 10.0, 9.0, 12.0],
        index=pd.date_range(
            start="2026-07-14",
            periods=4,
            freq="D",
        ),
        name="Close",
    )

    result = analyze_moving_average(
        symbol="QQQ",
        close_prices=close_prices,
        window=3,
    )

    assert result.position is PricePosition.ABOVE
    assert result.cross_signal is CrossSignal.CROSS_UP


def test_analyze_moving_average_rejects_insufficient_prices() -> None:
    close_prices = pd.Series(
        [10.0, 11.0, 12.0],
        index=pd.date_range(
            start="2026-07-15",
            periods=3,
            freq="D",
        ),
    )

    with pytest.raises(
        ValueError,
        match="at least 4 close prices are required",
    ):
        analyze_moving_average(
            symbol="QQQ",
            close_prices=close_prices,
            window=3,
        )


@pytest.mark.parametrize("symbol", ["", " ", "   "])
def test_analyze_moving_average_rejects_empty_symbol(
    symbol: str,
) -> None:
    close_prices = pd.Series(
        [10.0, 11.0],
        index=pd.date_range(
            start="2026-07-16",
            periods=2,
            freq="D",
        ),
    )

    with pytest.raises(
        ValueError,
        match="symbol must not be empty",
    ):
        analyze_moving_average(
            symbol=symbol,
            close_prices=close_prices,
            window=1,
        )


def test_analyze_moving_average_rejects_non_date_index() -> None:
    close_prices = pd.Series(
        [10.0, 11.0],
        index=[0, 1],
    )

    with pytest.raises(
        ValueError,
        match="close price index must contain date-like values",
    ):
        analyze_moving_average(
            symbol="QQQ",
            close_prices=close_prices,
            window=1,
        )
