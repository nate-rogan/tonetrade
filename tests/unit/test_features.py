"""Unit tests for tonetrade.features: GPR timing and no look-ahead in features or labels."""

import pandas as pd

import tonetrade as tt


H = tt.constants.HORIZON


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


def test_label_looks_exactly_horizon_days_ahead(market: pd.DataFrame) -> None:
    # The label at t may use prices up to t + H, and nothing later.
    full = tt.features.build_target(market["ita"])
    for t in (100, 400, 900):
        truncated = tt.features.build_target(market["ita"].iloc[: t + H + 1])
        assert truncated.iloc[t] == full.iloc[t] or (
            pd.isna(truncated.iloc[t]) and pd.isna(full.iloc[t])
        )
        assert pd.isna(tt.features.build_target(market["ita"].iloc[: t + H]).iloc[t])


def test_label_is_unknown_for_the_last_horizon_days(market: pd.DataFrame) -> None:
    target = tt.features.build_target(market["ita"])

    assert target.iloc[-H:].isna().all()
    assert target.iloc[:-H].notna().any()
