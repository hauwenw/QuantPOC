import talib
from backtesting import Strategy
from backtesting.lib import crossover

from strategies.utils import SMA


class ThreeWay(Strategy):
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
