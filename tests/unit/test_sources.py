"""Unit tests for tonetrade.sources and the GPR timing in tonetrade.features.

These read the committed GPR snapshot; no network.
"""

import pandas as pd

import tonetrade as tt


def test_fetch_gpr_data() -> None:
    result = tt.sources.fetch_gpr_data()
    assert list(result.columns) == ["gprd_act", "gprd_threat"]
    assert result.index.name == "date"


def test_geo_risk_is_lagged_to_business_days() -> None:
    geo = tt.features.geo_risk()
    raw = tt.sources.fetch_gpr_data()
    assert (geo.index.dayofweek < 5).all()
    assert geo.index.min() >= raw.index.min() + pd.offsets.BDay(1)
