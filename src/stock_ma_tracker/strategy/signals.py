from __future__ import annotations

import math
from enum import StrEnum


class InvalidSignalInputError(ValueError):
    """Raised when signal input values are not valid."""


class PricePosition(StrEnum):
    ABOVE = "above"
    BELOW = "below"
    EQUAL = "equal"


class CrossSignal(StrEnum):
    CROSS_UP = "cross_up"
    CROSS_DOWN = "cross_down"
    NONE = "none"


def _validate_signal_value(
    value: float,
    name: str,
) -> None:
    """Validate that a signal input is a finite numeric value."""
    if not math.isfinite(value):
        raise InvalidSignalInputError(
            f"{name} must be a finite number",
        )


def determine_price_position(
    price: float,
    moving_average: float,
) -> PricePosition:
    """Determine whether a price is above, below, or equal to a moving average.

    Raises:
        InvalidSignalInputError: If either input is not a finite number.
    """
    _validate_signal_value(price, "price")
    _validate_signal_value(moving_average, "moving_average")

    if price > moving_average:
        return PricePosition.ABOVE

    if price < moving_average:
        return PricePosition.BELOW

    return PricePosition.EQUAL


def detect_ma_cross(
    previous_price: float,
    previous_moving_average: float,
    current_price: float,
    current_moving_average: float,
) -> CrossSignal:
    """Detect whether the price crossed the moving average.

    Args:
        previous_price: The price from the previous observation.
        previous_moving_average: The moving average from the previous observation.
        current_price: The price from the current observation.
        current_moving_average: The moving average from the current observation.

    Returns:
        CROSS_UP when the price moves from at or below the moving average
        to above it.

        CROSS_DOWN when the price moves from at or above the moving average
        to below it.

        NONE when no crossing occurs.
    """
    previous_position = determine_price_position(
        price=previous_price,
        moving_average=previous_moving_average,
    )
    current_position = determine_price_position(
        price=current_price,
        moving_average=current_moving_average,
    )

    if (
        previous_position in {PricePosition.BELOW, PricePosition.EQUAL}
        and current_position is PricePosition.ABOVE
    ):
        return CrossSignal.CROSS_UP

    if (
        previous_position in {PricePosition.ABOVE, PricePosition.EQUAL}
        and current_position is PricePosition.BELOW
    ):
        return CrossSignal.CROSS_DOWN

    return CrossSignal.NONE
