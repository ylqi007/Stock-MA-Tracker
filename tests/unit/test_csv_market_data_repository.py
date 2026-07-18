from datetime import date

from stock_ma_tracker.market_data import (
    CsvMarketDataRepository,
    PriceBar,
)


def build_price_bars() -> list[PriceBar]:
    return [
        PriceBar(
            trading_date=date(2026, 7, 2),
            open=554.1,
            high=557.2,
            low=552.0,
            close=556.4,
            volume=38_900_000,
        ),
        PriceBar(
            trading_date=date(2026, 7, 1),
            open=550.2,
            high=554.8,
            low=548.9,
            close=553.7,
            volume=42_100_000,
        ),
    ]


def test_load_returns_empty_list_when_file_does_not_exist(tmp_path):
    repository = CsvMarketDataRepository(tmp_path)

    bars = repository.load("QQQ")

    assert bars == []


def test_save_and_load_price_bars(tmp_path):
    repository = CsvMarketDataRepository(tmp_path)

    repository.save(
        symbol="QQQ",
        bars=build_price_bars(),
    )

    loaded_bars = repository.load("QQQ")

    assert len(loaded_bars) == 2
    assert loaded_bars[0].trading_date == date(2026, 7, 1)
    assert loaded_bars[1].trading_date == date(2026, 7, 2)
    assert loaded_bars[0].close == 553.7
    assert loaded_bars[1].volume == 38_900_000


def test_save_normalizes_symbol_name(tmp_path):
    repository = CsvMarketDataRepository(tmp_path)

    repository.save(
        symbol=" qqq ",
        bars=build_price_bars(),
    )

    assert (tmp_path / "QQQ.csv").exists()


def test_save_creates_data_directory(tmp_path):
    data_directory = tmp_path / "nested" / "data"
    repository = CsvMarketDataRepository(data_directory)

    repository.save(
        symbol="QQQ",
        bars=build_price_bars(),
    )

    assert (data_directory / "QQQ.csv").exists()
