from __future__ import annotations

import pandas as pd


def calculate_sma(
    prices: pd.Series,
    window: int,
) -> pd.Series:
    """Calculate the simple moving average for a price series.

    Args:
        prices: A pandas Series containing price values.
        window: The number of observations used to calculate the average.

    Returns:
        A pandas Series containing the simple moving average.

    Raises:
        ValueError: If window is less than 1.
    """
    if window < 1:
        raise ValueError("window must be greater than or equal to 1")

    return prices.rolling(window=window).mean()
