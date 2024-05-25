import csv
from selenium import webdriver
from bs4 import BeautifulSoup

# 設定Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 無頭模式
options.add_argument('--disable-gpu')  # 關閉GPU加速
options.add_argument('--no-sandbox')  # 取消沙盒
options.add_argument('--disable-dev-shm-usage')  # 避免資源問題

# 下載ChromeDriver並指定其路徑，這裡假設chromedriver在系統PATH中
driver = webdriver.Chrome(options=options)

# 目標URL
url = 'https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID=2330'

# 使用Selenium獲取網頁內容
driver.get(url)
driver.implicitly_wait(10)  # 等待頁面加載完成

# 獲取頁面源代碼
page_source = driver.page_source

# 關閉瀏覽器
driver.quit()

# 解析HTML
soup = BeautifulSoup(page_source, 'html.parser')

# 查找目標表格
table = soup.find('table', class_='b1 p4_2 row_bg_2n row_mouse_over')

if table is None:
    print("未找到目標表格")
else:
    # 提取表格數據
    data = []
    for row in table.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)

    # 顯示提取的數據
    for row in data:
        print('\t'.join(row))

    # 保存到CSV文件
    with open('stock_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
