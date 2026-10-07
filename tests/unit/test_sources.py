"""
Integration tests for the ToneTrade sources module.
These call the live external APIs, so they need network access (and keys for FRED).
Run them with: pixi run test-integration
"""

import pandas as pd

import tonetrade as tt


# Note these are not hitting apis so are unit tests, not integration tests
def test_fetch_gpr_data() -> None:
    result = tt.sources.fetch_gpr_data()
    print(result.iloc[:5])
    assert isinstance(result, pd.DataFrame)
    assert "gprd" in result.columns
    assert "gprd_act" in result.columns
    assert "gprd_threat" in result.columns
    assert "date" in result.index.names


def test_geo_risk_is_lagged_to_business_days() -> None:
    geo = tt.series.geo_risk()
    raw = tt.sources.fetch_gpr_data()
    assert (geo.index.dayofweek < 5).all()
    assert geo.index.min() >= raw.index.min() + pd.offsets.BDay(1)
