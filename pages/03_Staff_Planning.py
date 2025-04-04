import streamlit as st
import pandas as pd
import numpy as np
from math import factorial
import plotly.graph_objects as go

def erlang_c(traffic_intensity, agents):
    """Calculate probability of queuing using Erlang C formula"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    sum_term = sum([(traffic_intensity**n)/factorial(n) for n in range(int(agents))])
    last_term = (traffic_intensity**agents)/(factorial(int(agents))*(1-traffic_intensity/agents))
    
    return last_term/(sum_term + last_term)

def calculate_wait_probability(traffic_intensity, agents, target_time, avg_handle_time):
    """Calculate probability of waiting longer than target time"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    p_queuing = erlang_c(traffic_intensity, agents)
    return p_queuing * np.exp(-(agents-traffic_intensity)*(target_time/avg_handle_time))

def calculate_required_staff(calls_per_interval, avg_handle_time, target_wait_time, target_service_level):
    """Calculate required staff for given parameters"""
    # Convert inputs to appropriate units
    interval_minutes = 30
    calls_per_hour = calls_per_interval * (60/interval_minutes)
    avg_handle_hours = avg_handle_time / 3600
    
    # Calculate traffic intensity (in erlangs)
    traffic = calls_per_hour * avg_handle_hours
    
    # Start with minimum staff needed
    staff = max(1, int(traffic + 1))
    
    # Iterate until we find the minimum staff that meets service level
    while staff < 100:  # Set reasonable upper limit
        wait_prob = calculate_wait_probability(traffic, staff, target_wait_time, avg_handle_time)
        service_level = 1 - wait_prob
        
        if service_level >= target_service_level:
            return staff
        staff += 1
    
    return staff  # Return max if target can't be met

def staff_planning_page():
    st.title("Staff Planning Calculator 👥")
    
    tabs = st.tabs(["Erlang Calculator", "ML Predictor (Coming Soon)"])
    
    with tabs[0]:
        st.write("""
        ### Erlang C Staff Calculator
        Calculate required staff levels based on call volumes and service level targets.
        """)
        
        # Get the data if available
        if 'call_data' not in st.session_state:
            st.warning("Please upload call data first in the Data Upload page.")
            return
        
        df = st.session_state['call_data']
        
        # Service level parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_handle_time = st.number_input(
                "Average Handle Time (seconds)",
                value=180,
                min_value=1,
                help="Average time to handle a call, including after-call work"
            )
        with col2:
            target_wait_time = st.number_input(
                "Target Wait Time (seconds)",
                value=60,
                min_value=1,
                help="Target maximum wait time for callers"
            )
        with col3:
            service_level = st.slider(
                "Target Service Level",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                format="%d%%",
                help="Percentage of calls to be answered within target wait time"
            )
        
        # Create time slots for the week
        hours = list(range(8, 18))  # 8 AM to 6 PM
        time_slots = [f"{hour:02d}:00" for hour in hours] + [f"{hour:02d}:30" for hour in hours]
        time_slots.sort()
        
        # Create empty staff grid if it doesn't exist
        if 'staff_grid' not in st.session_state:
            st.session_state['staff_grid'] = pd.DataFrame(
                0,
                index=time_slots,
                columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            )
        
        st.subheader("Current Staffing Levels")
        st.write("""
        💡 Quick Update Tips:
        1. Select cells using click & drag
        2. Press any number key (0-9) to fill selected cells
        3. Use Shift+Click to extend selection
        """)
        
        edited_df = st.data_editor(
            st.session_state['staff_grid'],
            use_container_width=True,
            num_rows="fixed",
            key="staff_grid_editor",
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    min_value=0,
                    max_value=100,
                    step=1,
                    default=0,
                    help="Press 0-9 while cells are selected to quickly update"
                ) for col in st.session_state['staff_grid'].columns
            },
            disabled=False
        )
        st.session_state['staff_grid'] = edited_df
        
        if st.button("Calculate Required Staff"):
            # Create results dataframe
            results = pd.DataFrame(index=time_slots, columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
            
            # Calculate for each time slot and day
            for time_slot in time_slots:
                hour = int(time_slot.split(':')[0])
                minute = int(time_slot.split(':')[1])
                
                for day in results.columns:
                    # Filter data for this time slot and day
                    mask = (
                        (df['Time'].dt.hour == hour) &
                        (df['Time'].dt.minute == minute) &
                        (df['Time'].dt.day_name() == day)
                    )
                    
                    if len(df[mask]) > 0:
                        avg_calls = df[mask]['Total Calls'].mean()
                        required_staff = calculate_required_staff(
                            avg_calls,
                            avg_handle_time,
                            target_wait_time,
                            service_level
                        )
                        results.loc[time_slot, day] = required_staff
                    else:
                        results.loc[time_slot, day] = 0
            
            # Display results
            st.subheader("Required Staff Levels")
            st.dataframe(results.astype(int), use_container_width=True)
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=results.values,
                x=results.columns,
                y=results.index,
                colorscale='Viridis',
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='Required Staff Levels Heatmap',
                xaxis_title='Day of Week',
                yaxis_title='Time of Day'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate gap analysis
            gap_analysis = results - edited_df
            
            st.subheader("Staffing Gap Analysis")
            st.dataframe(gap_analysis.astype(int), use_container_width=True)
            
            # Summary statistics
            total_required = results.sum().sum()
            total_current = edited_df.sum().sum()
            st.metric("Total Weekly Staff Hours Required", f"{total_required:.0f}")
            st.metric("Current Total Weekly Staff Hours", f"{total_current:.0f}")
            st.metric("Staffing Gap", f"{(total_required - total_current):.0f}")
    
    with tabs[1]:
        st.info("ML-based staff prediction coming soon!")

if __name__ == "__main__":
    staff_planning_page()
