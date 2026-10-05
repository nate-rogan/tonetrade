# ToneTrade

Trading research based on macro indicators and the tone of news articles.

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
  data.py        data access (APIs, local files, databases)
scripts/         percent-format scripts for interactive work
  model.py       model experiments
tests/unit/      pytest unit tests
data/            committed CSV data (model inputs)
```

## Percent-format scripts

Files in `scripts/` (starting with `model.py`) are plain Python files split into cells with
`# %%` markers:

```python
# %%
from tonetrade.data import fetch_text_test

# %%
print(fetch_text_test())
```

With the Jupyter extension installed, VS Code shows **Run Cell** above each `# %%`
(or press **Shift+Enter**). Output appears in the Interactive Window; pick the pixi
environment as the kernel the first time.

Because they are plain `.py` files, they diff cleanly in git. Cell outputs are not saved
to the file — rerun the cells to reproduce them.

## Tasks

```bash
pixi run lint    # pre-commit hooks on all files (ruff lint + format, whitespace, TOML/AST checks)
pixi run test    # pytest
pixi run check   # lint, then test
```

Ruff's lint and format hooks run on `src/` and `tests/` only; `scripts/` is not linted.

## Configuration

Copy `.env.example` to `.env` and fill in any API keys. `.env` is gitignored.
