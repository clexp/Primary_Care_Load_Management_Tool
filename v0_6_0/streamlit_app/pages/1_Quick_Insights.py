import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.title("Quick Insights 📈")
st.write("Explore key patterns and trends in your call center data")

# Check if data is loaded
if not st.session_state['processed_data']['data_loaded']:
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

# Get the cleaned data
df = st.session_state['processed_data']['clean_df']

if df is None:
    st.error("No data available. Please load your data in the Data Loader page.")
    st.stop()

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
if 'Time' in df.columns and 'Day' in df.columns and 'Total Calls' in df.columns:
    st.header("Daily Call Patterns")
    
    # Extract time slots and day of week
    df['time_slot'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
    df['day_of_week'] = df['Day']
    
    # Calculate mean and std for each day and time slot
    daily_stats = df.groupby(['day_of_week', 'time_slot']).agg({
        'Total Calls': ['mean', 'std', 'count']
    }).reset_index()
    daily_stats.columns = ['day_of_week', 'time_slot', 'mean_calls', 'std_calls', 'count']
    
    # Sort time slots
    daily_stats = daily_stats.sort_values(['day_of_week', 'time_slot'])
    
    # Create separate plots for each day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Create tabs for each day
    tabs = st.tabs(days)
    
    for i, day in enumerate(days):
        with tabs[i]:
            day_data = daily_stats[daily_stats['day_of_week'] == day]
            
            if not day_data.empty:
                # Create the figure
                fig = go.Figure()
                
                # Add mean line with markers
                fig.add_trace(go.Scatter(
                    x=day_data['time_slot'],
                    y=day_data['mean_calls'],
                    mode='lines+markers',
                    name='Mean Calls',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8, color='blue')
                ))
                
                # Add standard deviation area
                fig.add_trace(go.Scatter(
                    x=day_data['time_slot'],
                    y=day_data['mean_calls'] + day_data['std_calls'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=day_data['time_slot'],
                    y=day_data['mean_calls'] - day_data['std_calls'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(0,100,255,0.2)',
                    name='Standard Deviation'
                ))
                
                # Update layout
                fig.update_layout(
                    title=f'Call Volume Pattern - {day}',
                    xaxis_title='Time Slot',
                    yaxis_title='Number of Calls',
                    hovermode='x unified',
                    showlegend=True,
                    height=400
                )
                
                # Add hover template
                fig.update_traces(
                    hovertemplate="Time: %{x}<br>Mean Calls: %{y:.1f}<br>Std Dev: ±%{customdata:.1f}<br>Sample Size: %{customdata2}<extra></extra>",
                    customdata=day_data['std_calls'],
                    customdata2=day_data['count']
                )
                
                # Show the plot
                st.plotly_chart(fig, use_container_width=True)
                
                # Show statistics
                st.write("### Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Calls", f"{day_data['mean_calls'].mean():.1f}")
                with col2:
                    st.metric("Max Calls", f"{day_data['mean_calls'].max():.1f}")
                with col3:
                    st.metric("Min Calls", f"{day_data['mean_calls'].min():.1f}")
                
                # Show data table
                st.write("### Detailed Data")
                display_data = day_data.copy()
                display_data['time_slot'] = display_data['time_slot'].astype(str)
                display_data.columns = ['Day', 'Time Slot', 'Mean Calls', 'Std Dev', 'Sample Size']
                st.dataframe(display_data)

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