import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import time
import numpy as np
from ..simulation_model import run_multiple_simulations

st.set_page_config(page_title="Call Center Simulation", page_icon="📊", layout="wide")

st.title("Call Center Simulation")
st.write("""
This page allows you to run discrete event simulations of the call center operations.
Configure the parameters below and run the simulation to see the results.
""")

# Sidebar for parameters
with st.sidebar:
    st.header("Simulation Parameters")
    
    # Staff levels
    st.subheader("Staff Levels")
    morning_staff = st.number_input("Morning Staff (8:00-12:30)", min_value=1, value=5)
    afternoon_staff = st.number_input("Afternoon Staff (12:30-18:30)", min_value=1, value=3)
    
    # Call volume
    st.subheader("Call Volume (calls per minute)")
    morning_volume = st.number_input("Morning Volume (8:00-12:30)", min_value=0.1, value=2.5)
    afternoon_volume = st.number_input("Afternoon Volume (12:30-18:30)", min_value=0.1, value=1.5)
    
    # Call duration
    st.subheader("Call Duration (minutes)")
    mean_duration = st.number_input("Mean Duration", min_value=1.0, value=5.0)
    std_duration = st.number_input("Standard Deviation", min_value=0.1, value=2.0)
    
    # Simulation settings
    st.subheader("Simulation Settings")
    n_simulations = st.number_input("Number of Simulations", min_value=1, max_value=100, value=10)
    
    # Run button
    run_simulation = st.button("Run Simulation")

# Main content
if run_simulation:
    # Prepare simulation parameters
    staff_levels = {
        (0, 270): morning_staff,    # 8:00-12:30 (270 minutes)
        (270, 630): afternoon_staff  # 12:30-18:30 (630 minutes)
    }
    
    call_volume = {
        (0, 270): morning_volume,
        (270, 630): afternoon_volume
    }
    
    # Run simulations
    with st.spinner("Running simulations..."):
        results, stats = run_multiple_simulations(
            n_simulations=n_simulations,
            call_volume=call_volume,
            staff_levels=staff_levels,
            call_duration_mean=mean_duration,
            call_duration_std=std_duration,
            simulation_duration=630  # 8:00-18:30
        )
    
    # Display results
    st.header("Simulation Results")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Wait Time", f"{stats['mean_wait_time']:.1f} minutes")
    with col2:
        st.metric("Maximum Wait Time", f"{stats['max_wait_time']:.1f} minutes")
    with col3:
        st.metric("Average Queue Length", f"{stats['mean_queue_length']:.1f} calls")
    with col4:
        st.metric("Total Calls", f"{stats['total_calls']:.0f}")
    
    # Create time series plots
    st.subheader("Wait Times Over Time")
    
    # Aggregate results for plotting
    all_times = []
    all_wait_times = []
    all_queue_lengths = []
    
    for result in results:
        all_times.extend(result['time'])
        all_wait_times.extend(result['wait_time'])
        all_queue_lengths.extend(result['queue_length'])
    
    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'time': all_times,
        'wait_time': all_wait_times,
        'queue_length': all_queue_lengths
    })
    
    # Convert time to hours for better x-axis
    plot_df['hour'] = plot_df['time'] / 60 + 8  # Convert to hours starting from 8:00
    
    # Create wait time plot
    fig_wait = px.scatter(
        plot_df,
        x='hour',
        y='wait_time',
        title='Wait Times Throughout the Day',
        labels={'hour': 'Hour of Day', 'wait_time': 'Wait Time (minutes)'}
    )
    st.plotly_chart(fig_wait, use_container_width=True)
    
    # Create queue length plot
    st.subheader("Queue Length Over Time")
    fig_queue = px.scatter(
        plot_df,
        x='hour',
        y='queue_length',
        title='Queue Length Throughout the Day',
        labels={'hour': 'Hour of Day', 'queue_length': 'Number of Calls in Queue'}
    )
    st.plotly_chart(fig_queue, use_container_width=True)
    
    # Display raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(plot_df) 