import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.title("Quick Insights 📈")
st.write("Explore key patterns and trends in your call center data")

# Check if session state exists and has required data
if 'processed_data' not in st.session_state:
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

if not st.session_state['processed_data'].get('data_loaded', False):
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

# Get the cleaned data and daily pattern data
df = st.session_state['processed_data'].get('clean_df')
daily_pattern = st.session_state['processed_data'].get('daily_pattern')

if df is None or daily_pattern is None:
    st.error("No data available. Please load your data in the Data Loader page.")
    st.stop()

# Debug information
st.write("Debug - Daily Pattern Data:")
st.write("Columns:", daily_pattern.columns.tolist())
st.write("Unique Days:", daily_pattern['Day'].unique().tolist())
st.write("First few rows:", daily_pattern.head())

# Overview Section
st.header("Data Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(df))
with col2:
    date_min = df['Date'].min()
    date_max = df['Date'].max()
    if pd.notnull(date_min) and pd.notnull(date_max):
        st.metric("Date Range", f"{date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}")
with col3:
    if 'Total Calls' in df.columns:
        st.metric("Total Calls", df['Total Calls'].sum())

# Time Series Analysis
if 'datetime' in df.columns and 'Total Calls' in df.columns:
    st.header("Call Volume Over Time")
    fig = px.line(df, x='datetime', y='Total Calls',
                  title='Call Volume Over Time',
                  labels={'datetime': 'Date', 'Total Calls': 'Number of Calls'})
    st.plotly_chart(fig, use_container_width=True)

# Daily Patterns
st.header("Daily Call Patterns")

# Create tabs for each day using three-letter abbreviations
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
tabs = st.tabs(day_names)

for i, (day, day_name) in enumerate(zip(days, day_names)):
    with tabs[i]:
        st.write(f"### {day_name} Call Volume Pattern")
        
        # Get data for this day from the daily pattern
        day_data = daily_pattern[daily_pattern['Day'] == day].copy()
        
        if not day_data.empty:
            # Create the plot
            fig = go.Figure()
            
            # Add mean line with markers
            fig.add_trace(go.Scatter(
                x=day_data['Time Slot'],
                y=day_data['Average'],
                mode='lines+markers',
                name='Average Calls',
                line=dict(color='blue', width=2),
                marker=dict(size=8, color='blue')
            ))
            
            # Update layout
            fig.update_layout(
                title=f'Call Volume Pattern - {day_name}',
                xaxis_title='Time Slot',
                yaxis_title='Number of Calls',
                hovermode='x unified',
                showlegend=True,
                height=400
            )
            
            # Add hover template
            fig.update_traces(
                hovertemplate="Time: %{x}<br>Average Calls: %{y:.1f}<extra></extra>"
            )
            
            # Show the plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            st.write("### Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Calls", f"{day_data['Average'].mean():.1f}")
            with col2:
                st.metric("Max Calls", f"{day_data['Average'].max():.1f}")
            with col3:
                st.metric("Min Calls", f"{day_data['Average'].min():.1f}")
            
            # Show data table
            st.write("### Detailed Data")
            display_data = day_data.copy()
            st.dataframe(display_data)
        else:
            st.write(f"No data available for {day_name}")

# Statistical Summary
st.header("Statistical Summary")
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    stats_df = pd.DataFrame({
        'Column': numeric_cols,
        'Mean': df[numeric_cols].mean().round(2),
        'Std Dev': df[numeric_cols].std().round(2),
        'Min': df[numeric_cols].min(),
        'Max': df[numeric_cols].max()
    })
    st.dataframe(stats_df)

# Key Metrics Analysis
st.header("Key Metrics Analysis")
metrics = ['Total Calls', 'Connected Calls', 'Calls Not Connected', 
          'Availability (%)', 'Avg Call Length (s)', 'Avg Wait Time (s)']

for metric in metrics:
    if metric in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"Average {metric}", f"{df[metric].mean():.2f}")
        with col2:
            st.metric(f"Total {metric}", f"{df[metric].sum():.2f}")

# Export Options
st.header("Export Options")
if st.button("Export Cleaned Data"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_call_center_data.csv",
        mime="text/csv"
    )

# Add help text
st.markdown("""
### About Quick Insights
This page provides a quick overview of your call center data, including:
- Call volume patterns by time of day, day of week, and month
- Key metrics and statistics
- Wait time analysis
- Abandonment analysis

Use the tabs and expandable sections to explore different aspects of your data.
""") 