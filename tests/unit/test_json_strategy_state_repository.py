import json
from datetime import date
from pathlib import Path

import pytest

from stock_ma_tracker.state import (
    JsonStrategyStateRepository,
    StateRepositoryError,
    StoredStrategyState,
)
from stock_ma_tracker.strategy import StrategyState


def test_load_returns_none_when_state_does_not_exist(
    tmp_path: Path,
) -> None:
    repository = JsonStrategyStateRepository(tmp_path)

    assert repository.load("QQQ") is None


def test_save_and_load_state(tmp_path: Path) -> None:
    repository = JsonStrategyStateRepository(tmp_path)

    expected = StoredStrategyState(
        symbol="qqq",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 17),
        price=610.25,
        moving_average=585.40,
    )

    repository.save(expected)

    actual = repository.load(" QQQ ")

    assert actual == expected


def test_save_creates_normalized_symbol_file(tmp_path: Path) -> None:
    repository = JsonStrategyStateRepository(tmp_path)

    state = StoredStrategyState(
        symbol=" qqq ",
        state=StrategyState.RISK_OFF,
        trading_date=date(2026, 7, 17),
        price=560.0,
        moving_average=580.0,
    )

    repository.save(state)

    assert (tmp_path / "QQQ.json").exists()


def test_save_writes_expected_json(tmp_path: Path) -> None:
    repository = JsonStrategyStateRepository(tmp_path)

    state = StoredStrategyState(
        symbol="QQQ",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 17),
        price=610.25,
        moving_average=585.40,
    )

    repository.save(state)

    payload = json.loads((tmp_path / "QQQ.json").read_text(encoding="utf-8"))

    assert payload == {
        "moving_average": 585.40,
        "price": 610.25,
        "state": "RISK_ON",
        "symbol": "QQQ",
        "trading_date": "2026-07-17",
    }


def test_load_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "QQQ.json"
    path.write_text("{invalid-json", encoding="utf-8")

    repository = JsonStrategyStateRepository(tmp_path)

    with pytest.raises(
        StateRepositoryError,
        match="Failed to load strategy state",
    ):
        repository.load("QQQ")


def test_save_replaces_existing_state(tmp_path: Path) -> None:
    repository = JsonStrategyStateRepository(tmp_path)

    repository.save(
        StoredStrategyState(
            symbol="QQQ",
            state=StrategyState.RISK_OFF,
            trading_date=date(2026, 7, 16),
            price=560.0,
            moving_average=580.0,
        )
    )

    updated = StoredStrategyState(
        symbol="QQQ",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 17),
        price=610.0,
        moving_average=585.0,
    )

    repository.save(updated)

    assert repository.load("QQQ") == updated
