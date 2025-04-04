# In 02_Quick_Insights.py
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the root directory to Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from app.utils.visualizations import (plot_daily_patterns, plot_wait_times,
                                    plot_weekday_patterns, plot_weekday_averages,
                                    plot_individual_weekday_patterns,
                                    plot_connection_rates, plot_hourly_abandonment)

def call_analytics_page():
    st.title("Call Analytics Dashboard 📊")
    
    if 'call_data' not in st.session_state:
        st.warning("Please upload data first!")
        return
        
    df = st.session_state['call_data']
    
    # Add tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Daily Patterns", "Wait Times", 
        "Weekday Distribution", "Weekday Averages",
        "Connection Rates", "Hourly Abandonment"
    ])
    
    with tab1:
        st.plotly_chart(plot_daily_patterns(df), use_container_width=True)
    
    with tab2:
        st.plotly_chart(plot_wait_times(df), use_container_width=True)
    
    with tab3:
        st.plotly_chart(plot_weekday_patterns(df), use_container_width=True)
    
    with tab4:
        st.plotly_chart(plot_weekday_averages(df), use_container_width=True)
        st.plotly_chart(plot_individual_weekday_patterns(df), use_container_width=True)
    
    with tab5:
        st.plotly_chart(plot_connection_rates(df), use_container_width=True)
    
    with tab6:
        st.plotly_chart(plot_hourly_abandonment(df), use_container_width=True)
    
    # Key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Wait Time", f"{df['Avg Wait Time (s)'].mean():.1f}s")
    with col2:
        st.metric("Max Wait Time", f"{df['Longest Wait Time (s)'].max():.1f}s")
    with col3:
        dropped = df['Calls Not Connected'].sum()
        total = df['Total Calls'].sum()
        drop_rate = dropped / total if total > 0 else 0
        st.metric("Drop Rate", f"{drop_rate:.1%}")
    with col4:
        st.metric("Total Calls", f"{total:,}")

if __name__ == "__main__":
    call_analytics_page()