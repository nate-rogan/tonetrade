"""Unit tests for tonetrade.series."""

import pandas as pd

from tonetrade import series


def test_yield_spread_is_known_the_next_business_day(monkeypatch) -> None:
    friday = pd.Series([0.5], index=pd.DatetimeIndex(["2024-01-12"]))
    monkeypatch.setattr(series, "fetch_fred", lambda series_id, start: friday)

    spread = series.yield_spread()

    assert spread.index[0] == pd.Timestamp("2024-01-15")  # Monday
