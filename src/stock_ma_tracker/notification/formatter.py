"""Strategy notification message formatting."""

from __future__ import annotations

from stock_ma_tracker.application.strategy_runner import (
    StrategyRunResult,
)
from stock_ma_tracker.strategy import StrategyState


def _state_icon(state: StrategyState) -> str:
    """Return a directional icon for one strategy state."""

    if state is StrategyState.RISK_ON:
        return "📈"

    if state is StrategyState.RISK_OFF:
        return "📉"

    return "ℹ️"


def should_send_strategy_notification(mode: str, result: StrategyRunResult) -> bool:
    """Return whether a strategy run result should be sent as a notification."""

    normalized_mode = mode.strip().lower()

    if normalized_mode == "signal_only":
        return result.notification_required

    if normalized_mode in {"signal_and_status", "daily_summary"}:
        return True

    raise ValueError(f"Unknown notification mode: {mode}")


def format_strategy_notification(
    result: StrategyRunResult,
    *,
    moving_average_window: int,
) -> str:
    """Format a buffered strategy notification message."""

    if moving_average_window <= 0:
        raise ValueError("moving_average_window must be greater than zero")

    strategy = result.strategy

    if not result.notification_required:
        return "\n".join(
            [
                f"{_state_icon(strategy.current_state)} Stock MA Tracker Daily Check",
                "",
                "Daily check: no risk signal change.",
                "",
                f"Symbol: {result.symbol}",
                f"Date: {result.trading_date.isoformat()}",
                f"Close: {strategy.price:.2f}",
                (f"SMA{moving_average_window}: {strategy.moving_average:.2f}"),
                "",
                (f"Current state: {strategy.current_state.value}"),
            ]
        )

    return "\n".join(
        [
            f"{_state_icon(strategy.current_state)} Stock MA Tracker Risk Signal",
            "",
            f"Symbol: {result.symbol}",
            f"Date: {result.trading_date.isoformat()}",
            f"Close: {strategy.price:.2f}",
            (f"SMA{moving_average_window}: {strategy.moving_average:.2f}"),
            "",
            (f"Previous state: {strategy.previous_state.value}"),
            (f"Current state: {strategy.current_state.value}"),
            "",
            (f"Upper threshold: {strategy.upper_threshold:.2f}"),
            (f"Lower threshold: {strategy.lower_threshold:.2f}"),
        ]
    )
