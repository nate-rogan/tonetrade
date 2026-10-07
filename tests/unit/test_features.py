"""Unit tests for tonetrade.features: GPR timing and no look-ahead in features."""

import pandas as pd

import tonetrade as tt


def test_geo_risk_is_known_the_day_after() -> None:
    raw = tt.sources.fetch_gpr_data()
    geo = tt.features.geo_risk()
    day = raw.index[10]

    expected = raw.rolling(7).mean().loc[day]
    assert geo.loc[day + pd.Timedelta(days=1)].equals(expected)


def test_features_use_no_data_after_t(market: pd.DataFrame) -> None:
    # Features computed on data up to t must match the full-history features at t.
    cut = 500
    full = tt.features.build_features(market)
    truncated = tt.features.build_features(market.iloc[:cut])

    pd.testing.assert_frame_equal(truncated, full.iloc[:cut])
