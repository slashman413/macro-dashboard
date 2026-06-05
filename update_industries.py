#!/usr/bin/env python3
"""
update_industries.py — 每週動態更新 industries.json

功能：
1. 從 Yahoo Finance 的 ETF 真實持股數據更新各產業的龍頭股與前 10 大公司
2. 自動取得每檔持股的標準公司名稱
3. 保留原 industries.json 中的中文名稱、描述等靜態資料

Usage:
    python update_industries.py
"""

import yfinance as yf
import json
import time
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "industries.json")
BACKUP_PATH = os.path.join(SCRIPT_DIR, "industries-backup.json")


def load_industries():
    """載入基礎 industries.json"""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_industries(data):
    """備份舊檔並寫入更新後的 industries.json"""
    if os.path.exists(JSON_PATH):
        import shutil
        shutil.copy2(JSON_PATH, BACKUP_PATH)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_holdings(etf_ticker, max_items=10):
    """從 yfinance ETF 取得前 N 大持股，回傳 list of dict"""
    try:
        t = yf.Ticker(etf_ticker)
        fd = t.funds_data
        if fd is None:
            return None
        th = fd.top_holdings
        if th is None or len(th) == 0:
            return None

        holdings = []
        for symbol, row in th.head(max_items).iterrows():
            pct = float(row.iloc[1]) if len(row) > 1 else 0.0  # Holding Percent
            # 公司名已內建在 top_holdings 中
            name = str(row.iloc[0]) if row.iloc[0] else _get_company_name(symbol)
            holdings.append({
                "ticker": symbol,
                "name": name[:40],
                "weight_pct": round(pct * 100, 2),
            })

        return holdings

    except Exception as e:
        print(f"    ⚠️  {etf_ticker} holdings error: {e}")
        return None


def _get_company_name(ticker):
    """嘗試取得公司全名，失敗就回傳 ticker"""
    try:
        info = yf.Ticker(ticker).info
        name = info.get("shortName") or info.get("longName")
        if name:
            # 截短過長的名稱
            return name[:40]
    except Exception:
        pass
    return ticker


def update_industry(entry):
    """更新一個產業：取得 ETF 持股，更新龍頭股與公司列表"""
    etf = entry["etf"]
    print(f"  {entry['name']} ({etf})...")

    # 1. 更新 ETF 全名（可忽略）
    try:
        info = yf.Ticker(etf).info
        etf_name = info.get("shortName") or info.get("longName")
        if etf_name:
            entry["etf_name"] = etf_name
    except Exception:
        pass

    # 2. 取得即時持股
    holdings = get_holdings(etf, max_items=10)
    if holdings is None:
        print(f"    ⚠️  無法取得持股，保留原資料")
        return entry

    # 3. 更新前 10 大公司列表（保留原龍頭股不變）
    entry["companies"] = []
    for h in holdings:
        entry["companies"].append({
            "ticker": h["ticker"],
            "name": h["name"],
            "weight_pct": h["weight_pct"],
        })

    # 4. 摘要輸出

    print(f"    ✅  龍頭: {holdings[0]['ticker']} ({holdings[0]['name']})")
    print(f"       持股: {' '.join(h['ticker'] for h in holdings[:5])}...")

    return entry


def main():
    print("=" * 50)
    print(f"🔄  每週產業數據更新器")
    print(f"    {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
    print("=" * 50)

    industries = load_industries()
    print(f"\n📂 載入 {len(industries)} 個產業定義")

    updated = []
    for i, entry in enumerate(industries):
        result = update_industry(entry)
        updated.append(result)
        time.sleep(0.5)  # rate limit 保護

    save_industries(updated)
    print(f"\n✅ industries.json 已更新！（備份: industries-backup.json）")

    # 摘要
    print(f"\n{'─' * 50}")
    print(f"📊 更新摘要：")
    max_name = max(len(e["name"]) for e in updated)
    for e in updated:
        ticker = e.get("ticker", "?")
        top = ""
        if e.get("companies"):
            top = " ".join(c["ticker"] for c in e["companies"][:3])
        print(f"  {e['name']:{max_name}}  →  {ticker}  |  {top}")


if __name__ == "__main__":
    main()
