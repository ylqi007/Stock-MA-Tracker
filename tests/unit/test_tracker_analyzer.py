from datetime import date

from stock_ma_tracker.analysis import (
    CrossSignal,
    MovingAverageAnalysis,
    PricePosition,
)
from stock_ma_tracker.application.tracker_analyzer import (
    TrackerMarketAnalyzer,
)


class FakeTrackerService:
    def __init__(self, result: MovingAverageAnalysis) -> None:
        self._result = result
        self.received_symbol: str | None = None

    def track(self, symbol: str) -> MovingAverageAnalysis:
        self.received_symbol = symbol
        return self._result


def test_analyze_adapts_tracker_result() -> None:
    tracker = FakeTrackerService(
        MovingAverageAnalysis(
            symbol="QQQ",
            date=date(2026, 7, 17),
            close=608.0,
            moving_average=580.0,
            window=200,
            position=PricePosition.ABOVE,
            cross_signal=CrossSignal.NONE,
            distance_percentage=4.827586,
        )
    )

    analyzer = TrackerMarketAnalyzer(tracker)

    result = analyzer.analyze("QQQ")

    assert tracker.received_symbol == "QQQ"
    assert result.symbol == "QQQ"
    assert result.trading_date == date(2026, 7, 17)
    assert result.close == 608.0
    assert result.moving_average == 580.0
