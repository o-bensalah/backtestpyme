# backtestpyme
Backtesting python project. Used to test various strategies and evaluate their performance.

## Structure
#### Data collector
* Gathers the list of the 500 biggest US companies
* Downloads Close prices for those companies saves them to csv format
* Downloads T-bill Close prices, saves them to csv format
* Downloads SPY Close prices, saves them to csv format

#### Backtester
* Calls one of the strategies in the section below on the data previously downloaded

#### Metrics
* Computes to following metrics:
    * Equity Open
    * Equity Close
    * % Return
    * Sharpe Ratio - Use 
    * Max Drawdown

## Strategies
#### Cheapest N
* Buy the N cheapest stocks and hold undefinetly

#### Moving Average Crossover
* Strategy description

#### Momentum
* Strategy description

#### Mean Reversion
* trategy description

## Assumptions/Limitations
* Yahoo finance data is adjusted for splits and dividends but not, survivor-bias. Although this might cause a gap between computed vs real returns, an assumption is made that no company will go from being one for the Top 500 companies to $0 in the timeframe of the data we're using (~3 years)

 