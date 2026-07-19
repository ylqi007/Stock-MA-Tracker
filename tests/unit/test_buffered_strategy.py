import pytest

from stock_ma_tracker.strategy import (
    StrategyState,
    evaluate_buffered_strategy,
)


def test_returns_risk_on_at_upper_threshold() -> None:
    result = evaluate_buffered_strategy(
        price=104.0,
        moving_average=100.0,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        previous_state=StrategyState.UNKNOWN,
    )

    assert result.current_state is StrategyState.RISK_ON
    assert result.upper_threshold == pytest.approx(104.0)
    assert result.lower_threshold == pytest.approx(97.0)
    assert result.state_changed is True


def test_returns_risk_off_at_lower_threshold() -> None:
    result = evaluate_buffered_strategy(
        price=97.0,
        moving_average=100.0,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        previous_state=StrategyState.RISK_ON,
    )

    assert result.current_state is StrategyState.RISK_OFF
    assert result.state_changed is True


def test_retains_risk_on_inside_buffer() -> None:
    result = evaluate_buffered_strategy(
        price=101.0,
        moving_average=100.0,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        previous_state=StrategyState.RISK_ON,
    )

    assert result.current_state is StrategyState.RISK_ON
    assert result.state_changed is False


def test_retains_risk_off_inside_buffer() -> None:
    result = evaluate_buffered_strategy(
        price=101.0,
        moving_average=100.0,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        previous_state=StrategyState.RISK_OFF,
    )

    assert result.current_state is StrategyState.RISK_OFF
    assert result.state_changed is False


def test_remains_unknown_inside_buffer_without_previous_state() -> None:
    result = evaluate_buffered_strategy(
        price=100.0,
        moving_average=100.0,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        previous_state=StrategyState.UNKNOWN,
    )

    assert result.current_state is StrategyState.UNKNOWN
    assert result.state_changed is False


def test_rejects_non_positive_price() -> None:
    with pytest.raises(ValueError, match="price must be greater than zero"):
        evaluate_buffered_strategy(
            price=0.0,
            moving_average=100.0,
            risk_on_multiplier=1.04,
            risk_off_multiplier=0.97,
            previous_state=StrategyState.UNKNOWN,
        )


def test_rejects_invalid_multiplier_order() -> None:
    with pytest.raises(
        ValueError,
        match="risk_on_multiplier must be greater",
    ):
        evaluate_buffered_strategy(
            price=100.0,
            moving_average=100.0,
            risk_on_multiplier=0.97,
            risk_off_multiplier=1.04,
            previous_state=StrategyState.UNKNOWN,
        )
