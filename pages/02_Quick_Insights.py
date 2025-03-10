# In 02_Quick_Insights.py
import streamlit as st
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualizations import (plot_daily_patterns, plot_wait_times, 
                                plot_weekday_patterns, plot_heatmap)

def quick_insights_page():
    if 'call_data' not in st.session_state:
        st.warning("Please upload data first!")
        return
        
    df = st.session_state['call_data']
    
    # Add tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Daily Patterns", "Wait Times", 
                                     "Weekday Patterns", "Heatmap"])
    
    with tab1:
        st.plotly_chart(plot_daily_patterns(df), use_container_width=True)
    
    with tab2:
        st.plotly_chart(plot_wait_times(df), use_container_width=True)
    
    with tab3:
        st.plotly_chart(plot_weekday_patterns(df), use_container_width=True)
    
    with tab4:
        st.plotly_chart(plot_heatmap(df), use_container_width=True)
    
    # Key metrics
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Wait Time", f"{df['Avg Wait Time (s)'].mean():.1f}s")
    with col2:
        st.metric("Max Wait Time", f"{df['Longest Wait Time (s)'].max():.1f}s")
    with col3:
        dropped = df['Calls Not Connected'].sum()
        total = df['Total Calls'].sum()
        drop_rate = dropped / total if total > 0 else 0
        st.metric("Drop Rate", f"{drop_rate:.1%}")

if __name__ == "__main__":
    quick_insights_page()