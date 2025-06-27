import streamlit as st
import pandas as pd
import numpy as np
from math import factorial
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.title("Erlang Calculator 📊")
st.write("Calculate optimal staffing levels using Erlang formulas (A, B, C)")

# Create tabs
tabs = st.tabs(["Erlang C Calculator", "Erlang A Calculator", "Erlang B Calculator", "Comparison Tool"])

with tabs[0]:
    st.write("""
    ### Erlang C Calculator
    **Erlang C** assumes that all callers stay in the queue until the call is answered. 
    This method might overestimate the staff required since it doesn't account for call abandonment.
    
    **Key Assumptions:**
    - Infinite patience (no call abandonment)
    - Infinite queue length
    - All calls are eventually answered
    """)
    
    # Simple input parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        calls_per_hour = st.number_input("Calls per Hour", value=100, min_value=1)
    with col2:
        avg_handle_time = st.number_input("Average Handle Time (minutes)", value=5.0, min_value=0.1)
    with col3:
        target_wait_time = st.number_input("Target Wait Time (seconds)", value=60, min_value=1)
    
    service_level_pct = st.slider("Target Service Level", min_value=50, max_value=99, value=80, format="%d%%")
    service_level = service_level_pct / 100.0
    
    if st.button("Calculate Staffing (Erlang C)"):
        # Simple Erlang C calculation
        traffic_intensity = calls_per_hour * (avg_handle_time / 60)  # Convert to Erlangs
        
        # Start with minimum staff needed
        staff = max(1, int(traffic_intensity + 1))
        
        # Simple iteration to find required staff
        while staff < 50:  # Reasonable upper limit
            # Calculate probability of queuing (simplified)
            if traffic_intensity / staff >= 1:
                staff += 1
                continue
                
            # Simplified Erlang C probability
            p_queuing = (traffic_intensity ** staff) / (factorial(staff) * (1 - traffic_intensity/staff))
            
            # Calculate service level
            wait_prob = p_queuing * np.exp(-(staff - traffic_intensity) * (target_wait_time / (avg_handle_time * 60)))
            current_service_level = 1 - wait_prob
            
            if current_service_level >= service_level:
                break
            staff += 1
        
        # Display results
        st.subheader("Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Required Staff", f"{staff} agents")
        with col2:
            st.metric("Traffic Intensity", f"{traffic_intensity:.2f} Erlangs")
        with col3:
            avg_wait_time = (p_queuing * avg_handle_time * 60) / (staff - traffic_intensity) if staff > traffic_intensity else float('inf')
            st.metric("Average Wait Time", f"{avg_wait_time:.1f} seconds" if avg_wait_time != float('inf') else "∞")
        
        # Create a simple visualization
        st.subheader("Service Level vs Staff")
        staff_range = range(max(1, int(traffic_intensity)), staff + 5)
        service_levels = []
        
        for s in staff_range:
            if traffic_intensity / s >= 1:
                service_levels.append(0)
            else:
                p_q = (traffic_intensity ** s) / (factorial(s) * (1 - traffic_intensity/s))
                wait_p = p_q * np.exp(-(s - traffic_intensity) * (target_wait_time / (avg_handle_time * 60)))
                service_levels.append(1 - wait_p)
        
        fig = px.line(x=list(staff_range), y=service_levels, 
                     title="Service Level vs Number of Agents",
                     labels={'x': 'Number of Agents', 'y': 'Service Level'})
        fig.add_hline(y=service_level, line_dash="dash", line_color="red", 
                     annotation_text=f"Target: {service_level_pct}%")
        st.plotly_chart(fig)

with tabs[1]:
    st.write("""
    ### Erlang A Calculator
    **Erlang A** takes call abandonment into account, making it more realistic for modern call centers.
    
    **Key Assumptions:**
    - Finite patience (callers may abandon)
    - Abandonment rate affects staffing requirements
    - More accurate for high-abandonment environments
    """)
    
    st.info("Erlang A calculator implementation coming soon!")

with tabs[2]:
    st.write("""
    ### Erlang B Calculator
    **Erlang B** assumes calls are blocked if all agents are busy (no queuing).
    
    **Key Assumptions:**
    - No queuing allowed
    - Calls are blocked if all agents busy
    - Useful for emergency services or systems with no queue
    """)
    
    st.info("Erlang B calculator implementation coming soon!")

with tabs[3]:
    st.write("""
    ### Comparison Tool
    Compare staffing requirements across different Erlang models.
    """)
    
    st.info("Comparison tool implementation coming soon!")

# Add help text
st.markdown("""
### About the Erlang Calculator
This page provides tools for calculating optimal staffing levels using different Erlang formulas.

**Erlang C** is the most commonly used formula for call centers, but it may overestimate staffing needs.

**Erlang A** is more realistic as it accounts for call abandonment.

**Erlang B** is used when no queuing is allowed.

Use the tabs above to explore different models and their applications.
""") 