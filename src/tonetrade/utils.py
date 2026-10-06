"""Utility functions for ToneTrade."""

import pandas as pd


def align_to_grid(values: pd.Series, grid: pd.DatetimeIndex) -> pd.Series:
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
