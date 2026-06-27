import itertools
import pandas as pd
from backtester import run_backtest, compute_metrics


def tune(strategy_class, param_grid, prices, risk_free,
         initial_capital=100_000, fee_rate=0.0, benchmark=None, metric="sharpe_ratio"):
    keys = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))

    rows = []
    for combo in combos:
        params = dict(zip(keys, combo))
        strategy = strategy_class(**params)
        portfolio = run_backtest(prices, strategy, initial_capital, fee_rate)
        metrics = compute_metrics(portfolio["equity"], risk_free)

        if benchmark is not None:
            spy_metrics = compute_metrics(benchmark, risk_free)
            spy_metrics = {f"spy_{k}": v for k, v in spy_metrics.items() if k not in ("start date", "end date")}
            metrics = {**metrics, **spy_metrics}

        rows.append({**params, **metrics})

    results = pd.DataFrame(rows)
    results = results.sort_values(metric, ascending=False).reset_index(drop=True)
    return results
