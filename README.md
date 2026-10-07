# ToneTrade

Trading research: does geopolitical risk in the news help time defence equities?

## Question

Does geopolitical risk in the news (the GPR index's acts and threats) add information about defence equity returns (ITA), beyond ITA's own price history and oil? Output is a buy / sell / stay-out signal. A negative result with clean method is a valid outcome.

## Data

Daily data from 2009-01-01 to today (fetched from 2007-08-01 so rolling windows have
history), fetched and aligned by `scripts/model.py`. No API keys are needed.

| Series | Source | Notes |
| --- | --- | --- |
| ITA, Brent (`BZ=F`) | Yahoo Finance (`yfinance`) | Adjusted daily closes |
| Geopolitical Risk Index, daily (GPRD, GPRD_ACT, GPRD_THREAT) | Caldara & Iacoviello, snapshot in `data/data_gpr_daily_recent.csv` | News-based; known the next business day |

The grid is ITA's trading days. The GPR index is smoothed with a 7-day mean and lagged a
business day, since each day's value is built from that day's newspapers.

An earlier version also used macro data (CPI, unemployment, the 10y–2y spread, aligned
to first-release dates). It was dropped: the model scored at the base rate with it, it
needed a FRED API key, and trees can't extrapolate slow-moving levels into new regimes.
That version is commit `b48a993`.

### Geopolitical Risk (GPR) index

The GPR index is based on searches of the archives of 10 newspapers: Chicago Tribune, the
Daily Telegraph, Financial Times, The Globe and Mail, The Guardian, the Los Angeles Times,
The New York Times, USA Today, The Wall Street Journal and The Washington Post. It counts
the number of articles related to adverse geopolitical events in each newspaper as a share
of the total number of news articles, scaled so that the 1985–2019 average is 100.

The search is organised in eight categories: War Threats (1), Peace Threats (2), Military
Buildups (3), Nuclear Threats (4), Terror Threats (5), Beginning of War (6), Escalation of
War (7) and Terror Acts (8). Two subindexes are built from these: Geopolitical Threats
(GPRT, categories 1–5) and Geopolitical Acts (GPRA, categories 6–8).

| Column | Definition |
| --- | --- |
| `GPRD` | Daily GPR index: share of articles about adverse geopolitical events (all eight categories), 1985–2019 average = 100. A value of 150 means 50% more risk coverage than normal. |
| `GPRD_ACT` | Daily Geopolitical Acts: articles about events that are happening, i.e. the beginning of a war, escalation of a war, or terror acts (categories 6–8). |
| `GPRD_THREAT` | Daily Geopolitical Threats: articles about risks that haven't materialised, i.e. war, peace, military, nuclear and terror threats (categories 1–5). |

- **Source:** Caldara, Dario and Matteo Iacoviello (2022), "Measuring Geopolitical Risk,"
  *American Economic Review*, 112(4), pp. 1194–1225.
- **Data:** daily file `data_gpr_daily_recent.xls`, downloaded from
  <https://www.matteoiacoviello.com/gpr.htm> on 6 October 2026 (covers 1985-01-01 to
  2026-10-05) and saved as `data/data_gpr_daily_recent.csv`.
- **Licence:** Creative Commons BY. Used and redistributed here with credit to the source
  and authors.
- **Updates:** the daily file is updated every Monday. The latest values are preliminary
  and can be revised, so the committed snapshot is what results in this repo use.

## Method

*Planned; details are filled in as each step is built.*

- **Features.** ITA and Brent returns over 5, 20 and 60 days, ITA 20-day volatility and
  distance from its 50-day mean, and GPR acts and threats. Every window ends at *t*.
- **Target.** Buy if the 5-day forward return is above half a typical 5-day move
  (volatility-scaled), sell if below minus that; flat days are left out of training.
- **Models.** XGBoost with shallow trees, and a z-scored logistic regression as the
  baseline it has to beat.
- **Evaluation.** Walk-forward by year from 2015: each year is predicted by a model trained
  only on earlier years, with the last 5 training days dropped so labels can't reach into
  the test year.
- **Ablation.** The core test: rerun without the GPR features and compare.

## Results

Not yet written up. Will report precision, recall and F1 per class for both models, with
and without the GPR features.

## Backtest

Not yet run. Test-period signals become positions on the next period's return, net of a
per-trade transaction cost, compared against buy-and-hold ITA. Reports cumulative return,
hit rate and number of trades. Underperforming buy-and-hold is a likely and acceptable
result.

## Running

`scripts/model.py` is the whole pipeline: fetch, align, build features, train, backtest.
It needs network access for Yahoo Finance and no keys:

```bash
pixi run python scripts/model.py
```

Or run it cell by cell in VS Code (see [Percent-format scripts](#percent-format-scripts)).

**Daily signal** (planned): a scheduled GitHub Action fetches new data, produces the day's
signal, and posts it as a comment on a long-lived issue.

## Limitations

- GPR measures how much the news covers geopolitical risk, not its tone.
- Positions are re-decided daily although the label looks 5 days ahead, so labels overlap.
- Oil and geopolitical risk are correlated, so their relative feature importance shouldn't
  be over-read.
- Macro conditions aren't modelled (see Data).
- Out of scope: predicting conflicts, events or defence budgets, and forecasting price
  levels.

## Requirements

- [pixi](https://pixi.sh) — manages Python and every dependency (conda-forge + the project itself)
- [VS Code](https://code.visualstudio.com/) with the
  [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
  (`ms-toolsai.jupyter`) for running percent-format cells

## Setup

```bash
pixi install
pixi run pre-commit install
```

`pixi install` creates the environment in `.pixi/` from `pixi.lock` and installs the
`tonetrade` package in editable mode, so `import tonetrade` works from scripts, tests and
notebook cells, and code changes take effect without reinstalling.

`pre-commit install` adds the git hook that lints and formats code on each commit.

In VS Code, run **Python: Select Interpreter** and choose the pixi environment.

## Project layout

```text
src/tonetrade/   package code
  constants.py   date range, tickers, GPR columns, model and trading settings
  sources.py     data sources (Yahoo Finance prices, the GPR snapshot)
  features.py    market panel on the daily grid, features and labels
  evaluate.py    walk-forward predictions, positions, backtest and metrics
scripts/
  model.py       the end-to-end pipeline (percent-format cells)
tests/
  unit/          fast tests, no network
  integration/   tests that call the live APIs (marked `integration`)
data/            data files
```

## Percent-format scripts

`scripts/model.py` is a plain Python file split into cells with `# %%` markers:

```python
# %%
import tonetrade as tt

# %%
tt.features.build_market_data().tail()
```

With the Jupyter extension installed, VS Code shows **Run Cell** above each `# %%`
(or press **Shift+Enter**). Output appears in the Interactive Window; pick the pixi
environment as the kernel the first time.

Because they are plain `.py` files, they diff cleanly in git. Cell outputs are not saved
to the file — rerun the cells to reproduce them.

## Tasks

```bash
pixi run lint    # pre-commit hooks on all files (ruff lint + format, whitespace, TOML/AST checks)
pixi run test    # pytest, unit tests only (no network)
pixi run test-integration  # tests marked `integration`, which call Yahoo Finance
pixi run check   # lint, then test
```
