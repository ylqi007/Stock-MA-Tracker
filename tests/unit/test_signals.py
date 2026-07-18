import pytest

from stock_ma_tracker.strategy.signals import (
    CrossSignal,
    InvalidSignalInputError,
    PricePosition,
    detect_ma_cross,
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


def test_detect_ma_cross_returns_cross_up() -> None:
    result = detect_ma_cross(
        previous_price=99.0,
        previous_moving_average=100.0,
        current_price=102.0,
        current_moving_average=101.0,
    )

    assert result is CrossSignal.CROSS_UP


def test_detect_ma_cross_returns_cross_down() -> None:
    result = detect_ma_cross(
        previous_price=102.0,
        previous_moving_average=100.0,
        current_price=98.0,
        current_moving_average=99.0,
    )

    assert result is CrossSignal.CROSS_DOWN


@pytest.mark.parametrize(
    (
        "previous_price",
        "previous_moving_average",
        "current_price",
        "current_moving_average",
    ),
    [
        (101.0, 100.0, 102.0, 101.0),
        (99.0, 100.0, 98.0, 99.0),
        (100.0, 100.0, 100.0, 100.0),
    ],
)
def test_detect_ma_cross_returns_none_when_no_cross_occurs(
    previous_price: float,
    previous_moving_average: float,
    current_price: float,
    current_moving_average: float,
) -> None:
    result = detect_ma_cross(
        previous_price=previous_price,
        previous_moving_average=previous_moving_average,
        current_price=current_price,
        current_moving_average=current_moving_average,
    )

    assert result is CrossSignal.NONE


def test_detect_ma_cross_returns_cross_up_from_equal_position() -> None:
    result = detect_ma_cross(
        previous_price=100.0,
        previous_moving_average=100.0,
        current_price=102.0,
        current_moving_average=101.0,
    )

    assert result is CrossSignal.CROSS_UP


def test_detect_ma_cross_returns_cross_down_from_equal_position() -> None:
    result = detect_ma_cross(
        previous_price=100.0,
        previous_moving_average=100.0,
        current_price=98.0,
        current_moving_average=99.0,
    )

    assert result is CrossSignal.CROSS_DOWN


@pytest.mark.parametrize(
    ("price", "moving_average", "invalid_name"),
    [
        (float("nan"), 100.0, "price"),
        (100.0, float("nan"), "moving_average"),
    ],
)
def test_determine_price_position_rejects_nan(
    price: float,
    moving_average: float,
    invalid_name: str,
) -> None:
    with pytest.raises(
        InvalidSignalInputError,
        match=rf"{invalid_name} must be a finite number",
    ):
        determine_price_position(
            price=price,
            moving_average=moving_average,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        float("inf"),
        float("-inf"),
    ],
)
def test_determine_price_position_rejects_infinite_values(
    invalid_value: float,
) -> None:
    with pytest.raises(
        InvalidSignalInputError,
        match="price must be a finite number",
    ):
        determine_price_position(
            price=invalid_value,
            moving_average=100.0,
        )


@pytest.mark.parametrize(
    (
        "previous_price",
        "previous_moving_average",
        "current_price",
        "current_moving_average",
    ),
    [
        (float("nan"), 100.0, 101.0, 100.0),
        (99.0, float("nan"), 101.0, 100.0),
        (99.0, 100.0, float("nan"), 100.0),
        (99.0, 100.0, 101.0, float("nan")),
    ],
)
def test_detect_ma_cross_rejects_nan_inputs(
    previous_price: float,
    previous_moving_average: float,
    current_price: float,
    current_moving_average: float,
) -> None:
    with pytest.raises(InvalidSignalInputError):
        detect_ma_cross(
            previous_price=previous_price,
            previous_moving_average=previous_moving_average,
            current_price=current_price,
            current_moving_average=current_moving_average,
        )
