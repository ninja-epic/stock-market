# 📈 Expert Analyst Trading Dashboard

A professional-grade, Bloomberg-style trading dashboard built entirely in Python using **Streamlit**, **yfinance**, and **Plotly**. This application provides real-time market data, advanced algorithmic technical analysis, and interactive fundamental valuation models for serious equity research.

## ✨ Key Features

- 📊 **Dashboard**: Live price action, intraday VWAP proxies, Alpha vs S&P 500, Short Float squeeze risk metrics, and top Mega-Cap market breadth.
- 🔍 **Deep Analysis**: Comprehensive business summaries, sector tracking, and interactive historical pricing charts.
- 📉 **Technical Charts**: Advanced Plotly charting engine featuring:
  - Automated Support & Resistance plotting
  - Golden Cross & Death Cross algorithmic detection
  - Momentum Oscillators (RSI, MACD, Stoch RSI, Williams %R)
  - Volume Analysis and unusual volume alerts
- 🏦 **Fundamentals & Valuation**: 
  - Sell-side equity research scorecard scoring Profitability, Growth, and Safety
  - **Interactive DCF Calculator**: Tweak growth and discount rates to generate Margin of Safety and Buy/Sell signals.
  - Wall Street analyst consensus tracking
- 🗞️ **News & Sentiment**: Scrapes live headlines and runs algorithmic sentiment scoring (Bullish/Bearish), alongside recent Insider Transactions.
- ⭐ **Watchlist & Trade Builder**: Session-state live watchlist combined with a professional Trade Setup Builder. Generates dynamic entry points, ATR-based stop losses, and position sizing based on your defined risk percentage.

## 🛠️ Technology Stack

- **Frontend/Framework**: [Streamlit](https://streamlit.io/)
- **Data Pipeline**: [yfinance](https://pypi.org/project/yfinance/)
- **Charting**: [Plotly](https://plotly.com/python/)
- **Technical Analysis**: `pandas_ta`, `ta`

## 🚀 Installation & Setup

1. **Clone the repository** (or download the files).
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the Environment**:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Dashboard**:
   *(Note: The main application files for this project are currently located inside the `venv/Scripts/` directory)*
   ```bash
   cd venv/Scripts
   streamlit run app.py
   ```

## 🎨 Theme Configuration
This dashboard utilizes a custom dark-mode "Trading Terminal" theme. The configuration is automatically applied via the `.streamlit/config.toml` file, utilizing monospace fonts and optimized green/red color palettes for fast visual parsing.

---
*Disclaimer: Data provided by Yahoo Finance. This tool is built for educational and research purposes only and does not constitute financial advice.*
