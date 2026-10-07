"""Data sources: Yahoo Finance prices, and the committed price and GPR snapshots."""

import pandas as pd
import yfinance as yf

import tonetrade.constants as constants


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

    return closes[list(tickers)].rename_axis(index="date", columns=None)


def prices(refresh: bool = False) -> pd.DataFrame:
    """Daily closes for ``TICKERS``, read from the committed snapshot.

    Yahoo's adjusted closes differ slightly from one request to the next, so the model
    reads a committed snapshot instead of fetching live.

    Args:
        refresh: Refetch from Yahoo up to ``END_DATE`` and overwrite the snapshot first
            (``pixi run snapshot``).

    Returns:
        Adjusted daily closes indexed by date, one column per name in ``TICKERS``.
    """
    if refresh:
        start, end = constants.FETCH_START_DATE, constants.END_DATE
        fetch_prices(constants.TICKERS, start, end).to_csv(constants.PRICES_SNAPSHOT)
    return pd.read_csv(constants.PRICES_SNAPSHOT, index_col="date", parse_dates=True)


def fetch_gpr_data() -> pd.DataFrame:
    """Load the daily GPR snapshot committed in ``data/``.

    Returns:
        GPR acts and threats, indexed by observation date.
    """
    gpr = pd.read_csv(
        constants.GPR_DATA_SOURCE,
        usecols=list(constants.GPR_SERIES.values()),
        index_col="date",
        parse_dates=["date"],
        thousands=",",
    )
    return gpr.rename(columns={v: k for k, v in constants.GPR_SERIES.items()})
