import pandas as pd
import numpy as np
from cheapestN import CheapestN

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

def print_metrics(metrics, header=""):
    print("=" * 40)
    print(header.center(40))
    print("=" * 40)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    initial_capital=100_000
    fee_rate = 0.011

    prices = load_data("data/sp500_data.csv")
    risk_free = load_data("data/tbill_data.csv")["^IRX"]
    index = load_data("data/spy_data.csv")["SPY"]

    portfolio = run_backtest(prices, CheapestN(25), initial_capital, fee_rate)

    stategy_metrics = compute_metrics(portfolio["equity"], risk_free)
    print_metrics(stategy_metrics, "Buy and hold 25 cheapest stocks metrics")

    index_metrics = compute_metrics(index, risk_free)
    print_metrics(index_metrics, "SPY metrics")

    

