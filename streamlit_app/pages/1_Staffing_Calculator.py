import sys
import streamlit as st
import math
import numpy as np
import scipy.special as sc
import pandas as pd
from datetime import datetime, time

# Function to calculate Erlang A probability
def erlang_a(n, a, theta):
    # theta is abandonment rate (1/mean patience time)
    # Calculate P0 (probability of zero customers in system)
    sum_term = sum([(a**k) / math.factorial(k) for k in range(n)])
    
    def m_function(x):
        return sc.gammainc(x + 1, x) / math.gamma(x + 1)
    
    last_term = (a**n) / math.factorial(n) * m_function(n * theta / (theta + (n - a)))
    p0 = 1 / (sum_term + last_term)
    
    # Calculate probability of waiting
    erlang_a_prob = ((a**n) / math.factorial(n)) * p0
    return erlang_a_prob

# Function to calculate average waiting time with abandonment
def calculate_waiting_time_with_abandonment(arrival_rate, service_time, num_agents, patience_time):
    # Calculate offered load (a)
    a = arrival_rate * service_time
    
    # Calculate abandonment rate (theta)
    theta = 1 / patience_time if patience_time > 0 else float('inf')
    
    # Calculate probability of waiting
    prob_wait = erlang_a(num_agents, a, theta)
    
    # Calculate average waiting time with abandonment
    if theta == float('inf'):
        avg_wait = 0
    else:
        avg_wait = prob_wait / (theta * (1 - prob_wait))
    
    return avg_wait, prob_wait

# Title and description
st.title("Call Center Staffing Calculator 📞")
st.write("Calculate expected waiting times using the Erlang-A formula (includes abandonment)")

# Input parameters in the sidebar
with st.sidebar:
    st.header("Input Parameters")
    
    arrival_rate = st.number_input(
        "Arrival Rate (calls per hour)",
        min_value=1.0,
        value=30.0,
        help="Average number of calls arriving per hour"
    )
    
    service_time = st.number_input(
        "Average Service Time (hours)",
        min_value=0.01,
        value=0.25,
        help="Average time to handle one call (in hours)"
    )
    
    num_agents = st.number_input(
        "Number of Agents",
        min_value=1,
        value=10,
        help="Number of available agents"
    )
    
    patience_time = st.number_input(
        "Average Patience Time (minutes)",
        min_value=0.1,
        value=10.0,
        help="Average time a caller will wait before abandoning"
    )

    # Add this after the existing sidebar inputs
    st.header("Staffing Data")
    staffing_file = st.file_uploader(
        "Upload Staffing Schedule (CSV)",
        type=['csv'],
        help="Upload a CSV file with staffing schedule. See sample_staffing.csv for format."
    )

    if staffing_file is not None:
        try:
            staffing_df = pd.read_csv(staffing_file)
            st.success("Staffing data loaded successfully!")
            
            # Display staffing summary
            st.subheader("Staffing Summary")
            total_staff = staffing_df.groupby('staff_type')['number_of_staff'].sum()
            st.write(total_staff)
            
            # Use the staffing data for calculations
            current_staff = staffing_df[
                (staffing_df['date'] == datetime.now().strftime('%Y-%m-%d')) &
                (staffing_df['start_time'] <= datetime.now().strftime('%H:%M')) &
                (staffing_df['end_time'] > datetime.now().strftime('%H:%M'))
            ]
            
            if not current_staff.empty:
                num_agents = current_staff['number_of_staff'].sum()
                st.info(f"Current active staff: {num_agents}")
        except Exception as e:
            st.error(f"Error loading staffing data: {str(e)}")

# Main content
st.header("Results")

# Calculate and display results
try:
    # Convert patience time to hours
    patience_time_hours = patience_time / 60
    
    # Calculate waiting time and probability
    waiting_time, prob_wait = calculate_waiting_time_with_abandonment(
        arrival_rate, service_time, num_agents, patience_time_hours
    )
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Offered Load (Erlang)", round(arrival_rate * service_time, 2))
        st.metric("Agents Required", num_agents)
    
    with col2:
        # Convert waiting time to minutes for display
        waiting_time_minutes = waiting_time * 60
        st.metric("Average Waiting Time", f"{waiting_time_minutes:.1f} minutes")
        
        # Calculate abandonment rate
        abandonment_rate = prob_wait * (1 - np.exp(-waiting_time/patience_time_hours))
        st.metric("Abandonment Rate", f"{abandonment_rate*100:.1f}%")
        
        # Calculate service level (modified for abandonment)
        service_level_time = 20/60  # 20 seconds in hours
        service_level = 1 - (prob_wait * np.exp(-service_level_time/patience_time_hours))
        st.metric("Service Level (20s)", f"{service_level*100:.1f}%")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Add explanatory notes
st.markdown("""
### Notes:
- **Arrival Rate**: The average number of calls arriving per hour
- **Service Time**: The average time it takes to handle one call (in hours)
- **Number of Agents**: The number of agents available to handle calls
- **Patience Time**: Average time a caller will wait before hanging up
- **Offered Load**: Total workload in Erlangs (arrival rate × service time)
- **Abandonment Rate**: Percentage of callers who hang up before being served
- **Service Level**: Percentage of calls answered within 20 seconds
""") 