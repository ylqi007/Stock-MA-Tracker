"""Command-line interface for Stock MA Tracker."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

from stock_ma_tracker import __version__
from stock_ma_tracker.config import (
    ConfigurationError,
    load_config,
)
from stock_ma_tracker.market_data import (
    CsvMarketDataRepository,
    MarketDataSyncService,
    YahooFinanceProvider,
)

DEFAULT_CONFIG_PATH = Path("config/strategy.yaml")
DEFAULT_INITIAL_HISTORY_DAYS = 730


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="stock-ma-tracker",
        description="Track stock market moving-average signals.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=(f"Path to the YAML configuration file (default: {DEFAULT_CONFIG_PATH})"),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "validate-config",
        help="Validate the application configuration.",
    )

    sync_parser = subparsers.add_parser(
        "sync-data",
        help="Synchronize historical market data.",
    )

    sync_parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        default=None,
        help="Synchronization end date in YYYY-MM-DD format.",
    )

    sync_parser.add_argument(
        "--initial-start-date",
        type=date.fromisoformat,
        default=None,
        help=(
            "Initial history start date in YYYY-MM-DD format. Used only when no stored data exists."
        ),
    )

    return parser


def handle_validate_config(config_path: Path) -> int:
    """Validate and report configuration status."""

    load_config(config_path)

    print(f"Configuration is valid: {config_path}")
    return 0


def handle_sync_data(
    *,
    config,
    end_date: date | None,
    initial_start_date: date | None,
) -> int:
    """Synchronize configured market data."""

    effective_end_date = end_date or date.today()

    effective_initial_start_date = initial_start_date or effective_end_date - timedelta(
        days=DEFAULT_INITIAL_HISTORY_DAYS
    )

    provider_name = config.market_data.provider.strip().lower()

    if provider_name != "yahoo":
        raise ValueError(f"Unsupported market data provider: {provider_name}")

    provider = YahooFinanceProvider(
        auto_adjust=config.market_data.auto_adjust,
    )

    repository = CsvMarketDataRepository(
        Path(config.storage.data_directory),
    )

    sync_service = MarketDataSyncService(
        provider=provider,
        repository=repository,
        overlap_calendar_days=(config.market_data.overlap_calendar_days),
        max_stored_rows=config.market_data.max_stored_rows,
    )

    result = sync_service.sync(
        symbol=config.market_data.signal_symbol,
        initial_start_date=effective_initial_start_date,
        end_date=effective_end_date,
    )

    print_sync_result(result)

    return 0


def print_sync_result(result) -> None:
    """Print a synchronization summary."""

    latest_date = (
        result.latest_trading_date.isoformat() if result.latest_trading_date is not None else "none"
    )

    print("Market data synchronization completed")
    print(f"Symbol:               {result.symbol}")
    print(f"Requested date range: {result.requested_start_date} to {result.requested_end_date}")
    print(f"Downloaded rows:      {result.downloaded_count}")
    print(f"Stored rows:          {result.stored_count}")
    print(f"Latest trading date:  {latest_date}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)

        command_handlers = {
            "validate-config": lambda: handle_validate_config(args.config),
            "sync-data": lambda: handle_sync_data(
                config=config,
                end_date=args.end_date,
                initial_start_date=args.initial_start_date,
            ),
        }

        return command_handlers[args.command]()

    except (ConfigurationError, OSError, ValueError) as exc:
        parser.error(str(exc))

    return 1
