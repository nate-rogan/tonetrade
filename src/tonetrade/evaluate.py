"""Walk-forward predictions, signal rule, backtest and metrics: model in, results out."""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import roc_auc_score

from tonetrade import constants


def walk_forward(data: pd.DataFrame, model, cols: list[str]) -> pd.Series:
    """Predict out of sample with an expanding window, one fit per test year.

    Args:
        data: Features plus a ``label`` column (NaN = flat), indexed by day.
        model: Unfitted sklearn-style classifier; cloned for every fold.
        cols: Feature columns to train on.

    Returns:
        P(up move) for every day from ``FIRST_TEST_YEAR``. Each fold trains on
        labelled rows before the test year, minus the last ``HORIZON`` rows,
        whose labels reach into the test year.
    """
    preds = []
    for year in range(constants.FIRST_TEST_YEAR, data.index.year.max() + 1):
        train = data[data.index.year < year].iloc[: -constants.HORIZON]
        train = train.dropna(subset=["label"])
        test = data[data.index.year == year]
        fit = clone(model).fit(train[cols], train["label"])
        preds.append(pd.Series(fit.predict_proba(test[cols])[:, 1], index=test.index))
    return pd.concat(preds)


def to_positions(proba: pd.Series) -> pd.Series:
    """Convert buy probabilities into positions.

    Args:
        proba: Predicted probability of a buy, indexed by day.

    Returns:
        Series that is 1.0 above ``BUY`` and ``SHORT`` below ``SELL``. In
        between, it keeps the previous position. It is 0.0 until the first
        signal.
    """
    position = pd.Series(np.nan, index=proba.index)
    position[proba > constants.BUY] = 1.0
    position[proba < constants.SELL] = constants.SHORT
    return position.ffill().fillna(0.0)


def backtest(
    positions: pd.Series,
    daily_returns: pd.Series,
    cost: float = constants.COST,
    lag: int = 0,
) -> pd.DataFrame:
    """Backtest positions with execution lag and transaction costs.

    Args:
        positions: Target position decided at each close (e.g. from
            ``to_positions``).
        daily_returns: Return from t-1 to t, indexed by t.
        cost: Cost per unit of position change, e.g. 0.0005 for 5 bp.
        lag: Extra days of execution delay on top of the one-day hold.

    Returns:
        DataFrame with the ``position`` held each day, ``strategy_returns`` net
        of costs (including the first entry), and ``buy_hold`` returns.
    """
    lagged = positions.shift(lag).fillna(0)  # apply execution lag
    held = lagged.shift(1, fill_value=0.0)  # decided at t, earns t -> t+1
    raw_returns = held.mul(daily_returns)
    trades = held.diff().abs().fillna(held.abs())  # includes the first entry
    costs = trades.mul(cost)
    strategy_returns = raw_returns - costs
    return pd.DataFrame({
        "position": held,
        "strategy_returns": strategy_returns,
        "buy_hold": daily_returns,
    }).dropna()


def summarise(res: pd.DataFrame, proba: pd.Series, labels: pd.Series) -> dict:
    """Summarise one backtest as a row of metrics.

    Args:
        res: Output of ``backtest``.
        proba: The probabilities the positions came from.
        labels: Actual labels (1 = buy, 0 = sell, NaN = flat), indexed by day.

    Returns:
        Dict of ROC AUC and buy precision (on labelled days), hit rate, trade count,
        exposure, and total strategy and buy-and-hold returns.
    """
    position, strategy = res["position"], res["strategy_returns"]
    actual = labels.reindex(proba.index)
    labelled = actual.notna()
    return {
        "auc": roc_auc_score(actual[labelled], proba[labelled]),
        "precision_buy": actual[proba > constants.BUY].mean(),  # mean skips NaN = flat
        "hit_rate": (strategy[position != 0] > 0).mean(),
        "trades": position.diff().abs().fillna(position.abs()).sum(),
        "exposure": position.abs().mean(),
        "total": (1 + strategy).prod() - 1,
        "buy_hold": (1 + res["buy_hold"]).prod() - 1,
    }
