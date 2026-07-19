"""JSON-backed strategy-state repository."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from stock_ma_tracker.state.models import StoredStrategyState
from stock_ma_tracker.strategy import StrategyState


class StateRepositoryError(RuntimeError):
    """Raised when persisted strategy state cannot be read or written."""


class JsonStrategyStateRepository:
    """Store the latest strategy state as one JSON file per symbol."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def load(self, symbol: str) -> StoredStrategyState | None:
        path = self._path_for(symbol)

        if not path.exists():
            return None

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return self._deserialize(payload)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise StateRepositoryError(f"Failed to load strategy state from {path}") from exc

    def save(self, state: StoredStrategyState) -> None:
        path = self._path_for(state.symbol)
        temporary_path = path.with_suffix(".tmp")

        payload = {
            "symbol": state.symbol,
            "state": state.state.value,
            "trading_date": state.trading_date.isoformat(),
            "price": state.price,
            "moving_average": state.moving_average,
        }

        try:
            self._directory.mkdir(parents=True, exist_ok=True)

            temporary_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            temporary_path.replace(path)
        except OSError as exc:
            raise StateRepositoryError(f"Failed to save strategy state to {path}") from exc

    def _path_for(self, symbol: str) -> Path:
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("symbol must not be empty")

        if not normalized_symbol.replace("-", "").replace(".", "").isalnum():
            raise ValueError(f"invalid symbol: {symbol!r}")

        return self._directory / f"{normalized_symbol}.json"

    @staticmethod
    def _deserialize(payload: dict[str, Any]) -> StoredStrategyState:
        return StoredStrategyState(
            symbol=str(payload["symbol"]),
            state=StrategyState(str(payload["state"])),
            trading_date=date.fromisoformat(str(payload["trading_date"])),
            price=float(payload["price"]),
            moving_average=float(payload["moving_average"]),
        )
