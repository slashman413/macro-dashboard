📊 總經產業熱度儀表板 Macro Dashboard
========================================

一個串接 Yahoo Finance 即時數據的產業熱度分析工具。

📁 檔案說明
-----------
dashboard.html       👉 主儀表板（自含式，直接雙擊開啟）
build.py            👉 一鍵建構：抓數據 + 產生 HTML
update_data.py      👉 獨立數據抓取腳本（產生 data.json）
data.json           👉 最新數據快取

🚀 快速使用
-----------
1. 雙擊 dashboard.html 用瀏覽器開啟
2. 右上角 ☀️/🌙 切換深淺色主題
3. 點擊卡片查看該產業前 10 大公司詳細資料

🔄 更新數據
-----------
終端機執行：
  python build.py

需要安裝 yfinance：
  pip install yfinance

📡 數據來源：Yahoo Finance (yfinance)
自動追蹤 14 個產業 ETF，依 3 個月報酬率排名前 10 大熱門產業。
