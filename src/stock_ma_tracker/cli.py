"""Command-line interface for Stock MA Tracker."""

from __future__ import annotations

import argparse
from pathlib import Path

from stock_ma_tracker import __version__
from stock_ma_tracker.config import ConfigurationError, load_config


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line parser."""

    parser = argparse.ArgumentParser(
        prog="stock-ma-tracker",
        description="Stock moving-average strategy tracker",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "check",
        help="Check the project configuration and environment",
    )

    validate_parser = subparsers.add_parser(
        "validate-config", help="Validate the application configuration file."
    )

    validate_parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/strategy.yaml"),
        help="Path to the YAML configuration file.",
    )

    return parser


def main() -> int:
    """Run the command-line application."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        print("Stock MA Tracker is configured correctly.")
        return 0

    if args.command == "validate-config":
        try:
            config = load_config(args.config)
        except ConfigurationError as error:
            print(f"Configuration error: {error}")
            return 1

        print(
            "Configuration is valid: "
            f"{config.market_data.signal_symbol} "
            f"SMA{config.strategy.sma_window}"
        )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
