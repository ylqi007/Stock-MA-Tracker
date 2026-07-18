from datetime import date
from pathlib import Path

import pytest

from stock_ma_tracker.cli import build_parser, main


def test_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["stock-ma-tracker", "--version"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


def test_validate_config_command(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "stock-ma-tracker",
            "--config",
            "config/strategy.yaml",
            "validate-config",
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Configuration is valid" in captured.out
    assert "config/strategy.yaml" in captured.out


def test_sync_data_command_uses_default_values():
    parser = build_parser()

    args = parser.parse_args(["sync-data"])

    assert args.command == "sync-data"
    assert args.config == Path("config/strategy.yaml")
    assert args.end_date is None
    assert args.initial_start_date is None


def test_sync_data_command_parses_dates():
    parser = build_parser()

    args = parser.parse_args(
        [
            "sync-data",
            "--initial-start-date",
            "2025-01-01",
            "--end-date",
            "2026-07-18",
        ]
    )

    assert args.initial_start_date == date(2025, 1, 1)
    assert args.end_date == date(2026, 7, 18)


def test_config_path_can_be_overridden():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--config",
            "config/test.yaml",
            "sync-data",
        ]
    )

    assert args.config == Path("config/test.yaml")
