# backtestpyme

Python backtesting framework for equity strategies. Downloads historical price data,
runs strategies against it, and reports performance metrics against an SPY benchmark.

## Requirements

```
pandas
numpy
yfinance
```

## Structure

#### Data collector (`dataCollector.py`)
Downloads and saves CSV data to `data/`. Run manually when refreshing data (3-year
rolling window, end date hardcoded in the script).

```
python dataCollector.py 1   # S&P 500 close prices (tickers pulled live from Wikipedia)
python dataCollector.py 2   # T-bill yield (^IRX)
python dataCollector.py 3   # Russell 3000 close prices (tickers from iShares IWV holdings)
python dataCollector.py 4   # SPY close prices (benchmark)
```

#### Backtester (`backtester.py`)
Core engine and CLI entry point. Runs a strategy against the downloaded price data in
one of three modes:

* `--test` — single backtest over the full dataset (or a chosen date range), compared
  against SPY
* `--stress` — runs the strategy across many random date windows to check robustness
* `--tune` — grid search over strategy parameters, scored on averaged stress-test
  windows

```
python backtester.py --test --strategy cheapestN
python backtester.py --test --strategy cheapestN --param n=10 --fee 0.001
python backtester.py --stress --strategy cheapestN --timeframes 20 --end 2025-01-01 --period 180
python backtester.py --stress --strategy cheapestN --param n=25 --start 2024-01-01 --end 2025-06-01
python backtester.py --tune --strategy cheapestN --tune-param n=1:50 --end 2025-01-01 --period 252
python backtester.py --tune --strategy momentum --tune-param portfolio_size=1:30 --tune-param windows=5:50 --start 2025-01-01 --end 2026-05-29
```

Common flags: `--strategy`, `--param key=value` (repeatable), `--tune-param key=start:stop`
(repeatable), `--fee`, `--capital`, `--timeframes`, and a date range via any two of
`--start`, `--end`, `--period`.

#### Metrics
Computed by `compute_metrics` for both the strategy and the SPY benchmark:
* Portfolio open / close value
* Total return
* Sharpe ratio (excess return over T-bill yield, annualized)
* Max drawdown

## Strategies

Strategies implement the `Strategy` interface (`base.py`):
`compute_signals(prices)` builds a signal matrix, `execute_day(...)` turns that day's
signal into trades.

#### Cheapest N (`cheapestN.py`)
Buys the N lowest-priced stocks on day one and holds indefinitely.

#### Momentum (`momentum.py`)
Ranks stocks by average return over a set of lookback windows and rebalances daily
into the top `portfolio_size` performers.

## Tuner (`tuner.py`)
Grid search over a strategy's constructor params. For each combination, runs a stress
test across random windows and averages the metrics, then sorts by Sharpe ratio —
avoids overfitting to a single time period.

## Assumptions/Limitations
* Yahoo Finance data is adjusted for splits and dividends but not survivorship bias.
  This is mitigated by assuming no company drops from the S&P 500/Russell 3000 to $0
  within the dataset's ~3 year window, though it may still cause a gap between
  computed and real historical returns.
* See [survivorship-bias-free-data](https://github.com/o-bensalah/survivorship-bias-free-data)
  for a companion project that collects historical index membership + prices without
  this bias, a future data source for this backtester.
