#!/usr/bin/env python3
"""
update_data.py — Fetch real macroeconomic industry data via yfinance
Outputs data.json for the Bento Grid dashboard.

Industry definitions loaded from industries.json (maintained by update_industries.py).
"""

import yfinance as yf
import json
import time
import os
from datetime import datetime, timezone

# ── Load industry definitions from JSON ──
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_INDUSTRIES_PATH = os.path.join(_SCRIPT_DIR, "industries.json")

with open(_INDUSTRIES_PATH, "r", encoding="utf-8") as _f:
    _json_data = json.load(_f)

# Convert to the internal format expected by fetch_industry_data
# JSON format: companies = [{ticker, name, weight_pct}, ...]
# Internal format: companies = [(ticker, name), ...]
INDUSTRIES = []
for entry in _json_data:
    companies = entry.get("companies")
    if companies:
        companies_tuples = [(c["ticker"], c["name"]) for c in companies]
    else:
        # Fallback: just the bellwether ticker
        companies_tuples = [(entry["ticker"], entry["ticker"])]

    INDUSTRIES.append({
        "etf": entry["etf"],
        "ticker": entry["ticker"],
        "name": entry["name"],
        "name_en": entry["name_en"],
        "desc": entry["desc"],
        "companies": companies_tuples,
    })

# ── Helpers ────────────────────────────────────────────────────────────

def safe_get(info, keys, default="N/A"):
    for k in keys:
        v = info.get(k)
        if v is not None:
            return v
    return default

def fetch_industry_data(ind):
    """Fetch all data for one industry."""
    etf_ticker = ind["etf"]
    stock_ticker = ind["ticker"]
    slug = ind["name_en"].lower().replace(" & ", "-").replace(" ", "-")
    
    try:
        etf = yf.Ticker(etf_ticker)
        etf_info = etf.info
    except Exception:
        etf_info = {}
    
    try:
        stock = yf.Ticker(stock_ticker)
        stock_info = stock.info
    except Exception:
        stock_info = {}
    
    # ── ETF-level metrics ──
    pe = safe_get(etf_info, ["trailingPE", "forwardPE"])
    assets = safe_get(etf_info, ["totalAssets"], 0)
    etf_name = safe_get(etf_info, ["shortName", "longName"], etf_ticker)
    
    # ── Returns ──
    returns = {}
    for period, label in [("1mo", "1m"), ("3mo", "3m"), ("6mo", "6m"), ("1y", "1y")]:
        try:
            hist = etf.history(period=period)
            if len(hist) >= 2:
                ret = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
                returns[label] = round(ret, 1)
            else:
                returns[label] = None
        except Exception:
            returns[label] = None
    
    # ── Bellwether stock fundamentals ──
    rev_growth = safe_get(stock_info, ["revenueGrowth"])
    profit_margin = safe_get(stock_info, ["profitMargins"])
    mkt_cap = safe_get(stock_info, ["marketCap"], 0)
    
    if isinstance(rev_growth, (int, float)):
        rev_growth = round(rev_growth * 100, 1)
    if isinstance(profit_margin, (int, float)):
        profit_margin = round(profit_margin * 100, 1)
    
    # ── Top companies data ──
    companies_data = []
    for ticker, cname in ind["companies"]:
        try:
            t = yf.Ticker(ticker)
            ti = t.info
            mc = ti.get("marketCap", 0)
            companies_data.append({
                "ticker": ticker,
                "name": ti.get("shortName", ti.get("longName", cname)),
                "market_cap": mc,
                "pe": ti.get("trailingPE"),
                "revenue_growth": round(ti.get("revenueGrowth", 0) * 100, 1) if ti.get("revenueGrowth") else None,
                "price": ti.get("currentPrice", ti.get("regularMarketPrice")),
                "change_pct": ti.get("regularMarketChangePercent"),
            })
        except Exception:
            companies_data.append({
                "ticker": ticker, "name": cname,
                "market_cap": None, "pe": None,
                "revenue_growth": None, "price": None, "change_pct": None,
            })
        time.sleep(0.1)  # rate limit safety
    
    # Sort by market cap descending
    companies_data.sort(key=lambda x: x["market_cap"] or 0, reverse=True)
    
    # ── News ──
    news_data = []
    try:
        news = stock.news
        for article in news[:5]:
            c = article.get("content", {})
            url = c.get("clickThroughUrl")
            if isinstance(url, dict):
                url = url.get("url", "")
            news_data.append({
                "title": c.get("title", ""),
                "url": url or "",
                "source": c.get("provider", {}).get("displayName", ""),
                "time": c.get("pubDate", ""),
            })
    except Exception:
        pass
    
    return {
        "rank": 0,  # will be set after sorting
        "slug": slug,
        "name": ind["name"],
        "name_en": ind["name_en"],
        "description": ind["desc"],
        "etf": etf_ticker,
        "etf_name": etf_name,
        "bellwether": stock_ticker,
        "metrics": {
            "pe_ratio": round(pe, 1) if isinstance(pe, (int, float)) else None,
            "revenue_growth": rev_growth if isinstance(rev_growth, (int, float)) else None,
            "profit_margin": profit_margin if isinstance(profit_margin, (int, float)) else None,
            "total_assets": int(assets) if assets else None,
        },
        "returns": returns,
        "hot_score": returns.get("3m") or returns.get("6m") or 0,
        "news": news_data,
        "top_companies": companies_data,
    }


def main():
    print(f"🔄 Fetching data for {len(INDUSTRIES)} industries...")
    
    results = []
    for i, ind in enumerate(INDUSTRIES):
        print(f"  [{i+1}/{len(INDUSTRIES)}] {ind['name']} ({ind['etf']})...")
        try:
            data = fetch_industry_data(ind)
            results.append(data)
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            results.append({
                "rank": 0, "slug": ind["name_en"].lower().replace(" ", "-"),
                "name": ind["name"], "name_en": ind["name_en"],
                "description": ind["desc"],
                "etf": ind["etf"], "etf_name": ind["etf"],
                "bellwether": ind["ticker"],
                "metrics": {"pe_ratio": None, "revenue_growth": None,
                            "profit_margin": None, "total_assets": None},
                "returns": {}, "hot_score": 0,
                "news": [],
                "top_companies": [{"ticker": t, "name": n, "market_cap": None,
                                    "pe": None, "revenue_growth": None,
                                    "price": None, "change_pct": None}
                                   for t, n in ind["companies"]],
            })
        time.sleep(0.3)
    
    # Rank by hot_score (3-month return, descending)
    results.sort(key=lambda x: x["hot_score"] or 0, reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    
    # Keep only top 10
    top10 = [r for r in results if r["rank"] <= 10]
    
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_tracked": len(INDUSTRIES),
        "industries": top10,
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Done! data.json written with {len(top10)} industries.")
    for r in top10:
        print(f"  #{r['rank']} {r['name']} ({r['etf']}) — 3m: {r['returns'].get('3m', 'N/A')}%")


if __name__ == "__main__":
    main()
