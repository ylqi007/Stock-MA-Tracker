# Stock MA Tracker

A maintainable stock-market trend tracker built with Python, Yahoo Finance, GitHub Actions, and Telegram.

The project uses **QQQ** as the market signal source and is designed to generate strategy notifications for **TQQQ** based on a buffered long-term moving-average strategy.

The application currently supports configuration management, historical market-data synchronization, moving-average analysis, buffered strategy evaluation, and local strategy-state persistence.

> The project only generates informational strategy signals. It does not automatically place trades.

## Strategy Overview

The strategy uses the 200-day simple moving average of QQQ.

```text
Upper threshold = SMA200 × 1.04
Lower threshold = SMA200 × 0.97
```

The strategy evaluates the latest adjusted closing price as follows:

| Condition                | Result                    |
| ------------------------ | ------------------------- |
| Price ≥ upper threshold  | `RISK_ON`                 |
| Price ≤ lower threshold  | `RISK_OFF`                |
| Price between thresholds | Retain the previous state |

The buffer between the upper and lower thresholds reduces frequent state changes when the price moves close to the moving average.

Example:

```text
SMA200 = 500.00
Upper threshold = 520.00
Lower threshold = 485.00
```

In this example:

* A QQQ price of `522.00` produces `RISK_ON`.
* A QQQ price of `482.00` produces `RISK_OFF`.
* A QQQ price of `505.00` retains the previously stored strategy state.

## Current Features

### Configuration

* YAML-based application configuration
* Typed and immutable configuration models
* Configuration loading and validation
* Configurable market-data, strategy, notification, and storage settings
* CLI-based configuration validation

### Market Data

* Yahoo Finance historical market-data provider
* Daily OHLCV price retrieval
* Adjusted-price support
* Typed `PriceBar` domain model
* CSV-based local persistence
* One CSV file per symbol
* Symbol normalization
* Chronological sorting
* Incremental market-data synchronization
* Configurable overlap reconciliation
* Duplicate trading-date replacement
* Configurable historical-data retention

### Strategy Analysis

* Simple moving-average calculation
* Latest price and moving-average analysis
* Price-position evaluation
* Moving-average crossover detection
* Buffered strategy thresholds
* Persistent `RISK_ON`, `RISK_OFF`, and `UNKNOWN` states
* State-change detection

### State Persistence

* JSON-based strategy-state storage
* One state file per symbol
* Atomic-style file replacement through temporary files
* Stored trading date, price, moving average, and strategy state
* Graceful handling of missing state files
* Validation of persisted state data

### Development

* Unit tests with pytest
* Temporary-directory filesystem testing
* Ruff formatting and lint checks
* Editable package installation
* Command-line entry point

## Planned Features

* Application workflow connecting synchronization, analysis, and persistence
* CLI command for buffered strategy evaluation
* Telegram signal notifications
* Notification only when strategy state changes
* Strategy chart generation
* Scheduled GitHub Actions workflow
* Persistent state support in GitHub Actions
* Monthly full-history reconciliation
* Additional tracked symbols
* Improved logging and operational diagnostics

## Application Flow

The intended end-to-end workflow is:

```text
Load configuration
        ↓
Synchronize Yahoo Finance data
        ↓
Store and load PriceBar records
        ↓
Calculate SMA200
        ↓
Load previous strategy state
        ↓
Evaluate buffered thresholds
        ↓
Detect whether the state changed
        ↓
Persist the latest state
        ↓
Send a notification when required
```

## Architecture

The project separates external infrastructure, domain logic, persistence, and application orchestration.

```text
Yahoo Finance
      ↓
YahooFinanceProvider
      ↓
list[PriceBar]
      ↓
MarketDataSyncService
      ↓
CsvMarketDataRepository
      ↓
Moving-average analysis
      ↓
Buffered strategy evaluation
      ↓
JsonStrategyStateRepository
      ↓
Telegram notification
```

The principal abstractions include:

* `MarketDataProvider`: retrieves market data from an external source
* `YahooFinanceProvider`: retrieves historical prices through `yfinance`
* `MarketDataRepository`: defines market-data persistence behavior
* `CsvMarketDataRepository`: stores and loads daily price bars
* `PriceBar`: represents one daily OHLCV record
* `TrackerService`: performs moving-average analysis
* `StrategyState`: represents `UNKNOWN`, `RISK_ON`, or `RISK_OFF`
* `BufferedStrategyResult`: represents one buffered-strategy evaluation
* `StrategyStateRepository`: defines strategy-state persistence behavior
* `JsonStrategyStateRepository`: persists the latest state as JSON

The interfaces allow external data providers and persistence implementations to be replaced without rewriting the core strategy logic.

## Project Structure

```text
Stock-MA-Tracker/
├── config/
│   └── strategy.yaml
├── data/
├── state/
├── history/
├── charts/
├── docs/
├── src/
│   └── stock_ma_tracker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── analysis/
│       ├── application/
│       │   ├── __init__.py
│       │   └── factory.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   └── validator.py
│       ├── market_data/
│       │   ├── __init__.py
│       │   ├── csv_repository.py
│       │   ├── models.py
│       │   ├── provider.py
│       │   ├── repository.py
│       │   ├── sync.py
│       │   └── yahoo.py
│       ├── state/
│       │   ├── __init__.py
│       │   ├── json_repository.py
│       │   ├── models.py
│       │   └── repository.py
│       ├── strategy/
│       │   ├── __init__.py
│       │   ├── buffered.py
│       │   ├── moving_average.py
│       │   └── signals.py
│       └── tracker/
├── tests/
│   └── unit/
├── .env.example
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

The two `state` directories have different purposes:

```text
src/stock_ma_tracker/state/   Python persistence implementation
state/                        Runtime JSON state files
```

## Requirements

* Python 3.12 or later
* Git
* Internet access for Yahoo Finance retrieval

## Installation

Clone the repository:

```bash
git clone https://github.com/ylqi007/Stock-MA-Tracker.git
cd Stock-MA-Tracker
```

Create and activate a virtual environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Verify the CLI:

```bash
stock-ma-tracker --help
stock-ma-tracker --version
```

## Configuration

The primary configuration file is:

```text
config/strategy.yaml
```

Example:

```yaml
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
  include_chart: true

storage:
  data_directory: data
  state_directory: state
  history_directory: history
  chart_directory: charts
```

Validate the configuration:

```bash
stock-ma-tracker validate-config
```

Alternatively:

```bash
python -m stock_ma_tracker validate-config
```

## Synchronizing Market Data

Download or update the configured market data:

```bash
stock-ma-tracker sync-data
```

The synchronization process:

1. Loads existing CSV data.
2. Determines the required Yahoo Finance date range.
3. Re-downloads a configurable overlap period.
4. Replaces duplicate trading dates with the newest records.
5. Sorts records chronologically.
6. Applies the configured retention limit.
7. Saves the merged result.

For QQQ, the resulting file is:

```text
data/QQQ.csv
```

Example CSV structure:

```csv
trading_date,open,high,low,close,volume
2026-07-01,550.2,554.8,548.9,553.7,42100000
2026-07-02,554.1,557.2,552.0,556.4,38900000
```

## Tracking a Symbol

Run the existing moving-average analysis for one symbol:

```bash
stock-ma-tracker track QQQ
```

The command analyzes the latest closing price relative to the configured moving-average window.

The current tracking command provides foundational moving-average analysis. Integration with persisted buffered strategy state is the next application milestone.

## Buffered Strategy Evaluation

The buffered strategy is implemented as pure domain logic.

Example:

```python
from stock_ma_tracker.strategy import (
    StrategyState,
    evaluate_buffered_strategy,
)

result = evaluate_buffered_strategy(
    price=525.0,
    moving_average=500.0,
    risk_on_multiplier=1.04,
    risk_off_multiplier=0.97,
    previous_state=StrategyState.RISK_OFF,
)

print(result.current_state)
print(result.state_changed)
```

Expected result:

```text
StrategyState.RISK_ON
True
```

Pure strategy logic does not perform network or filesystem operations, which makes it straightforward to test independently.

## Strategy State Persistence

The latest strategy state is stored as one JSON file per symbol.

Example:

```text
state/QQQ.json
```

Example content:

```json
{
  "moving_average": 500.0,
  "price": 525.0,
  "state": "RISK_ON",
  "symbol": "QQQ",
  "trading_date": "2026-07-17"
}
```

Example repository usage:

```python
from datetime import date
from pathlib import Path

from stock_ma_tracker.state import (
    JsonStrategyStateRepository,
    StoredStrategyState,
)
from stock_ma_tracker.strategy import StrategyState

repository = JsonStrategyStateRepository(Path("state"))

repository.save(
    StoredStrategyState(
        symbol="QQQ",
        state=StrategyState.RISK_ON,
        trading_date=date(2026, 7, 17),
        price=525.0,
        moving_average=500.0,
    )
)

stored_state = repository.load("QQQ")
print(stored_state)
```

A missing state file is treated as an uninitialized symbol rather than an error.

## Development

Format the project:

```bash
ruff format .
```

Run lint checks:

```bash
ruff check .
```

Verify formatting without changing files:

```bash
ruff format --check .
```

Run all tests:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/unit/test_buffered_strategy.py -v
```

Run the state repository tests:

```bash
pytest tests/unit/test_json_strategy_state_repository.py -v
```

Run the full quality check:

```bash
ruff format --check .
ruff check .
pytest
```

## Development Progress

### Foundation

* [x] Initialize the Python project
* [x] Configure editable package installation
* [x] Add CLI entry points
* [x] Add pytest and Ruff tooling

### Configuration

* [x] Add typed configuration models
* [x] Add YAML configuration loading
* [x] Add configuration validation
* [x] Refactor configuration code into a package

### Market Data

* [x] Add the `PriceBar` domain model
* [x] Add the market-data provider interface
* [x] Add the Yahoo Finance provider
* [x] Add the market-data repository interface
* [x] Add CSV market-data persistence
* [x] Add incremental synchronization
* [x] Add overlap reconciliation
* [x] Add duplicate-date replacement
* [x] Add historical-data retention

### Analysis and Strategy

* [x] Add moving-average calculations
* [x] Add price-position analysis
* [x] Add moving-average crossover detection
* [x] Add buffered strategy evaluation
* [x] Add strategy-state transition detection

### State Management

* [x] Add persistent strategy-state models
* [x] Add the strategy-state repository interface
* [x] Add JSON strategy-state persistence
* [x] Add state repository unit tests
* [ ] Connect state persistence to the application workflow

### Notifications and Automation

* [ ] Add Telegram notification delivery
* [ ] Notify only when the strategy state changes
* [ ] Add chart generation
* [ ] Add a scheduled GitHub Actions workflow
* [ ] Persist runtime state across GitHub Actions executions
* [ ] Add monthly full-data reconciliation

## Next Milestone

The next milestone is an application service that coordinates the complete strategy run:

```text
Synchronize market data
        ↓
Calculate the latest SMA
        ↓
Load the previous strategy state
        ↓
Evaluate the buffered strategy
        ↓
Persist the resulting state
        ↓
Return whether a notification is required
```

After that workflow is complete and tested, Telegram notifications can be added without coupling notification code directly to strategy logic.

## Disclaimer

This project is intended for educational and research purposes only. It does not provide financial advice, make investment recommendations, or automatically execute trades.
