st.title("Discrete Event Simulation Modeler 🎯")
st.write("Simulate call center operations with varying staff levels")

# Check if session state exists and has required data
if 'processed_data' not in st.session_state:
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

if not st.session_state['processed_data'].get('data_loaded', False):
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

# Get the required data from session state
call_time_pattern = st.session_state['processed_data'].get('call_time_pattern')
wait_time_pattern = st.session_state['processed_data'].get('wait_time_pattern')
daily_pattern = st.session_state['processed_data'].get('daily_pattern')

if call_time_pattern is None or wait_time_pattern is None or daily_pattern is None:
    st.error("Required pattern data not available. Please process your data in the Data Loader page first.")
    st.stop()

# Simulation Parameters
st.header("Simulation Parameters")

# Time settings
col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("Start Time", time(8, 0))
with col2:
    end_time = st.time_input("End Time", time(18, 30))

# Staffing levels
st.subheader("Staffing Levels")
col1, col2 = st.columns(2)
with col1:
    morning_staff = st.number_input("Morning Staff (until 12:30)", min_value=1, max_value=20, value=5)
with col2:
    afternoon_staff = st.number_input("Afternoon Staff (after 12:30)", min_value=1, max_value=20, value=3)

# Simulation settings
st.subheader("Simulation Settings")
simulation_days = st.number_input("Number of Days to Simulate", min_value=1, max_value=30, value=7)
simulation_speed = st.slider("Simulation Speed (minutes per second)", min_value=1, max_value=60, value=10)

# Call Center Class
class CallCenter:
    def __init__(self, env, staff_morning, staff_afternoon):
        self.env = env
        self.staff_morning = staff_morning
        self.staff_afternoon = staff_afternoon
        self.staff = simpy.Resource(env, capacity=staff_morning)
        self.wait_times = []
        self.current_time = None
        
    def update_staff(self):
        current_hour = self.env.now // 60
        current_minute = self.env.now % 60
        current_time = time(current_hour, current_minute)
        
        if current_time >= time(12, 30):
            self.staff.capacity = self.staff_afternoon
        else:
            self.staff.capacity = self.staff_morning

# Call Process
def call_process(env, name, call_center, call_duration, time_slot):
    arrival_time = env.now
    with call_center.staff.request() as request:
        yield request
        wait_time = env.now - arrival_time
        call_center.wait_times.append({
            'time_slot': time_slot,
            'wait_time': wait_time
        })
        yield env.timeout(call_duration)

# Simulation Environment
def run_simulation(call_center, daily_pattern, call_time_pattern, simulation_days):
    env = simpy.Environment()
    call_center.env = env
    
    # Convert time slots to minutes
    time_slots = {}
    for idx, slot in enumerate(daily_pattern['Time Slot'].unique()):
        hour = slot.hour
        minute = slot.minute
        time_slots[slot] = idx * 30  # 30-minute slots
    
    # Simulation loop
    for day in range(simulation_days):
        for time_slot in time_slots:
            # Get call volume and duration for this time slot
            slot_data = daily_pattern[daily_pattern['Time Slot'] == time_slot]
            call_time_data = call_time_pattern[call_time_pattern['Time Slot'] == time_slot]
            
            if not slot_data.empty and not call_time_data.empty:
                avg_calls = slot_data['Average'].iloc[0]
                std_calls = slot_data['Standard Deviation'].iloc[0]
                avg_duration = call_time_data['Average Call Time (s)'].iloc[0]
                std_duration = call_time_data['Standard Deviation (s)'].iloc[0]
                
                # Generate calls for this time slot
                num_calls = int(np.random.normal(avg_calls, std_calls))
                num_calls = max(0, num_calls)  # Ensure non-negative
                
                for _ in range(num_calls):
                    # Generate call duration
                    duration = np.random.normal(avg_duration, std_duration)
                    duration = max(30, duration)  # Minimum 30 seconds
                    
                    # Schedule call
                    env.process(call_process(env, f'Call_{day}_{time_slot}', 
                                          call_center, duration/60, time_slot))
            
            # Wait for next time slot
            yield env.timeout(30)  # 30-minute slots
    
    # Run simulation
    env.run()

# Run Simulation Button
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        # Initialize call center
        call_center = CallCenter(None, morning_staff, afternoon_staff)
        
        # Create and run simulation
        env = simpy.Environment()
        call_center.env = env
        env.process(run_simulation(call_center, daily_pattern, call_time_pattern, simulation_days))
        env.run()
        
        # Process results
        wait_times_df = pd.DataFrame(call_center.wait_times)
        
        # Calculate statistics by time slot
        results = wait_times_df.groupby('time_slot').agg({
            'wait_time': ['mean', 'std', 'count']
        }).reset_index()
        
        results.columns = ['Time Slot', 'Average Wait Time (min)', 'Std Dev (min)', 'Sample Size']
        
        # Display results
        st.header("Simulation Results")
        
        # Plot average wait times
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results['Time Slot'],
            y=results['Average Wait Time (min)'],
            mode='lines+markers',
            name='Average Wait Time',
            error_y=dict(
                type='data',
                array=results['Std Dev (min)'],
                visible=True
            )
        ))
        
        fig.update_layout(
            title='Average Wait Times by Time Slot',
            xaxis_title='Time Slot',
            yaxis_title='Wait Time (minutes)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Detailed Statistics")
        st.dataframe(results)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Wait Time", f"{results['Average Wait Time (min)'].mean():.1f} min")
        with col2:
            st.metric("Max Wait Time", f"{results['Average Wait Time (min)'].max():.1f} min")
        with col3:
            st.metric("Total Calls", f"{results['Sample Size'].sum():,}")

# Add help text
st.markdown("""
### About the DES Modeler
This page simulates call center operations using discrete event simulation:
- Models call arrivals based on historical patterns
- Simulates call handling with variable staff levels
- Tracks wait times and queue lengths
- Provides detailed statistics and visualizations

Use the simulation parameters to test different staffing scenarios and see their impact on wait times.
""") 