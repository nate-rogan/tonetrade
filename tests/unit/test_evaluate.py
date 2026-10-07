"""Unit tests for tonetrade.evaluate: walk-forward purge, signal rule and backtest timing."""

from typing import ClassVar

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, ClassifierMixin

import tonetrade as tt


H = tt.constants.HORIZON


class RecordingModel(ClassifierMixin, BaseEstimator):
    """Records the training rows of every fit and predicts 0.5."""

    fitted_on: ClassVar[list[pd.DatetimeIndex]] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RecordingModel":
        RecordingModel.fitted_on.append(X.index)
        self.classes_ = np.array([0.0, 1.0])
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return np.full((len(X), 2), 0.5)


@pytest.fixture
def data(market: pd.DataFrame) -> pd.DataFrame:
    features = tt.features.build_features(market)
    labelled = features.assign(label=tt.features.build_target(market["ita"]))
    return labelled.dropna(subset=list(features))


def test_walk_forward_trains_only_on_earlier_years_minus_purge(
    data: pd.DataFrame,
) -> None:
    RecordingModel.fitted_on.clear()
    tt.evaluate.walk_forward(data, RecordingModel(), ["ita_ret_5"])

    years = range(tt.constants.FIRST_TEST_YEAR, data.index.year.max() + 1)
    assert len(RecordingModel.fitted_on) == len(years)
    for year, train_index in zip(years, RecordingModel.fitted_on, strict=True):
        before = data.index[data.index.year < year]
        # The last H rows before the test year are purged: their labels reach into it.
        assert train_index.max() <= before[-H - 1]


def test_walk_forward_predicts_every_test_day(data: pd.DataFrame) -> None:
    proba = tt.evaluate.walk_forward(data, RecordingModel(), ["ita_ret_5"])

    test_days = data.index[data.index.year >= tt.constants.FIRST_TEST_YEAR]
    assert proba.index.equals(test_days)


def test_positions_hold_between_thresholds() -> None:
    days = pd.bdate_range("2024-01-01", periods=6)
    proba = pd.Series([0.5, 0.6, 0.5, 0.4, 0.5, 0.6], index=days)

    positions = tt.evaluate.to_positions(proba)

    short = tt.constants.SHORT
    assert positions.tolist() == [0.0, 1.0, 1.0, short, short, 1.0]


def test_position_earns_the_next_days_return_net_of_entry_cost() -> None:
    days = pd.bdate_range("2024-01-01", periods=4)
    positions = pd.Series([1.0, 1.0, 1.0, 1.0], index=days)
    returns = pd.Series([0.01, 0.02, -0.03, 0.04], index=days)

    res = tt.evaluate.backtest(positions, returns, cost=0.001)

    # Decided at day 0's close, so day 0's own return is not earned.
    strategy = res["strategy_returns"].tolist()
    assert strategy == pytest.approx([0.0, 0.02 - 0.001, -0.03, 0.04])


def test_lag_delays_the_position_by_a_day() -> None:
    days = pd.bdate_range("2024-01-01", periods=4)
    positions = pd.Series([1.0, 1.0, 1.0, 1.0], index=days)
    returns = pd.Series([0.01, 0.02, -0.03, 0.04], index=days)

    res = tt.evaluate.backtest(positions, returns, cost=0.0, lag=1)

    assert res["strategy_returns"].tolist() == pytest.approx([0.0, 0.0, -0.03, 0.04])


def test_trade_count_includes_the_first_entry() -> None:
    days = pd.bdate_range("2024-01-01", periods=4)
    proba = pd.Series([0.6, 0.6, 0.4, 0.4], index=days)
    returns = pd.Series([0.0, 0.01, 0.01, 0.01], index=days)
    res = tt.evaluate.backtest(tt.evaluate.to_positions(proba), returns)

    summary = tt.evaluate.summarise(res, proba, pd.Series(1.0, index=days))

    assert summary["trades"] == 2  # enter long, then exit to flat
