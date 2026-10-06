# ToneTrade

Trading research based on macro indicators and the tone of news articles.

## Question

Does media sentiment add information about defence equity returns (ITA), beyond oil and macro conditions? Output is a buy / sell / stay-out signal. A negative result with clean method is a valid outcome.

## Data

Daily data from 2023-01-01 to today (fetched from 2021-10-01 so rolling windows and CPI's
12-month change have history), fetched and aligned by `scripts/model.py`.

| Series | Source | Notes |
| --- | --- | --- |
| ITA, S&P 500, NASDAQ, Brent (`BZ=F`) | Yahoo Finance (`yfinance`) | Adjusted daily closes |
| CPI (CPIAUCSL) | FRED / ALFRED | 12-month % change from first-release index levels |
| Unemployment rate (UNRATE) | FRED / ALFRED | First-release level |
| 10y–2y Treasury spread (T10Y2Y) | FRED | Daily, known the next business day |
| News headlines | GDELT via BigQuery | Two themes: geopolitical / defence, and AI (planned) |
| Headline tone | FinBERT or GDELT's own tone (to be decided) | One value per theme per day (planned) |

The grid is ITA's trading days. Monthly macro values are placed on the date they were
first released, not their reference month, and carried forward. The yield spread is
lagged a business day because FRED posts it after the close. Headlines will count toward
day *t* only if published before that day's market close.

## Method

*Planned; details are filled in as each step is built.*

- **Features.** Macro sets the regime (CPI change, unemployment, yield spread); price and
  tone set the timing (ITA and Brent returns over several windows, ITA realised volatility
  and distance from a moving average, daily geopolitical tone). Every window ends at *t*.
- **Target.** Buy if the forward return is above a threshold, sell if below minus the
  threshold; flat days are dropped.
- **Model.** XGBoost with shallow trees, trained on a time-ordered split (never random).
- **Ablation.** The core test: retrain without the tone features and compare.
- **Contrast.** The same pipeline with AI-theme tone against NASDAQ.

## Results

Not yet run. Will report precision, recall and F1 per class, and feature importance, for
the model with tone, without tone, and the AI / NASDAQ contrast.

## Backtest

Not yet run. Test-period signals become positions on the next period's return, net of a
per-trade transaction cost, compared against buy-and-hold ITA. Reports cumulative return,
hit rate and number of trades. Underperforming buy-and-hold is a likely and acceptable
result.

## Running

`scripts/model.py` is the whole pipeline: fetch, align, build features, train, backtest. It
needs a FRED API key in `.env` (and, once headlines are added, Google Cloud credentials
for BigQuery):

```bash
pixi run python scripts/model.py
```

Or run it cell by cell in VS Code (see [Percent-format scripts](#percent-format-scripts)).

**Daily signal** (planned): a scheduled GitHub Action fetches new data, produces the day's
signal, and posts it as a comment on a long-lived issue.

## Limitations

- About three years of daily data is a small sample for a classifier.
- Tone comes from headlines only, and GDELT's theme tagging is noisy.
- Off-the-shelf tone (FinBERT or GDELT's lexicon tone) isn't trained on geopolitical news.
- Oil and geopolitical tone are correlated, so their relative feature importance shouldn't
  be over-read.
- The 10y–2y spread is market-priced, so it isn't independent of equities.
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
  constants.py   date range, tickers and FRED series IDs
  sources.py     clients for external sources (Yahoo Finance, FRED/ALFRED)
  series.py      the project's named series, indexed by the date each value became known
  utils.py       helpers, e.g. aligning series onto the daily grid
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
tt.series.prices().tail()
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
pixi run test-integration  # tests marked `integration`, which call Yahoo and FRED
pixi run check   # lint, then test
```

## Configuration

Copy `.env.example` to `.env` and set `FRED_API_KEY` (free from
[FRED](https://fred.stlouisfed.org/docs/api/api_key.html)). `.env` is gitignored.
