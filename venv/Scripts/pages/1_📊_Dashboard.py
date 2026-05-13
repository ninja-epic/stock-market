import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

st.title("📊 Expert Analyst Dashboard")

col_search, col_refresh = st.columns([3, 1])
with col_search:
    ticker_symbol = st.text_input("Enter Ticker Symbol", value="AAPL").upper()
with col_refresh:
    st.write("")
    st.write("")
    auto_refresh = st.checkbox("Auto-Refresh (60s)", value=True)

if not ticker_symbol:
    st.stop()

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=60)
def fetch_ticker_info(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        
        # Approximate VWAP for today
        hist = t.history(period="1d", interval="5m")
        if not hist.empty and hist['Volume'].sum() > 0:
            typical_price = (hist['High'] + hist['Low'] + hist['Close']) / 3
            vwap = (typical_price * hist['Volume']).sum() / hist['Volume'].sum()
        else:
            vwap = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
        return info, vwap
    except Exception:
        return None, 0

@st.cache_data(ttl=60)
def fetch_market_indices():
    indices = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow": "^DJI", "VIX": "^VIX", "Russell 2k": "^RUT"}
    data = {}
    for name, sym in indices.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d") # Fetch slightly more in case of weekends
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                pct = ((curr - prev) / prev) * 100
                data[name] = {"price": curr, "pct": pct}
        except:
            pass
    return data

@st.cache_data(ttl=60)
def fetch_market_breadth():
    # Proxy using Mega-cap 10 to prevent long load times scraping thousands of stocks
    proxy_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'JNJ', 'JPM']
    data = yf.download(proxy_tickers, period="3mo", group_by="ticker", progress=False)
    
    advancing = 0
    declining = 0
    above_50 = 0
    
    for t in proxy_tickers:
        try:
            df = data[t] if len(proxy_tickers) > 1 else data
            if not df.empty and len(df) >= 2:
                if df['Close'].iloc[-1] > df['Close'].iloc[-2]:
                    advancing += 1
                elif df['Close'].iloc[-1] < df['Close'].iloc[-2]:
                    declining += 1
                    
            if not df.empty and len(df) >= 50:
                sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                if df['Close'].iloc[-1] > sma_50:
                    above_50 += 1
        except:
            pass
            
    return advancing, declining, (above_50 / len(proxy_tickers)) * 100

with st.spinner("Fetching live market data..."):
    info, vwap = fetch_ticker_info(ticker_symbol)
    indices = fetch_market_indices()
    advancing, declining, breadth_pct = fetch_market_breadth()

if not info:
    st.error("Error fetching data for this ticker. Please check the symbol.")
    st.stop()

# --- PRICE PANEL ---
short_name = info.get('shortName', ticker_symbol)
website = info.get('website', '')

# More reliable logo fetching using Google Favicon API
if website:
    logo_url = f"https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={website}&size=128"
else:
    logo_url = ""

title_col, logo_col = st.columns([11, 1])
with title_col:
    st.markdown(f"<h2 style='margin-bottom: 0px;'>{short_name} ({ticker_symbol})</h2>", unsafe_allow_html=True)
    st.caption(f"Sector: **{info.get('sector', 'N/A')}** | Industry: **{info.get('industry', 'N/A')}** | [Website]({website})")
with logo_col:
    if logo_url:
        try:
            st.image(logo_url, width=60)
        except:
            pass
        
st.markdown("### 💰 Real-Time Price Action")
current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
prev_close = info.get('previousClose', info.get('regularMarketPreviousClose', 1))
pct_change = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0

p_col1, p_col2, p_col3, p_col4 = st.columns(4)

with p_col1:
    color = "#00E676" if pct_change >= 0 else "#FF5252"
    st.markdown(f"<h1 style='color: {color}; margin-bottom: 0px;'>${current_price:,.2f}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color: {color}; margin-top: 0px;'>{pct_change:+.2f}%</h4>", unsafe_allow_html=True)

with p_col2:
    st.metric("Bid / Ask", f"${info.get('bid', 0):.2f} / ${info.get('ask', 0):.2f}", 
              f"Spread: ${(info.get('ask', 0) - info.get('bid', 0)):.2f}")
              
with p_col3:
    st.metric("VWAP (Intraday Proxy)", f"${vwap:,.2f}")
    if info.get('preMarketPrice'):
        st.caption(f"Pre-Market: **${info['preMarketPrice']}**")
    elif info.get('postMarketPrice'):
        st.caption(f"After-Hours: **${info['postMarketPrice']}**")

with p_col4:
    day_low = info.get('dayLow', 0)
    day_high = info.get('dayHigh', 0)
    st.markdown("**Day Range**")
    st.markdown(f"Low: ${day_low:.2f} | High: ${day_high:.2f}")
    if day_high > day_low:
        progress = (current_price - day_low) / (day_high - day_low)
        progress = max(0.0, min(1.0, progress)) # clamp
        st.progress(progress)
    else:
        st.progress(0)

st.markdown("---")

# --- ANALYST METRICS CARDS ---
st.markdown("### 📊 Analyst & Squeeze Metrics")
c1, c2, c3, c4 = st.columns(4)

with c1:
    high_52 = info.get('fiftyTwoWeekHigh', 0)
    low_52 = info.get('fiftyTwoWeekLow', 0)
    pct_from_high = ((current_price - high_52) / high_52) * 100 if high_52 else 0
    st.metric("vs 52-Week High", f"${high_52:,.2f}", f"{pct_from_high:.2f}%", delta_color="inverse")
    st.caption(f"52W Low: ${low_52:,.2f}")

with c2:
    sp500_pct = indices.get("S&P 500", {}).get("pct", 0)
    alpha = pct_change - sp500_pct
    st.metric("Alpha (vs S&P 500)", f"{alpha:+.2f}%", help="Today's performance relative to the S&P 500")
    st.caption(f"Beta: {info.get('beta', 'N/A')}")

with c3:
    avg_vol = info.get('averageVolume', 1)
    today_vol = info.get('volume', 0)
    vol_ratio = today_vol / avg_vol if avg_vol else 0
    vol_color = "normal" if vol_ratio <= 1.5 else "inverse" # Inverse because high volume relative to average can mean high volatility
    st.metric("Volume Activity", f"{today_vol:,.0f}", f"{(vol_ratio * 100):.0f}% of Avg", delta_color=vol_color)
    st.caption(f"Avg Vol: {avg_vol:,.0f}")

with c4:
    # Handle float safely 
    short_float_val = info.get('shortPercentOfFloat')
    short_float = (short_float_val * 100) if short_float_val is not None else 0
    days_to_cover = info.get('shortRatio', 0)
    
    if short_float > 15 or days_to_cover > 5:
        squeeze_risk = "🔥 HIGH"
    elif short_float > 5:
        squeeze_risk = "⚠️ MODERATE"
    else:
        squeeze_risk = "✅ LOW"
        
    st.metric("Short Float %", f"{short_float:.2f}%", squeeze_risk, delta_color="off")
    st.caption(f"Days to Cover: {days_to_cover}")

st.markdown("---")

# --- MARKET BREADTH PANEL ---
st.markdown("### 🌐 Market Breadth & Indices")
b_col1, b_col2 = st.columns([1, 2])

with b_col1:
    st.markdown("**Mega-Cap Breadth Proxy**")
    st.metric("Advance/Decline", f"{advancing} / {declining}", help="Advance/Decline ratio based on top 10 Mega-Cap stocks")
    st.metric("Above 50-Day MA", f"{breadth_pct:.0f}%", help="Percentage of proxy basket in uptrend")

with b_col2:
    idx_cols = st.columns(5)
    for i, (name, data) in enumerate(indices.items()):
        if i < 5:
            with idx_cols[i]:
                c = "#00E676" if data['pct'] >= 0 else "#FF5252"
                st.markdown(f"**{name}**")
                st.markdown(f"${data['price']:,.2f}")
                st.markdown(f"<span style='color:{c}'>**{data['pct']:+.2f}%**</span>", unsafe_allow_html=True)

# --- AUTO-REFRESH LOGIC ---
if auto_refresh:
    st.sidebar.info("⏱️ Auto-refresh active (60s)")
    time.sleep(60)
    st.rerun()
