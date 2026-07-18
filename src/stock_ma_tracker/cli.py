"""Command-line interface for Stock MA Tracker."""

from __future__ import annotations

import argparse

from stock_ma_tracker import __version__


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

    subparsers.add_parser(
        "test",
        help="Just a test parser without any meaning",
    )

    return parser


def main() -> int:
    """Run the command-line application."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        print("Stock MA Tracker is configured correctly.")
        return 0
    elif args.command == "test":
        print("Stock MA Tracker is configured correctly -- Just a test parser")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
