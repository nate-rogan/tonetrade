# scripts

| File | What it is |
| --- | --- |
| `model.py` | The pipeline: data, features, walk-forward models, backtest. **Edit this one.** |
| `model.ipynb` | `model.py` rendered with its outputs (tables and charts). **For viewing only.** |

`model.py` is a plain Python file split into cells with `# %%` markers. It's the
source of truth: it diffs cleanly, it's linted, and it counts toward the 200-line budget.

`model.ipynb` is generated from it and committed so the results and charts can be read
on GitHub without running anything. Don't edit the notebook: changes are overwritten
the next time it's generated.

## Regenerating the notebook

After changing `model.py`, rerun it into the notebook and commit both files together:

```bash
pixi run notebook
```

That task runs:

```bash
jupytext --to ipynb --set-kernel - --execute scripts/model.py
```

- `--to ipynb` converts each `# %%` cell into a notebook cell and writes
  `scripts/model.ipynb` next to the script.
- `--set-kernel -` uses the pixi environment's Python as the kernel.
- `--execute` runs every cell top to bottom, so the saved outputs always match the code.

Running it fetches prices live from Yahoo Finance (network needed, no API keys) and takes
a minute or two. Because prices are fetched live, XGBoost numbers can shift slightly
between runs.

## Running interactively

To explore rather than regenerate, open `model.py` in VS Code with the Jupyter extension
and use **Run Cell** above each `# %%` (or **Shift+Enter**). Output goes to the
Interactive Window and isn't saved anywhere.
