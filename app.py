import streamlit as st
from utils import display_market_badge
import yfinance as yf
import pandas as pd

# FINAL POLISH: Page config with wide mode and expanded sidebar
st.set_page_config(
    page_title="Terminal Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Custom CSS for Footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117;
        color: #888888;
        text-align: center;
        padding: 8px;
        font-size: 11px;
        border-top: 1px solid #333;
        z-index: 999;
    }
    </style>
    <div class="footer">
        Data: Yahoo Finance | Built for Educational Purposes Only
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 🏦 Market Status")
display_market_badge()

# Sidebar: Quick Top Movers proxy
st.sidebar.markdown("### 🚀 Top Movers (Proxy)")
try:
    # Quick proxy check on highly volatile stocks
    tickers = ['NVDA', 'TSLA', 'AMD', 'COIN']
    movers = yf.download(tickers, period="2d", group_by='ticker', progress=False)
    for ticker in tickers:
        df = movers[ticker] if len(tickers) > 1 else movers
        if not df.empty and len(df) >= 2:
            close = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            pct = ((close - prev)/prev)*100
            c = "🟢" if pct >= 0 else "🔴"
            st.sidebar.write(f"{c} **{ticker}**: {pct:+.2f}%")
except:
    pass

st.sidebar.markdown("---")

# Use st.navigation for multipage layout (requires Streamlit 1.36+)
dashboard_page = st.Page("pages/1_📊_Dashboard.py", title="Dashboard", icon="📊", default=True)
deep_analysis_page = st.Page("pages/2_🔍_Deep_Analysis.py", title="Deep Analysis", icon="🔍")
tech_charts_page = st.Page("pages/3_📉_Technical_Charts.py", title="Technical Charts", icon="📉")
fundamentals_page = st.Page("pages/4_🏦_Fundamentals.py", title="Fundamentals", icon="🏦")
news_page = st.Page("pages/5_🗞️_News_Sentiment.py", title="News & Sentiment", icon="🗞️")
watchlist_page = st.Page("pages/6_⭐_Watchlist.py", title="Watchlist & Trade Builder", icon="⭐")

pg = st.navigation([
    dashboard_page, 
    deep_analysis_page, 
    tech_charts_page, 
    fundamentals_page, 
    news_page, 
    watchlist_page
])

pg.run()
