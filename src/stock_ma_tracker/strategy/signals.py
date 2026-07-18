from __future__ import annotations

from enum import Enum


class PricePosition(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    EQUAL = "equal"


def determine_price_position(
    price: float,
    moving_average: float,
) -> PricePosition:
    """Determine whether a price is above, below, or equal to a moving average."""
    if price > moving_average:
        return PricePosition.ABOVE

    if price < moving_average:
        return PricePosition.BELOW

    return PricePosition.EQUAL
