import pandas as pd
import numpy as np
import random
from cheapestN import CheapestN

STRATEGIES = {
    "cheapestN": CheapestN,
}

def parse_params(param_list):
    if not param_list:
        return {}
    params = {}
    for p in param_list:
        key, val = p.split("=", 1)
        for cast in (int, float, str):
            try:
                params[key] = cast(val)
                break
            except ValueError:
                continue
    return params

def load_data(filepath):
    return pd.read_csv(filepath, index_col="Date", parse_dates=True)

def compute_portfolio_value(prices_row, shares, cash):
    equity = cash + float(np.nansum(np.array(shares) * prices_row.values))

    weights = [cash / equity]
    for share, price in zip(shares, prices_row):
        weights.append(share * price / equity)
    return equity, weights

def run_backtest(prices, strategy, initial_capital=100_000, fee_rate=0):
    shares = [0] * len(prices.columns)
    cash = float(initial_capital)
    signals = strategy.compute_signals(prices)

    rows = []
    for date, prices_row in prices.iterrows():
        signal_row = signals.loc[date]
        cash_before = cash
        shares, cash = strategy.execute_day(prices_row, signal_row, shares, cash)
        cash -= abs(cash_before - cash) * fee_rate
        equity, _ = compute_portfolio_value(prices_row, shares, cash)
        row = {"equity": equity, "cash": cash}
        row.update(zip(prices.columns, shares))
        rows.append(row)

    return pd.DataFrame(rows, index=prices.index)

def compute_metrics(portfolio, risk_free):
    total_return = (portfolio.iloc[-1] - portfolio.iloc[0]) / portfolio.iloc[0]

    daily_returns = portfolio.pct_change().dropna()
    daily_rf = (risk_free.reindex(portfolio.index).ffill() / 100 / 252)
    excess_returns = daily_returns - daily_rf
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)

    rolling_max = portfolio.cummax()
    max_drawdown = ((portfolio - rolling_max) / rolling_max).min()

    return {
        "start date": f"{portfolio.index[0].date()}",
        "end date": f"{portfolio.index[-1].date()}",
        "portfolio open": f"${round(float(portfolio.iloc[0]), 4)}",
        "portfolio close": f"${round(float(portfolio.iloc[-1]), 4)}",
        "total_return": f"{round(float(total_return) * 100, 2)}%",
        "sharpe_ratio": round(float(sharpe), 4),
        "max_drawdown": round(float(max_drawdown), 4),
    } 

def generate_windows(index, n_timeframes, min_period):
    valid_ends = index[min_period:]
    windows = []
    for _ in range(n_timeframes):
        end = random.choice(valid_ends)
        end_loc = index.get_loc(end)
        start = index[random.randint(0, end_loc - min_period)]
        windows.append((start, end))
    return windows


def run_stress_test(prices, strategy, risk_free, windows, initial_capital=100_000, fee_rate=0.0, benchmark=None):
    rows = []
    for start, end in windows:
        slice_prices = prices.loc[start:end]
        portfolio = run_backtest(slice_prices, strategy, initial_capital, fee_rate)
        metrics = compute_metrics(portfolio["equity"], risk_free)

        if benchmark is not None:
            spy_metrics = compute_metrics(benchmark.loc[start:end], risk_free)
            spy_metrics = {f"spy_{k}": v for k, v in spy_metrics.items() if k not in ("start date", "end date")}
            metrics = {**metrics, **spy_metrics}

        rows.append(metrics)

    return pd.DataFrame(rows)


def print_metrics(metrics, header=""):
    print("=" * 40)
    print(header.center(40))
    print("=" * 40)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    import argparse
    from tuner import tune

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Equity strategy backtester",
        epilog=(
            "examples:\n"
            "  python backtester.py --test --strategy cheapestN\n"
            "  python backtester.py --test --strategy cheapestN --param n=10 --fee 0.001\n"
            "  python backtester.py --stress --strategy cheapestN --timeframes 20 --period 180\n"
            "  python backtester.py --stress --strategy cheapestN --param n=25\n"
            "  python backtester.py --tune --strategy cheapestN --timeframes 10 --period 90\n"
        )
    )

    modes = parser.add_argument_group("modes (one required)")
    modes.add_argument("--test", action="store_true",
                       help="Simple backtest on full dataset")
    modes.add_argument("--stress", action="store_true",
                       help="Stress test across random timeframes")
    modes.add_argument("--tune", action="store_true",
                       help="Grid search over strategy params using stress test windows")

    strategy_args = parser.add_argument_group("strategy")
    strategy_args.add_argument("--strategy", default=None, choices=STRATEGIES.keys(),
                               help="(required) strategy to run [all modes]")
    strategy_args.add_argument("--param", action="append", metavar="key=value",
                               help="(optional) strategy constructor param, repeatable\n"
                                    "  e.g. --param n=10  [--test, --stress only]")

    run_args = parser.add_argument_group("run options")
    run_args.add_argument("--fee", type=float, default=0.011,
                          help="Fee rate per trade (default: 0.011) [all modes]")
    run_args.add_argument("--capital", type=float, default=100_000,
                          help="Initial capital (default: 100000) [all modes]")
    run_args.add_argument("--timeframes", type=int, default=10,
                          help="Number of random windows (default: 10) [--stress, --tune]")
    run_args.add_argument("--period", type=int, default=90,
                          help="Minimum window length in trading days (default: 90) [--stress, --tune]")
    args = parser.parse_args()

    prices = load_data("data/sp500_data.csv")
    risk_free = load_data("data/tbill_data.csv")["^IRX"]
    index = load_data("data/spy_data.csv")["SPY"]

    no_mode = not (args.test or args.stress or args.tune)
    if no_mode or args.strategy is None:
        parser.print_help()

    elif args.test:
        strategy_class = STRATEGIES[args.strategy]
        params = parse_params(args.param)
        portfolio = run_backtest(prices, strategy_class(**params), args.capital, args.fee)
        print_metrics(compute_metrics(portfolio["equity"], risk_free), args.strategy)
        print_metrics(compute_metrics(index, risk_free), "SPY")

    elif args.stress:
        strategy_class = STRATEGIES[args.strategy]
        params = parse_params(args.param)
        windows = generate_windows(prices.index, args.timeframes, args.period)
        stress = run_stress_test(prices, strategy_class(**params), risk_free, windows,
                                 initial_capital=args.capital, fee_rate=args.fee,
                                 benchmark=index)
        print(stress.to_string())

    elif args.tune:
        strategy_class = STRATEGIES[args.strategy]
        param_grid = {"n": range(1, 50)}
        windows = generate_windows(prices.index, args.timeframes, args.period)
        results = tune(strategy_class, param_grid, prices, risk_free, windows,
                       initial_capital=args.capital, fee_rate=args.fee, benchmark=index)
        print(results.to_string())

    

