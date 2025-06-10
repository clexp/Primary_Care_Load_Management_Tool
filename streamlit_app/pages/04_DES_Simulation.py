import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path to import the DES model
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)
from des_models import Model, Trial

st.set_page_config(
    page_title="DES Simulation",
    page_icon="📊",
    layout="wide"
)

st.title("Discrete Event Simulation Model 📊")
st.write("""
This page allows you to run discrete event simulations of the call center operations.
The simulation models call arrivals, queue behavior, and service times to help understand
system performance under different conditions.
""")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Parameters")
    
    # Basic parameters
    number_of_runs = st.number_input(
        "Number of Simulation Runs",
        min_value=1,
        max_value=50,
        value=10,
        help="Number of independent simulation runs to perform"
    )
    
    number_of_handlers = st.number_input(
        "Number of Call Handlers",
        min_value=1,
        max_value=20,
        value=4,
        help="Number of available call handlers"
    )
    
    max_queue_size = st.number_input(
        "Maximum Queue Size",
        min_value=10,
        max_value=100,
        value=30,
        help="Maximum number of calls that can wait in queue"
    )
    
    mean_call_duration = st.number_input(
        "Mean Call Duration (minutes)",
        min_value=1.0,
        max_value=30.0,
        value=4.0,
        help="Average duration of a call in minutes"
    )
    
    retry_probability = st.slider(
        "Retry Probability",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="Probability that a bounced call will be retried"
    )
    
    max_retries = st.number_input(
        "Maximum Retries",
        min_value=0,
        max_value=5,
        value=3,
        help="Maximum number of times a call can be retried"
    )
    
    abandonment_threshold = st.number_input(
        "Abandonment Threshold (minutes)",
        min_value=1.0,
        max_value=30.0,
        value=5.0,
        help="Average time before a caller abandons the queue"
    )

# Run simulation button
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        # Create and run trial
        trial = Trial()
        trial.number_of_runs = number_of_runs
        trial.run_trial()
        
        # Get summary statistics
        summary = trial.get_summary_statistics()
        
        # Display results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average Queue Time",
                f"{summary['mean_queue_time']:.1f} minutes"
            )
            st.metric(
                "Average Service Time",
                f"{summary['mean_service_time']:.1f} minutes"
            )
        
        with col2:
            st.metric(
                "Total Calls",
                f"{summary['total_calls']:,}"
            )
            st.metric(
                "Abandoned Calls",
                f"{summary['abandoned_calls']:,}"
            )
        
        with col3:
            st.metric(
                "Bounced Calls",
                f"{summary['bounced_calls']:,}"
            )
            st.metric(
                "Maximum Queue Length",
                f"{summary['max_queue_length']:,}"
            )
        
        # Create visualizations
        st.subheader("Simulation Results")
        
        # Queue length over time
        if trial.models:
            queue_data = []
            for model in trial.models:
                queue_data.extend(model.queue_length_history)
            
            queue_df = pd.DataFrame(queue_data, columns=['time', 'queue_length'])
            
            fig_queue = px.line(
                queue_df,
                x='time',
                y='queue_length',
                title='Queue Length Over Time',
                labels={'time': 'Simulation Time (minutes)', 'queue_length': 'Queue Length'}
            )
            st.plotly_chart(fig_queue, use_container_width=True)
        
        # Distribution of waiting times
        if trial.models:
            wait_times = []
            for model in trial.models:
                wait_times.extend(model.results_df['queue_time'].tolist())
            
            fig_wait = px.histogram(
                x=wait_times,
                title='Distribution of Waiting Times',
                labels={'x': 'Waiting Time (minutes)', 'y': 'Frequency'},
                nbins=30
            )
            st.plotly_chart(fig_wait, use_container_width=True)

# Add explanatory notes
st.markdown("""
### Notes:
- **Number of Simulation Runs**: Multiple runs help account for random variation
- **Call Handlers**: Number of staff available to take calls
- **Queue Size**: Maximum number of calls that can wait in queue
- **Call Duration**: Average time to handle a call
- **Retry Probability**: Chance that a bounced call will be retried
- **Abandonment Threshold**: Average time before callers hang up
- **Results**: Shows average waiting times, service levels, and queue behavior
""") 