import pandas as pd
import numpy as np
from strategies import CheapestN


def load_data(filepath):
    return pd.read_csv(filepath, index_col="Date", parse_dates=True)

def compute_portfolio_value(prices_row, shares, cash):
    equity = cash + float(np.nansum(np.array(shares) * prices_row.values))

    weights = [cash / equity]
    for share, price in zip(shares, prices_row):
        weights.append(share * price / equity)
    return equity, weights

def run_backtest(prices, strategy, initial_capital=100_000):
    shares = [0] * len(prices.columns)
    cash = float(initial_capital)
    signals = strategy.compute_signals(prices)

    rows = []
    for date, prices_row in prices.iterrows():
        signal_row = signals.loc[date]
        shares, cash = strategy.execute_day(prices_row, signal_row, shares, cash)
        equity, _ = compute_portfolio_value(prices_row, shares, cash)
        row = {"equity": equity, "cash": cash}
        row.update(zip(prices.columns, shares))
        rows.append(row)

    return pd.DataFrame(rows, index=prices.index)

def compute_metrics(equity, risk_free):
    total_return = (equity.iloc[-1] - equity.iloc[0]) / equity.iloc[0]

    daily_returns = equity.pct_change().dropna()
    daily_rf = (risk_free.reindex(equity.index).ffill() / 100 / 252)
    excess_returns = daily_returns - daily_rf
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)

    rolling_max = equity.cummax()
    max_drawdown = ((equity - rolling_max) / rolling_max).min()

    return {
        "equity open": f"${round(float(equity.iloc[0]), 4)}",
        "equity close": f"${round(float(equity.iloc[-1]), 4)}",
        "total_return": f"{round(float(total_return) * 100, 2)}%",
        "sharpe_ratio": round(float(sharpe), 4),
        "max_drawdown": round(float(max_drawdown), 4),
    } 

if __name__ == "__main__":
    prices = load_data("data/sp500_data.csv")
    risk_free = load_data("data/tbill_data.csv")["^IRX"]
    index = load_data("data/spy_data.csv")["SPY"]
    
    strategy = CheapestN(5)
    results = run_backtest(prices, strategy, initial_capital=100_000)

    stategy_metrics = compute_metrics(results["equity"], risk_free)
    index_metrics = compute_metrics(index, risk_free)

    print(stategy_metrics)
    print(index_metrics)
    

