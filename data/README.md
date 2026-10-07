# data

The analysis reads only the files here, so it runs offline and gives the same results
every time.

| File | What it is | How it's made |
| --- | --- | --- |
| `prices.csv` | ITA and Brent crude adjusted daily closes, 2007-08-01 to 2026-10-06 | `pixi run snapshot` (Yahoo Finance) |
| `data_gpr_daily_recent.csv` | Daily Geopolitical Risk index (acts and threats), 1985 to 2026-10-05 | Downloaded by hand, see below |
| `raw/` | Scratch space for downloads, not committed | |

## Why snapshots

Yahoo's adjusted closes differ very slightly from one request to the next (about
0.0001 on ITA), which is enough to change some XGBoost splits and the results. Committing
the prices means the same code always gives the same numbers. The GPR file is revised by
its authors each week, so it's a fixed snapshot for the same reason.

## Updating the data

1. **Prices.** Set `END_DATE` in `src/tonetrade/constants.py` to the day after the last
   date you want (it's exclusive), then run:

   ```bash
   pixi run snapshot   # rewrites data/prices.csv; needs network, no API keys
   ```

2. **GPR.** Download `data_gpr_daily_recent.xls` from
   <https://www.matteoiacoviello.com/gpr.htm> (updated on Mondays), save it as
   `data/data_gpr_daily_recent.csv`, and keep the `date`, `GPRD_ACT` and `GPRD_THREAT`
   columns. Its last date should be close to the prices' last date; otherwise the most
   recent days carry stale GPR values forward.
3. **Results.** Regenerate the notebook and run the tests:

   ```bash
   pixi run notebook
   pixi run test
   ```

4. **Findings.** Check the Findings cell at the end of `scripts/model.py` against the new
   results. Update its numbers and dates (and the data dates in this file and the main
   README), then run `pixi run notebook` again so the notebook picks up the text.
5. **Commit** the data files, `scripts/model.py`, `scripts/model.ipynb` and the READMEs
   together, e.g. "Data to 2026-11-30, findings unchanged".

## Sources and licence

- **Prices:** Yahoo Finance via `yfinance`, for research use.
- **GPR:** Caldara, Dario and Matteo Iacoviello (2022), "Measuring Geopolitical Risk,"
  *American Economic Review*, 112(4), pp. 1194–1225. Creative Commons BY; redistributed
  here with credit to the authors.
