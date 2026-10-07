"""Configuration: dates, tickers, data files, and model and trading settings."""

from pathlib import Path


FETCH_START_DATE = "2007-08-01"  # Brent's first full month; warm-up for 60-day windows
START_DATE = "2009-01-01"  # first modelling row
END_DATE = "2026-10-07"  # exclusive: the price snapshot runs to 2026-10-06

TARGET = "ita"  # defines the trading-day grid and the prediction target

TICKERS = {
    "ita": "ITA",  # iShares U.S. Aerospace & Defense ETF
    "brent": "BZ=F",  # Brent crude front-month futures
}

DATA_DIR = Path(__file__).parents[2] / "data"
PRICES_SNAPSHOT = DATA_DIR / "prices.csv"  # written by `pixi run snapshot`
GPR_DATA_SOURCE = DATA_DIR / "data_gpr_daily_recent.csv"

GPR_SERIES = {
    "date": "date",  # Observation date
    "gprd_act": "GPRD_ACT",  # Actual Geo Political Risk acts, war, terror, etc.
    "gprd_threat": "GPRD_THREAT",  # Threats, potential conflicts, geopolitical tensions
}

# Backtesting and trading configuration
FIRST_TEST_YEAR = 2015
HORIZON = 5  # forward horizon, trading days
BUY, SELL, COST = 0.55, 0.45, 0.0005
SHORT = 0.0  # 0 = flat on sell, -1 = short
