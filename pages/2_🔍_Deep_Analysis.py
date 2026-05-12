import streamlit as st
import yfinance as yf
import pandas as pd

st.title("🔍 Deep Analysis")
st.markdown("Analyze specific stocks with detailed metrics and comparative analysis.")

ticker = st.text_input("Enter Ticker Symbol", value="AAPL")

if st.button("Analyze"):
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            st.subheader(f"{info.get('shortName', ticker)} ({ticker})")
            
            st.markdown(f"**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}")
            st.markdown(f"**Business Summary:**\n{info.get('longBusinessSummary', 'No summary available.')}")
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
