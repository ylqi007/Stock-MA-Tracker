import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from stock_ma_tracker.strategy.moving_average import calculate_sma


def test_calculate_sma_returns_expected_values() -> None:
    prices = pd.Series(
        [10.0, 12.0, 14.0, 16.0, 18.0],
        name="Close",
    )

    result = calculate_sma(prices, window=3)

    expected = pd.Series(
        [float("nan"), float("nan"), 12.0, 14.0, 16.0],
        name="Close",
    )

    assert_series_equal(result, expected)


def test_calculate_sma_preserves_index() -> None:
    index = pd.date_range(
        start="2026-07-01",
        periods=4,
        freq="D",
    )
    prices = pd.Series(
        [100.0, 102.0, 104.0, 106.0],
        index=index,
        name="Close",
    )

    result = calculate_sma(prices, window=2)

    assert result.index.equals(index)


def test_calculate_sma_with_window_of_one_returns_original_prices() -> None:
    prices = pd.Series(
        [100.0, 102.0, 104.0],
        name="Close",
    )

    result = calculate_sma(prices, window=1)

    assert_series_equal(result, prices)


@pytest.mark.parametrize("window", [0, -1, -100])
def test_calculate_sma_rejects_invalid_window(window: int) -> None:
    prices = pd.Series([100.0, 102.0, 104.0])

    with pytest.raises(
        ValueError,
        match="window must be greater than or equal to 1",
    ):
        calculate_sma(prices, window=window)
