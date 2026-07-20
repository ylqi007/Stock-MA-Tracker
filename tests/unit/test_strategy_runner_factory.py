from pathlib import Path

from stock_ma_tracker.application import (
    StrategyRunner,
    create_strategy_runner,
)
from stock_ma_tracker.config import load_config


def test_create_strategy_runner(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "strategy.yaml"
    data_directory = tmp_path / "data"
    state_directory = tmp_path / "state"

    config_path.write_text(
        f"""
project:
  name: stock-ma-tracker
  version: 0.1.0

market_data:
  provider: yahoo
  signal_symbol: QQQ
  trade_symbol: TQQQ
  interval: 1d
  auto_adjust: true
  overlap_calendar_days: 7
  max_stored_rows: 400

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
  include_chart: false

storage:
  data_directory: {data_directory}
  state_directory: {state_directory}
  history_directory: {tmp_path / "history"}
  chart_directory: {tmp_path / "charts"}
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    runner = create_strategy_runner(config)

    assert isinstance(runner, StrategyRunner)
