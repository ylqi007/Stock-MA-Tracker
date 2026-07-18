"""Allow the package to run with python -m stock_ma_tracker."""

from stock_ma_tracker.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
