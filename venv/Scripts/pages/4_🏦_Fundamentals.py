import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.title("🏦 Fundamentals & Valuation")
st.markdown("Sell-side equity research scorecard and interactive DCF models.")

col_search, _ = st.columns([1, 2])
with col_search:
    ticker_symbol = st.text_input("Enter Ticker", value="AAPL").upper()

if not ticker_symbol:
    st.stop()

@st.cache_data(ttl=3600)
def fetch_fundamental_data(ticker):
    t = yf.Ticker(ticker)
    
    try:
        info = t.info
    except Exception:
        info = None
        
    try:
        earnings = t.earnings_dates
    except Exception:
        earnings = None
        
    try:
        recommendations = t.recommendations
    except Exception:
        recommendations = None
        
    try:
        cashflow = t.cashflow
    except Exception:
        cashflow = None
        
    try:
        financials = t.financials
    except Exception:
        financials = None
        
    return info, earnings, recommendations, cashflow, financials

with st.spinner("Fetching financial reports..."):
    info, earnings_dates, recommendations, cashflow, financials = fetch_fundamental_data(ticker_symbol)

if not info:
    st.error("Failed to retrieve fundamental data.")
    st.stop()

current_price = info.get('currentPrice', info.get('regularMarketPrice', 1))

# --- VALUATION RATIOS ---
st.markdown("### ⚖️ Valuation Ratios")

# Approximate Sector Averages for demo purposes
sector_avgs = {
    "Trailing P/E": 25.0,
    "Forward P/E": 20.0,
    "PEG Ratio": 1.5,
    "Price/Book": 4.0,
    "Price/Sales": 3.0,
    "EV/EBITDA": 15.0
}

ratios = {
    "Trailing P/E": info.get("trailingPE", np.nan),
    "Forward P/E": info.get("forwardPE", np.nan),
    "PEG Ratio": info.get("pegRatio", np.nan),
    "Price/Book": info.get("priceToBook", np.nan),
    "Price/Sales": info.get("priceToSalesTrailing12Months", np.nan),
    "EV/EBITDA": info.get("enterpriseToEbitda", np.nan)
}

v_cols = st.columns(6)
for i, (metric, val) in enumerate(ratios.items()):
    with v_cols[i]:
        avg = sector_avgs[metric]
        if pd.isna(val) or val is None:
            st.metric(metric, "N/A")
        else:
            diff = val - avg
            color = "normal" if diff <= 0 else "inverse"  # Lower valuation is "better/green"
            st.metric(metric, f"{val:.2f}", f"vs Avg: {diff:+.2f}", delta_color=color)

st.markdown("---")

# --- FINANCIAL HEALTH SCORECARD ---
st.markdown("### 🏥 Financial Health Scorecard")
# We'll calculate a pseudo-score out of 100 based on standard metrics

# Profitability
gross_margin = info.get("grossMargins", 0) or 0
net_margin = info.get("profitMargins", 0) or 0
roe = info.get("returnOnEquity", 0) or 0
roa = info.get("returnOnAssets", 0) or 0
prof_score = min(100, max(0, int((gross_margin*50) + (net_margin*100) + (roe*100))))

# Growth
rev_growth = info.get("revenueGrowth", 0) or 0
eps_growth = info.get("earningsQuarterlyGrowth", 0) or 0
growth_score = min(100, max(0, int((rev_growth*150) + (eps_growth*100))))

# Safety
debt_eq = info.get("debtToEquity", 100) or 100
debt_eq = debt_eq / 100
current_ratio = info.get("currentRatio", 1) or 1
safety_score = min(100, max(0, int((current_ratio * 30) + max(0, (2 - debt_eq)*20))))

# Overall Score
total_score = int((prof_score + growth_score + safety_score) / 3)
color = "#00E676" if total_score > 70 else ("#FF9800" if total_score > 40 else "#FF5252")

score_col1, score_col2 = st.columns([1, 3])
with score_col1:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        title={'text': "Overall Health"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': color}}
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), template='plotly_dark', paper_bgcolor='#0e1117')
    st.plotly_chart(fig_gauge, use_container_width=True)

with score_col2:
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"**💰 Profitability ({prof_score}/100)**")
        st.caption(f"Gross Margin: {gross_margin*100:.1f}%")
        st.caption(f"Net Margin: {net_margin*100:.1f}%")
        st.caption(f"ROE: {roe*100:.1f}%")
        st.caption(f"ROA: {roa*100:.1f}%")
    with sc2:
        st.markdown(f"**📊 Growth ({growth_score}/100)**")
        st.caption(f"Revenue YoY: {rev_growth*100:.1f}%")
        st.caption(f"EPS YoY: {eps_growth*100:.1f}%")
    with sc3:
        st.markdown(f"**🛡️ Safety ({safety_score}/100)**")
        st.caption(f"Debt/Equity: {debt_eq:.2f}")
        st.caption(f"Current Ratio: {current_ratio:.2f}")

st.markdown("---")

# --- EARNINGS ANALYSIS ---
st.markdown("### 📅 Earnings Analysis")
e_col1, e_col2 = st.columns([2, 1])

with e_col1:
    if earnings_dates is not None and not earnings_dates.empty:
        # Filter for past earnings
        try:
            # yfinance earnings_dates index is tz-aware
            past_earnings = earnings_dates[earnings_dates.index < datetime.now().astimezone(earnings_dates.index.tz)]
            if not past_earnings.empty:
                past_earnings = past_earnings.head(8).sort_index(ascending=True) # last 8 quarters
                
                fig_earn = go.Figure()
                fig_earn.add_trace(go.Bar(x=past_earnings.index.strftime('%Y-%m'), y=past_earnings['EPS Estimate'], name="Estimate", marker_color='#FF9800'))
                fig_earn.add_trace(go.Bar(x=past_earnings.index.strftime('%Y-%m'), y=past_earnings['Reported EPS'], name="Actual", marker_color='#00E676'))
                
                fig_earn.update_layout(title="Last 8 Quarters EPS vs Estimates", barmode='group', template='plotly_dark', paper_bgcolor='#0e1117', height=300)
                st.plotly_chart(fig_earn, use_container_width=True)
                
                # Calculate Streak
                streak = 0
                for i in range(len(past_earnings)-1, -1, -1):
                    if past_earnings['Reported EPS'].iloc[i] > past_earnings['EPS Estimate'].iloc[i]:
                        streak += 1
                    else:
                        break
            else:
                st.info("No past earnings data available.")
        except:
            st.info("Earnings timeline data could not be parsed.")
    else:
        st.info("No earnings data available.")

with e_col2:
    if earnings_dates is not None and not earnings_dates.empty:
        try:
            future_earnings = earnings_dates[earnings_dates.index >= datetime.now().astimezone(earnings_dates.index.tz)]
            if not future_earnings.empty:
                next_date = future_earnings.index[0]
                days_until = (next_date.date() - datetime.now().date()).days
                st.metric("Next Earnings Date", next_date.strftime('%Y-%m-%d'), f"in {days_until} days", delta_color="off")
            else:
                st.metric("Next Earnings Date", "Unknown")
                
            try:
                if 'streak' in locals():
                    st.metric("Beat Streak", f"{streak} Quarters 🔥")
            except:
                pass
        except:
            pass

st.markdown("---")

# --- DCF VALUATION CALCULATOR ---
st.markdown("### 🧮 Interactive DCF Valuation Calculator")

d_col1, d_col2, d_col3 = st.columns([1, 1, 2])
with d_col1:
    proj_growth = st.number_input("Projected FCF Growth Rate (%)", value=10.0, step=1.0) / 100
    discount_rate = st.number_input("Discount Rate / WACC (%)", value=9.0, step=0.5) / 100
with d_col2:
    term_growth = st.number_input("Terminal Growth Rate (%)", value=2.5, step=0.5) / 100
    years_proj = st.slider("Projection Years", 1, 10, 5)

with d_col3:
    st.caption("Discounted Cash Flow Model Parameters:")
    st.write(f"Uses Free Cash Flow data from YFinance. Assumes a {years_proj}-year high-growth period followed by terminal growth.")

try:
    if cashflow is not None and not cashflow.empty:
        # Get FCF (Operating Cash Flow - Capital Expenditures)
        ocf = cashflow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cashflow.index else 0
        capex = cashflow.loc['Capital Expenditure'].iloc[0] if 'Capital Expenditure' in cashflow.index else 0
        
        # In YF, Capex is usually negative, so we add it (OCF + (-Capex) = FCF)
        fcf_ttm = ocf + capex if capex < 0 else ocf - capex
        
        shares_out = info.get('sharesOutstanding')
        if shares_out and fcf_ttm > 0:
            # Simple DCF Math
            projected_fcf = []
            current_fcf = fcf_ttm
            for i in range(1, years_proj + 1):
                current_fcf *= (1 + proj_growth)
                projected_fcf.append(current_fcf / ((1 + discount_rate) ** i))
                
            terminal_val = (current_fcf * (1 + term_growth)) / (discount_rate - term_growth)
            terminal_pv = terminal_val / ((1 + discount_rate) ** years_proj)
            
            enterprise_val = sum(projected_fcf) + terminal_pv
            
            # Add cash, subtract debt to get Equity Value
            total_cash = info.get('totalCash', 0)
            total_debt = info.get('totalDebt', 0)
            equity_val = enterprise_val + total_cash - total_debt
            
            intrinsic_value = equity_val / shares_out
            margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100
            
            dc1, dc2, dc3, dc4 = st.columns(4)
            dc1.metric("Current Price", f"${current_price:.2f}")
            dc2.metric("Intrinsic Value (DCF)", f"${intrinsic_value:.2f}")
            
            if intrinsic_value > current_price:
                mos_color = "normal"
                signal = "🟢 BUY (Undervalued)"
            else:
                mos_color = "inverse"
                signal = "🔴 SELL (Overvalued)"
                
            dc3.metric("Margin of Safety", f"{margin_of_safety:.1f}%", delta_color=mos_color)
            dc4.markdown(f"#### {signal}")
        else:
            st.warning("Negative FCF or missing share count prevents DCF calculation.")
    else:
        st.warning("Cash flow data not available to calculate DCF.")
except Exception as e:
    st.error(f"DCF Calculation Error: {e}")

st.markdown("---")

# --- ANALYST CONSENSUS ---
st.markdown("### 👔 Analyst Consensus")
if recommendations is not None and not recommendations.empty:
    try:
        latest_rec = recommendations[recommendations['period'] == '0m'].iloc[0]
        
        labels = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
        values = [latest_rec.get('strongBuy', 0), latest_rec.get('buy', 0), latest_rec.get('hold', 0), latest_rec.get('sell', 0), latest_rec.get('strongSell', 0)]
        colors = ['#00E676', '#81C784', '#FFEB3B', '#FF9800', '#FF5252']
        
        a_col1, a_col2 = st.columns([1, 1])
        with a_col1:
            fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=colors)])
            fig_donut.update_layout(title="Analyst Ratings", template='plotly_dark', paper_bgcolor='#0e1117', height=300, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with a_col2:
            st.write("")
            st.write("")
            target_mean = info.get('targetMeanPrice', 0)
            target_high = info.get('targetHighPrice', 0)
            target_low = info.get('targetLowPrice', 0)
            upside = ((target_mean - current_price) / current_price) * 100 if target_mean else 0
            
            st.metric("Average Price Target", f"${target_mean:.2f}", f"{upside:+.2f}% Upside")
            st.caption(f"High Target: ${target_high:.2f} | Low Target: ${target_low:.2f}")
            
    except Exception as e:
        st.info("Analyst consensus data format not recognized.")
else:
    st.info("No analyst consensus data available.")
