"""Buffered moving-average strategy evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StrategyState(StrEnum):
    """Persistent state produced by the buffered strategy."""

    UNKNOWN = "UNKNOWN"
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"


@dataclass(frozen=True)
class BufferedStrategyResult:
    """Result of evaluating one price against buffered SMA thresholds."""

    previous_state: StrategyState
    current_state: StrategyState
    price: float
    moving_average: float
    upper_threshold: float
    lower_threshold: float

    @property
    def state_changed(self) -> bool:
        """Return whether the strategy moved to a different known state."""
        return (
            self.previous_state != self.current_state
            and self.current_state is not StrategyState.UNKNOWN
        )


def evaluate_buffered_strategy(
    *,
    price: float,
    moving_average: float,
    risk_on_multiplier: float,
    risk_off_multiplier: float,
    previous_state: StrategyState,
) -> BufferedStrategyResult:
    """Evaluate a buffered moving-average strategy.

    Rules:

    - price >= moving_average * risk_on_multiplier -> RISK_ON
    - price <= moving_average * risk_off_multiplier -> RISK_OFF
    - otherwise retain the previous state
    """

    if price <= 0:
        raise ValueError("price must be greater than zero")

    if moving_average <= 0:
        raise ValueError("moving_average must be greater than zero")

    if risk_on_multiplier <= risk_off_multiplier:
        raise ValueError("risk_on_multiplier must be greater than risk_off_multiplier")

    upper_threshold = moving_average * risk_on_multiplier
    lower_threshold = moving_average * risk_off_multiplier

    if price >= upper_threshold:
        current_state = StrategyState.RISK_ON
    elif price <= lower_threshold:
        current_state = StrategyState.RISK_OFF
    else:
        current_state = previous_state

    return BufferedStrategyResult(
        previous_state=previous_state,
        current_state=current_state,
        price=price,
        moving_average=moving_average,
        upper_threshold=upper_threshold,
        lower_threshold=lower_threshold,
    )
