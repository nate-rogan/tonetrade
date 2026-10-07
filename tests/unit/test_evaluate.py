"""Unit tests for tonetrade.evaluate: no train/test leakage, correct backtest timing."""

from typing import ClassVar

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, ClassifierMixin

import tonetrade as tt


class RecordingModel(ClassifierMixin, BaseEstimator):
    """Records the training rows of every fit and predicts 0.5."""

    fitted_on: ClassVar[list[pd.DatetimeIndex]] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RecordingModel":
        RecordingModel.fitted_on.append(X.index)
        self.classes_ = np.array([0.0, 1.0])
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return np.full((len(X), 2), 0.5)


def test_walk_forward_trains_only_on_earlier_years_minus_purge(
    market: pd.DataFrame,
) -> None:
    data = tt.features.build_features(market).assign(
        label=tt.features.build_target(market["ita"])
    )
    RecordingModel.fitted_on.clear()
    tt.evaluate.walk_forward(data.dropna(), RecordingModel(), ["ita_ret_5"])

    years = range(tt.constants.FIRST_TEST_YEAR, data.index.year.max() + 1)
    for year, train_index in zip(years, RecordingModel.fitted_on, strict=True):
        before = data.dropna().index[data.dropna().index.year < year]
        # The last HORIZON rows before the test year are purged: their labels reach into it.
        assert train_index.max() <= before[-tt.constants.HORIZON - 1]


def test_position_earns_the_next_days_return_net_of_entry_cost() -> None:
    days = pd.bdate_range("2024-01-01", periods=4)
    positions = pd.Series([1.0, 1.0, 1.0, 1.0], index=days)
    returns = pd.Series([0.01, 0.02, -0.03, 0.04], index=days)

    res = tt.evaluate.backtest(positions, returns, cost=0.001)

    # Decided at day 0's close, so day 0's own return is not earned.
    strategy = res["strategy_returns"].tolist()
    assert strategy == pytest.approx([0.0, 0.02 - 0.001, -0.03, 0.04])
