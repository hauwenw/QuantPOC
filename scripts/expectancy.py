import csv
import time
from collections import defaultdict

import pandas as pd
import twstock
import yfinance as yf
from backtesting import Backtest, Strategy  # 回測套件
from backtesting.lib import crossover
import heapq
import logging
import multiprocessing
from FinMind.data import DataLoader
import platform
from scipy import stats

if platform.system() == 'Windows':
    pass
else:
    multiprocessing.set_start_method('fork')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def PE(data):
    return data.sma30 / data.last_4_quarters_eps


def EPS(data, sorted_eps: list[tuple], n):
    def get_pe_ration(row):
        for eps in sorted_eps:
            if row.name > eps[0]:
                return eps[1] * n

    return data.df.apply(get_pe_ration, axis=1)


def get_strategy_cls(ticker):
    class PERatio(Strategy):
        low_pe = 12
        high_pe = 20

        def init(self):
            self.pe = self.I(PE, self.data)

        def next(self):
            if self.pe <= self.low_pe:
                self.position.close()
                self.buy()
            elif self.pe >= self.high_pe:
                self.position.close()
                self.sell()

    return PERatio


markets = ['上市']  # '上市', '上櫃'

types = ['股票']  # '特別股', 'ETF', '臺灣存託憑證(TDR)', '上市認購(售)權證', '受益證券-不動產投資信託', '股票'

targets = [c for c in twstock.codes if twstock.codes[c].market in markets and twstock.codes[c].type in types]
# targets = ['2236']

heap = []
runtime_summary = dict(
    processed=0,
    failed=0,
    failed_stock=[]
)
start_time = time.time()

data_period = '3y'

# get TW stock index
df_TWII = yf.download('^TWII', period=data_period)

for target in targets:
    stock_id = f"{target}.tw"

    if not stock_id.startswith('2'):
        continue

    logger.info(f'run stock {stock_id}')

    try:
        # get EPS df
        api = DataLoader()
        # api.login_by_token()
        df = api.taiwan_stock_financial_statement(
            stock_id=target,
            start_date='2019-01-01',
        )
        eps_df = df[df['type'] == 'EPS']
        eps_df['quarter'] = pd.to_datetime(eps_df['date']).dt.to_period('Q')
        eps_df['date'] = pd.to_datetime(eps_df['date'])


        def get_last_4_quarters(quarter, quarterly_eps):
            selected_quarters = pd.period_range(end=quarter, periods=5, freq='Q')[:-1]
            return quarterly_eps[quarterly_eps['date'].dt.to_period('Q').isin(selected_quarters)]['value'].sum()


        # get stock price df
        df = yf.download(stock_id, period=data_period)
        df['quarter'] = df.index.to_period('Q')

        # calc
        df['sma30'] = pd.Series(df['Close']).rolling(30).mean()
        df['last_4_quarters_eps'] = df['quarter'].apply(lambda x: get_last_4_quarters(x, eps_df))

        # Calculate stock returns
        df['stock_returns'] = df['Close'].pct_change()
        # Calculate market returns (use TWII as market benchmark)
        df['market_returns'] = df_TWII['Adj Close'].pct_change()

        # Drop NaN values
        df.dropna(subset=['stock_returns', 'market_returns'], inplace=True)

        # Calculate Alpha and Beta using linear regression
        beta, alpha, _, _, _ = stats.linregress(df['market_returns'], df['stock_returns'])

        bt = Backtest(df, get_strategy_cls(stock_id), cash=150000, commission=0.004, exclusive_orders=True)
        bt_stats = bt.optimize(low_pe=range(5, 20, 2),
                            high_pe=range(10, 40, 5),
                            maximize='Equity Final [$]',
                            constraint=lambda param: param.low_pe < param.high_pe)

        # only keep best 10 stock
        if bt_stats['Expectancy [%]'] > 0:
            heapq.heappush(heap, (
                bt_stats['Expectancy [%]'] * -1, bt_stats['Return [%]'], stock_id, bt_stats['_strategy'].low_pe,
                bt_stats['_strategy'].high_pe, alpha, beta))

        runtime_summary['processed'] += 1
    except Exception as e:
        runtime_summary['failed'] += 1
        runtime_summary['failed_stock'].append(stock_id)
        logger.exception(f'stock {stock_id} backtest failed')

with open('output.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['stock_id', 'low_pe', 'high_pe', 'Expectancy [%]', 'Return [%]', 'Alpha', 'Beta'])
    while heap:
        expectancy, return_percent, stock_id, low_pe, high_pe, alpha, beta = heapq.heappop(heap)
        csvwriter.writerow([stock_id, low_pe, high_pe, expectancy * -1, return_percent, alpha, beta])

end_time = time.time()
runtime_summary['duration'] = end_time - start_time
logger.info(runtime_summary)
