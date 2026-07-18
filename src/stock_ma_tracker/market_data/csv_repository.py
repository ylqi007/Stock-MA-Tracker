"""CSV implementation of the market data repository."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from stock_ma_tracker.market_data.models import PriceBar
from stock_ma_tracker.market_data.repository import MarketDataRepository


class CsvMarketDataRepository(MarketDataRepository):
    """Persist market data in one CSV file per symbol."""

    _FIELDNAMES = [
        "trading_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    def __init__(self, data_directory: Path) -> None:
        self._data_directory = data_directory

    def load(self, symbol: str) -> list[PriceBar]:
        """Load stored price bars ordered by trading date."""

        file_path = self._get_file_path(symbol)

        if not file_path.exists():
            return []

        bars: list[PriceBar] = []

        with file_path.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                bars.append(
                    PriceBar(
                        trading_date=date.fromisoformat(row["trading_date"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=int(row["volume"]),
                    )
                )

        return sorted(
            bars,
            key=lambda bar: bar.trading_date,
        )

    def save(self, symbol: str, bars: list[PriceBar]) -> None:
        """Write price bars to a symbol CSV file."""

        self._data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = self._get_file_path(symbol)

        sorted_bars = sorted(
            bars,
            key=lambda bar: bar.trading_date,
        )

        with file_path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._FIELDNAMES,
            )

            writer.writeheader()

            for bar in sorted_bars:
                writer.writerow(
                    {
                        "trading_date": bar.trading_date.isoformat(),
                        "open": bar.open,
                        "high": bar.high,
                        "low": bar.low,
                        "close": bar.close,
                        "volume": bar.volume,
                    }
                )

    def _get_file_path(self, symbol: str) -> Path:
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("symbol must not be empty")

        return self._data_directory / f"{normalized_symbol}.csv"
