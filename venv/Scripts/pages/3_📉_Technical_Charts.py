import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import pandas_ta as ta
import numpy as np

st.title("📉 Technical Analysis Pro")
st.markdown("Advanced charting engine with automated pattern detection.")

# --- UI CONTROLS ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper()
with col2:
    period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
with col3:
    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

st.sidebar.header("Technical Indicators")
with st.sidebar.expander("📈 Trend Indicators", expanded=True):
    show_ema = st.checkbox("EMA 9 & 21", value=True)
    show_sma = st.checkbox("SMA 50 & 200", value=True)
    show_bb = st.checkbox("Bollinger Bands (20,2)", value=False)
    show_cross = st.checkbox("Golden/Death Cross Alerts", value=True)

with st.sidebar.expander("📊 Momentum Oscillators", expanded=True):
    show_rsi = st.checkbox("RSI (14)", value=True)
    show_macd = st.checkbox("MACD (12,26,9)", value=True)
    show_stochrsi = st.checkbox("Stoch RSI", value=False)
    show_willr = st.checkbox("Williams %R", value=False)

with st.sidebar.expander("📉 Volume Analysis", expanded=True):
    show_vol = st.checkbox("Volume Histogram", value=True)
    show_obv = st.checkbox("OBV (On Balance Vol)", value=False)
    show_vol_alert = st.checkbox("Unusual Volume Alert", value=True)

with st.sidebar.expander("📐 Pattern Detection", expanded=True):
    show_sr = st.checkbox("Support & Resistance (Swings)", value=True)

if ticker:
    with st.spinner("Fetching data & calculating indicators..."):
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            st.error("No data found.")
            st.stop()
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        # Clean data
        df = df.dropna()

        # Add logo and name
        try:
            info = yf.Ticker(ticker).info
            short_name = info.get('shortName', ticker)
            website = info.get('website', '')
            if website:
                logo_url = f"https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={website}&size=128"
            else:
                logo_url = ""
                
            title_col, logo_col = st.columns([11, 1])
            with title_col:
                st.markdown(f"<h3 style='margin-bottom: 0px;'>{short_name} ({ticker})</h3>", unsafe_allow_html=True)
            with logo_col:
                if logo_url:
                    try:
                        st.image(logo_url, width=50)
                    except:
                        pass
            st.markdown("---")
        except:
            pass

        # --- CALCULATE INDICATORS (pandas_ta) ---
        # EMAs & SMAs
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        
        # Bollinger Bands
        df.ta.bbands(length=20, std=2, append=True)
        
        # Momentum
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.stochrsi(append=True)
        df.ta.willr(append=True)
        
        # Volume
        df.ta.obv(append=True)
        
        # --- SUBPLOT LAYOUT CALCULATION ---
        subplot_titles = ["Price Action"]
        row_heights = [0.5]
        plots_to_add = []
        
        if show_vol:
            plots_to_add.append("Volume")
            row_heights.append(0.15)
            subplot_titles.append("Volume")
        if show_rsi:
            plots_to_add.append("RSI")
            row_heights.append(0.15)
            subplot_titles.append("RSI (14)")
        if show_macd:
            plots_to_add.append("MACD")
            row_heights.append(0.15)
            subplot_titles.append("MACD")
        if show_stochrsi:
            plots_to_add.append("Stoch RSI")
            row_heights.append(0.15)
            subplot_titles.append("Stochastic RSI")
        if show_willr:
            plots_to_add.append("Williams %R")
            row_heights.append(0.15)
            subplot_titles.append("Williams %R")
        if show_obv:
            plots_to_add.append("OBV")
            row_heights.append(0.15)
            subplot_titles.append("On Balance Volume")

        num_rows = 1 + len(plots_to_add)
        
        fig = make_subplots(
            rows=num_rows, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )

        # 1. MAIN CHART
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Price", showlegend=False
        ), row=1, col=1)
        
        if show_ema:
            if 'EMA_9' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='#2196F3', width=1), name='EMA 9'), row=1, col=1)
            if 'EMA_21' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='#FF9800', width=1), name='EMA 21'), row=1, col=1)
                
        if show_sma:
            if 'SMA_50' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#FFEB3B', width=2), name='SMA 50'), row=1, col=1)
            if 'SMA_200' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#F44336', width=2), name='SMA 200'), row=1, col=1)

        if show_bb:
            bb_cols = [c for c in df.columns if 'BB' in c]
            if len(bb_cols) >= 3:
                bb_u = [c for c in bb_cols if 'BBU' in c][0]
                bb_m = [c for c in bb_cols if 'BBM' in c][0]
                bb_l = [c for c in bb_cols if 'BBL' in c][0]
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_u], line=dict(color='rgba(255,255,255,0.2)'), name='BB Upper', showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_l], line=dict(color='rgba(255,255,255,0.2)'), name='BB Lower', fill='tonexty', fillcolor='rgba(255,255,255,0.05)', showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_m], line=dict(color='rgba(255,255,255,0.4)', dash='dash'), name='BB Mid', showlegend=False), row=1, col=1)

        # Golden / Death Cross
        if show_cross and 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            df['Cross'] = 0.0
            df.loc[(df['SMA_50'] > df['SMA_200']) & (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1)), 'Cross'] = 1
            df.loc[(df['SMA_50'] < df['SMA_200']) & (df['SMA_50'].shift(1) >= df['SMA_200'].shift(1)), 'Cross'] = -1
            
            golden_crosses = df[df['Cross'] == 1]
            death_crosses = df[df['Cross'] == -1]
            
            for idx in golden_crosses.index:
                fig.add_annotation(x=idx, y=golden_crosses.loc[idx, 'SMA_50'], text="Golden Cross", showarrow=True, arrowhead=1, arrowcolor="#00E676", ax=0, ay=40, row=1, col=1, font=dict(color="#00E676", size=10))
            for idx in death_crosses.index:
                fig.add_annotation(x=idx, y=death_crosses.loc[idx, 'SMA_50'], text="Death Cross", showarrow=True, arrowhead=1, arrowcolor="#FF5252", ax=0, ay=-40, row=1, col=1, font=dict(color="#FF5252", size=10))

        # Support & Resistance (Peaks/Valleys)
        if show_sr:
            window = 20
            df['Roll_Max'] = df['High'].rolling(window=window, center=True).max()
            df['Roll_Min'] = df['Low'].rolling(window=window, center=True).min()
            
            peaks = df[df['High'] == df['Roll_Max']]
            valleys = df[df['Low'] == df['Roll_Min']]
            
            recent_peaks = peaks.tail(3)
            recent_valleys = valleys.tail(3)
            
            for p in recent_peaks['High']:
                fig.add_hline(y=p, line_dash="dot", line_color="#FF5252", opacity=0.5, row=1, col=1, annotation_text="Resistance", annotation_font_size=10, annotation_position="right")
            for v in recent_valleys['Low']:
                fig.add_hline(y=v, line_dash="dot", line_color="#00E676", opacity=0.5, row=1, col=1, annotation_text="Support", annotation_font_size=10, annotation_position="right")

        # --- SUBPLOTS ---
        current_row = 2
        
        if show_vol:
            colors = ['#00E676' if close >= open else '#FF5252' for open, close in zip(df['Open'], df['Close'])]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=current_row, col=1)
            
            if show_vol_alert:
                df['Vol_Avg'] = df['Volume'].rolling(window=30).mean()
                unusual = df[df['Volume'] > 2 * df['Vol_Avg']]
                if not unusual.empty:
                    last_alert_idx = unusual.index[-1]
                    # Check if the alert is within the last 5 periods to be considered "recent/today"
                    if len(df) > 0 and (df.index[-1] - last_alert_idx).days <= 7:
                        st.sidebar.warning(f"🚨 Unusual Volume Detected Recently ({last_alert_idx.strftime('%Y-%m-%d')}): {unusual.loc[last_alert_idx, 'Volume']:,.0f}")
            current_row += 1
            
        if show_rsi:
            rsi_col = [c for c in df.columns if 'RSI' in c]
            if rsi_col:
                fig.add_trace(go.Scatter(x=df.index, y=df[rsi_col[0]], name="RSI", line=dict(color='#00BCD4')), row=current_row, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="#FF5252", row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#00E676", row=current_row, col=1)
                fig.add_hrect(y0=70, y1=100, fillcolor="#FF5252", opacity=0.1, line_width=0, row=current_row, col=1)
                fig.add_hrect(y0=0, y1=30, fillcolor="#00E676", opacity=0.1, line_width=0, row=current_row, col=1)
            current_row += 1
            
        if show_macd:
            macd_col = [c for c in df.columns if c.startswith('MACD_')]
            sig_col = [c for c in df.columns if c.startswith('MACDs_')]
            hist_col = [c for c in df.columns if c.startswith('MACDh_')]
            
            if macd_col and sig_col and hist_col:
                fig.add_trace(go.Scatter(x=df.index, y=df[macd_col[0]], name="MACD", line=dict(color='#00BCD4')), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[sig_col[0]], name="Signal", line=dict(color='#FF9800')), row=current_row, col=1)
                
                hist_colors = ['#00E676' if val >= 0 else '#FF5252' for val in df[hist_col[0]]]
                fig.add_trace(go.Bar(x=df.index, y=df[hist_col[0]], name="Histogram", marker_color=hist_colors), row=current_row, col=1)
            current_row += 1
            
        if show_stochrsi:
            stoch_k = [c for c in df.columns if 'STOCHRSIk' in c]
            stoch_d = [c for c in df.columns if 'STOCHRSId' in c]
            if stoch_k and stoch_d:
                fig.add_trace(go.Scatter(x=df.index, y=df[stoch_k[0]], name="%K", line=dict(color='#00BCD4')), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[stoch_d[0]], name="%D", line=dict(color='#FF9800')), row=current_row, col=1)
                fig.add_hline(y=80, line_dash="dash", line_color="#FF5252", row=current_row, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="#00E676", row=current_row, col=1)
            current_row += 1
            
        if show_willr:
            willr_col = [c for c in df.columns if 'WILLR' in c]
            if willr_col:
                fig.add_trace(go.Scatter(x=df.index, y=df[willr_col[0]], name="Will %R", line=dict(color='#E040FB')), row=current_row, col=1)
                fig.add_hline(y=-20, line_dash="dash", line_color="#FF5252", row=current_row, col=1)
                fig.add_hline(y=-80, line_dash="dash", line_color="#00E676", row=current_row, col=1)
            current_row += 1
            
        if show_obv:
            obv_col = [c for c in df.columns if 'OBV' in c]
            if obv_col:
                fig.add_trace(go.Scatter(x=df.index, y=df[obv_col[0]], name="OBV", line=dict(color='#FFEB3B')), row=current_row, col=1)
            current_row += 1

        # --- LAYOUT FINISHING TOUCHES ---
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            height=400 + (180 * (num_rows - 1)), # Dynamic height
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False
        )
        
        # Hide x-axis labels for all but the bottom subplot
        fig.update_xaxes(showticklabels=False)
        fig.update_xaxes(showticklabels=True, row=num_rows, col=1)

        st.plotly_chart(fig, use_container_width=True)
