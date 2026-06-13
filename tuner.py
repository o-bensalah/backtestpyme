import itertools
import pandas as pd
from backtester import run_stress_test


def tune(strategy_class, param_grid, prices, risk_free, windows,
         initial_capital=100_000, fee_rate=0.0, benchmark=None, metric="sharpe_ratio"):
    keys = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))

    rows = []
    for combo in combos:
        params = dict(zip(keys, combo))
        strategy = strategy_class(**params)
        stress = run_stress_test(prices, strategy, risk_free, windows,
                                 initial_capital=initial_capital, fee_rate=fee_rate,
                                 benchmark=benchmark)
        for _, window_row in stress.iterrows():
            rows.append({**params, **window_row.to_dict()})

    results = pd.DataFrame(rows)
    results = results.sort_values(["start date", metric], ascending=[True, False]).reset_index(drop=True)
    return results
