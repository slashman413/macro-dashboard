#!/usr/bin/env python3
"""
build.py — Fetches live data + builds a self-contained dashboard.html
with multilingual support (15 languages).
"""

from update_data import INDUSTRIES, fetch_industry_data
import json, time, os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load translations
with open(os.path.join(SCRIPT_DIR, "translations.json"), "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

LANGUAGES = TRANSLATIONS["_meta"]["languages"]
UI_STRINGS = TRANSLATIONS["ui"]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-TW" data-theme="dark">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{TITLE}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--font-sans:'Inter',system-ui,-apple-system,sans-serif;--font-mono:'JetBrains Mono',monospace;--radius-sm:8px;--radius-md:14px;--radius-lg:20px;--radius-xl:28px;--shadow-sm:0 1px 2px rgba(0,0,0,.06);--shadow-md:0 4px 16px rgba(0,0,0,.08);--shadow-lg:0 8px 40px rgba(0,0,0,.12);--shadow-xl:0 20px 60px rgba(0,0,0,.16);--transition:0.35s cubic-bezier(.22,1,.36,1);--ease-spring:cubic-bezier(.34,1.56,.64,1)}
html{font-family:var(--font-sans);background:var(--bg);color:var(--text);transition:background var(--transition),color var(--transition)}
body{min-height:100dvh;display:flex;flex-direction:column;padding:0 24px 40px;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent);color:#fff}::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--scrollbar);border-radius:3px}
[data-theme="dark"]{--bg:#080b12;--bg-secondary:#0e121f;--bg-tertiary:#141a2a;--card-bg:#1a2035;--card-border:#262d44;--card-border-hover:#3b4470;--card-glow:rgba(59,130,246,.08);--text:#e8edf5;--text-secondary:#8892b0;--text-tertiary:#5a6484;--accent:#4f8cff;--accent-glow:rgba(79,140,255,.15);--green:#34d399;--red:#f87171;--yellow:#fbbf24;--rank-1:#fbbf24;--rank-2:#94a3b8;--rank-3:#cd7f32;--modal-overlay:rgba(0,0,0,.7);--scrollbar:#262d44}
[data-theme="light"]{--bg:#f5f7fa;--bg-secondary:#eef1f6;--bg-tertiary:#e4e8f0;--card-bg:#ffffff;--card-border:#e2e6ef;--card-border-hover:#c8cfe0;--card-glow:rgba(59,123,239,.06);--text:#1a1d2e;--text-secondary:#5a6484;--text-tertiary:#98a2b8;--accent:#3b7bef;--accent-glow:rgba(59,123,239,.1);--green:#10b981;--red:#ef4444;--yellow:#f59e0b;--rank-1:#f59e0b;--rank-2:#6b7280;--rank-3:#b45309;--modal-overlay:rgba(0,0,0,.3);--scrollbar:#d1d5db}
.header{position:relative;z-index:1000;display:flex;justify-content:space-between;align-items:center;padding:28px 0 20px;max-width:1280px;width:100%;margin:0 auto;animation:fadeDown .6s var(--ease-spring) both;flex-wrap:wrap;gap:12px}
.header-left h1{font-size:1.65rem;font-weight:800;letter-spacing:-.03em;background:linear-gradient(135deg,var(--text),var(--text-secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.header-left .sub{font-size:.82rem;color:var(--text-tertiary);margin-top:4px;display:flex;align-items:center;gap:6px}
.header-left .sub .dot{width:6px;height:6px;border-radius:50%;background:var(--green);display:inline-block;animation:pulse 2s infinite}
.header-right{display:flex;align-items:center;gap:10px;flex-shrink:0}
.header-right .update-badge{font-size:.7rem;color:var(--text-tertiary);background:var(--bg-secondary);padding:6px 12px;border-radius:999px;border:1px solid var(--card-border);white-space:nowrap}
.lang-dropdown-backdrop{position:fixed;inset:0;z-index:999;display:none}
.lang-dropdown-backdrop.show{display:block}
.lang-selector{position:relative}
.lang-btn{display:flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;border:1px solid var(--card-border);background:var(--bg-secondary);color:var(--text-secondary);cursor:pointer;font-size:.8rem;font-family:var(--font-sans);transition:all var(--transition)}
.lang-btn:hover{border-color:var(--card-border-hover);color:var(--text)}
.lang-btn .arrow{font-size:.55rem;transition:transform .2s}
.lang-btn.open .arrow{transform:rotate(180deg)}
.lang-dropdown{position:absolute;top:calc(100%+6px);right:0;background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--radius-md);padding:6px;z-index:1001;min-width:200px;opacity:0;pointer-events:none;transform:translateY(-4px);transition:all .2s var(--ease-spring);box-shadow:var(--shadow-xl);-webkit-tap-highlight-color:transparent}
.lang-dropdown.show{opacity:1;pointer-events:auto;transform:translateY(0)}
.lang-option{display:flex;align-items:center;gap:8px;padding:10px 12px;border-radius:8px;cursor:pointer;font-size:.85rem;color:var(--text-secondary);transition:all .15s;border:none;background:none;width:100%;text-align:left;font-family:var(--font-sans);-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.lang-option:hover{background:var(--bg-secondary);color:var(--text)}
.lang-option.active{color:var(--accent);font-weight:600;background:var(--accent-glow)}
.lang-option .flag{font-size:1.2rem}
.theme-toggle{width:48px;height:28px;border-radius:999px;border:1px solid var(--card-border);background:var(--bg-secondary);cursor:pointer;position:relative;transition:all var(--transition);flex-shrink:0;display:flex;align-items:center;padding:4px}
.theme-toggle:hover{border-color:var(--card-border-hover)}.theme-toggle .knob{width:18px;height:18px;border-radius:50%;background:var(--accent);transition:transform var(--transition);position:absolute;left:4px;display:flex;align-items:center;justify-content:center}
[data-theme="light"] .theme-toggle .knob{transform:translateX(20px)}.theme-toggle .knob svg{width:10px;height:10px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round}
.dashboard{max-width:1280px;width:100%;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{position:relative;border-radius:var(--radius-lg);background:var(--card-bg);border:1px solid var(--card-border);padding:20px;cursor:pointer;transition:all var(--transition);animation:cardIn 0.7s var(--ease-spring) both;overflow:hidden;display:flex;flex-direction:column;min-height:200px}
.card::before{content:'';position:absolute;inset:0;background:radial-gradient(600px circle at var(--mx,50%) var(--my,50%),var(--card-glow),transparent 70%);opacity:0;transition:opacity .5s;pointer-events:none;z-index:0}
.card:hover::before{opacity:1}.card:hover{border-color:var(--card-border-hover);transform:translateY(-3px);box-shadow:var(--shadow-lg),0 0 40px var(--card-glow)}
.card:active{transform:translateY(-1px)}.card>*{position:relative;z-index:1}
.card.hero{grid-column:span 2;grid-row:span 2;min-height:360px;padding:28px}
.card.hero .rank-badge{font-size:4rem;font-weight:800;background:linear-gradient(135deg,var(--rank-1),rgba(251,191,36,.3));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1}
.card.hero .card-name{font-size:1.6rem;font-weight:700;margin-top:4px}.card.hero .card-name small{font-size:.8rem;font-weight:400;color:var(--text-tertiary);margin-left:8px}
.card.hero .card-desc{font-size:.88rem;color:var(--text-secondary);margin-top:6px;max-width:90%}
.card.hero .metrics-group{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.card.hero .hero-metric{background:var(--bg-secondary);border-radius:var(--radius-md);padding:12px 16px}
.card.hero .hero-metric .mlabel{font-size:.7rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.05em}
.card.hero .hero-metric .mvalue{font-size:1.3rem;font-weight:700;margin-top:2px}
.card.hero .hero-metric .msub{font-size:.7rem;color:var(--text-secondary);margin-top:2px}
.card.hero .news-strip{margin-top:auto;padding-top:14px;border-top:1px solid var(--card-border);display:flex;align-items:center;gap:8px;overflow:hidden}
.card.hero .news-strip .label{font-size:.68rem;color:var(--text-tertiary);white-space:nowrap;text-transform:uppercase;letter-spacing:.06em}
.card.hero .news-strip .news-text{font-size:.8rem;color:var(--text-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card.hero .news-strip .news-date{font-size:.68rem;color:var(--text-tertiary);white-space:nowrap}
.rank-badge{display:inline-flex;align-items:center;gap:6px;font-size:1.1rem;font-weight:700;margin-bottom:6px}
.rank-1 .rank-badge .num{color:var(--rank-1)}.rank-2 .rank-badge .num{color:var(--rank-2)}.rank-3 .rank-badge .num{color:var(--rank-3)}
.card .card-top{display:flex;justify-content:space-between;align-items:flex-start}
.card .card-name{font-size:1.05rem;font-weight:600;line-height:1.3}.card .card-name .ticker{font-size:.7rem;font-weight:500;color:var(--text-tertiary);font-family:var(--font-mono);margin-left:6px}
.card .card-desc{font-size:.78rem;color:var(--text-secondary);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:4px}
.card .return-badge{font-size:.75rem;font-weight:600;padding:4px 10px;border-radius:999px;font-family:var(--font-mono)}
.return-badge.pos{background:rgba(52,211,153,.12);color:var(--green)}.return-badge.neg{background:rgba(248,113,113,.12);color:var(--red)}
.card .metric-pills{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:auto;padding-top:14px}
.card .metric-pill{text-align:center}.card .metric-pill .pill-label{font-size:.62rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.04em}
.card .metric-pill .pill-value{font-size:.95rem;font-weight:700;margin-top:1px}
.mini-bar-wrap{display:flex;align-items:flex-end;gap:3px;height:32px;margin-top:8px;padding:0 2px}
.mini-bar{width:100%;border-radius:2px;min-height:4px;transition:height .8s var(--ease-spring);background:linear-gradient(to top,var(--bar-color,#4f8cff),var(--bar-color-light,#4f8cff));opacity:.8}
.card .click-hint{position:absolute;bottom:12px;right:14px;font-size:.62rem;color:var(--text-tertiary);opacity:0;transition:opacity var(--transition)}
.card:hover .click-hint{opacity:1}
.modal-overlay{position:fixed;inset:0;z-index:1000;background:var(--modal-overlay);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .4s;padding:20px}
.modal-overlay.active{opacity:1;pointer-events:all}.modal-overlay.active .modal-content{transform:scale(1) translateY(0);opacity:1}
.modal-content{background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--radius-xl);max-width:800px;width:100%;max-height:85vh;overflow-y:auto;padding:32px;transform:scale(.95) translateY(20px);opacity:0;transition:all .4s var(--ease-spring)}
.modal-content::-webkit-scrollbar{width:4px}.modal-content::-webkit-scrollbar-thumb{background:var(--scrollbar);border-radius:2px}
.modal-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px}
.modal-header h2{font-size:1.3rem;font-weight:700}.modal-header h2 small{font-size:.75rem;font-weight:400;color:var(--text-tertiary);margin-left:8px}
.modal-close{width:32px;height:32px;border-radius:50%;border:1px solid var(--card-border);background:var(--bg-secondary);color:var(--text-secondary);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1rem;transition:all var(--transition);flex-shrink:0}
.modal-close:hover{background:var(--card-border-hover);color:var(--text)}
.modal-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.modal-summary .ms-item{background:var(--bg-secondary);border-radius:var(--radius-md);padding:10px 14px;text-align:center}
.modal-summary .ms-item .ms-label{font-size:.65rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.04em}
.modal-summary .ms-item .ms-value{font-size:1.1rem;font-weight:700;margin-top:2px}
.company-table{width:100%;border-collapse:collapse}
.company-table th{text-align:left;padding:8px 12px;font-size:.68rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.05em;font-weight:600;border-bottom:1px solid var(--card-border)}
.company-table td{padding:10px 12px;font-size:.82rem;border-bottom:1px solid var(--card-border);transition:background var(--transition)}
.company-table tr:hover td{background:var(--bg-secondary)}
.company-table .ticker-cell{font-family:var(--font-mono);font-weight:600;color:var(--accent);font-size:.78rem}
.company-table .ticker-link{color:var(--accent);text-decoration:none;transition:opacity var(--transition)}
.company-table .ticker-link:hover{opacity:.7;text-decoration:underline}
.company-table .name-cell{font-weight:500}
.company-table .num-cell{text-align:right;font-family:var(--font-mono);font-size:.78rem}
.company-table .change-cell{text-align:right;font-family:var(--font-mono);font-size:.78rem;font-weight:600}
.change-up{color:var(--green)}.change-down{color:var(--red)}
@keyframes fadeDown{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
@keyframes cardIn{from{opacity:0;transform:translateY(30px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@media(max-width:1024px){.dashboard{grid-template-columns:repeat(2,1fr);gap:14px}.card.hero{grid-column:span 2}}
@media(max-width:640px){.dashboard{grid-template-columns:1fr;gap:12px}.card.hero{grid-column:1;grid-row:auto;min-height:auto}.card.hero .metrics-group{grid-template-columns:1fr}.header{flex-direction:column;align-items:flex-start;gap:12px}.header-right{width:100%;justify-content:flex-start;flex-wrap:wrap}}
</style>
</head>
<body>
<header class="header">
  <div class="header-left">
    <h1 id="headerTitle">📊 {{TITLE}}</h1>
    <div class="sub"><span class="dot"></span><span id="liveLabel">{{TRACKING}}</span></div>
  </div>
  <div class="header-right">
    <span class="update-badge" id="updateBadge">{{UPDATED_SHORT}}</span>
    <div class="lang-selector" id="langSelector">
      <button class="lang-btn" id="langBtn">{{LANG_BTN}} <span class="arrow">▾</span></button>
      <div class="lang-dropdown" id="langDropdown">{{LANG_OPTIONS}}</div>
    </div>
    <button class="theme-toggle" id="themeToggle" aria-label="{{TOGGLE_THEME}}">
      <span class="knob"><svg viewBox="0 0 24 24"><path d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M7.05 16.95l-1.414 1.414M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></span>
    </button>
  </div>
</header>

<div class="lang-dropdown-backdrop" id="langBackdrop"></div>

<div class="dashboard" id="dashboard"></div>

<div class="bottom-bar" style="max-width:1280px;width:100%;margin:24px auto 0;display:flex;justify-content:space-between;align-items:center;padding-top:16px;border-top:1px solid var(--card-border);font-size:.75rem;color:var(--text-tertiary)">
  <span id="dataSource">{{DATA_SOURCE}}</span>
  <div class="legend" style="display:flex;gap:16px">
    <span><span class="swatch" style="width:8px;height:8px;border-radius:2px;display:inline-block;background:var(--green)"></span> <span id="legRev">{{LEG_REV}}</span></span>
    <span><span class="swatch" style="width:8px;height:8px;border-radius:2px;display:inline-block;background:var(--accent)"></span> <span id="legPe">{{LEG_PE}}</span></span>
    <span><span class="swatch" style="width:8px;height:8px;border-radius:2px;display:inline-block;background:var(--yellow)"></span> <span id="legMargin">{{LEG_MARGIN}}</span></span>
  </div>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal-content" id="modalContent">
    <div class="modal-header">
      <h2><span id="modalTitle">{{DEFAULT_INDUSTRY}}</span> <small id="modalEtf"></small></h2>
      <button class="modal-close" id="modalClose">✕</button>
    </div>
    <div class="modal-summary" id="modalSummary"></div>
    <table class="company-table">
      <thead><tr>
        <th>#</th><th id="thTicker">{{TH_TICKER}}</th><th id="thName">{{TH_NAME}}</th>
        <th id="thCap" class="num-cell-header">{{TH_CAP}}</th><th id="thPe" class="num-cell-header">{{TH_PE}}</th>
        <th id="thRev" class="num-cell-header">{{TH_REV}}</th><th id="thPrice" class="num-cell-header">{{TH_PRICE}}</th>
        <th id="thChange" class="num-cell-header">{{TH_CHANGE}}</th>
      </tr></thead>
      <tbody id="modalBody"></tbody>
    </table>
  </div>
</div>

<script>
// ═══ Embedded data ═══
const DATA = {{JSON}};
const L10N = {{L10N_JSON}};
const IND_LANGS = {{IND_LANG_JSON}};

let currentLang = localStorage.getItem('lang') || 'zh-TW';
let industries = DATA.industries;

// ═══ Utilities ═══
function t(key){return L10N[key]?.[currentLang]||L10N[key]?.['en']||key}
function indName(ind){return ind['name_'+currentLang.replace('-','_')]||ind.name}
function indDesc(ind){return ind['desc_'+currentLang.replace('-','_')]||ind.desc}

function fmtLarge(n){if(!n)return'—';if(n>=1e12)return(n/1e12).toFixed(2)+'T';if(n>=1e9)return(n/1e9).toFixed(2)+'B';if(n>=1e6)return(n/1e6).toFixed(1)+'M';return n.toLocaleString()}
function fmtPct(n){if(n==null)return'—';const v=n<1&&n>-1?n*100:n;return(v>0?'+':'')+v.toFixed(1)+'%'}
function medalIcon(r){if(r===1)return'🥇';if(r===2)return'🥈';if(r===3)return'🥉';return''}
function timeAgo(s){if(!s)return'';const d=new Date(s);const diff=(Date.now()-d)/1000;if(diff<60)return t('just_now');if(diff<3600)return Math.floor(diff/60)+t('min_ago');if(diff<86400)return Math.floor(diff/3600)+t('hours_ago');return Math.floor(diff/86400)+t('days_ago')}
function genBars(val){if(!val||val<=0)return[10,15,12,18,20];const b=[];for(let i=0;i<4;i++)b.push(Math.round(val*(0.3+Math.random()*0.6)*10)/10);b.push(val);const m=Math.max(...b,1);return b.map(v=>Math.round(v/m*100))}
function animateValue(el,start,end,duration=800){end??=0;const t0=performance.now();(function fn(nw){const t=Math.min((nw-t0)/duration,1);const e=1-Math.pow(1-t,3);const v=start+(end-start)*e;el.textContent=end>100?Math.round(v).toLocaleString():v.toFixed(1);if(t<1)requestAnimationFrame(fn)})(t0)}

// ═══ Language Switching ═══
function applyLang(){
  // Update HTML lang attribute
  document.documentElement.lang = currentLang;

  // Update header
  document.getElementById('headerTitle').textContent = '📊 '+t('title');
  document.getElementById('liveLabel').textContent = t('tracking').replace('{total}',industries.length);

  // Update data source
  document.getElementById('dataSource').textContent = '📡 '+t('data_source')+': Yahoo Finance (yfinance)';

  // Update legend
  document.getElementById('legRev').textContent = t('revenue_growth');
  document.getElementById('legPe').textContent = t('pe_ratio');
  document.getElementById('legMargin').textContent = t('profit_margin');

  // Update table headers
  document.getElementById('thTicker').textContent = t('ticker');
  document.getElementById('thName').textContent = t('company_name');
  document.getElementById('thCap').textContent = t('market_cap');
  document.getElementById('thPe').textContent = t('pe_ratio');
  document.getElementById('thRev').textContent = t('revenue_growth');
  document.getElementById('thPrice').textContent = t('price');
  document.getElementById('thChange').textContent = t('change_pct');

  // Update all cards (re-render)
  renderCards();
}

// ═══ Render Cards ═══
function renderCards(){
  const dash = document.getElementById('dashboard');
  dash.innerHTML = '';

  industries.forEach((d,i)=>{
    const isHero = d.rank===1;
    const card = document.createElement('div');
    card.className = 'card'+(isHero?' hero':'')+' rank-'+d.rank;
    card.style.animationDelay = (i*0.08)+'s';
    
    const ret = d.returns?.['3m'];
    const retCls = ret>0?'pos':'neg';
    const retLabel = ret!=null?fmtPct(ret):'—';
    const bars = genBars(d.metrics?.revenue_growth||d.metrics?.pe_ratio||50);
    const bc = ['#4f8cff','#34d399','#fbbf24'];

    const nameTranslated = indName(d);
    const descTranslated = indDesc(d);
    const etf = d.etf;
    const ticker = d.bellwether;
    const revGrowth = d.metrics?.revenue_growth;
    const pe = d.metrics?.pe_ratio;
    const margin = d.metrics?.profit_margin;

    if(isHero){
      card.innerHTML = `
        <div class="rank-badge"><span class="num">#${d.rank}</span><span class="medal">🥇</span></div>
        <div class="card-name">${nameTranslated} <small>${etf} · ${d.name_en}</small></div>
        <div class="card-desc">${descTranslated}</div>
        <div class="metrics-group">
          <div class="hero-metric"><div class="mlabel">📈 ${t('revenue_growth')}</div><div class="mvalue" data-count="${revGrowth??0}">—</div><div class="msub">${t('bellwether')} ${ticker}</div></div>
          <div class="hero-metric"><div class="mlabel">💹 ${t('pe_ratio')}</div><div class="mvalue" data-count="${pe??0}">—</div><div class="msub">${t('etf_weighted_avg')}</div></div>
          <div class="hero-metric"><div class="mlabel">🏆 ${t('profit_margin')}</div><div class="mvalue" data-count="${margin??0}">—</div><div class="msub">${ticker} ${t('ttm')}</div></div>
        </div>
        <div class="mini-bar-wrap">${bars.map(b=>'<div class="mini-bar" style="height:'+b+'%;--bar-color:'+bc[0]+';--bar-color-light:'+bc[0]+'"></div>').join('')}</div>
        <div class="news-strip"><span class="label">📰 ${t('news_latest')}</span><span class="news-text">${d.news?.[0]?.title||t('no_news')}</span><span class="news-date">${d.news?.[0]?.time?timeAgo(d.news[0].time):''}</span></div>
        <span class="click-hint">${t('click_hint')} →</span>`;
    } else {
      card.innerHTML = `
        <div class="card-top"><div class="rank-badge"><span class="num">#${d.rank}</span>${medalIcon(d.rank)?'<span class="medal">'+medalIcon(d.rank)+'</span>':''}</div><span class="return-badge ${retCls}">${retLabel}</span></div>
        <div class="card-name">${nameTranslated} <span class="ticker">${etf}</span></div>
        <div class="card-desc">${descTranslated}</div>
        <div class="mini-bar-wrap">${bars.map((b,j)=>'<div class="mini-bar" style="height:'+b+'%;--bar-color:'+bc[j%3]+';--bar-color-light:'+bc[j%3]+'"></div>').join('')}</div>
        <div class="metric-pills">
          <div class="metric-pill"><div class="pill-label">${t('revenue_growth')}</div><div class="pill-value" style="color:var(--green)" data-count="${revGrowth??0}">—</div></div>
          <div class="metric-pill"><div class="pill-label">${t('pe_ratio')}</div><div class="pill-value" style="color:var(--accent)" data-count="${pe??0}">—</div></div>
          <div class="metric-pill"><div class="pill-label">${t('profit_margin')}</div><div class="pill-value" style="color:var(--yellow)" data-count="${margin??0}">—</div></div>
        </div>
        <span class="click-hint">${t('click_hint')} →</span>`;
    }

    card.addEventListener('click',()=>{
      const mTitle=document.getElementById('modalTitle'),mEtf=document.getElementById('modalEtf');
      const mSummary=document.getElementById('modalSummary'),mBody=document.getElementById('modalBody');
      mTitle.textContent=d.rank+'. '+indName(d);
      mEtf.textContent=d.etf+' · '+d.name_en;
      mSummary.innerHTML=
        '<div class="ms-item"><div class="ms-label">📈 '+t('revenue_growth')+'</div><div class="ms-value" style="color:var(--green)">'+(revGrowth!=null?revGrowth+'%':'—')+'</div><div class="ms-sub">'+t('bellwether')+' '+ticker+'</div></div>'+
        '<div class="ms-item"><div class="ms-label">💹 '+t('pe_ratio')+'</div><div class="ms-value" style="color:var(--accent)">'+(pe!=null?pe.toFixed(1)+'x':'—')+'</div><div class="ms-sub">ETF '+etf+'</div></div>'+
        '<div class="ms-item"><div class="ms-label">🏆 '+t('profit_margin')+'</div><div class="ms-value" style="color:var(--yellow)">'+(margin!=null?margin+'%':'—')+'</div></div>'+
        '<div class="ms-item"><div class="ms-label">📊 '+t('return_3m')+'</div><div class="ms-value" style="color:'+((ret||0)>0?'var(--green)':'var(--red)')+'">'+(ret!=null?fmtPct(ret):'—')+'</div></div>';
      mBody.innerHTML=d.top_companies.map((c,i)=>'<tr><td>'+(i+1)+'</td><td class="ticker-cell"><a href="https://finance.yahoo.com/quote/'+c.ticker+'" target="_blank" rel="noopener" class="ticker-link">'+c.ticker+'</a></td><td class="name-cell">'+c.name+'</td><td class="num-cell">'+fmtLarge(c.market_cap)+'</td><td class="num-cell">'+(c.pe!=null?c.pe.toFixed(1)+'x':'—')+'</td><td class="num-cell">'+(c.revenue_growth!=null?c.revenue_growth+'%':'—')+'</td><td class="num-cell">'+(c.price!=null?'$'+c.price.toFixed(2):'—')+'</td><td class="change-cell '+((c.change_pct||0)>0?'change-up':'change-down')+'">'+(c.change_pct!=null?fmtPct(c.change_pct):'—')+'</td></tr>').join('');
      document.getElementById('modalOverlay').classList.add('active');
      document.body.style.overflow='hidden';
    });
    dash.appendChild(card);
  });

  // Animate numbers
  requestAnimationFrame(()=>{
    document.querySelectorAll('[data-count]').forEach(el=>{const v=parseFloat(el.dataset.count);if(!isNaN(v))animateValue(el,0,v,800)});
  });
  requestAnimationFrame(()=>{
    document.querySelectorAll('.mini-bar').forEach((b,i)=>{setTimeout(()=>b.style.height=b.style.height||'90%',i*20)});
  });
}

// ═══ Init ═══
(function(){
  // Theme toggle
  const html=document.documentElement;
  const stored=localStorage.getItem('theme');
  if(stored)html.setAttribute('data-theme',stored);
  document.getElementById('themeToggle').addEventListener('click',()=>{
    const n=html.getAttribute('data-theme')==='dark'?'light':'dark';
    html.setAttribute('data-theme',n);
    localStorage.setItem('theme',n);
  });

  // Language selector
  const langBtn=document.getElementById('langBtn');
  const langDropdown=document.getElementById('langDropdown');
  
  // Build language options from embedded language data
  const LANG_LIST = {{LANG_LIST_JSON}};
  
  function renderLangBtn(){
    const curr = LANG_LIST.find(l=>l.code===currentLang)||LANG_LIST[0];
    langBtn.innerHTML = curr.flag+' '+curr.name+' <span class="arrow">▾</span>';
  }
  
  function renderLangDropdown(){
    langDropdown.innerHTML = LANG_LIST.map(l=>
      '<button class="lang-option'+(l.code===currentLang?' active':'')+'" data-lang="'+l.code+'"><span class="flag">'+l.flag+'</span> '+l.name+'</button>'
    ).join('');
    
    langDropdown.querySelectorAll('.lang-option').forEach(btn=>{
      btn.addEventListener('click',(e)=>{
        e.stopPropagation();
        currentLang = btn.dataset.lang;
        localStorage.setItem('lang',currentLang);
        renderLangBtn();
        renderLangDropdown();
        applyLang();
        langDropdown.classList.remove('show');
        langBtn.classList.remove('open');
        document.getElementById('langBackdrop').classList.remove('show');
      });
    });
  }
  
  renderLangBtn();
  renderLangDropdown();
  
  langBtn.addEventListener('click',(e)=>{
    e.stopPropagation();
    const open = !langDropdown.classList.contains('show');
    langDropdown.classList.toggle('show');
    langBtn.classList.toggle('open');
    document.getElementById('langBackdrop').classList.toggle('show', open);
  });
  document.getElementById('langBackdrop').addEventListener('click',()=>{
    langDropdown.classList.remove('show');
    langBtn.classList.remove('open');
    document.getElementById('langBackdrop').classList.remove('show');
  });
  document.addEventListener('click',e=>{
    if(!e.target.closest('.lang-selector')){
      langDropdown.classList.remove('show');
      langBtn.classList.remove('open');
      document.getElementById('langBackdrop').classList.remove('show');
    }
  });

  // Modal close
  document.getElementById('modalClose').addEventListener('click',()=>{document.getElementById('modalOverlay').classList.remove('active');document.body.style.overflow=''});
  document.getElementById('modalOverlay').addEventListener('click',e=>{if(e.target===document.getElementById('modalOverlay')){document.getElementById('modalOverlay').classList.remove('active');document.body.style.overflow=''}});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.getElementById('modalOverlay').classList.remove('active');document.body.style.overflow=''}});

  // Mouse follower
  document.getElementById('dashboard').addEventListener('mousemove',e=>{const c=e.target.closest('.card');if(!c)return;const r=c.getBoundingClientRect();c.style.setProperty('--mx',((e.clientX-r.left)/r.width*100)+'%');c.style.setProperty('--my',((e.clientY-r.top)/r.height*100)+'%')});

  // Apply initial language
  applyLang();
})();
</script>
<div style="text-align:center;padding:18px;font-size:12px;color:#94a3b8"><div class="reco-widget" data-cat="finance"></div><script src="https://slashmantools.us/reco-widget.js" defer></script><a href="https://ko-fi.com/ytstories0413" target="_blank" rel="noopener" style="color:#ff5e5b;text-decoration:none">☕ 支持我們 Support · Ko-fi</a></div>  <script src="https://slashmantools.us/kofi-widget.js" defer></script>
</body>
</html>"""

TR_KEY = {
    "TITLE": "title",
    "TRACKING": ("tracking", {"total": len(INDUSTRIES)}),
    "TOGGLE_THEME": "toggle_theme",
    "DATA_SOURCE": "data_source",
    "LEG_REV": "revenue_growth",
    "LEG_PE": "pe_ratio",
    "LEG_MARGIN": "profit_margin",
    "TH_TICKER": "ticker",
    "TH_NAME": "company_name",
    "TH_CAP": "market_cap",
    "TH_PE": "pe_ratio",
    "TH_REV": "revenue_growth",
    "TH_PRICE": "price",
    "TH_CHANGE": "change_pct",
    "DEFAULT_INDUSTRY": "industry",
}

def main():
    print("🔄 Fetching industry data...")
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
                "returns": {}, "hot_score": 0, "news": [],
                "top_companies": [],
            })
        time.sleep(0.3)

    # Sort and rank
    results.sort(key=lambda x: x["hot_score"] or 0, reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    top10 = [r for r in results if r["rank"] <= 10]

    # Load industries.json for multilingual names
    ind_json_path = os.path.join(SCRIPT_DIR, "industries.json")
    with open(ind_json_path, "r", encoding="utf-8") as f:
        ind_translations = json.load(f)
    
    # Create lookup by ETF ticker
    ind_lookup = {ind["etf"]: ind for ind in ind_translations}

    # Merge multilingual fields into top10
    for r in top10:
        etf = r["etf"]
        if etf in ind_lookup:
            ext = ind_lookup[etf]
            for k, v in ext.items():
                if k.startswith("name_") or k.startswith("desc_"):
                    r[k] = v

    # Build language list JSON for the HTML
    lang_list = LANGUAGES
    
    # Build L10N flat dict for JS
    l10n_flat = {}
    for key, values in UI_STRINGS.items():
        l10n_flat[key] = values

    now = datetime.now(timezone.utc)
    updated_short = now.strftime('%m/%d %H:%M')

    json_str = json.dumps({"industries": top10}, ensure_ascii=False)
    l10n_json = json.dumps(l10n_flat, ensure_ascii=False)
    ind_lang_json = json.dumps(ind_lookup, ensure_ascii=False)
    lang_list_json = json.dumps(lang_list, ensure_ascii=False)

    # Default (zh-TW) values for template
    def tv(key):
        v = UI_STRINGS.get(key, {})
        return v.get("zh-TW", v.get("en", key))

    def replace_tracking(s):
        return s.replace("{total}", str(len(top10)))

    lang_btn = "🇹🇼 繁體中文"
    lang_opts = "".join(
        f'<button class="lang-option{" active" if l["code"]=="zh-TW" else ""}" data-lang="{l["code"]}">'
        f'<span class="flag">{l["flag"]}</span> {l["name"]}</button>'
        for l in lang_list
    )

    html = (TEMPLATE
        .replace("{{TITLE}}", tv("title"))
        .replace("{{TRACKING}}", replace_tracking(tv("tracking")))
        .replace("{{UPDATED_SHORT}}", "🔄 " + updated_short)
        .replace("{{TOGGLE_THEME}}", tv("toggle_theme"))
        .replace("{{DATA_SOURCE}}", "📡 "+tv("data_source")+": Yahoo Finance (yfinance)")
        .replace("{{LEG_REV}}", tv("revenue_growth"))
        .replace("{{LEG_PE}}", tv("pe_ratio"))
        .replace("{{LEG_MARGIN}}", tv("profit_margin"))
        .replace("{{TH_TICKER}}", tv("ticker"))
        .replace("{{TH_NAME}}", tv("company_name"))
        .replace("{{TH_CAP}}", tv("market_cap"))
        .replace("{{TH_PE}}", tv("pe_ratio"))
        .replace("{{TH_REV}}", tv("revenue_growth"))
        .replace("{{TH_PRICE}}", tv("price"))
        .replace("{{TH_CHANGE}}", tv("change_pct"))
        .replace("{{DEFAULT_INDUSTRY}}", tv("industry"))
        .replace("{{LANG_BTN}}", lang_btn)
        .replace("{{LANG_OPTIONS}}", lang_opts)
        .replace("{{JSON}}", json_str)
        .replace("{{L10N_JSON}}", l10n_json)
        .replace("{{IND_LANG_JSON}}", ind_lang_json)
        .replace("{{LANG_LIST_JSON}}", lang_list_json)
    )

    out_path = os.path.join(SCRIPT_DIR, "dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ dashboard.html 已產生！（{len(html):,} bytes）")
    for r in top10:
        print(f"  #{r['rank']} {r['name']} ({r['etf']}) — 3m: {r['returns'].get('3m', 'N/A')}%")
    print(f"\n🌐 支援 {len(lang_list)} 種語言")


if __name__ == "__main__":
    main()
