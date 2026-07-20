"""Unit tests for strategy notification formatting."""

from __future__ import annotations

from datetime import date

import pytest

from stock_ma_tracker.application import StrategyRunResult
from stock_ma_tracker.notification import (
    format_strategy_notification,
)
from stock_ma_tracker.strategy import (
    BufferedStrategyResult,
    StrategyState,
)


def test_format_strategy_notification() -> None:
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 20),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_OFF,
            current_state=StrategyState.RISK_ON,
            price=525.0,
            moving_average=500.0,
            upper_threshold=520.0,
            lower_threshold=485.0,
        ),
    )

    message = format_strategy_notification(
        result,
        moving_average_window=200,
    )

    assert message == (
        "📈 Stock MA Tracker\n"
        "\n"
        "Symbol: QQQ\n"
        "Date: 2026-07-20\n"
        "Close: 525.00\n"
        "SMA200: 500.00\n"
        "\n"
        "Previous state: RISK_OFF\n"
        "Current state: RISK_ON\n"
        "\n"
        "Upper threshold: 520.00\n"
        "Lower threshold: 485.00"
    )


def test_format_strategy_notification_rounds_values() -> None:
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 20),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.UNKNOWN,
            current_state=StrategyState.RISK_ON,
            price=525.126,
            moving_average=500.987,
            upper_threshold=521.02648,
            lower_threshold=485.95739,
        ),
    )

    message = format_strategy_notification(
        result,
        moving_average_window=200,
    )

    assert "Close: 525.13" in message
    assert "SMA200: 500.99" in message
    assert "Upper threshold: 521.03" in message
    assert "Lower threshold: 485.96" in message


def test_format_strategy_notification_uses_requested_window() -> None:
    result = StrategyRunResult(
        symbol="VOO",
        trading_date=date(2026, 7, 20),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_ON,
            current_state=StrategyState.RISK_OFF,
            price=480.0,
            moving_average=500.0,
            upper_threshold=520.0,
            lower_threshold=485.0,
        ),
    )

    message = format_strategy_notification(
        result,
        moving_average_window=50,
    )

    assert "Symbol: VOO" in message
    assert "SMA50: 500.00" in message
    assert "Previous state: RISK_ON" in message
    assert "Current state: RISK_OFF" in message


@pytest.mark.parametrize(
    "moving_average_window",
    [
        0,
        -1,
        -200,
    ],
)
def test_format_strategy_notification_rejects_invalid_window(
    moving_average_window: int,
) -> None:
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 20),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.UNKNOWN,
            current_state=StrategyState.RISK_ON,
            price=525.0,
            moving_average=500.0,
            upper_threshold=520.0,
            lower_threshold=485.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match=("moving_average_window must be greater than zero"),
    ):
        format_strategy_notification(
            result,
            moving_average_window=moving_average_window,
        )
