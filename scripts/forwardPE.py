import yfinance as yf
import twstock
import datetime
 



info_text = ""

markets = ['上市']  # '上市', '上櫃'

types = ['股票']  # '特別股', 'ETF', '臺灣存託憑證(TDR)', '上市認購(售)權證', '受益證券-不動產投資信託', '股票'

targets = [c for c in twstock.codes if twstock.codes[c].market in markets and twstock.codes[c].type in types]

for target in targets:
    stock_id = f"{target}.tw"
    gb = yf.Ticker(stock_id)

    
    for k, v in gb.info.items():
        if k == 'forwardEps':
            info_text += f"{target}\t{k}\t{v}\n"
        if k == 'forwardPE':
            info_text += f"{k}\t{v}\n"

# output txt
file_name = f"{'forwardEPS and forwardPE for all tw stocks'}.{datetime.datetime.today().strftime('%Y%m%d')}.txt"

with open(file_name, "w") as file:
    file.write(info_text)
    

print("data saved: ", file_name)


