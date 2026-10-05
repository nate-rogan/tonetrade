"""Clients for external data sources: Yahoo Finance and FRED/ALFRED.

These functions fetch any ticker or series by ID. The project's named series, with their
transforms and timing, are in ``tonetrade.series``.

"""

import pandas as pd
import yfinance as yf
from fredapi import Fred


def fetch_prices(tickers: dict[str, str], start: str, end: str) -> pd.DataFrame:
    """Fetch adjusted daily closes from Yahoo Finance.

    Args:
        tickers: Column name to Yahoo ticker, e.g. ``{"ita": "ITA"}``.
        start: First date to fetch, ISO format.
        end: Day after the last date to fetch, ISO format (Yahoo treats it as exclusive).

    Returns:
        Closes indexed by date, one column per name in ``tickers``.

    Raises:
        ValueError: If any ticker returned no data.
    """
    # threads=False: the threaded download can fail on Windows with "database is locked".
    raw = yf.download(
        list(tickers.values()),
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    names = {ticker: name for name, ticker in tickers.items()}
    closes = raw["Close"].rename(columns=names)
    missing = [n for n in tickers if n not in closes or closes[n].isna().all()]
    if missing:
        raise ValueError(f"No price data for: {missing}")

    closes = closes[list(tickers)]
    closes.index.name = "date"
    closes.columns.name = None
    return closes


def fetch_fred(series_id: str, start: str) -> pd.Series:
    """Fetch the latest values of a FRED series.

    Use this for series that aren't revised, such as daily market rates. The API key is
    read from the ``FRED_API_KEY`` environment variable.

    Args:
        series_id: FRED series ID, e.g. ``"T10Y2Y"``.
        start: First observation date, ISO format.

    Returns:
        Values indexed by observation date, with missing days dropped.
    """
    values = Fred().get_series(series_id, observation_start=start)
    return values.dropna().rename(series_id)


def fetch_fred_first_release(series_id: str) -> pd.DataFrame:
    """Fetch each observation's first-release value and release date from ALFRED.

    Using the first release, not today's revised value, means a value is only ever paired
    with the date it was actually published. The API key is read from the
    ``FRED_API_KEY`` environment variable.

    Args:
        series_id: FRED series ID, e.g. ``"CPIAUCSL"``.

    Returns:
        Indexed by observation date, with columns ``release_date`` and ``value``.
        Observations FRED reports as missing (``"."``) have a NaN value.
    """
    releases = Fred().get_series_all_releases(series_id)
    releases = releases.assign(
        date=pd.to_datetime(releases["date"]),
        release_date=pd.to_datetime(releases["realtime_start"]),
        value=pd.to_numeric(releases["value"], errors="coerce"),
    )
    first = releases.sort_values("release_date").drop_duplicates("date", keep="first")
    return first.set_index("date").sort_index()[["release_date", "value"]]


def fetch_text_test():
    """Fetch a test text string.

    Returns:
        str: A test text string.
    """
    return "Test text data"
