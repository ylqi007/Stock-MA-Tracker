"""Unit tests for the CLI run command."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from stock_ma_tracker.application import StrategyRunResult
from stock_ma_tracker.cli import main
from stock_ma_tracker.config import ConfigurationError
from stock_ma_tracker.notification import NotificationError
from stock_ma_tracker.strategy import (
    BufferedStrategyResult,
    StrategyState,
)
from stock_ma_tracker.tracker import TrackerError


class FakeStrategyRunner:
    """Fake strategy runner used by CLI unit tests."""

    def __init__(self, result: StrategyRunResult) -> None:
        self._result = result
        self.received_symbol: str | None = None

    def run(self, symbol: str) -> StrategyRunResult:
        self.received_symbol = symbol
        return self._result


class FailingStrategyRunner:
    """Strategy runner that always raises a TrackerError."""

    def run(self, symbol: str) -> StrategyRunResult:
        raise TrackerError(f"no market data returned for {symbol}")


class FakeNotifier:
    """Fake notifier used by CLI unit tests."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)


@pytest.fixture
def run_config() -> SimpleNamespace:
    """Return the minimum configuration required by the run command."""

    return SimpleNamespace(
        market_data=SimpleNamespace(
            signal_symbol="QQQ",
        ),
        strategy=SimpleNamespace(
            sma_window=200,
        ),
        notification=SimpleNamespace(
            mode="signal_only",
        ),
    )


@pytest.fixture
def risk_on_result() -> StrategyRunResult:
    """Return a strategy result representing a RISK_OFF to RISK_ON change."""

    return StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 17),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_OFF,
            current_state=StrategyState.RISK_ON,
            price=610.25,
            moving_average=584.42,
            upper_threshold=607.80,
            lower_threshold=566.89,
        ),
    )


def test_run_command_executes_buffered_strategy(
    run_config: SimpleNamespace,
    risk_on_result: StrategyRunResult,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    runner = FakeStrategyRunner(risk_on_result)
    notifier = FakeNotifier()

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_telegram_notifier",
        lambda: notifier,
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert runner.received_symbol == "QQQ"

    assert "Buffered strategy run completed" in captured.out
    assert "Symbol: QQQ" in captured.out
    assert "Date: 2026-07-17" in captured.out
    assert "Close: 610.25" in captured.out
    assert "SMA200: 584.42" in captured.out
    assert "Upper threshold: 607.80" in captured.out
    assert "Lower threshold: 566.89" in captured.out
    assert "Previous state: RISK_OFF" in captured.out
    assert "Current state: RISK_ON" in captured.out
    assert "State changed: yes" in captured.out
    assert "Notification required: yes" in captured.out

    assert captured.err == ""
    assert len(notifier.messages) == 1

    assert "Stock MA Tracker" in notifier.messages[0]
    assert "Symbol: QQQ" in notifier.messages[0]
    assert "Current state: RISK_ON" in notifier.messages[0]
    assert "Notification sent: yes" in captured.out


def test_run_command_uses_configured_signal_symbol(
    run_config: SimpleNamespace,
    risk_on_result: StrategyRunResult,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_config.market_data.signal_symbol = "VOO"
    runner = FakeStrategyRunner(risk_on_result)

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_telegram_notifier",
        FakeNotifier,
    )

    exit_code = main(["run"])

    assert exit_code == 0
    assert runner.received_symbol == "VOO"


def test_run_command_passes_config_to_strategy_runner_factory(
    run_config: SimpleNamespace,
    risk_on_result: StrategyRunResult,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_arguments: dict[str, Any] = {}
    runner = FakeStrategyRunner(risk_on_result)

    def fake_load_config(
        config_path: Path,
    ) -> SimpleNamespace:
        captured_arguments["config_path"] = config_path
        return run_config

    def fake_create_strategy_runner(
        config: object,
    ) -> FakeStrategyRunner:
        captured_arguments["config"] = config
        return runner

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        fake_load_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        fake_create_strategy_runner,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_telegram_notifier",
        FakeNotifier,
    )

    exit_code = main(
        [
            "--config",
            "configs/test.yaml",
            "run",
        ]
    )

    assert exit_code == 0
    assert captured_arguments["config_path"] == Path("configs/test.yaml")
    assert captured_arguments["config"] is run_config
    assert runner.received_symbol == "QQQ"


def test_run_command_reports_unchanged_state(
    run_config: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 17),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_ON,
            current_state=StrategyState.RISK_ON,
            price=600.00,
            moving_average=584.42,
            upper_threshold=607.80,
            lower_threshold=566.89,
        ),
    )

    runner = FakeStrategyRunner(result)

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert runner.received_symbol == "QQQ"

    assert "Previous state: RISK_ON" in captured.out
    assert "Current state: RISK_ON" in captured.out
    assert "State changed: no" in captured.out
    assert "Notification required: no" in captured.out

    assert captured.err == ""


def test_run_command_sends_status_notification_when_signal_and_status_mode(
    run_config: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_config.notification.mode = "signal_and_status"
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 17),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_ON,
            current_state=StrategyState.RISK_ON,
            price=600.00,
            moving_average=584.42,
            upper_threshold=607.80,
            lower_threshold=566.89,
        ),
    )

    runner = FakeStrategyRunner(result)
    notifier = FakeNotifier()

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_telegram_notifier",
        lambda: notifier,
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Notification required: no" in captured.out
    assert "Notification sent: yes" in captured.out
    assert len(notifier.messages) == 1
    assert "Daily check: no risk signal change." in notifier.messages[0]


def test_run_command_reports_unknown_state_inside_buffer(
    run_config: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 17),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.UNKNOWN,
            current_state=StrategyState.UNKNOWN,
            price=584.42,
            moving_average=584.42,
            upper_threshold=607.80,
            lower_threshold=566.89,
        ),
    )

    runner = FakeStrategyRunner(result)

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Previous state: UNKNOWN" in captured.out
    assert "Current state: UNKNOWN" in captured.out
    assert "State changed: no" in captured.out
    assert "Notification required: no" in captured.out

    assert captured.err == ""


def test_run_command_returns_error_when_config_loading_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_load_config(config_path: Path) -> object:
        raise ConfigurationError(f"configuration file not found: {config_path}")

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        fake_load_config,
    )

    exit_code = main(
        [
            "--config",
            "configs/missing.yaml",
            "run",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "Error: configuration file not found: configs/missing.yaml\n" == captured.err


def test_run_command_returns_error_when_strategy_runner_fails(
    run_config: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: FailingStrategyRunner(),
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: no market data returned for QQQ\n"


def test_run_command_returns_error_when_notification_fails(
    run_config: SimpleNamespace,
    risk_on_result: StrategyRunResult,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class FailingNotifier:
        def send(self, message: str) -> None:
            raise NotificationError("failed to send Telegram notification")

    runner = FakeStrategyRunner(risk_on_result)

    monkeypatch.setattr(
        "stock_ma_tracker.cli.load_config",
        lambda config_path: run_config,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_strategy_runner",
        lambda config: runner,
    )
    monkeypatch.setattr(
        "stock_ma_tracker.cli.create_telegram_notifier",
        lambda: FailingNotifier(),
    )

    exit_code = main(["run"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == ("Error: failed to send Telegram notification\n")
