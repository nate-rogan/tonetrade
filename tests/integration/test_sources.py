"""
Integration tests for the ToneTrade sources module.
These call the live external APIs, so they need network access (and keys for FRED).
Run them with: pixi run test-integration
"""

import pandas as pd
import pytest

import tonetrade as tt


@pytest.mark.integration
def test_fetch_prices() -> None:
    result = tt.sources.fetch_prices(
        tickers={"ita": "ITA"}, start="2023-01-01", end="2023-01-10"
    )
    assert isinstance(result, pd.DataFrame)
    assert "ita" in result.columns


# @pytest.mark.integration
def test_fetch_gpr_data() -> None:
    result = tt.sources.fetch_gpr_data()
    print(result.iloc[:5])
    assert isinstance(result, pd.DataFrame)
    assert "gprd" in result.columns
    assert "gprd_act" in result.columns
    assert "gprd_threat" in result.columns
    assert "date" in result.index.names
