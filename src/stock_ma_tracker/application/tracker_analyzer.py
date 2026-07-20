"""Moving-average analyzer backed by TrackerService."""

from __future__ import annotations

from stock_ma_tracker.application.strategy_runner import LatestMarketAnalysis
from stock_ma_tracker.tracker import TrackerService


class TrackerMarketAnalyzer:
    """Adapt TrackerService to the StrategyRunner analyzer interface."""

    def __init__(self, tracker: TrackerService) -> None:
        self._tracker = tracker

    def analyze(self, symbol: str) -> LatestMarketAnalysis:
        """Return the latest close and moving average for one symbol."""
        analysis = self._tracker.track(symbol)

        return LatestMarketAnalysis(
            symbol=analysis.symbol,
            trading_date=analysis.date,
            close=analysis.close,
            moving_average=analysis.moving_average,
        )
