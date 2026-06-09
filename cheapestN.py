import pandas as pd
from base import Strategy

class CheapestN(Strategy):
    def __init__(self, n=10):
        self.n = n

    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        topN = prices.iloc[0].nsmallest(self.n).index
        signals.loc[signals.index[0], topN] = 1.0
        return signals

    def execute_day(self, prices_row, signal_row, shares, cash) -> tuple:
        shares = list(shares)
        allocation = cash / self.n
        for ticker in signal_row[signal_row > 0].index:
            price = prices_row[ticker]
            if pd.notna(price) and price > 0:
                idx = prices_row.index.get_loc(ticker)
                n = int(allocation // price)
                shares[idx] += n
                cash -= n * price
        return shares, cash