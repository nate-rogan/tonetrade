"""Unit tests for tonetrade.sources (read the committed GPR snapshot; no network)."""

import pandas as pd

import tonetrade as tt


def test_fetch_gpr_data() -> None:
    result = tt.sources.fetch_gpr_data()
    assert list(result.columns) == ["gprd_act", "gprd_threat"]
    assert result.index.name == "date"


def test_price_snapshot_covers_the_pinned_range() -> None:
    prices = tt.sources.load_prices()
    assert list(prices.columns) == list(tt.constants.TICKERS)
    assert prices.index[0] >= pd.Timestamp(tt.constants.FETCH_START_DATE)
    assert prices.index[-1] < pd.Timestamp(tt.constants.END_DATE)
    assert prices.index.is_monotonic_increasing and prices.index.is_unique
