import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.title("🗞️ News & Sentiment Analysis")
st.markdown("Algorithmic sentiment scoring and insider transaction tracker.")

ticker_symbol = st.text_input("Enter Ticker Symbol", value="AAPL").upper()
if not ticker_symbol:
    st.stop()

@st.cache_data(ttl=600)
def fetch_news_data(ticker):
    try:
        t = yf.Ticker(ticker)
        news = t.news
        insider = t.insider_transactions
        inst_holders = t.institutional_holders
        info = t.info
        return news, insider, inst_holders, info
    except Exception as e:
        return None, None, None, None

with st.spinner(f"Analyzing sentiment for {ticker_symbol}..."):
    news, insider, inst_holders, info = fetch_news_data(ticker_symbol)

st.markdown("---")
# Algorithmic Sentiment Logic
bullish_words = ['beat', 'upgrade', 'record', 'growth', 'breakout', 'acquisition', 'soar', 'surge', 'jump', 'profit', 'buy']
bearish_words = ['miss', 'downgrade', 'layoff', 'decline', 'investigation', 'loss', 'plunge', 'fall', 'lawsuit', 'sell', 'debt']

sentiment_score = 0
analyzed_news = []

if news:
    for item in news[:10]:
        title = item.get('title', '').lower()
        bull_count = sum(1 for w in bullish_words if w in title)
        bear_count = sum(1 for w in bearish_words if w in title)
        
        if bull_count > bear_count:
            sent = "🟢 Bullish"
            sentiment_score += 1
        elif bear_count > bull_count:
            sent = "🔴 Bearish"
            sentiment_score -= 1
        else:
            sent = "🟡 Neutral"
            
        try:
            time_str = pd.to_datetime(item.get('providerPublishTime', 0), unit='s').strftime('%Y-%m-%d %H:%M')
        except:
            time_str = "Recent"
            
        analyzed_news.append({
            'Title': item.get('title'),
            'Source': item.get('publisher'),
            'Link': item.get('link'),
            'Time': time_str,
            'Sentiment': sent
        })

n_col1, n_col2 = st.columns([2, 1])
with n_col1:
    st.subheader("📰 Latest News")
    if analyzed_news:
        for article in analyzed_news:
            with st.container():
                st.markdown(f"#### [{article['Title']}]({article['Link']})")
                st.caption(f"**{article['Source']}** • {article['Time']} • **{article['Sentiment']}**")
                st.markdown("---")
    else:
        st.info("No recent news found.")

with n_col2:
    st.subheader("🌡️ Sentiment Meter")
    
    # Map score to a 0-100 gauge (0 is extremely bearish, 100 is extremely bullish, 50 neutral)
    max_score = len(analyzed_news) if analyzed_news else 10
    normalized_score = 50 + (sentiment_score / max(1, max_score)) * 50
    normalized_score = max(0, min(100, normalized_score))
    
    color = "#00E676" if normalized_score >= 60 else ("#FF5252" if normalized_score <= 40 else "#FFEB3B")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = normalized_score,
        title = {'text': "Overall Headline Sentiment"},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': color}}
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), template="plotly_dark", paper_bgcolor='#0e1117')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🏦 Institutional Ownership")
    try:
        inst_pct = info.get('heldPercentInstitutions', 0) * 100 if info.get('heldPercentInstitutions') else 0
        st.metric("Institutions Hold", f"{inst_pct:.1f}%")
        if inst_holders is not None and not inst_holders.empty:
            st.dataframe(inst_holders[['Holder', 'Shares', 'Value']].head(5), hide_index=True, use_container_width=True)
        else:
            st.info("No major institutional holders found.")
    except:
        pass

st.markdown("---")
st.subheader("🕵️ Insider Transactions")
if insider is not None and not insider.empty:
    try:
        # Style dataframe slightly
        st.dataframe(insider.head(15), use_container_width=True)
    except:
        st.info("Unable to parse insider transactions format.")
else:
    st.info("No recent insider transactions found.")
