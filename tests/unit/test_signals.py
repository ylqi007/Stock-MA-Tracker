import pytest

from stock_ma_tracker.strategy.signals import (
    PricePosition,
    determine_price_position,
)


@pytest.mark.parametrize(
    ("price", "moving_average", "expected"),
    [
        (105.0, 100.0, PricePosition.ABOVE),
        (95.0, 100.0, PricePosition.BELOW),
        (100.0, 100.0, PricePosition.EQUAL),
    ],
)
def test_determine_price_position(
    price: float,
    moving_average: float,
    expected: PricePosition,
) -> None:
    result = determine_price_position(
        price=price,
        moving_average=moving_average,
    )

    assert result is expected
