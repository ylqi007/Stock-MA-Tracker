# Stock MA Tracker

A maintainable stock market trend tracker built with Python, Yahoo Finance, GitHub Actions, and Telegram.

The project uses **QQQ** as the market signal source and is designed to generate strategy notifications for **TQQQ** based on a long-term moving-average strategy.

> The current version only retrieves and stores market data. Strategy calculation and Telegram notifications will be added in later stages.

## Strategy Overview

The planned strategy uses the 200-day simple moving average of QQQ:

* Upper threshold: `SMA200 × 1.04`
* Lower threshold: `SMA200 × 0.97`
* Price at or above the upper threshold: `RISK_ON`
* Price at or below the lower threshold: `RISK_OFF`
* Price between the thresholds: retain the previous state

The system will only generate notifications. It will not automatically place trades.

## Current Features

* YAML-based application configuration
* Typed and immutable configuration models
* Configuration loading and validation
* Yahoo Finance historical market data provider
* Daily OHLCV market data retrieval
* Automatic adjusted-price support
* CSV-based local market data storage
* One CSV file per symbol
* Symbol normalization
* Chronological sorting of stored price bars
* Unit tests with pytest
* Code quality checks with Ruff
* Incremental market data synchronization
* Seven-day overlap reconciliation
* Duplicate-date replacement
* Configurable historical-data retention
* CLI-based market data synchronization

## Planned Features

* Incremental market data synchronization
* Seven-day overlap when updating historical data
* Duplicate-date reconciliation
* Historical-data retention limits
* SMA200 calculation
* Strategy state management
* Signal-change detection
* Telegram notifications
* Strategy charts
* Scheduled GitHub Actions workflow
* Monthly full-data reconciliation

## Project Structure

```text
Stock-MA-Tracker/
├── config/
│   └── strategy.yaml
├── src/
│   └── stock_ma_tracker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   └── validator.py
│       └── market_data/
│           ├── __init__.py
│           ├── csv_repository.py
│           ├── models.py
│           ├── provider.py
│           ├── repository.py
│           ├── sync.py
│           └── yahoo.py
├── tests/
│   └── unit/
├── data/
├── state/
├── history/
├── charts/
├── pyproject.toml
└── README.md
```

## Architecture

The project separates external data retrieval from local persistence and strategy logic.

```text
Yahoo Finance
      ↓
YahooFinanceProvider
      ↓
list[PriceBar]
      ↓
CsvMarketDataRepository
      ↓
CSV files
```

The main abstractions are:

* `MarketDataProvider`: retrieves market data from an external source
* `YahooFinanceProvider`: retrieves historical data through `yfinance`
* `MarketDataRepository`: defines local market-data persistence behavior
* `CsvMarketDataRepository`: stores and loads price bars using CSV files
* `PriceBar`: represents one daily OHLCV market-data record

This design allows Yahoo Finance or CSV storage to be replaced without changing the future strategy implementation.

## Requirements

* Python 3.12 or later
* Git
* Internet access for Yahoo Finance data retrieval

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-github-username>/stock-ma-tracker.git
cd stock-ma-tracker
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Install development dependencies if they are defined separately:

```bash
python -m pip install -e ".[dev]"
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

## Retrieving Yahoo Finance Data

`YahooFinanceProvider` retrieves daily historical prices through the `yfinance` package.

Example:

```python
from datetime import date

from stock_ma_tracker.market_data import YahooFinanceProvider

provider = YahooFinanceProvider(auto_adjust=True)

bars = provider.get_daily_prices(
    symbol="QQQ",
    start_date=date(2026, 7, 1),
    end_date=date(2026, 7, 10),
)

for bar in bars:
    print(bar.trading_date, bar.close)
```

The provider returns a list of `PriceBar` objects instead of exposing a pandas DataFrame to the rest of the application.

## Saving Market Data to CSV

Use `CsvMarketDataRepository` to store downloaded price bars:

```python
from datetime import date
from pathlib import Path

from stock_ma_tracker.market_data import (
    CsvMarketDataRepository,
    YahooFinanceProvider,
)

provider = YahooFinanceProvider(auto_adjust=True)
repository = CsvMarketDataRepository(Path("data"))

bars = provider.get_daily_prices(
    symbol="QQQ",
    start_date=date(2026, 7, 1),
    end_date=date(2026, 7, 10),
)

repository.save(
    symbol="QQQ",
    bars=bars,
)
```

This creates:

```text
data/QQQ.csv
```

Example CSV structure:

```csv
trading_date,open,high,low,close,volume
2026-07-01,550.2,554.8,548.9,553.7,42100000
2026-07-02,554.1,557.2,552.0,556.4,38900000
```

Load the stored data:

```python
stored_bars = repository.load("QQQ")

for bar in stored_bars:
    print(bar)
```

Symbols are normalized before file names are generated. For example:

```python
repository.save(" qqq ", bars)
```

still writes to:

```text
data/QQQ.csv
```

```bash
stock-ma-tracker sync-data
```

## Development

Format the project:

```bash
ruff format .
```

Run lint checks:

```bash
ruff check .
```

Run all tests:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/unit/test_csv_market_data_repository.py -v
```

## Development Progress

* [x] Initialize project structure
* [x] Add typed configuration models
* [x] Add YAML configuration loading
* [x] Add configuration validation
* [x] Refactor configuration module into a package
* [x] Add market-data domain models
* [x] Add the market-data provider interface
* [x] Add the Yahoo Finance provider
* [x] Add the market-data repository interface
* [x] Add CSV market-data persistence
* [x] Add incremental market-data synchronization
* [ ] Add duplicate-date reconciliation
* [ ] Add historical-data retention
* [ ] Add SMA calculations
* [ ] Add strategy state evaluation
* [ ] Add Telegram notifications
* [ ] Add chart generation
* [ ] Add scheduled GitHub Actions workflows

## Disclaimer

This project is intended for educational and research purposes only. It does not provide financial advice and does not automatically execute trades.
