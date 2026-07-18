import pytest

from stock_ma_tracker.cli import main


def test_check_command(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["stock-ma-tracker", "check"])

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "configured correctly" in captured.out


def test_test_command(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["stock-ma-tracker", "test"])

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Just a test parser" in captured.out


def test_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["stock-ma-tracker", "--version"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "0.1.0" in captured.out
