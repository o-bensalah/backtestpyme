import itertools
import pandas as pd
from backtester import run_backtest, compute_metrics


def tune(strategy_class, param_grid, prices, risk_free, metric="sharpe_ratio"):
    keys = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))

    rows = []
    for combo in combos:
        params = dict(zip(keys, combo))
        strategy = strategy_class(**params)
        portfolio = run_backtest(prices, strategy)
        metrics = compute_metrics(portfolio["equity"], risk_free)
        rows.append({**params, **metrics})

    results = pd.DataFrame(rows)
    results = results.sort_values(metric, ascending=False).reset_index(drop=True)
    return results


if __name__ == "__main__":
    from backtester import load_data
    from cheapestN import CheapestN

    prices = load_data("data/sp500_data.csv")
    risk_free = load_data("data/tbill_data.csv")["^IRX"]

    param_grid = {"n": range(1, 500)}
    results = tune(CheapestN, param_grid, prices, risk_free)
    print(results.to_string())
