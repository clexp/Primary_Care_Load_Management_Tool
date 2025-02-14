import streamlit as st
import math

# Set page configuration
st.set_page_config(
    page_title="Call Center Calculator",
    page_icon="📞",
    layout="wide"
)

# Function to calculate Erlang C probability
def erlang_c(n, a):
    # Calculate P0 (probability of zero customers in system)
    sum_term = sum([(a**k) / math.factorial(k) for k in range(n)])
    last_term = (a**n) / (math.factorial(n) * (1 - a/n))
    p0 = 1 / (sum_term + last_term)
    
    # Calculate probability of waiting (Erlang C formula)
    erlang_c_prob = ((a**n) / (math.factorial(n))) * (1 / (1 - a/n)) * p0
    return erlang_c_prob

# Function to calculate average waiting time
def calculate_waiting_time(arrival_rate, service_time, num_agents):
    # Calculate offered load (a)
    a = arrival_rate * service_time
    
    # Ensure stability condition
    if a/num_agents >= 1:
        return float('inf')
    
    # Calculate probability of waiting
    prob_wait = erlang_c(num_agents, a)
    
    # Calculate average waiting time
    avg_wait = (prob_wait * service_time) / (num_agents * (1 - a/num_agents))
    
    return avg_wait

# Title and description
st.title("Call Center Waiting Time Calculator 📞")
st.write("Calculate expected waiting times using the Erlang-C formula")

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

# Main content
st.header("Results")

# Calculate and display results
try:
    # Convert arrival rate to per hour
    waiting_time = calculate_waiting_time(arrival_rate, service_time, num_agents)
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Offered Load (Erlang)", round(arrival_rate * service_time, 2))
        st.metric("Agents Required", num_agents)
    
    with col2:
        if waiting_time == float('inf'):
            st.error("System is unstable! Add more agents or reduce load.")
        else:
            # Convert waiting time to minutes for display
            waiting_time_minutes = waiting_time * 60
            st.metric("Average Waiting Time", f"{waiting_time_minutes:.1f} minutes")
            
            # Calculate and display service level
            service_level_time = 20/60  # 20 seconds in hours
            service_level = 1 - (erlang_c(num_agents, arrival_rate * service_time) * 
                               math.exp(-(num_agents - arrival_rate * service_time) * 
                                      service_level_time / service_time))
            st.metric("Service Level (20s)", f"{service_level*100:.1f}%")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Add explanatory notes
st.markdown("""
### Notes:
- **Arrival Rate**: The average number of calls arriving per hour
- **Service Time**: The average time it takes to handle one call (in hours)
- **Number of Agents**: The number of agents available to handle calls
- **Offered Load**: Total workload in Erlangs (arrival rate × service time)
- **Service Level**: Percentage of calls answered within 20 seconds
""") 