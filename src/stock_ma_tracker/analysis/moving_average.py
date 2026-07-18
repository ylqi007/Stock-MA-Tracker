from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from stock_ma_tracker.strategy.moving_average import calculate_sma
from stock_ma_tracker.strategy.signals import (
    CrossSignal,
    PricePosition,
    detect_ma_cross,
    determine_price_position,
)


class MovingAverageAnalysisError(ValueError):
    """Raised when moving-average analysis cannot be completed."""


@dataclass(frozen=True)
class MovingAverageAnalysis:
    symbol: str
    date: date
    close: float
    moving_average: float
    window: int
    position: PricePosition
    cross_signal: CrossSignal
    distance_percentage: float


def analyze_moving_average(
    symbol: str,
    close_prices: pd.Series,
    window: int,
) -> MovingAverageAnalysis:
    """Analyze the latest price against a simple moving average."""
    if not symbol.strip():
        raise MovingAverageAnalysisError("symbol must not be empty")

    minimum_required_rows = window + 1

    if len(close_prices) < minimum_required_rows:
        raise MovingAverageAnalysisError(
            f"at least {minimum_required_rows} close prices are required "
            f"for a {window}-period moving-average cross analysis",
        )

    moving_averages = calculate_sma(
        prices=close_prices,
        window=window,
    )

    previous_close = float(close_prices.iloc[-2])
    current_close = float(close_prices.iloc[-1])

    previous_moving_average = float(moving_averages.iloc[-2])
    current_moving_average = float(moving_averages.iloc[-1])

    position = determine_price_position(
        price=current_close,
        moving_average=current_moving_average,
    )

    cross_signal = detect_ma_cross(
        previous_price=previous_close,
        previous_moving_average=previous_moving_average,
        current_price=current_close,
        current_moving_average=current_moving_average,
    )

    distance_percentage = (current_close - current_moving_average) / current_moving_average * 100

    analysis_date = _extract_analysis_date(close_prices.index[-1])

    return MovingAverageAnalysis(
        symbol=symbol.strip().upper(),
        date=analysis_date,
        close=current_close,
        moving_average=current_moving_average,
        window=window,
        position=position,
        cross_signal=cross_signal,
        distance_percentage=distance_percentage,
    )


def _extract_analysis_date(index_value: object) -> date:
    """Convert the latest Series index value into a date."""
    if isinstance(index_value, pd.Timestamp):
        return index_value.date()

    if isinstance(index_value, date):
        return index_value

    raise MovingAverageAnalysisError(
        "close price index must contain date-like values",
    )
