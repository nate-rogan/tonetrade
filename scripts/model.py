"""ToneTrade model script in percent-format (# %%) cells.

Builds market data, features and labels, fits XGBoost and a logistic baseline with
walk-forward evaluation, and backtests the signal against buy-and-hold ITA.
"""

# %% Imports and config
from itertools import product

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

import tonetrade as tt


pd.options.plotting.backend = "plotly"


# %% Market data and features
market = tt.features.build_market_data()
features = tt.features.build_features(market)
features.plot(subplots=True, figsize=(12, 12), backend="matplotlib")


# %% Data set: features + label, warm-up trimmed
feature_cols = list(features)
data = features.assign(label=tt.features.build_target(market["ita"])).loc[
    tt.constants.START_DATE :
]
data = data.dropna(subset=feature_cols)
labels = data["label"]
returns = market["ita"].pct_change()  # t-1 -> t, as backtest expects


# %% Data checks: first date, rows, NaNs, label balance
print(data.index[0], len(data), data[feature_cols].isna().sum().sum())
print(labels.value_counts(dropna=False, normalize=True).round(2))  # NaN = flat
print(labels.groupby(labels.index.year).value_counts().unstack())


# %% Models and feature sets
MODELS = {
    "xgb": XGBClassifier(
        max_depth=3,
        n_estimators=200,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=0,
    ),
    "logit": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
}

GPR = ["gprd_act", "gprd_threat"]
FEATURE_SETS = {
    "all": feature_cols,
    "no_gpr": [c for c in feature_cols if c not in GPR],
    "no_act": [c for c in feature_cols if c != "gprd_act"],
    "no_threat": [c for c in feature_cols if c != "gprd_threat"],
}


# %% Evaluate: every model x feature set
rows, runs = [], {}
for (m, model), (f, cols) in product(MODELS.items(), FEATURE_SETS.items()):
    proba = tt.evaluate.walk_forward(data, model, cols)
    res = tt.evaluate.backtest(tt.evaluate.to_positions(proba), returns)
    runs[m, f] = proba, res
    rows.append({
        "model": m,
        "features": f,
        **tt.evaluate.summarise(res, proba, labels),
    })

results = pd.DataFrame(rows).set_index(["model", "features"])
print(results.round(3))


# %% Cumulative returns vs buy-and-hold
shown = [("xgb", "all"), ("logit", "all"), ("xgb", "no_gpr")]
cum = pd.DataFrame({
    f"{m}/{f}": (1 + runs[m, f][1]["strategy_returns"]).cumprod() for m, f in shown
})
cum["buy_hold"] = (1 + runs["xgb", "all"][1]["buy_hold"]).cumprod()
cum.plot()


# %% Classification report: xgb, all features, labelled days (0.5 cut)
proba, res = runs["xgb", "all"]
actual = labels.reindex(proba.index)
labelled = actual.notna()
print(
    classification_report(
        actual[labelled],
        (proba[labelled] > 0.5).astype(float),
        target_names=["sell", "buy"],
    )
)


# %% Robustness: one day of execution delay
delayed = tt.evaluate.backtest(tt.evaluate.to_positions(proba), returns, lag=1)
print(
    pd.DataFrame({
        "lag 0": tt.evaluate.summarise(res, proba, labels),
        "lag 1": tt.evaluate.summarise(delayed, proba, labels),
    }).round(3)
)
