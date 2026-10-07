"""The project's named series.

Each macro function returns a Series indexed by the date its value became known, so every
series can be put on the daily grid the same way with ``utils.align_to_grid``. The
timing rule for each series lives here, next to the series.

"""

import pandas as pd

from tonetrade import constants
from tonetrade.sources import (
    fetch_fred,
    fetch_fred_first_release,
    fetch_gpr_data,
)


def cpi_yoy() -> pd.Series:
    """CPI 12-month % change, indexed by release date.

    Both ends of the change use first-release index levels.

    Returns:
        Percent change, indexed by the date the month's CPI was first released.
    """
    releases = fetch_fred_first_release(constants.FRED_SERIES["cpi"])
    level = releases["value"]
    change = (level / level.shift(12, freq="MS") - 1) * 100
    return change.reindex(releases.index).set_axis(releases["release_date"])


def unemployment() -> pd.Series:
    """Unemployment rate (%), indexed by release date.

    Returns:
        First-release rate, indexed by the date it was first released.
    """
    releases = fetch_fred_first_release(constants.FRED_SERIES["unemployment"])
    return releases["value"].set_axis(releases["release_date"])


def yield_spread() -> pd.Series:
    """10-year minus 2-year Treasury yield (pp), indexed by the next business day.

    FRED posts each day's value after the US close, so it isn't known until the next
    trading day.

    Returns:
        Spread, indexed by the business day after its observation date.
    """
    values = fetch_fred(
        constants.FRED_SERIES["yield_spread"], constants.FETCH_START_DATE
    )
    return values.set_axis(values.index + pd.offsets.BDay(1))


def geo_risk() -> pd.DataFrame:
    """GPR acts and threats, 7-day mean, indexed by the next business day."""
    gpr = fetch_gpr_data()[["gprd_act", "gprd_threat"]]
    smooth = gpr.rolling(7).mean()  # calendar days, window ends at t
    return smooth.set_axis(smooth.index + pd.offsets.BDay(1))


# Column name -> function, for every macro series. Each is aligned the same way.
MACRO = {
    "cpi_yoy": cpi_yoy,
    "unemployment": unemployment,
    "yield_spread": yield_spread,
}
