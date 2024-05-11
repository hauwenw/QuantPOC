import os
import yfinance as yf
import datetime
import twstock
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_stock_info(stock_id, folder_name):
    logger.info(f"Collecting {stock_id}")

    start_time = time.time()

    try:
        gb = yf.Ticker(stock_id)

        info_text = ""
        financials_text = ""

        for k,v in gb.info.items():
            if k in ['exDividendDate', 'lastFiscalYearEnd', 'nextFiscalYearEnd', 'mostRecentQuarter', 'lastSplitDate', 'lastDividendDate', 'firstTradeDateEpochUtc']:
                exDivDate = datetime.datetime.fromtimestamp(v)
                info_text += f"{k}\t{v}\t ({exDivDate})\n"
            else:
                info_text += f"{k}\t{v}\n"

        financials_text = gb.financials.to_string()

        # Create the directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = f"{stock_id.replace('.', '_')}.{datetime.datetime.today().strftime('%Y%m%d')}.txt"
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, "w") as file:
            file.write("=== Ticker Info ===\n")
            file.write(info_text)
            file.write("\n=== Financials ===\n")
            file.write(financials_text)

    except Exception as e:
        logger.error(f"Failed to collect data for {stock_id}: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Time taken for {stock_id}: {elapsed_time:.2f} seconds")

def main():
    markets = ['上市']
    types = ['股票']
    targets = [c for c in twstock.codes if twstock.codes[c].market in markets and twstock.codes[c].type in types]

    # Create the folder name based on the current date and time
    folder_name = os.path.join("ticker_history_data", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    total_start_time = time.time()

    for target in targets:
        stock_id = f"{target}.tw"
        fetch_stock_info(stock_id, folder_name)
        time.sleep(1)  # Add a sleep to avoid overwhelming the server with requests

    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time
    logger.info(f"Total time taken: {total_elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
