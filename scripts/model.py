"""ToneTrade model script as a percent-format testing script.

This script is intended for testing the model functionality within the ToneTrade project using percent-format cells.
For simplicity, this script focuses on building and visualizing market data.

lru_cache is used to cache the results of  data access functions like build_market_data.
"""

# %% Import necessary modules and functions for testing the model.

from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv

import tonetrade as tt


load_dotenv()


# %% Build Market Data
@lru_cache
def build_market_data() -> pd.DataFrame:
    """Returns market data as a pandas DataFrame."""
    closes = tt.series.prices()
    grid = closes.index[closes[tt.constants.TARGET].notna()]

    # Fill short gaps, e.g. Brent on UK holidays.
    market = closes.loc[grid].ffill(limit=3)

    for name, fetch in tt.series.MACRO.items():
        market[name] = tt.utils.align_to_grid(fetch(), grid)
    return market


# %% Build Headlines
def build_headlines() -> pd.DataFrame:
    """Returns headlines as a pandas DataFrame."""
    # Implement the logic to build headlines here.
    pass


# %% Build Features
def build_features() -> pd.DataFrame:
    """Returns features as a pandas DataFrame."""
    # Implement the logic to build features here.
    pass


# %% Build Model
market = build_market_data()
market.plot(subplots=True, figsize=(12, 12))

# %%
