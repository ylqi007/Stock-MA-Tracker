"""Strategy-state repository interface."""

from __future__ import annotations

from typing import Protocol

from stock_ma_tracker.state.models import StoredStrategyState


class StrategyStateRepository(Protocol):
    """Persistence interface for the latest strategy state."""

    def load(self, symbol: str) -> StoredStrategyState | None:
        """Load the latest stored state for a symbol."""
        ...

    def save(self, state: StoredStrategyState) -> None:
        """Persist the latest state for a symbol."""
        ...
