"""Configuration for ToneTrade data prep."""

from datetime import date


START = "2023-01-01"
FETCH_START = "2021-10-01"  # warm-up for CPI 12-month change and 60-day windows
END = date.today().isoformat()

TARGET = "ita"  # defines the trading-day grid and the prediction target

TICKERS = {
    "ita": "ITA",  # iShares U.S. Aerospace & Defense ETF
    "sp500": "^GSPC",  # S&P 500 index
    "nasdaq": "^IXIC",  # NASDAQ Composite index
    "brent": "BZ=F",  # Brent crude front-month futures
}

FRED_SERIES = {
    "cpi": "CPIAUCSL",  # CPI, all urban consumers, all items (index level)
    "unemployment": "UNRATE",  # Unemployment rate (%)
    "yield_spread": "T10Y2Y",  # 10-year minus 2-year Treasury yield (pp)
}
