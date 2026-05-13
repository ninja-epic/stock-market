import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta

st.title("⭐ Watchlist & Trade Setup Builder")

# --- WATCHLIST ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'MSFT', 'TSLA', 'SPY', 'NVDA']

st.subheader("📝 Live Watchlist")
add_col, remove_col, _ = st.columns([1, 1, 2])
with add_col:
    new_ticker = st.text_input("Add Ticker").upper()
    if st.button("Add") and new_ticker:
        if new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            st.rerun()

with remove_col:
    rem_ticker = st.selectbox("Remove Ticker", [""] + st.session_state.watchlist)
    if st.button("Remove") and rem_ticker:
        st.session_state.watchlist.remove(rem_ticker)
        st.rerun()

@st.cache_data(ttl=60)
def get_watchlist_data(tickers):
    data_rows = []
    for t in tickers:
        try:
            df = yf.download(t, period="3mo", interval="1d", progress=False)
            if df.empty: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            close = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            change = ((close - prev)/prev)*100
            
            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)
            
            rsi = df['RSI_14'].iloc[-1] if 'RSI_14' in df.columns else np.nan
            macd_h = df[[c for c in df.columns if c.startswith('MACDh_')][0]].iloc[-1] if any(c.startswith('MACDh_') for c in df.columns) else 0
            macd_signal = "🟢 Bullish" if macd_h > 0 else "🔴 Bearish"
            
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            vol_today = df['Volume'].iloc[-1]
            vol_alert = "🔥 High" if vol_today > 1.5 * vol_avg else "Normal"
            
            # Simple Scoring
            score = 0
            if rsi > 30 and rsi < 70: score += 1 # Not overextended
            if macd_h > 0: score += 1
            if vol_alert == "🔥 High": score += 1
            if close > df['Close'].rolling(50).mean().iloc[-1]: score += 1
            
            data_rows.append({
                "Ticker": t,
                "Price": f"${close:.2f}",
                "Change %": f"{change:+.2f}%",
                "RSI (14)": f"{rsi:.1f}",
                "MACD Signal": macd_signal,
                "Volume Alert": vol_alert,
                "Setup Score": f"{score}/4"
            })
        except:
            pass
    return pd.DataFrame(data_rows)

if st.session_state.watchlist:
    with st.spinner("Updating Watchlist Data..."):
        wl_df = get_watchlist_data(st.session_state.watchlist)
        if not wl_df.empty:
            st.dataframe(wl_df, use_container_width=True, hide_index=True)
            
            csv = wl_df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Export Watchlist to CSV", data=csv, file_name="watchlist.csv", mime="text/csv")
else:
    st.info("Watchlist is empty.")

st.markdown("---")

# --- TRADE SETUP BUILDER ---
st.subheader("🛠️ Analyst Trade Setup Builder")
st.markdown("Build and size professional trade setups based on technical structures.")

t_col1, t_col2, t_col3 = st.columns([1, 1, 2])
with t_col1:
    trade_ticker = st.selectbox("Select Asset to Trade", st.session_state.watchlist if st.session_state.watchlist else ["AAPL"])
    capital = st.number_input("Account Capital ($)", value=10000, step=1000)
with t_col2:
    strategy = st.selectbox("Strategy Type", ["Breakout", "Pullback", "Reversal"])
    risk_pct = st.number_input("Risk per Trade (%)", value=1.0, step=0.1) / 100

if trade_ticker:
    if st.button("Generate Trade Plan", type="primary"):
        with st.spinner(f"Analyzing setup for {trade_ticker}..."):
            try:
                df = yf.download(trade_ticker, period="6mo", interval="1d", progress=False)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                current_p = df['Close'].iloc[-1]
                
                # Calculate ATR for dynamic stops
                df.ta.atr(length=14, append=True)
                atr = df['ATRr_14'].iloc[-1]
                
                if strategy == "Breakout":
                    entry = df['High'].rolling(20).max().iloc[-1]
                    stop_loss = entry - (1.5 * atr)
                elif strategy == "Pullback":
                    entry = current_p
                    stop_loss = df['Low'].rolling(10).min().iloc[-1] - (0.5 * atr)
                else: # Reversal
                    entry = current_p
                    stop_loss = current_p - (2.0 * atr)
                    
                risk_per_share = entry - stop_loss
                
                if risk_per_share > 0:
                    t1 = entry + (1.5 * risk_per_share)
                    t2 = entry + (2.5 * risk_per_share)
                    t3 = entry + (4.0 * risk_per_share)
                    
                    total_risk_dollars = capital * risk_pct
                    position_size = int(total_risk_dollars / risk_per_share)
                    position_value = position_size * entry
                    
                    rr_ratio = (t2 - entry) / risk_per_share # Using T2 as primary target
                    
                    st.markdown("### 📝 Generated Trade Plan Card")
                    if rr_ratio >= 2.0:
                        st.success(f"✅ **VALID SETUP**: Risk/Reward ratio is **{rr_ratio:.2f}:1** (Meets 2:1 minimum)")
                    else:
                        st.warning(f"⚠️ **MARGINAL SETUP**: Risk/Reward ratio is **{rr_ratio:.2f}:1** (Needs >= 2:1)")
                        
                    tc1, tc2, tc3, tc4 = st.columns(4)
                    tc1.metric("📌 Entry Price", f"${entry:.2f}")
                    tc2.metric("🛑 Stop Loss", f"${stop_loss:.2f}", f"-${risk_per_share:.2f} risk/sh", delta_color="inverse")
                    tc3.metric("📊 Position Size", f"{position_size} Shares", f"Value: ${position_value:,.2f}")
                    tc4.metric("💰 Max Risk", f"${total_risk_dollars:.2f}", f"{risk_pct*100:.1f}% of Acct", delta_color="inverse")
                    
                    st.info(f"""
                    **Take Profit Targets:**
                    - 🎯 **Target 1 (1.5R):** ${t1:.2f}
                    - 🎯 **Target 2 (2.5R):** ${t2:.2f} *(Primary)*
                    - 🚀 **Target 3 (4.0R):** ${t3:.2f} *(Runner)*
                    """)
                else:
                    st.error("Invalid stop loss calculation. Market structure too tight for strategy.")
            except Exception as e:
                st.error(f"Error analyzing setup: {e}")
