"""Strategy calculation helpers."""

from stock_ma_tracker.strategy.buffered import (
    BufferedStrategyResult,
    StrategyState,
    evaluate_buffered_strategy,
)
from stock_ma_tracker.strategy.moving_average import calculate_sma
from stock_ma_tracker.strategy.signals import (
    CrossSignal,
    InvalidSignalInputError,
    PricePosition,
    detect_ma_cross,
    determine_price_position,
)

__all__ = [
    "BufferedStrategyResult",
    "CrossSignal",
    "InvalidSignalInputError",
    "PricePosition",
    "StrategyState",
    "calculate_sma",
    "detect_ma_cross",
    "determine_price_position",
    "evaluate_buffered_strategy",
]
