"""Strategy-state persistence models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from stock_ma_tracker.strategy import StrategyState


@dataclass(frozen=True)
class StoredStrategyState:
    """Latest persisted strategy state for one symbol."""

    symbol: str
    state: StrategyState
    trading_date: date
    price: float
    moving_average: float
