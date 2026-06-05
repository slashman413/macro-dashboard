# Macro Dashboard 📊

總經產業熱度儀表板 — 串接 Yahoo Finance 即時數據的產業熱度分析工具。

## 功能

- **14 個產業 ETF** 即時追蹤，依 3 個月報酬率排名
- 點擊卡片查看該產業前 10 大成分股詳細資料
- 🌙 深色/淺色主題切換
- 多語言支援（15 種語言）
- 總經危機事件時間軸

## 快速開始

### 方式一：直接開啟（免安裝）

雙擊 `dashboard.html` 用瀏覽器開啟即可。

### 方式二：更新數據

```bash
pip install yfinance
python build.py
```

重新整理 `dashboard.html` 即可看到最新數據。

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `dashboard.html` | 主儀表板（自含式，直接雙擊開啟） |
| `build.py` | 一鍵建構：抓數據 + 產生 HTML |
| `update_data.py` | 獨立數據抓取腳本（產生 data.json） |
| `data.json` | 最新數據快取 |
| `industries.json` | 產業定義與 ETF 對照 |
| `translations.json` | 多語言翻譯 |

## 技術棧

- **純前端** — 單一 HTML 檔案，零依賴
- **數據來源** — Yahoo Finance (yfinance)
- **圖表** — Chart.js（CDN）
- **圖示** — Font Awesome（CDN）

## 數據來源

自動追蹤以下 14 個產業 ETF，依 3 個月報酬率排名前 10 大熱門產業：

XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY, SMH, IBB, ARKK
