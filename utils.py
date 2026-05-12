import streamlit as st
from datetime import datetime
import pytz

def get_market_status():
    """Returns the current market status and a formatted time string based on NYSE hours (EST)."""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # NYSE is open Monday-Friday, 9:30 AM to 4:00 PM EST
    is_weekday = now.weekday() < 5
    is_open_time = (now.hour > 9 or (now.hour == 9 and now.minute >= 30)) and now.hour < 16
    
    if is_weekday and is_open_time:
        status_color = "🟢"
        status_text = "MARKET OPEN"
    else:
        status_color = "🔴"
        status_text = "MARKET CLOSED"
        
    time_str = now.strftime("%Y-%m-%d %H:%M:%S EST")
    return f"{status_color} **{status_text}** | {time_str}"

def display_market_badge():
    """Displays the market status badge in the sidebar or main page."""
    status_str = get_market_status()
    st.sidebar.markdown(f"**{status_str}**")
    st.sidebar.markdown("---")
