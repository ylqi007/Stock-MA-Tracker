"""Application workflow for running the buffered strategy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from stock_ma_tracker.state import (
    StoredStrategyState,
    StrategyStateRepository,
)
from stock_ma_tracker.strategy import (
    BufferedStrategyResult,
    StrategyState,
    evaluate_buffered_strategy,
)


@dataclass(frozen=True)
class LatestMarketAnalysis:
    symbol: str
    trading_date: date
    close: float
    moving_average: float


class MarketAnalyzer(Protocol):
    def analyze(self, symbol: str) -> LatestMarketAnalysis: ...


@dataclass(frozen=True)
class StrategyRunResult:
    symbol: str
    trading_date: date
    strategy: BufferedStrategyResult

    @property
    def notification_required(self) -> bool:
        return self.strategy.state_changed


class StrategyRunner:
    def __init__(
        self,
        *,
        analyzer: MarketAnalyzer,
        state_repository: StrategyStateRepository,
        risk_on_multiplier: float,
        risk_off_multiplier: float,
        initial_state: StrategyState,
    ) -> None:
        self._analyzer = analyzer
        self._state_repository = state_repository
        self._risk_on_multiplier = risk_on_multiplier
        self._risk_off_multiplier = risk_off_multiplier
        self._initial_state = initial_state

    def run(self, symbol: str) -> StrategyRunResult:
        normalized_symbol = symbol.strip().upper()

        analysis = self._analyzer.analyze(normalized_symbol)
        stored_state = self._state_repository.load(normalized_symbol)

        previous_state = stored_state.state if stored_state is not None else self._initial_state

        strategy_result = evaluate_buffered_strategy(
            price=analysis.close,
            moving_average=analysis.moving_average,
            risk_on_multiplier=self._risk_on_multiplier,
            risk_off_multiplier=self._risk_off_multiplier,
            previous_state=previous_state,
        )

        self._state_repository.save(
            StoredStrategyState(
                symbol=normalized_symbol,
                state=strategy_result.current_state,
                trading_date=analysis.trading_date,
                price=analysis.close,
                moving_average=analysis.moving_average,
            )
        )

        return StrategyRunResult(
            symbol=normalized_symbol,
            trading_date=analysis.trading_date,
            strategy=strategy_result,
        )
