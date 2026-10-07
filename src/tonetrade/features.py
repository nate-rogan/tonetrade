"""Market panel, feature matrix and labels: raw data in, model inputs out."""

from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv

from tonetrade import constants, series, sources


load_dotenv()


def _align_to_grid(values: pd.Series, grid: pd.DatetimeIndex) -> pd.Series:
    """Carry values forward onto a daily grid from the date each became known.

    Args:
        values: Values indexed by the date they became known (e.g. release date). If two
            values share a date, the later one in ``values`` wins.
        grid: Target dates, e.g. trading days.

    Returns:
        ``values`` reindexed to ``grid``. Each grid date gets the latest value known on or
        before it, and dates before the first value are NaN.
    """
    known = values.sort_index(kind="stable")
    known = known[~known.index.duplicated(keep="last")]
    return known.reindex(grid, method="ffill")


@lru_cache
def build_market_data() -> pd.DataFrame:
    """Build the daily market panel on the target's trading-day grid.

    Prices are forward-filled for up to 3 days. Macro and geopolitical-risk
    series are aligned to the grid by release date.

    Returns:
        DataFrame indexed by trading day with one column per price, macro and
        GPR series. Cached, so treat it as read-only.
    """
    closes = sources.fetch_prices(
        constants.TICKERS, constants.FETCH_START_DATE, constants.END_DATE
    )
    grid = closes.index[closes[constants.TARGET].notna()]

    # Fill short gaps, e.g. Brent on UK holidays.
    market = closes.loc[grid].ffill(limit=3)

    for name, fetch in series.MACRO.items():
        market[name] = _align_to_grid(fetch(), grid)

    geo = series.geo_risk()
    for name in geo:
        market[name] = _align_to_grid(geo[name], grid)

    return market


def build_features(market: pd.DataFrame) -> pd.DataFrame:
    """Build the feature matrix. Every window ends at t, so there's no look-ahead.

    Args:
        market: Output of ``build_market_data``. Needs ``ita``, ``brent`` and the
            macro/GPR columns.

    Returns:
        DataFrame with macro/GPR levels, 5/20/60-day ITA and Brent returns,
        20-day ITA volatility, and ITA's distance from its 50-day mean.
    """
    ita_close, brent_close = market["ita"], market["brent"]
    features = market[
        ["cpi_yoy", "unemployment", "yield_spread", "gprd_act", "gprd_threat"]
    ].copy()
    for window in (5, 20, 60):
        features[f"ita_ret_{window}"] = ita_close.pct_change(window)
        features[f"brent_ret_{window}"] = brent_close.pct_change(window)
    features["ita_vol_20"] = ita_close.pct_change().rolling(20).std()
    features["ita_ma_dist"] = ita_close / ita_close.rolling(50).mean() - 1
    return features


def build_target(close: pd.Series) -> pd.Series:
    """Label each day by its forward return relative to recent volatility.

    Args:
        close: Daily close prices.

    Returns:
        Series of 1.0 (buy) when the ``HORIZON``-day forward return exceeds half
        a typical move over that horizon, 0.0 (sell) when it falls below minus
        that threshold, and NaN when it's in between or the future isn't
        known yet (the last ``HORIZON`` days).
    """
    fwd_return = close.shift(-constants.HORIZON) / close - 1
    threshold = 0.5 * close.pct_change().rolling(20).std() * constants.HORIZON**0.5
    is_up, is_down = fwd_return > threshold, fwd_return < -threshold
    target = is_up.astype(float).where(is_up | is_down)
    return target
