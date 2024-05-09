import yfinance as yf
import datetime

stock_id = "2376.tw"  # 技嘉

gb = yf.Ticker(stock_id)

# output text
info_text = ""
financials_text = ""

# [Note] yfinance 的 ticker.info 資料如下
#   dividendRate = 現金股利 (例如 2024 會抓到去年 2023 的 6.2 元)
#   dividendYield 殖利率 = 股利 / 現在股價 = dividendRate/currentPrice
#                          股利也可以抓 lastDividendValue
#   exDividendDate = 上次股利發放日，是 Unix time format 從1970/1/1起算，要用datetime 轉換
#   payoutRatio 配息率 = 每股股利/EPS = dividendRate/trainlingEPS [!!!] 這是 chatGPT 給的公式， yfinance 看似用不同公式，算出來有差
#   fiveYearAvgDividendYield 五年平均殖利率
#   beta 相對市場的波動率， 1.0 代表與市場整體波動率相同， > 1.0 表示波動率大於市場，反之 < 1.0 表示較市場整體還穩定
#   trailingPE 本益比 = currentPrice / trailingEPS
#   forwardPE 預測本益比 currentPrice / forwardEPS
#   volume 交易量 [!!!] 跟 yahoo 上看到的有差異
#   averageVolume10days 十天平均交易量
#   marketCap 總市值 = sharesOutstanding 總流通股數 * currentPrice
#   fiftyTwoWeekLow 52周最低價
#   fiftyTwoWeekHigh 52周最高價
#   priceToSalesTrailing12Months 市銷率 = 市值 / 過去 12 個月營收
#   enterpriseValue 企業價值 = 市值 + 凈債 = marketCap + (totalDebt - totalCash) [!!!] 這是 chatGPT 給的公式， yfinance 看似用不同公式，算出來有差
#   profitMargins 淨利率 = netIncomeToCommon 淨收入 / totalRevenue 總營收
#   heldPercentInsiders ???
#   heldPercentInstitutions ???
#   impliedSharesOutstanding ???
#   bookValue ???
#   priceToBook ???
#   earningsQuarterlyGrowth 季度營利成長率
#   netIncomeToCommon 淨收入
#   trailingEps 目前每股盈餘
#   forwardEps 預測每股盈餘
#   pegRatio 本益成長比 = trailingPE / 淨利潤增長率 [!!!] 分母是什麼?券商預估?
#   recommendationMean 分析師評級?
#   recommendationKey 分析師推薦策略
#       -> Strong Buy
#       -> Buy
#       -> Hold
#       -> Underperform (表現不佳)
#       -> Sell
#       -> Strong Sell
#   numberOfAnalystOpinions 參與評級的分析師數量
#   debtToEquity 負債比
#   revenuePerShare 每股收益 = totalRevenue / sharesOutstanding
#   returnOnAssets 資產報酬率 = netIncomeToCommon / totalRevenue

# [Note] yfinance 的 ticker.financials 資料如下
#   dividendRate = 現金股利 (例如 2024 會抓到去年 2023 的 6.2 元)

for k, v in gb.info.items():
    if k == 'exDividendDate' or \
            k == 'lastFiscalYearEnd' or \
            k == 'nextFiscalYearEnd' or \
            k == 'mostRecentQuarter' or \
            k == 'lastSplitDate' or \
            k == 'lastDividendDate' or \
            k == 'firstTradeDateEpochUtc':
        exDivDate = datetime.datetime.fromtimestamp(v)
        info_text += f"{k}\t{v}\t ({exDivDate})\n"
    else:
        info_text += f"{k}\t{v}\n"

for k, v in gb.financials.items():
    financials_text += f"{k}\t{v}\n"

# output txt
file_name = f"{stock_id.replace('.', '_')}.{datetime.datetime.today().strftime('%Y%m%d')}.txt"

with open(file_name, "w") as file:
    file.write("=== Ticker Info ===\n")
    file.write(info_text)
    file.write("\n=== Financials ===\n")
    file.write(financials_text)

print("data saved: ", file_name)
