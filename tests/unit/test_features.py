"""Unit tests for tonetrade.features (read the committed GPR snapshot; no network)."""

import pandas as pd

import tonetrade as tt


def test_geo_risk_is_known_the_day_after() -> None:
    raw = tt.sources.fetch_gpr_data()
    geo = tt.features.geo_risk()
    day = raw.index[10]

    expected = raw.rolling(7).mean().loc[day]
    assert geo.loc[day + pd.Timedelta(days=1)].equals(expected)
