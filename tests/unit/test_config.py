from pathlib import Path

import pytest

from stock_ma_tracker.config import (
    ConfigurationError,
    load_config,
)


def test_load_valid_config():
    config = load_config(Path("config/strategy.yaml"))

    assert config.project.name == "stock-ma-tracker"
    assert config.market_data.signal_symbol == "QQQ"
    assert config.market_data.trade_symbol == "TQQQ"
    assert config.strategy.sma_window == 200
    assert config.strategy.risk_on_multiplier == 1.04
    assert config.strategy.risk_off_multiplier == 0.97
    assert config.strategy.initial_state == "UNKNOWN"


def test_missing_config_file():
    with pytest.raises(
        ConfigurationError,
        match="does not exist",
    ):
        load_config("config/not-found.yaml")


def test_rejects_insufficient_stored_rows(tmp_path):
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
project:
  name: stock-ma-tracker
  version: "0.1.0"

market_data:
  provider: yahoo
  signal_symbol: QQQ
  trade_symbol: TQQQ
  interval: 1d
  auto_adjust: true
  overlap_calendar_days: 7
  max_stored_rows: 100

strategy:
  name: sma_buffer
  version: 1
  sma_window: 200
  risk_on_multiplier: 1.04
  risk_off_multiplier: 0.97
  threshold_inclusive: true
  neutral_behavior: keep_previous
  initial_state: UNKNOWN

notification:
  provider: telegram
  mode: signal_only
  include_chart: true

storage:
  data_directory: data
  state_directory: state
  history_directory: history
  chart_directory: charts
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError,
        match="max_stored_rows",
    ):
        load_config(config_file)
