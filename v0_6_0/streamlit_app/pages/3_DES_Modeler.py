import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import simpy
import random
from datetime import datetime, time

# Global settings class
class g:
    # Staffing levels
    staff = 5  # Total staff available
    
    # Staff unavailability settings
    unav_time = 3600 * 6  # Duration of unavailability (6 hours)
    unav_freq = 3600 * 4  # Frequency of unavailability check (4 hours)
    
    # Simulation settings
    simulation_days = 1
    number_of_runs = 10
    start_time = time(8, 0)
    end_time = time(18, 30)

class Caller:
    def __init__(self, caller_id):
        self.id = caller_id
        self.wait_time = 0
        self.queue_length = 0
        self.time_slot = None
        self.day = None

class CallHandler:
    """Class to track individual call handlers"""
    next_id = 1

    def __init__(self):
        self.id = CallHandler.next_id
        CallHandler.next_id += 1
        self.is_secretarial = False
        self.current_call = None

class CallHandlerPool:
    def __init__(self, env, start_handlers=5):
        self.env = env
        self.target_cnt = start_handlers
        self.curr_cnt = start_handlers
        self.handlers = simpy.Store(env)
        self.wait_times = []
        self.queue_lengths = []  # Track queue lengths over time
        self.debug_stats = {
            'calls_processed': 0,
            'handlers_added': 0,
            'handlers_removed': 0,
            'secretarial_transitions': 0
        }
        
        # Initialize the store with handlers
        self.handlers.items = [CallHandler() for _ in range(start_handlers)]
        print(f'Initialized pool with {start_handlers} handlers')

    def add_handler(self):
        """Add a handler to the pool"""
        self.target_cnt += 1
        if self.curr_cnt < self.target_cnt:
            handler = CallHandler()
            self.handlers.put(handler)
            self.curr_cnt += 1
            self.debug_stats['handlers_added'] += 1
            print(f'{self.env.now:.2f}: Handler {handler.id} added. Current count: {self.curr_cnt}/{self.target_cnt}')

    def remove_handler(self):
        """Remove a handler from the pool"""
        self.target_cnt -= 1
        if self.curr_cnt > self.target_cnt:
            # First try to get an idle handler
            if len(self.handlers.items) > 0:
                handler = yield self.handlers.get()
                self.curr_cnt -= 1
                self.debug_stats['handlers_removed'] += 1
                print(f'{self.env.now:.2f}: Idle handler {handler.id} removed. Current count: {self.curr_cnt}/{self.target_cnt}')
            else:
                # No idle handlers, mark the next returning handler for removal
                print(f'{self.env.now:.2f}: No idle handlers available. Next returning handler will be removed.')

    def transition_to_secretarial(self, handler):
        """Transition a handler to secretarial work"""
        handler.is_secretarial = True
        self.debug_stats['secretarial_transitions'] += 1
        print(f'{self.env.now:.2f}: Handler {handler.id} transitioned to secretarial work')

    def get_handler(self):
        """Get a handler from the pool - this is the generator function"""
        print(f'{self.env.now:.2f}: Requesting handler. Available: {len(self.handlers.items)}, Queue: {len(self.handlers.get_queue)}')
        handler = yield self.handlers.get()
        handler.current_call = self.env.now
        return handler

    def put(self, handler):
        """Return a handler to the pool"""
        handler.current_call = None
        if self.curr_cnt <= self.target_cnt:
            self.handlers.put(handler)
            print(f'{self.env.now:.2f}: Handler {handler.id} returned to pool. Available: {len(self.handlers.items)}')
        else:
            self.curr_cnt -= 1
            self.debug_stats['handlers_removed'] += 1
            print(f'{self.env.now:.2f}: Handler {handler.id} removed on return to pool. Current count: {self.curr_cnt}/{self.target_cnt}')

    def record_queue_length(self, time_slot):
        """Record current queue length"""
        current_length = len(self.handlers.get_queue)
        self.queue_lengths.append({
            'time_slot': time_slot,
            'queue_length': current_length,
            'sim_time': self.env.now
        })

def secretarial_work(env, handler_pool, handler):
    """Process for secretarial work"""
    try:
        print(f'{env.now:.2f}: Handler {handler.id} starting secretarial work')
        # Simulate secretarial work duration
        yield env.timeout(3600)  # 1 hour of secretarial work
        print(f'{env.now:.2f}: Handler {handler.id} completed secretarial work')
        handler.is_secretarial = False
    except Exception as e:
        print(f"Error in secretarial work: {str(e)}")
        raise

def call_process(env, handler_pool, time_slot, day):
        """Process a single call"""
    try:
        print(f'{env.now:.2f}: Starting call process for time slot {time_slot}')
        
        # Record queue length at arrival
        queue_length = len(handler_pool.handlers.get_queue)
        handler_pool.record_queue_length(time_slot)
        print(f'{env.now:.2f}: Queue length at arrival: {queue_length}')
        
        # Record wait start time
        wait_start = env.now
        
        # Get a handler from the pool
        handler = yield from handler_pool.get_handler()
        print(f'{env.now:.2f}: Got handler {handler.id}')
        
        # Calculate actual wait time
        wait_time = env.now - wait_start
            
            # Get call duration from pattern
        call_duration = call_time_pattern.loc[
            (call_time_pattern['Day'] == day) & 
            (call_time_pattern['Time Slot'] == time_slot), 
                'Average Call Time (s)'
            ].values[0]
        
        # Scale down call duration for testing
        call_duration = min(call_duration, 60)  # Cap at 60 seconds for testing
        
        print(f'{env.now:.2f}: Processing call with duration {call_duration:.2f}')
            
            # Simulate call duration
        yield env.timeout(call_duration)
        
        # Return handler to pool
        handler_pool.put(handler)
        
        # Record results
        handler_pool.wait_times.append({
            'time_slot': time_slot,
            'wait_time': wait_time,
            'queue_length': queue_length,
            'sim_time': env.now
        })
        handler_pool.debug_stats['calls_processed'] += 1
        
        print(f'{env.now:.2f}: Call completed. Total calls processed: {handler_pool.debug_stats["calls_processed"]}')
        
    except Exception as e:
        st.error(f"Error in call process: {str(e)}")
        print(f"Error in call process: {str(e)}")
        raise

def run_simulation(handler_pool, daily_pattern, call_time_pattern, simulation_days):
    """Run the simulation for specified number of days"""
    try:
        print(f'Starting simulation for {simulation_days} days')
        
        # Convert time slots to simulation time
        def time_to_sim_time(t):
            if isinstance(t, str):
                h, m = map(int, t.split(':'))
            else:
                h, m = t.hour, t.minute
            return (h - 8) * 3600 + m * 60  # Start at 8:00 = 0
        
        for day in range(simulation_days):
            print(f'Starting day {day + 1}')
            
            # Sort time slots by time
            sorted_pattern = daily_pattern.sort_values('Time Slot')
            
            for _, row in sorted_pattern.iterrows():
                    time_slot = row['Time Slot']
                sim_time = time_to_sim_time(time_slot)
                    num_calls = int(row['Average'])
                    
                print(f'Current sim time: {handler_pool.env.now:.2f}, Processing time slot {time_slot} (sim time: {sim_time:.2f}) with {num_calls} calls')
                
                # Wait until we reach this time slot
                if handler_pool.env.now < sim_time:
                    wait_time = sim_time - handler_pool.env.now
                    print(f'Waiting {wait_time:.2f} seconds to reach time slot {time_slot}')
                    yield handler_pool.env.timeout(wait_time)
                
                # Update staffing based on time
                if time_slot < time(12, 30):
                    print(f'{handler_pool.env.now:.2f}: Morning shift - target staff: {morning_staff}')
                    while handler_pool.curr_cnt < morning_staff:
                        handler_pool.add_handler()
                    while handler_pool.curr_cnt > morning_staff:
                        handler_pool.env.process(handler_pool.remove_handler())
                else:
                    print(f'{handler_pool.env.now:.2f}: Afternoon shift - target staff: {afternoon_staff}')
                    # For afternoon shift, transition excess handlers to secretarial work
                    excess_handlers = handler_pool.curr_cnt - afternoon_staff
                    if excess_handlers > 0:
                        # Get idle handlers first
                        idle_handlers = [h for h in handler_pool.handlers.items if not h.is_secretarial]
                        for handler in idle_handlers[:excess_handlers]:
                            handler_pool.transition_to_secretarial(handler)
                            handler_pool.env.process(secretarial_work(handler_pool.env, handler_pool, handler))
                    
                    # Update target count
                    handler_pool.target_cnt = afternoon_staff
                
                # Create calls for this time slot
                for i in range(num_calls):
                    print(f'{handler_pool.env.now:.2f}: Creating call {i+1}/{num_calls}')
                    handler_pool.env.process(call_process(handler_pool.env, handler_pool, time_slot, row['Day']))
                    # Add small delay between calls
                    yield handler_pool.env.timeout(1)
                
            # Wait until end of day
            end_of_day = time_to_sim_time(time(18, 30))
            if handler_pool.env.now < end_of_day:
                wait_time = end_of_day - handler_pool.env.now
                print(f'Waiting {wait_time:.2f} seconds to reach end of day')
                yield handler_pool.env.timeout(wait_time)
                
        print('Simulation completed')
        print('Debug Statistics:')
        print(f'Total calls processed: {handler_pool.debug_stats["calls_processed"]}')
        print(f'Handlers added: {handler_pool.debug_stats["handlers_added"]}')
        print(f'Handlers removed: {handler_pool.debug_stats["handlers_removed"]}')
        print(f'Secretarial transitions: {handler_pool.debug_stats["secretarial_transitions"]}')
        
    except Exception as e:
        st.error(f"Error in simulation: {str(e)}")
        print(f"Error in simulation: {str(e)}")
        raise

# Streamlit UI
st.title("Call Center Discrete Event Simulation 🎯")
st.write("Simulate call center operations with variable staffing levels")

# Check if data is loaded
if 'processed_data' not in st.session_state or not st.session_state['processed_data']['data_loaded']:
    st.warning("Please load data in the Data Loader page first")
    st.stop()

# Get data from session state
daily_pattern = st.session_state['processed_data']['daily_pattern']
call_time_pattern = st.session_state['processed_data']['call_time_pattern']

# Simulation Parameters
st.header("Simulation Parameters")

# Time settings
col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("Start Time", time(8, 0))
with col2:
    end_time = st.time_input("End Time", time(18, 30))

# Staffing levels
col1, col2 = st.columns(2)
with col1:
    morning_staff = st.number_input("Morning Staff (until 12:30)", min_value=1, value=5)
with col2:
    afternoon_staff = st.number_input("Afternoon Staff (after 12:30)", min_value=1, value=3)

# Simulation settings
simulation_days = st.number_input("Number of Days to Simulate", min_value=1, value=1)

# Run Simulation Button
if st.button("Run Simulation"):
    try:
        with st.spinner("Running simulation..."):
            print('Initializing simulation...')
            # Create environment first
            env = simpy.Environment()
            
            # Initialize handler pool with environment
            handler_pool = CallHandlerPool(env, morning_staff)
            
            # Run simulation
            print('Starting simulation process...')
            env.process(run_simulation(handler_pool, daily_pattern, call_time_pattern, simulation_days))
            print('Running simulation...')
            env.run()
            print('Simulation run completed')
            
            # Process results
            if not handler_pool.wait_times:
                st.warning("No calls were processed in the simulation. Try adjusting the parameters.")
                st.stop()
                
            # Convert results to DataFrame
            results_df = pd.DataFrame(handler_pool.wait_times)
            queue_df = pd.DataFrame(handler_pool.queue_lengths)
            
            # Debug: Show the structure of our data
            st.write("Debug: Call Results DataFrame columns:", results_df.columns.tolist())
            st.write("Debug: First few rows of call data:", results_df.head())
            st.write("Debug: Queue Length DataFrame columns:", queue_df.columns.tolist())
            st.write("Debug: First few rows of queue data:", queue_df.head())
                
            # Calculate statistics by time slot
            call_stats = results_df.groupby('time_slot').agg({
                'wait_time': ['mean', 'std', 'count'],
                'queue_length': ['mean', 'max']
            }).reset_index()
            
            queue_stats = queue_df.groupby('time_slot').agg({
                'queue_length': ['mean', 'max', 'count']
            }).reset_index()
            
            # Flatten the multi-level columns
            call_stats.columns = ['_'.join(col).strip() for col in call_stats.columns.values]
            queue_stats.columns = ['_'.join(col).strip() for col in queue_stats.columns.values]
            
            # Display results
            st.header("Simulation Results")
            
            # Create visualizations
            fig_wait = px.line(call_stats, 
                             x='time_slot_', 
                             y='wait_time_mean',
                             error_y='wait_time_std',
                             title='Average Wait Time by Time Slot')
            st.plotly_chart(fig_wait)
            
            fig_queue = px.line(queue_stats, 
                              x='time_slot_', 
                              y='queue_length_mean',
                              title='Average Queue Length by Time Slot')
            st.plotly_chart(fig_queue)
            
            # Display detailed statistics
            st.subheader("Call Processing Statistics")
            st.dataframe(call_stats)
            
            st.subheader("Queue Length Statistics")
            st.dataframe(queue_stats)
            
    except Exception as e:
        st.error(f"Error running simulation: {str(e)}")
        print(f"Error running simulation: {str(e)}")
        st.stop()

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