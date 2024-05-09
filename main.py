import argparse
import importlib

import yfinance as yf

from backtesting import Backtest  # 回測套件

from strategies import get_strategy_class


def main(stock_id: str, strategy_name: str, period):
    strategy_class = get_strategy_class(strategy_name)
    df = yf.download(stock_id, period=period)
    bt = Backtest(df, strategy_class, cash=150000, commission=0.004, exclusive_orders=True)
    stats = bt.run()
    bt.plot()
    print(stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process stock ID and strategy")
    parser.add_argument("--stock_id", required=True, help="Stock ID", default='2376.tw')
    parser.add_argument("--period", required=True, help="Backtest period", default='5y')
    parser.add_argument("--strategy", required=True, help="Strategy", default='SmaCross')
    args = parser.parse_args()

    main(args.stock_id, args.strategy, args.period)

# test 2