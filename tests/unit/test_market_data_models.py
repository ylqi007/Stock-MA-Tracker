from datetime import date

from stock_ma_tracker.market_data import PriceBar


def test_price_bar_contains_expected_values():
    bar = PriceBar(
        trading_date=date(2026, 7, 17),
        open=550.0,
        high=555.0,
        low=548.0,
        close=553.0,
        volume=42_000_000,
    )

    assert bar.trading_date == date(2026, 7, 17)
    assert bar.close == 553.0
    assert bar.volume == 42_000_000
