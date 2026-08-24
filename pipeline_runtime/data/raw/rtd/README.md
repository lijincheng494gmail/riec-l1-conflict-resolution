# RTD raw data

`data3.csv` is the residence-time-distribution tracer response table used by `scripts/run_rtd.py`.
`data1.csv` is retained as an auxiliary/source table from the original workspace; the main runtime uses `data3.csv`.

The adapter constructs long-form normalized E(t) responses and evaluates candidates by leave-one-run-out grouped CV.
