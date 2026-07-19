from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pytest

from stock_ma_tracker.cli import main
from stock_ma_tracker.config import ConfigurationError
from stock_ma_tracker.strategy.signals import (
    CrossSignal,
    PricePosition,
)
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
        result: FakeMovingAverageAnalysis,
    ) -> None:
        self._result = result
        self.tracked_symbol: str | None = None

    def track(
        self,
        symbol: str,
    ) -> FakeMovingAverageAnalysis:
        self.tracked_symbol = symbol
        return self._result


class FailingTrackerService:
    def track(
        self,
        symbol: str,
    ) -> FakeMovingAverageAnalysis:
        raise TrackerError(
            f"no market data returned for {symbol.upper()}",
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


def test_track_command_tracks_symbol_and_prints_analysis(
    analysis_result: FakeMovingAverageAnalysis,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tracker = FakeTrackerService(analysis_result)
    fake_config = object()

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: fake_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        lambda config: tracker,
    )

    exit_code = main(
        [
            "--config",
            "test-config.yaml",
            "track",
            "qqq",
        ],
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert tracker.tracked_symbol == "qqq"
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


def test_track_command_passes_config_to_factory(
    analysis_result: FakeMovingAverageAnalysis,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_arguments: dict[str, Any] = {}
    tracker = FakeTrackerService(analysis_result)
    fake_config = object()

    def fake_load_config(
        config_path: str,
    ) -> object:
        captured_arguments["config_path"] = config_path
        return fake_config

    def fake_create_tracker_service(
        config: object,
    ) -> FakeTrackerService:
        captured_arguments["config"] = config
        return tracker

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        fake_load_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        fake_create_tracker_service,
    )

    exit_code = main(
        [
            "--config",
            "configs/test.yaml",
            "track",
            "QQQ",
        ],
    )

    assert exit_code == 0
    assert captured_arguments["config_path"] == "configs/test.yaml"
    assert captured_arguments["config"] is fake_config


def test_track_command_returns_error_when_tracking_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_config = object()
    tracker = FailingTrackerService()

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: fake_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_tracker_service",
        lambda config: tracker,
    )

    exit_code = main(
        [
            "track",
            "QQQ",
        ],
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == ("Error: no market data returned for QQQ\n")


def test_track_command_returns_error_when_config_loading_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_load_config(
        config_path: str,
    ) -> object:
        raise ConfigurationError(
            f"configuration file not found: {config_path}",
        )

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        fake_load_config,
    )

    exit_code = main(
        [
            "--config",
            "missing.yaml",
            "track",
            "QQQ",
        ],
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == ("Error: configuration file not found: missing.yaml\n")


def test_track_command_requires_symbol(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as error:
        main(["track"])

    captured = capsys.readouterr()

    assert error.value.code == 2
    assert "the following arguments are required: symbol" in captured.err
