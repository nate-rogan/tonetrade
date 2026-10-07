"""
Integration tests for the ToneTrade sources module.
These call Yahoo Finance, so they need network access.
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
