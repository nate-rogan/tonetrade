"""ToneTrade data prep script as a percent-format script.

Pulls prices, macro series and news headlines, scores headline tone with FinBERT, and
writes data/features.csv for scripts/model.py.

Run end to end with: pixi run python scripts/prep.py

"""

# %%
# Imports and config: date range, tickers, paths.
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import tonetrade
from tonetrade import constants, series
from tonetrade.utils import align_to_grid


ROOT = Path(tonetrade.__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
load_dotenv()


def build_market(force: bool = False) -> pd.DataFrame:
    """Pull prices and macro series and align them on a daily grid.

    The grid is the TARGET ticker's trading days from FETCH_START. Monthly macro values are placed by
    their first-release date, and the yield spread is lagged a day because FRED posts it
    after the close. Warm-up rows before START are kept; trim them after features are
    built.

    Args:
        force: Refetch even if the saved file exists.

    Returns:
        One row per trading day: a close per ticker, cpi_yoy (%), unemployment (%) and
        yield_spread (pp).
    """
    path = RAW_DIR / "market.parquet"
    if path.exists() and not force:
        return pd.read_parquet(path)

    closes = series.prices()
    grid = closes.index[closes[constants.TARGET].notna()]
    # Fill short gaps, e.g. Brent on UK holidays.
    market = closes.loc[grid].ffill(limit=3)

    for name, fetch in series.MACRO.items():
        market[name] = align_to_grid(fetch(), grid)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    market.to_parquet(path)
    return market


def build_headlines() -> None:
    """Pull geopolitical and AI headlines from GDELT."""


def build_features() -> None:
    """Score headline tone, join with market data and write data/features.csv."""


# Run all stages. Don't run this cell interactively: it runs the full pipeline.
def main() -> None:
    """Run every prep stage in order."""
    build_market()
    build_headlines()
    build_features()


if __name__ == "__main__":
    main()
