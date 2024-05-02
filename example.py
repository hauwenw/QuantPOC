# source: https://hackmd.io/@Linnn/Hy5xfxQgC?utm_source=preview-mode&utm_medium=rec

import yfinance as yf
import pandas as pd  # 資料處理套件
import datetime as dt  # 時間套件

from backtesting import Backtest, Strategy  # 回測套件
from backtesting.lib import crossover

import talib

# 輸入股票代號
stock_id = "2376.tw"  # 以技嘉為例
# 抓取 5 年資料
df = yf.download(stock_id, period="5y")  # 設定回測期間


def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()


class Three_way_strategy(Strategy):
    def init(self):
        price = self.data.Close

        # 初始化
        self.ma5 = self.I(SMA, price, 5)
        self.ma20 = self.I(SMA, price, 20)

        # 初始化 KD
        self.slow_k, self.slow_d = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close,
                                          fastk_period=9, slowk_period=3, slowd_period=3)
        # 初始化RSI
        self.RSI = self.I(talib.RSI, price, timeperiod=14)

    def next(self):
        if crossover(self.ma5, self.ma20) and crossover(self.slow_k, self.slow_d) or self.RSI[-1] < 20:
            self.buy()
        elif crossover(self.ma20, self.ma5) and crossover(self.slow_d, self.slow_k) or self.RSI[-1] > 80:
            if len(self.trades) > 0:
                self.trades[0].close()


bt = Backtest(df, Three_way_strategy, cash=150000, commission=0.004, exclusive_orders=True)
stats = bt.run()
bt.plot()
print(stats)
