from datetime import date

from stock_ma_tracker.application.strategy_runner import (
    LatestMarketAnalysis,
    StrategyRunner,
)
from stock_ma_tracker.state import StoredStrategyState
from stock_ma_tracker.strategy import StrategyState


class FakeAnalyzer:
    def __init__(self, result: LatestMarketAnalysis) -> None:
        self.result = result
        self.received_symbol: str | None = None

    def analyze(self, symbol: str) -> LatestMarketAnalysis:
        self.received_symbol = symbol
        return self.result


class FakeStateRepository:
    def __init__(
        self,
        stored_state: StoredStrategyState | None = None,
    ) -> None:
        self.stored_state = stored_state
        self.saved_state: StoredStrategyState | None = None

    def load(self, symbol: str) -> StoredStrategyState | None:
        return self.stored_state

    def save(self, state: StoredStrategyState) -> None:
        self.saved_state = state


def test_run_enters_risk_on_and_saves_state() -> None:
    analyzer = FakeAnalyzer(
        LatestMarketAnalysis(
            symbol="QQQ",
            trading_date=date(2026, 7, 20),
            close=525.0,
            moving_average=500.0,
        )
    )
    repository = FakeStateRepository()

    runner = StrategyRunner(
        analyzer=analyzer,
        state_repository=repository,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        initial_state=StrategyState.UNKNOWN,
    )

    result = runner.run("qqq")

    assert analyzer.received_symbol == "QQQ"
    assert result.strategy.current_state is StrategyState.RISK_ON
    assert result.notification_required is True

    assert repository.saved_state is not None
    assert repository.saved_state.symbol == "QQQ"
    assert repository.saved_state.state is StrategyState.RISK_ON


def test_run_retains_previous_state_inside_buffer() -> None:
    analyzer = FakeAnalyzer(
        LatestMarketAnalysis(
            symbol="QQQ",
            trading_date=date(2026, 7, 20),
            close=500.0,
            moving_average=500.0,
        )
    )

    previous = StoredStrategyState(
        symbol="QQQ",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 19),
        price=521.0,
        moving_average=500.0,
    )

    repository = FakeStateRepository(previous)

    runner = StrategyRunner(
        analyzer=analyzer,
        state_repository=repository,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        initial_state=StrategyState.UNKNOWN,
    )

    result = runner.run("QQQ")

    assert result.strategy.current_state is StrategyState.RISK_ON
    assert result.notification_required is False


def test_run_detects_risk_off_transition() -> None:
    analyzer = FakeAnalyzer(
        LatestMarketAnalysis(
            symbol="QQQ",
            trading_date=date(2026, 7, 20),
            close=480.0,
            moving_average=500.0,
        )
    )

    previous = StoredStrategyState(
        symbol="QQQ",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 19),
        price=525.0,
        moving_average=500.0,
    )

    repository = FakeStateRepository(previous)

    runner = StrategyRunner(
        analyzer=analyzer,
        state_repository=repository,
        risk_on_multiplier=1.04,
        risk_off_multiplier=0.97,
        initial_state=StrategyState.UNKNOWN,
    )

    result = runner.run("QQQ")

    assert result.strategy.previous_state is StrategyState.RISK_ON
    assert result.strategy.current_state is StrategyState.RISK_OFF
    assert result.notification_required is True
