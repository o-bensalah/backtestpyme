class Strategy:
    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def execute_day(self, prices_row, signal_row, shares, cash) -> tuple:
        raise NotImplementedError