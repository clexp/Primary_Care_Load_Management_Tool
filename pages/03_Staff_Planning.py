import streamlit as st
import pandas as pd
import numpy as np
from math import factorial
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add the root directory to Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from app.utils.data_processor import create_staffing_template

def erlang_c(traffic_intensity, agents):
    """Calculate probability of queuing using Erlang C formula"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    sum_term = sum([(traffic_intensity**n)/factorial(n) for n in range(int(agents))])
    last_term = (traffic_intensity**agents)/(factorial(int(agents))*(1-traffic_intensity/agents))
    
    return last_term/(sum_term + last_term)

def erlang_b(traffic_intensity, agents):
    """Calculate blocking probability using Erlang B formula"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    sum_term = sum([(traffic_intensity**n)/factorial(n) for n in range(int(agents) + 1)])
    return (traffic_intensity**agents)/(factorial(int(agents)) * sum_term)

def erlang_a(traffic_intensity, agents, patience_time, avg_handle_time, queue_size=None):
    """Calculate abandonment probability using Erlang A formula (approximation)"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    # This is a simplified approximation of Erlang A
    # For a more accurate implementation, we would need to solve the M/M/n+M queue
    p_queuing = erlang_c(traffic_intensity, agents)
    
    # If queue_size is specified, adjust the queuing probability
    if queue_size is not None:
        # This is a simplified adjustment for finite queue size
        # A more accurate implementation would use the M/M/n/N+M queue formulas
        p_queuing = p_queuing * (1 - (traffic_intensity/agents)**queue_size)
    
    abandonment_rate = patience_time / avg_handle_time
    
    return p_queuing * (1 - np.exp(-abandonment_rate))

def calculate_wait_probability(traffic_intensity, agents, target_time, avg_handle_time, model_type="A", queue_size=None, patience_time=None):
    """Calculate probability of waiting longer than target time"""
    if traffic_intensity/agents >= 1:
        return 1.0
    
    if model_type == "C":
        p_queuing = erlang_c(traffic_intensity, agents)
        return p_queuing * np.exp(-(agents-traffic_intensity)*(target_time/avg_handle_time))
    elif model_type == "B":
        # For Erlang B, there is no queuing
        return 0.0
    elif model_type == "A":
        # For Erlang A, we need to account for abandonment and possibly finite queue size
        p_queuing = erlang_c(traffic_intensity, agents)
        
        # Adjust for finite queue size if specified
        if queue_size is not None:
            p_queuing = p_queuing * (1 - (traffic_intensity/agents)**queue_size)
        
        return p_queuing * np.exp(-(agents-traffic_intensity)*(target_time/avg_handle_time))
    else:
        # Default to Erlang A
        p_queuing = erlang_c(traffic_intensity, agents)
        return p_queuing * np.exp(-(agents-traffic_intensity)*(target_time/avg_handle_time))

def calculate_required_staff(calls_per_interval, avg_handle_time, target_wait_time, target_service_level, model_type="A", patience_time=None, queue_size=None):
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
        wait_prob = calculate_wait_probability(traffic, staff, target_wait_time, avg_handle_time, model_type, queue_size, patience_time)
        service_level = 1 - wait_prob
        
        if service_level >= target_service_level:
            return staff
        staff += 1
    
    return staff  # Return max if target can't be met

def calculate_abandonment_rate(df, time_slot=None, day=None):
    """Calculate abandonment rate from call data"""
    if 'Connected Calls' not in df.columns or 'Total Calls' not in df.columns:
        return None
    
    # Filter by time slot and day if provided
    filtered_df = df.copy()
    if time_slot is not None:
        hour, minute = map(int, time_slot.split(':'))
        filtered_df = filtered_df[
            (filtered_df['Time'].dt.hour == hour) & 
            (filtered_df['Time'].dt.minute == minute)
        ]
    
    if day is not None:
        filtered_df = filtered_df[filtered_df['Time'].dt.day_name() == day]
    
    # Calculate abandonment rate
    if len(filtered_df) > 0:
        total_calls = filtered_df['Total Calls'].sum()
        if total_calls > 0:
            connected_calls = filtered_df['Connected Calls'].sum()
            return (total_calls - connected_calls) / total_calls
    
    return None

def staff_optimization_page():
    st.title("Staff Optimization Calculator 👥")
    
    tabs = st.tabs(["Erlang Calculator", "ML Predictor (Coming Soon)"])
    
    with tabs[0]:
        st.write("""
        ### Erlang Staff Calculator
        Calculate required staff levels based on call volumes and service level targets.
        """)
        
        # Get the data if available
        if 'call_data' not in st.session_state:
            st.warning("Please upload call data first in the Data Management page.")
            return
        
        df = st.session_state['call_data']
        
        # Model selection - in alphabetical order
        st.subheader("Queue Model Selection")
        
        # Define models in alphabetical order
        models = {
            "A": "Erlang A (With Abandonment)",
            "B": "Erlang B (Without Queuing)",
            "C": "Erlang C (With Queuing)"
        }
        
        # Default to Erlang A
        default_model = "A"
        
        # Use radio buttons for model selection
        selected_model = st.radio(
            "Select Queue Model",
            options=["A", "B", "C"],
            format_func=lambda x: models[x],
            index=0,  # Default to Erlang A
            horizontal=True,
            help="Select the queue model that best represents your call center"
        )
        
        # Model descriptions
        model_descriptions = {
            "A": """
            **Erlang A (With Abandonment)**
            - Assumes calls wait in queue but may abandon if wait time is too long
            - Best for call centers with high abandonment rates
            - More realistic for modern call centers
            - Accounts for caller patience and abandonment behavior
            - Suitable for systems with finite queue length
            """,
            "B": """
            **Erlang B (Without Queuing)**
            - Assumes calls are blocked if all agents are busy
            - Best for systems where callers cannot wait (e.g., emergency services)
            - Useful for calculating blocking probability
            - Does not account for queuing or abandonment
            - Suitable for systems with no queue
            """,
            "C": """
            **Erlang C (With Queuing)**
            - Assumes calls wait in queue if all agents are busy
            - Best for call centers where callers are willing to wait
            - Most commonly used model for inbound call centers
            - Does not account for call abandonment
            - Suitable for systems with infinite queue length
            """
        }
        
        # Display the description of the selected model
        st.markdown(model_descriptions[selected_model])
        
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
            service_level_pct = st.slider(
                "Target Service Level",
                min_value=0,
                max_value=100,
                value=80,
                format="%d%%",
                help="Percentage of calls to be answered within target wait time"
            )
            # Convert percentage to decimal for calculations
            service_level = service_level_pct / 100.0
        
        # Additional parameters for Erlang A
        if selected_model == "A":
            st.subheader("Erlang A Parameters")
            
            # Check if we have abandonment data in the dataset
            has_abandonment_data = 'Connected Calls' in df.columns and 'Total Calls' in df.columns
            
            if has_abandonment_data:
                # Calculate overall abandonment rate from the data
                overall_abandonment_rate = calculate_abandonment_rate(df)
                
                if overall_abandonment_rate is not None:
                    st.info(f"Overall abandonment rate from data: {overall_abandonment_rate:.2%}")
                    
                    # Allow user to override the calculated abandonment rate
                    use_calculated_rate = st.checkbox(
                        "Use calculated abandonment rate from data",
                        value=True,
                        help="Use the abandonment rate calculated from your call data"
                    )
                    
                    if use_calculated_rate:
                        # Convert abandonment rate to patience time
                        # This is an approximation: patience_time = -avg_handle_time * ln(1 - abandonment_rate)
                        if overall_abandonment_rate < 1.0:
                            patience_time = -avg_handle_time * np.log(1 - overall_abandonment_rate)
                            st.write(f"Calculated patience time: {patience_time:.1f} seconds")
                        else:
                            patience_time = 300  # Default if abandonment rate is 100%
                            st.warning("Abandonment rate is 100%, using default patience time")
                    else:
                        patience_time = st.number_input(
                            "Average Patience Time (seconds)",
                            value=300,
                            min_value=1,
                            help="Average time callers are willing to wait before abandoning"
                        )
                else:
                    patience_time = st.number_input(
                        "Average Patience Time (seconds)",
                        value=300,
                        min_value=1,
                        help="Average time callers are willing to wait before abandoning"
                    )
            else:
                patience_time = st.number_input(
                    "Average Patience Time (seconds)",
                    value=300,
                    min_value=1,
                    help="Average time callers are willing to wait before abandoning"
                )
            
            # Create two columns for the parameters
            param_col1, param_col2 = st.columns(2)
            
            with param_col1:
                # Add option for finite queue size
                use_finite_queue = st.checkbox(
                    "Use Finite Queue Size",
                    value=False,
                    help="Enable if your system has a maximum queue length"
                )
                
                if use_finite_queue:
                    queue_size = st.number_input(
                        "Maximum Queue Size (N)",
                        value=10,
                        min_value=1,
                        help="Maximum number of callers that can wait in queue"
                    )
                else:
                    queue_size = None
        else:
            patience_time = None
            queue_size = None
        
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
        
        # Add template download button
        st.write("""
        ### Need a template?
        Download a sample template to see the required format for your staffing data.
        """)
        
        template_bytes = create_staffing_template()
        st.download_button(
            label="Download Staffing Template",
            data=template_bytes,
            file_name="staffing_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Add file uploader for staffing data
        st.write("---")
        st.write("### Upload Staffing Data")
        uploaded_staffing_file = st.file_uploader(
            "Upload Staffing Data File (CSV or Excel)",
            type=['csv', 'xlsx'],
            help="Upload a file with your current staffing levels"
        )
        
        if uploaded_staffing_file:
            try:
                if uploaded_staffing_file.name.endswith('.csv'):
                    staffing_df = pd.read_csv(uploaded_staffing_file)
                else:
                    staffing_df = pd.read_excel(uploaded_staffing_file)
                
                # Check if the file has the expected structure
                if 'Time' in staffing_df.columns and all(day in staffing_df.columns for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']):
                    # Set the index to the Time column
                    staffing_df = staffing_df.set_index('Time')
                    
                    # Update the staff grid
                    st.session_state['staff_grid'] = staffing_df
                    st.success("Staffing data loaded successfully!")
                else:
                    st.error("The uploaded file does not have the expected structure. Please use the template.")
            except Exception as e:
                st.error(f"Error processing staffing file: {str(e)}")
        
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
                        
                        # For Erlang A, check if we have abandonment data for this time slot and day
                        if selected_model == "A" and 'Connected Calls' in df.columns:
                            slot_abandonment_rate = calculate_abandonment_rate(df, time_slot, day)
                            
                            # If we have abandonment data for this slot, use it to calculate patience time
                            if slot_abandonment_rate is not None and slot_abandonment_rate < 1.0:
                                slot_patience_time = -avg_handle_time * np.log(1 - slot_abandonment_rate)
                            else:
                                slot_patience_time = patience_time
                        else:
                            slot_patience_time = patience_time
                        
                        required_staff = calculate_required_staff(
                            avg_calls,
                            avg_handle_time,
                            target_wait_time,
                            service_level,
                            selected_model,
                            slot_patience_time,
                            queue_size
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
    staff_optimization_page()
