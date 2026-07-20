"""Strategy notification message formatting."""

from __future__ import annotations

from stock_ma_tracker.application import StrategyRunResult


def format_strategy_notification(
    result: StrategyRunResult,
    *,
    moving_average_window: int,
) -> str:
    """Format a buffered strategy state change for notification."""

    if moving_average_window <= 0:
        raise ValueError("moving_average_window must be greater than zero")

    strategy = result.strategy

    return "\n".join(
        [
            "📈 Stock MA Tracker",
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
