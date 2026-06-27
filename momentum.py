import pandas as pd
from base import Strategy

class Momentum(Strategy):
    def __init__(self, portfolio_size=10,windows=(3,5,10,20)):
        self.windows = [windows] if isinstance(windows, int) else list(windows)
        self.portfolio_size = portfolio_size

    def compute_momentum(self, prices):
        return sum(prices.pct_change(w) for w in self.windows) / len(self.windows)


    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        signal = self.compute_momentum(prices)
        return signal

    def execute_day(self, prices_row, signal_row, shares, cash) -> tuple:
        shares = list(shares)
        top_n = signal_row.nlargest(self.portfolio_size).index

        for i, ticker in enumerate(signal_row.index):
            if shares[i] > 0 and ticker not in top_n:
                cash += shares[i] * prices_row[ticker]
                shares[i] = 0

        allocation = cash / self.portfolio_size
        for ticker in top_n:
            i = signal_row.index.get_loc(ticker)
            if shares[i] == 0 and pd.notna(prices_row[ticker]) and prices_row[ticker] > 0:
                n = int(allocation // prices_row[ticker])
                shares[i] += n
                cash -= n * prices_row[ticker]
        return shares, cash