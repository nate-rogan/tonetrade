"""Unit tests for tonetrade.utils."""

import pandas as pd

from tonetrade.utils import align_to_grid


def test_value_is_only_used_from_the_date_it_became_known() -> None:
    values = pd.Series([1.0], index=pd.DatetimeIndex(["2024-01-10"]))
    grid = pd.DatetimeIndex(["2024-01-09", "2024-01-10", "2024-01-11"])

    aligned = align_to_grid(values, grid)

    assert pd.isna(aligned["2024-01-09"])
    assert aligned["2024-01-10":].tolist() == [1.0, 1.0]
