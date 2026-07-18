"""Market data domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PriceBar:
    """Daily adjusted market price data."""

    trading_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
