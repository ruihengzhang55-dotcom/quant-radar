import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from auth import (
    register_user, login_user, save_session, clear_session,
    current_user, is_logged_in, get_user_status
)

st.set_page_config(
    page_title="QuantGold · 量化挖金",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

LANG = {
    "zh": {
        "hero_title": "🥇 量化挖金 QuantGold · 全市场扫描",
        "hero_sub": "VSA量价异动 · 均线收敛 · 美股+A股 · 1-7日短线策略",
        "login_tab": "登录", "register_tab": "注册",
        "email": "邮箱", "password": "密码",
        "login_btn": "登录", "register_btn": "注册",
        "logout_btn": "退出登录",
        "login_success": "登录成功！",
        "register_success": "注册成功！已开启7天免费试用",
        "welcome": "你好，{email}",
        "status_paid": "✅ 已订阅会员",
        "status_trial": "⏳ 试用期剩余 {d} 天",
        "status_locked": "🔒 试用已到期",
        "upgrade_btn": "💳 立即订阅解锁全部功能",
        "upgrade_tip": "订阅后可解锁：全市场扫描（90+只）· 完整回测 · 数据导出",
        "paywall_title": "🔒 该功能需要订阅会员",
        "paywall_sub": "您的7天免费试用已结束",
        "paywall_free": "免费版可用：",
        "paywall_free_items": "• 每日扫描前5条信号预览\n• 查看信号类型（不含诊断详情）",
        "paywall_paid": "订阅后解锁：",
        "paywall_paid_items": "• 全市场500+只股票实时扫描\n• 完整量化诊断报告\n• 历史回测胜率数据\n• CSV数据导出",
        "paywall_price": "订阅价格：¥29/月 或 ¥199/年",
        "paywall_contact": "👉 联系微信：your_wechat_id 完成订阅",
        "sidebar_config": "⚙️ 扫描配置",
        "market_label": "选择市场",
        "pool_size": "股票池：{n} 只",
        "custom_label": "自定义股票代码（每行一个）",
        "filter_title": "🔍 信号过滤",
        "bt_title": "📊 回测参数",
        "bt_period_label": "回测周期",
        "bt_ticker_label": "回测标的",
        "bt_ticker_hint": "如 NVDA 或 600519.SS",
        "data_source": "数据：Yahoo Finance | 15分钟延迟",
        "tab_scan": "📡 实时扫描",
        "tab_bt": "🔬 策略回测",
        "tab_help": "📖 使用说明",
        "scan_btn": "🚀 开始扫描",
        "scan_est": "将扫描 {n} 只股票，预计 {t} 秒",
        "scanning": "正在分析 {t}... ({i}/{total})",
        "scan_error": "数据获取失败，请检查网络",
        "stat_scanned": "扫描完成", "stat_fire": "🔥 强启动",
        "stat_gold": "⏳ 黄金坑", "stat_warn": "⚠️ 弱势",
        "show_n": "显示 {n} 条结果",
        "no_filter": "无结果，请在左侧勾选更多信号类型",
        "preview_tip": "👆 试用版仅展示前5条，订阅后查看全部 {n} 条",
        "col_ticker": "代码", "col_price": "现价",
        "col_chg": "涨跌", "col_vol": "量比",
        "col_ma": "均线粘合", "col_status": "信号", "col_diag": "诊断",
        "export_btn": "⬇️ 导出CSV",
        "sig_fire": "🔥 右侧强启动", "sig_gold": "⏳ 黄金坑筑底",
        "sig_warn": "⚠️ 弱势下破", "sig_watch": "👀 观察中",
        "diag_fire": "突破+放量，主力资金介入，重点关注",
        "diag_gold": "均线高度收敛+缩量，蓄势待发",
        "diag_warn": "放量破位，规避", "diag_watch": "暂无明显信号",
        "market_us_large": "🏆 标普500全览", "market_us_small": "🚀 美股小盘活跃",
        "market_a": "🇨🇳 A股沪深精选", "market_mix": "🌏 美股+A股混合",
        "market_custom": "🔧 自定义",
        "bt_header": "🔬 单股历史信号回测",
        "bt_caption": "回放历史信号，统计胜率与收益",
        "bt_input_label": "股票代码", "bt_run_btn": "▶ 开始回测",
        "bt_spinning": "回测 {t} 中（{p}）...",
        "bt_no_signal": "未找到信号，请换标的或延长周期",
        "bt_count": "触发次数", "bt_wr5": "5日胜率", "bt_wr7": "7日胜率",
        "bt_avg5": "5日均收益", "bt_avg7": "7日均收益", "bt_maxdd": "最大亏损",
        "bt_detail": "#### 📋 信号明细",
        "bt_col_type": "类型", "bt_col_date": "日期",
        "bt_col_entry": "入场价", "bt_col_r5": "5日%", "bt_col_r7": "7日%",
        "bt_export": "⬇️ 导出回测", "bt_disclaimer": "⚠️ 历史回测不代表未来表现",
        "help_md": """## 📖 使用说明
### 🔍 信号含义
| 信号 | 触发条件 | 建议 |
|------|----------|------|
| 🔥 右侧强启动 | 突破3周高点+量比>1.5 | 可考虑入场 |
| ⏳ 黄金坑筑底 | 三线粘合<3%+量比<0.6 | 等放量再入 |
| ⚠️ 弱势下破 | 跌破3周低点+量比>1.5 | 规避 |
### ⚙️ A股代码格式
- 沪市加 `.SS`：如 `600519.SS`
- 深市加 `.SZ`：如 `000858.SZ`
### 💳 订阅说明
注册后免费使用7天，到期后订阅 ¥29/月 解锁全部功能
### ⚠️ 免责声明
本工具仅供策略研究，不构成投资建议。"""
    },
    "en": {
        "hero_title": "🥇 QuantGold · Global Market Scanner",
        "hero_sub": "VSA Volume Anomaly · MA Convergence · US + A-Shares · 1–7 Day Swing",
        "login_tab": "Log In", "register_tab": "Sign Up",
        "email": "Email", "password": "Password",
        "login_btn": "Log In", "register_btn": "Create Account",
        "logout_btn": "Log Out",
        "login_success": "Welcome back!",
        "register_success": "Account created! 7-day free trial started.",
        "welcome": "Hi, {email}",
        "status_paid": "✅ Active Subscriber",
        "status_trial": "⏳ Trial: {d} days left",
        "status_locked": "🔒 Trial Expired",
        "upgrade_btn": "💳 Subscribe to Unlock All",
        "paywall_title": "🔒 Subscription Required",
        "paywall_sub": "Your 7-day free trial has ended.",
        "paywall_free": "Free includes:",
        "paywall_free_items": "• Top 5 daily signals preview\n• Signal type visible",
        "paywall_paid": "Subscribers get:",
        "paywall_paid_items": "• 500+ tickers scanned\n• Full AI diagnosis\n• Backtest data\n• CSV export",
        "paywall_price": "Price: $5/month or $30/year",
        "paywall_contact": "👉 Email: your@email.com to subscribe",
        "sidebar_config": "⚙️ Scan Settings",
        "market_label": "Market",
        "pool_size": "Pool: {n} tickers",
        "custom_label": "Custom tickers (one per line)",
        "filter_title": "🔍 Signal Filter",
        "bt_title": "📊 Backtest",
        "bt_period_label": "Period", "bt_ticker_label": "Ticker",
        "bt_ticker_hint": "e.g. NVDA or 600519.SS",
        "data_source": "Data: Yahoo Finance | ~15 min delay",
        "tab_scan": "📡 Live Scan", "tab_bt": "🔬 Backtest", "tab_help": "📖 Help",
        "scan_btn": "🚀 Start Scan",
        "scan_est": "Scanning {n} tickers · ~{t} sec",
        "scanning": "Analyzing {t}... ({i}/{total})",
        "scan_error": "No data. Check your network.",
        "stat_scanned": "Scanned", "stat_fire": "🔥 Breakout",
        "stat_gold": "⏳ Basing", "stat_warn": "⚠️ Breakdown",
        "show_n": "Showing {n} signals",
        "no_filter": "No results. Enable more signal types.",
        "preview_tip": "👆 Trial shows top 5 only. Subscribe to see all {n}.",
        "col_ticker": "Ticker", "col_price": "Price", "col_chg": "Change",
        "col_vol": "Vol Ratio", "col_ma": "MA Spread",
        "col_status": "Signal", "col_diag": "Diagnosis",
        "export_btn": "⬇️ Export CSV",
        "sig_fire": "🔥 Breakout", "sig_gold": "⏳ Basing",
        "sig_warn": "⚠️ Breakdown", "sig_watch": "👀 Watching",
        "diag_fire": "Price breakout + volume surge — smart money entering",
        "diag_gold": "MA convergence + low volume — coiling before a move",
        "diag_warn": "Volume breakdown — avoid", "diag_watch": "No clear signal yet",
        "market_us_large": "🏆 S&P 500 Full", "market_us_small": "🚀 US Small Cap",
        "market_a": "🇨🇳 A-Shares", "market_mix": "🌏 US + A-Shares",
        "market_custom": "🔧 Custom",
        "bt_header": "🔬 Signal Backtest",
        "bt_caption": "Replay historical signals and view win-rate stats.",
        "bt_input_label": "Ticker", "bt_run_btn": "▶ Run Backtest",
        "bt_spinning": "Backtesting {t} ({p})...",
        "bt_no_signal": "No signals found. Try different ticker or longer period.",
        "bt_count": "Signals", "bt_wr5": "5D Win Rate", "bt_wr7": "7D Win Rate",
        "bt_avg5": "Avg 5D Ret", "bt_avg7": "Avg 7D Ret", "bt_maxdd": "Max Loss",
        "bt_detail": "#### 📋 Signal Log",
        "bt_col_type": "Signal", "bt_col_date": "Date",
        "bt_col_entry": "Entry", "bt_col_r5": "5D%", "bt_col_r7": "7D%",
        "bt_export": "⬇️ Export CSV", "bt_disclaimer": "⚠️ Past performance does not guarantee future results.",
        "help_md": """## 📖 Help
### 🔍 Signal Definitions
| Signal | Trigger | Action |
|--------|---------|--------|
| 🔥 Breakout | Close > 3-week high + Vol > 1.5x | Consider entry |
| ⏳ Basing | MA spread < 3% + Vol < 0.6x | Wait for volume |
| ⚠️ Breakdown | Close < 3-week low + Vol > 1.5x | Avoid |
### ⚙️ A-Share Format
- Shanghai: append `.SS` e.g. `600519.SS`
- Shenzhen: append `.SZ` e.g. `000858.SZ`
### 💳 Subscription
7-day free trial on signup. Subscribe at $5/month for full access.
### ⚠️ Disclaimer
For research only. Not financial advice."""
    }
}
### 💳 Subscription
7-day free trial on signup. Subscribe at $5/month for full access.
### ⚠️ Disclaimer
For research only. Not financial advice."""
    }
}

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    .hero-header { background: linear-gradient(135deg, #1a1f2e 0%, #161b22 100%);
        border: 1px solid #21262d; border-radius: 12px; padding: 20px 28px; margin-bottom: 20px; }
    .hero-title { font-size: 24px; font-weight: 700; margin: 0;
        background: linear-gradient(90deg, #f0c040, #ff8c00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { color: #8b949e; font-size: 13px; margin-top: 5px; }
    .stat-card { background: #161b22; border-radius: 10px;
        border: 1px solid #21262d; padding: 14px 16px; text-align: center; }
    .stat-value { font-size: 26px; font-weight: 700; color: #f0c040; }
    .stat-label { font-size: 11px; color: #8b949e; margin-top: 3px; }
    .paywall-box { background: #161b22; border: 1px solid #f85149;
        border-radius: 12px; padding: 28px; text-align: center; margin: 20px 0; }
    .paywall-title { font-size: 20px; font-weight: 700; color: #f85149; margin-bottom: 8px; }
    .paywall-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; text-align: left; }
    .paywall-col { background: #0d1117; border-radius: 8px; padding: 14px; border: 1px solid #21262d; }
    .paywall-col-title { font-size: 12px; color: #8b949e; margin-bottom: 8px; font-weight: 600; }
    .paywall-col-items { font-size: 13px; line-height: 1.8; color: #e6edf3; white-space: pre-line; }
    .trial-badge { background: #1f3d1f; color: #3fb950; border: 1px solid #3fb950;
        border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }
    .locked-badge { background: #3d1f1f; color: #f85149; border: 1px solid #f85149;
        border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }
    .paid-badge { background: #1f2d3d; color: #58a6ff; border: 1px solid #58a6ff;
        border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }
    .preview-tip { background: #1f2d1f; border: 1px solid #3fb950; border-radius: 8px;
        padding: 10px 14px; color: #3fb950; font-size: 13px; margin: 12px 0; }
    .bt-card { background: #161b22; border-radius: 10px; padding: 18px;
        border-left: 4px solid; margin-bottom: 14px; }
    .bt-card.fire { border-color: #ff6b35; }
    .bt-card.gold { border-color: #3fb950; }
    .bt-card.warn { border-color: #d29922; }
    .win-high { color: #3fb950; font-weight: 700; }
    .win-mid { color: #d29922; font-weight: 700; }
    .win-low { color: #f85149; font-weight: 700; }
    .scan-info { color: #8b949e; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

US_LARGE_CAP = ["MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB","AKAM","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE","AEP","AXP","AIG","AMT","AWK","AMP","AME","AMGN","APH","ADI","ANSS","AON","APA","APO","AAPL","AMAT","APTV","ACGL","ADM","ANET","AJG","AIZ","T","ATO","ADSK","ADP","AZO","AVB","AVY","AXON","BKR","BALL","BAC","BAX","BDX","BBY","TECH","BIIB","BLK","BX","BK","BA","BKNG","BSX","BMY","AVGO","BR","BRO","BLDR","BG","BXP","CHRW","CDNS","CZR","CPT","CPB","COF","CAH","KMX","CCL","CARR","CTLT","CAT","CBOE","CBRE","CDW","CE","COR","CNC","CNP","CF","CRL","SCHW","CHTR","CVX","CMG","CB","CHD","CI","CINF","CTAS","CSCO","C","CFG","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CAG","COP","ED","STZ","CEG","COO","CPRT","GLW","CPAY","CTVA","CSGP","COST","CTRA","CRWD","CCI","CSX","CMI","CVS","DHR","DRI","DVA","DAY","DECK","DE","DELL","DAL","DVN","DXCM","FANG","DLR","DFS","DG","DLTR","D","DPZ","DOV","DOW","DHI","DTE","DUK","DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","EMR","ENPH","ETR","EOG","EPAM","EQT","EFX","EQIX","EQR","ERIE","ESS","EL","EG","EVRG","ES","EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST","FRT","FDX","FIS","FITB","FSLR","FE","FI","FMC","F","FTNT","FTV","FOXA","FOX","BEN","FCX","GRMN","IT","GE","GEHC","GEV","GEN","GNRC","GD","GIS","GM","GPC","GILD","GPN","GL","GDDY","GS","HAL","HIG","HAS","HCA","DOC","HSIC","HSY","HES","HPE","HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN","HII","IBM","IEX","IDXX","ITW","INCY","IR","PODD","INTC","ICE","IFF","IP","IPG","INTU","ISRG","IVZ","INVH","IQV","IRM","JBHT","JBL","JKHY","J","JNJ","JCI","JPM","JNPR","K","KVUE","KDP","KEY","KEYS","KMB","KIM","KMI","KKR","KLAC","KHC","KR","LHX","LH","LRCX","LW","LVS","LDOS","LEN","LII","LLY","LIN","LYV","LKQ","LMT","L","LOW","LULU","LYB","MTB","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MTCH","MKC","MCD","MCK","MDT","MRK","META","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA","MHK","MOH","TAP","MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NEM","NWSA","NWS","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVDA","NVR","NXPI","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OTIS","PCAR","PKG","PLTR","PANW","PARA","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW","PNC","POOL","PPG","PPL","PFG","PG","PGR","PLD","PRU","PEG","PTC","PSA","PHM","QRVO","PWR","QCOM","DGX","RL","RJF","RTX","O","REG","REGN","RF","RSG","RMD","RVTY","ROK","ROL","ROP","ROST","RCL","SPGI","CRM","SBAC","SLB","STX","SRE","NOW","SHW","SPG","SWKS","SJM","SNA","SOLV","SO","LUV","SWK","SBUX","STT","STLD","STE","SYK","SMCI","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TGT","TEL","TDY","TER","TSLA","TXN","TPL","TXT","TMO","TJX","TKO","TSCO","TT","TDG","TRV","TRMB","TFC","TYL","TSN","USB","UBER","UDR","ULTA","UNP","UAL","UPS","URI","UNH","UHS","VLO","VTR","VLTO","VRSN","VRSK","VZ","VRTX","VTRS","VICI","V","VST","VMC","WRB","GWW","WAB","WBA","WMT","DIS","WBD","WM","WAT","WEC","WFC","WELL","WST","WDC","WY","WSM","WMB","WTW","WDAY","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS"]
US_SMALL_CAP = ["LGVN","AEI","JZXN","MVIS","CLOV","WKHS","SPCE","NKLA","GOEV","RIDE",
    "FFIE","MULN","PHIL","IDEX","ILUS","OCGN","NVAX","SNDL","ACB","CGC",
    "TLRY","APHA","MARA","RIOT","HUT","CIFR","BTBT","CLSK","WULF","IREN"]
A_SHARE_POOL = ["600519.SS","000858.SZ","601318.SS","000333.SZ","600036.SS",
    "300750.SZ","002594.SZ","300059.SZ","600900.SS","601166.SS",
    "000001.SZ","600030.SS","601888.SS","000725.SZ","002415.SZ",
    "300015.SZ","002352.SZ","300760.SZ","600585.SS","601012.SS"]

def analyze_stock(ticker, L):
    try:
        hist = yf.Ticker(ticker).history(period="2mo")
        if len(hist) < 22: return None
        close, volume = hist["Close"], hist["Volume"]
        latest, prev = close.iloc[-1], close.iloc[-2]
        lat_vol = volume.iloc[-1]
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ref = hist.iloc[-16:-1]
        avg_v = ref["Volume"].mean()
        if avg_v == 0: return None
        vol_ratio = lat_vol / avg_v
        chg_pct = (latest - prev) / prev * 100
        ma_spread = (max(ma5,ma10,ma20) - min(ma5,ma10,ma20)) / min(ma5,ma10,ma20)
        if latest > ref["Close"].max() and vol_ratio > 1.5:
            status, score, priority = L["sig_fire"], L["diag_fire"], 1
        elif ma_spread < 0.03 and vol_ratio < 0.6:
            status, score, priority = L["sig_gold"], L["diag_gold"], 2
        elif latest < ref["Close"].min() and vol_ratio > 1.5:
            status, score, priority = L["sig_warn"], L["diag_warn"], 4
        else:
            status, score, priority = L["sig_watch"], L["diag_watch"], 3
        return {"ticker": ticker, "close": round(latest,3), "chg_pct": round(chg_pct,2),
                "vol_ratio": round(vol_ratio,2), "ma_spread": round(ma_spread*100,2),
                "status": status, "score": score, "priority": priority}
    except: return None

def run_backtest(ticker, period, L):
    try:
        hist = yf.Ticker(ticker).history(period=period)
        if len(hist) < 30: return None
        close, volume = hist["Close"], hist["Volume"]
        signals = []
        for i in range(20, len(hist)-7):
            avg_v = volume.iloc[i-16:i].mean()
            if avg_v == 0: continue
            vol_r = volume.iloc[i] / avg_v
            c_now = close.iloc[i]
            c_win = close.iloc[i-16:i]
            ma5 = close.iloc[i-5:i].mean()
            ma10 = close.iloc[i-10:i].mean()
            ma20 = close.iloc[i-20:i].mean()
            spread = (max(ma5,ma10,ma20)-min(ma5,ma10,ma20))/min(ma5,ma10,ma20)
            if c_now > c_win.max() and vol_r > 1.5: sig = L["sig_fire"]
            elif spread < 0.03 and vol_r < 0.6: sig = L["sig_gold"]
            elif c_now < c_win.min() and vol_r > 1.5: sig = L["sig_warn"]
            else: continue
            signals.append({L["bt_col_type"]: sig, L["bt_col_date"]: hist.index[i].strftime("%Y-%m-%d"),
                L["bt_col_entry"]: round(c_now,3),
                L["bt_col_r5"]: round((close.iloc[i+5]-c_now)/c_now*100,2),
                L["bt_col_r7"]: round((close.iloc[i+7]-c_now)/c_now*100,2)})
        return {"ticker": ticker, "signals": signals}
    except: return None

with st.sidebar:
    lang_choice = st.radio("🌐 语言 / Language", ["中文","English"], horizontal=True)
    L = LANG["zh"] if lang_choice == "中文" else LANG["en"]
    st.divider()
    if not is_logged_in():
        login_t, reg_t = st.tabs([L["login_tab"], L["register_tab"]])
        with login_t:
            with st.form("login_form"):
                email_in = st.text_input(L["email"], placeholder="you@email.com")
                pass_in = st.text_input(L["password"], type="password")
                submitted = st.form_submit_button(L["login_btn"], use_container_width=True)
            if submitted:
                res = login_user(email_in, pass_in)
                if res["ok"]:
                    save_session(res["user"])
                    st.success(L["login_success"])
                    st.rerun()
                else:
                    st.error(res["msg"])
        with reg_t:
            with st.form("reg_form"):
                email_r = st.text_input(L["email"], placeholder="you@email.com", key="re")
                pass_r = st.text_input(L["password"], type="password", key="rp")
                pass_r2 = st.text_input(L["password"]+" ×2", type="password", key="rp2")
                submitted_r = st.form_submit_button(L["register_btn"], use_container_width=True)
            if submitted_r:
                if pass_r != pass_r2:
                    st.error("两次密码不一致" if lang_choice=="中文" else "Passwords don't match")
                else:
                    res = register_user(email_r, pass_r)
                    if res["ok"]:
                        login_res = login_user(email_r, pass_r)
                        save_session(login_res["user"])
                        st.success(L["register_success"])
                        st.rerun()
                    else:
                        st.error(res["msg"])
    else:
        user = current_user()
        status = get_user_status(user)
        st.markdown(f"**{L['welcome'].format(email=user['email'].split('@')[0])}**")
        if status["access"] == "full":
            st.markdown(f'<span class="paid-badge">{L["status_paid"]}</span>', unsafe_allow_html=True)
        elif status["access"] == "trial":
            st.markdown(f'<span class="trial-badge">{L["status_trial"].format(d=status["trial_days_left"])}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="locked-badge">{L["status_locked"]}</span>', unsafe_allow_html=True)
        if status["access"] != "full":
            if st.button(L["upgrade_btn"], use_container_width=True, type="primary"):
                st.session_state["show_paywall"] = True
        if st.button(L["logout_btn"], use_container_width=True):
            clear_session()
            st.rerun()
    st.divider()
            st.rerun()
    st.divider()
    if is_logged_in():
        st.markdown(f"### {L['sidebar_config']}")
        user = current_user()
        status = get_user_status(user)
        MARKET_CONFIG = {
            L["market_us_large"]: US_LARGE_CAP, L["market_us_small"]: US_SMALL_CAP,
            L["market_a"]: A_SHARE_POOL, L["market_mix"]: US_LARGE_CAP[:20]+A_SHARE_POOL[:10],
            L["market_custom"]: []}
        market_choice = st.selectbox(L["market_label"], list(MARKET_CONFIG.keys()))
        if market_choice == L["market_custom"]:
            custom_input = st.text_area(L["custom_label"], height=120)
            watch_list = [t.strip().upper() for t in custom_input.splitlines() if t.strip()]
        else:
            watch_list = MARKET_CONFIG[market_choice]
        st.caption(L["pool_size"].format(n=len(watch_list)))
        st.divider()
        st.markdown(f"### {L['filter_title']}")
        show_fire = st.checkbox(L["sig_fire"], value=True)
        show_gold = st.checkbox(L["sig_gold"], value=True)
        show_warn = st.checkbox(L["sig_warn"], value=False)
        show_watch = st.checkbox(L["sig_watch"], value=False)
        st.divider()
        st.markdown(f"### {L['bt_title']}")
        bt_period = st.selectbox(L["bt_period_label"], ["3mo","6mo","1y"], index=1)
        bt_ticker = st.text_input(L["bt_ticker_label"], placeholder=L["bt_ticker_hint"])
        st.divider()
        st.caption(L["data_source"])
    else:
        watch_list = []
        show_fire = show_gold = show_warn = show_watch = True
        bt_period = "6mo"; bt_ticker = ""

if not is_logged_in():
    st.markdown(f'<div class="hero-header"><div class="hero-title">{L["hero_title"]}</div><div class="hero-sub">{L["hero_sub"]}</div></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col,icon,title,desc in [
        (c1,"📡","全市场扫描" if lang_choice=="中文" else "Full Market Scan","覆盖标普500+A股" if lang_choice=="中文" else "S&P 500 + A-shares"),
        (c2,"🔬","历史回测" if lang_choice=="中文" else "Backtest","自动统计胜率与收益" if lang_choice=="中文" else "Win rate & return stats"),
        (c3,"⏳","7天免费试用" if lang_choice=="中文" else "7-Day Free Trial","注册即开始，无需信用卡" if lang_choice=="中文" else "No credit card needed"),
    ]:
        with col:
            st.markdown(f'<div class="stat-card" style="padding:20px;text-align:left;"><div style="font-size:28px;">{icon}</div><div style="font-size:15px;font-weight:700;color:#e6edf3;margin:8px 0 4px;">{title}</div><div style="font-size:13px;color:#8b949e;">{desc}</div></div>', unsafe_allow_html=True)
    st.info("👈 " + ("左侧注册，开始7天免费试用" if lang_choice=="中文" else "Sign up on the left to start your free trial"))
    st.stop()

user = current_user()
status = get_user_status(user)
st.markdown(f'<div class="hero-header"><div class="hero-title">{L["hero_title"]}</div><div class="hero-sub">{L["hero_sub"]}</div></div>', unsafe_allow_html=True)

if st.session_state.get("show_paywall"):
    st.markdown(f'<div class="paywall-box"><div class="paywall-title">{L["paywall_title"]}</div><div style="color:#8b949e;margin-bottom:16px;">{L["paywall_sub"]}</div><div class="paywall-grid"><div class="paywall-col"><div class="paywall-col-title">{L["paywall_free"]}</div><div class="paywall-col-items">{L["paywall_free_items"]}</div></div><div class="paywall-col" style="border-color:#f0c040;"><div class="paywall-col-title" style="color:#f0c040;">{L["paywall_paid"]}</div><div class="paywall-col-items">{L["paywall_paid_items"]}</div></div></div><div style="font-size:18px;font-weight:700;color:#f0c040;margin:12px 0;">{L["paywall_price"]}</div><div style="color:#e6edf3;">{L["paywall_contact"]}</div></div>', unsafe_allow_html=True)
    if st.button("✕ " + ("关闭" if lang_choice=="中文" else "Close")):
        st.session_state["show_paywall"] = False
        st.rerun()
    st.stop()

tab1, tab2, tab3 = st.tabs([L["tab_scan"], L["tab_bt"], L["tab_help"]])

with tab1:
    col_btn, col_info = st.columns([2,5])
    with col_btn:
        scan_btn = st.button(L["scan_btn"], use_container_width=True, type="primary")
    with col_info:
        st.caption(L["scan_est"].format(n=len(watch_list), t=len(watch_list)//3+5))
    if scan_btn:
        if not watch_list:
            st.warning("请配置股票池" if lang_choice=="中文" else "Configure a stock pool first.")
        else:
            results = []
            progress = st.progress(0)
            stxt = st.empty()
            total = len(watch_list)
            for i, ticker in enumerate(watch_list):
                stxt.markdown(f"<div class='scan-info'>{L['scanning'].format(t=ticker,i=i+1,total=total)}</div>", unsafe_allow_html=True)
                r = analyze_stock(ticker, L)
                if r: results.append(r)
                progress.progress((i+1)/total)
                time.sleep(0.05)
            progress.empty(); stxt.empty()
            if not results:
                st.error(L["scan_error"])
            else:
                results.sort(key=lambda x:(x["priority"],-abs(x["chg_pct"])))
                fire_cnt = sum(1 for r in results if r["status"]==L["sig_fire"])
                gold_cnt = sum(1 for r in results if r["status"]==L["sig_gold"])
                warn_cnt = sum(1 for r in results if r["status"]==L["sig_warn"])
                c1,c2,c3,c4 = st.columns(4)
                for col,val,label,color in [(c1,len(results),L["stat_scanned"],"#f0c040"),(c2,fire_cnt,L["stat_fire"],"#ff6b35"),(c3,gold_cnt,L["stat_gold"],"#3fb950"),(c4,warn_cnt,L["stat_warn"],"#d29922")]:
                    with col:
                        st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{color}">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)
                st.markdown("---")
                allowed = []
                if show_fire: allowed.append(L["sig_fire"])
                if show_gold: allowed.append(L["sig_gold"])
                if show_warn: allowed.append(L["sig_warn"])
                if show_watch: allowed.append(L["sig_watch"])
                filtered = [r for r in results if r["status"] in allowed]
                if not filtered:
                    st.info(L["no_filter"])
                else:
                    is_full = status["access"] in ["full","trial"]
                    display = filtered if is_full else filtered[:5]
                    if not is_full:
                        st.markdown(f'<div class="preview-tip">{L["preview_tip"].format(n=len(filtered))}</div>', unsafe_allow_html=True)
                    st.markdown(f"**{L['show_n'].format(n=len(display))}**")
                    rows = []
                    for r in display:
                        chg = f"+{r['chg_pct']}%" if r['chg_pct']>=0 else f"{r['chg_pct']}%"
                        row = {L["col_ticker"]:r["ticker"],L["col_price"]:r["close"],L["col_chg"]:chg,L["col_vol"]:f"{r['vol_ratio']}x",L["col_ma"]:f"{r['ma_spread']}%",L["col_status"]:r["status"]}
                        if is_full: row[L["col_diag"]] = r["score"]
                        rows.append(row)
                    df = pd.DataFrame(rows)
                    def csig(v):
                        s=str(v)
                        if "🔥" in s: return "background-color:#2d1b0e;color:#ff6b35;font-weight:600"
                        if "⏳" in s: return "background-color:#0d2818;color:#3fb950;font-weight:600"
                        if "⚠️" in s: return "background-color:#2a1f00;color:#d29922;font-weight:600"
                        return "color:#8b949e"
                    def cchg(v):
                        if isinstance(v,str) and v.startswith("+"): return "color:#3fb950;font-weight:600"
                        if isinstance(v,str) and v.startswith("-"): return "color:#f85149;font-weight:600"
                        return ""
                    st.dataframe(df.style.map(csig,subset=[L["col_status"]]).map(cchg,subset=[L["col_chg"]]), use_container_width=True, height=480)
                    if is_full:
                        csv = df.to_csv(index=False,encoding="utf-8-sig")
                        st.download_button(L["export_btn"],csv,f"quantgold_{datetime.now().strftime('%Y%m%d_%H%M')}.csv","text/csv")
                    else:
                        if st.button(L["upgrade_btn"]):
                            st.session_state["show_paywall"] = True
                            st.rerun()

with tab2:
    if status["access"] == "locked":
        st.markdown(f'<div class="paywall-box"><div class="paywall-title">{L["paywall_title"]}</div><div style="color:#8b949e">{L["paywall_sub"]}</div></div>', unsafe_allow_html=True)
        if st.button(L["upgrade_btn"], type="primary"):
            st.session_state["show_paywall"] = True
            st.rerun()
    else:
        st.markdown(f"### {L['bt_header']}")
        st.caption(L["bt_caption"])
        col_i,col_r = st.columns([3,1])
        with col_i:
            ticker_input = st.text_input(L["bt_input_label"], value=bt_ticker or "NVDA", placeholder=L["bt_ticker_hint"])
        with col_r:
            st.markdown("<br>",unsafe_allow_html=True)
            run_bt = st.button(L["bt_run_btn"], type="primary", use_container_width=True)
        if run_bt and ticker_input.strip():
            with st.spinner(L["bt_spinning"].format(t=ticker_input.upper(),p=bt_period)):
                bt_res = run_backtest(ticker_input.strip().upper(), bt_period, L)
            if not bt_res or not bt_res["signals"]:
                st.warning(L["bt_no_signal"])
            else:
                df_bt = pd.DataFrame(bt_res["signals"])
                for sig_type,card_cls,color in [(L["sig_fire"],"fire","#ff6b35"),(L["sig_gold"],"gold","#3fb950"),(L["sig_warn"],"warn","#d29922")]:
                    sub = df_bt[df_bt[L["bt_col_type"]]==sig_type]
                    if sub.empty: continue
                    cnt=len(sub); wr5=(sub[L["bt_col_r5"]]>0).mean()*100; wr7=(sub[L["bt_col_r7"]]>0).mean()*100
                    avg5=sub[L["bt_col_r5"]].mean(); avg7=sub[L["bt_col_r7"]].mean(); mdd=sub[L["bt_col_r7"]].min()
                    wrc="win-high" if wr7>=60 else ("win-mid" if wr7>=45 else "win-low")
                    st.markdown(f'<div class="bt-card {card_cls}"><b style="color:{color};font-size:14px;">{sig_type}</b><div style="display:flex;gap:32px;margin-top:10px;flex-wrap:wrap;"><div><div style="color:#8b949e;font-size:11px;">{L["bt_count"]}</div><div style="font-size:20px;font-weight:700;color:#e6edf3;">{cnt}</div></div><div><div style="color:#8b949e;font-size:11px;">{L["bt_wr5"]}</div><div class="{wrc}" style="font-size:20px;">{wr5:.1f}%</div></div><div><div style="color:#8b949e;font-size:11px;">{L["bt_wr7"]}</div><div class="{wrc}" style="font-size:20px;">{wr7:.1f}%</div></div><div><div style="color:#8b949e;font-size:11px;">{L["bt_avg5"]}</div><div style="font-size:20px;font-weight:700;color:{"#3fb950" if avg5>0 else "#f85149"};">{avg5:+.2f}%</div></div><div><div style="color:#8b949e;font-size:11px;">{L["bt_avg7"]}</div><div style="font-size:20px;font-weight:700;color:{"#3fb950" if avg7>0 else "#f85149"};">{avg7:+.2f}%</div></div><div><div style="color:#8b949e;font-size:11px;">{L["bt_maxdd"]}</div><div style="font-size:20px;font-weight:700;color:#f85149;">{mdd:.2f}%</div></div></div></div>', unsafe_allow_html=True)
                st.markdown(L["bt_detail"])
                def cret(v):
                    try: return "color:#3fb950;font-weight:600" if float(v)>0 else ("color:#f85149;font-weight:600" if float(v)<0 else "")
                    except: return ""
                st.dataframe(df_bt.style.map(cret,subset=[L["bt_col_r5"],L["bt_col_r7"]]), use_container_width=True)
                csv_bt = df_bt.to_csv(index=False,encoding="utf-8-sig")
                st.download_button(L["bt_export"],csv_bt,f"quantgold_bt_{ticker_input}_{bt_period}.csv","text/csv")
                st.info(L["bt_disclaimer"])

with tab3:
    st.markdown(L["help_md"])
