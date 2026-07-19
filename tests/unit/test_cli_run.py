from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pytest

from stock_ma_tracker.cli import main
from stock_ma_tracker.config import (
    AppConfig,
    ConfigurationError,
    MarketDataConfig,
    NotificationConfig,
    ProjectConfig,
    StorageConfig,
    StrategyConfig,
)
from stock_ma_tracker.strategy.signals import CrossSignal, PricePosition
from stock_ma_tracker.tracker.service import TrackerError


@dataclass(frozen=True)
class FakeMovingAverageAnalysis:
    symbol: str
    date: date
    close: float
    moving_average: float
    window: int
    position: PricePosition
    cross_signal: CrossSignal
    distance_percentage: float


class FakeTrackerService:
    def __init__(
        self,
        results: list[FakeMovingAverageAnalysis],
    ) -> None:
        self._results = results
        self.tracked_symbols: list[str] | None = None

    def track_many(
        self,
        symbols: list[str],
    ) -> list[FakeMovingAverageAnalysis]:
        self.tracked_symbols = symbols
        return self._results


class FailingTrackerService:
    def track_many(
        self,
        symbols: list[str],
    ) -> list[FakeMovingAverageAnalysis]:
        raise TrackerError(f"no market data returned for {symbols[0].upper()}")


@pytest.fixture
def run_config() -> AppConfig:
    return AppConfig(
        project=ProjectConfig(
            name="stock-ma-tracker",
            version="0.1.0",
        ),
        market_data=MarketDataConfig(
            provider="yahoo",
            signal_symbol="QQQ",
            trade_symbol="TQQQ",
            interval="1d",
            auto_adjust=True,
            overlap_calendar_days=7,
            max_stored_rows=400,
        ),
        strategy=StrategyConfig(
            name="sma_buffer",
            version=1,
            sma_window=200,
            risk_on_multiplier=1.04,
            risk_off_multiplier=0.97,
            threshold_inclusive=True,
            neutral_behavior="keep_previous",
            initial_state="UNKNOWN",
        ),
        notification=NotificationConfig(
            provider="telegram",
            mode="signal_only",
            include_chart=True,
        ),
        storage=StorageConfig(
            data_directory="data",
            state_directory="state",
            history_directory="history",
            chart_directory="charts",
        ),
    )


@pytest.fixture
def analysis_result() -> FakeMovingAverageAnalysis:
    return FakeMovingAverageAnalysis(
        symbol="QQQ",
        date=date(2026, 7, 17),
        close=610.25,
        moving_average=584.42,
        window=200,
        position=PricePosition.ABOVE,
        cross_signal=CrossSignal.NONE,
        distance_percentage=4.419424,
    )


def test_run_command_tracks_configured_signal_symbol_and_prints_analysis(
    analysis_result: FakeMovingAverageAnalysis,
    run_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tracker = FakeTrackerService([analysis_result])

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        lambda config: tracker,
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert tracker.tracked_symbols == ["QQQ"]
    assert captured.err == ""
    assert captured.out == (
        "Symbol: QQQ\n"
        "Date: 2026-07-17\n"
        "Close: 610.25\n"
        "SMA200: 584.42\n"
        "Position: above\n"
        "Cross signal: none\n"
        "Distance: +4.42%\n"
    )


def test_run_command_passes_config_to_factory(
    analysis_result: FakeMovingAverageAnalysis,
    run_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_arguments: dict[str, Any] = {}
    tracker = FakeTrackerService([analysis_result])

    def fake_load_config(config_path: object) -> AppConfig:
        captured_arguments["config_path"] = config_path
        return run_config

    def fake_create_tracker_service(config: AppConfig) -> FakeTrackerService:
        captured_arguments["config"] = config
        return tracker

    monkeypatch.setattr("stock_ma_tracker.cli.load_config", fake_load_config)
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        fake_create_tracker_service,
    )

    exit_code = main(["--config", "configs/test.yaml", "run"])

    assert exit_code == 0
    assert str(captured_arguments["config_path"]) == "configs/test.yaml"
    assert captured_arguments["config"] is run_config


def test_run_command_returns_error_when_tracking_fails(
    run_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        lambda config: FailingTrackerService(),
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: no market data returned for QQQ\n"


def test_run_command_returns_error_when_config_loading_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_load_config(config_path: object) -> AppConfig:
        raise ConfigurationError(f"configuration file not found: {config_path}")

    monkeypatch.setattr("stock_ma_tracker.cli.load_config", fake_load_config)

    exit_code = main(["--config", "missing.yaml", "run"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: configuration file not found: missing.yaml\n"
