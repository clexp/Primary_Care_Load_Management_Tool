import simpy
import numpy as np
from datetime import datetime, time
import pandas as pd

class CallCenterSimulation:
    def __init__(self, call_volume, staff_levels, call_duration_mean, call_duration_std, 
                 simulation_duration=480, time_step=1):
        """
        Initialize the call center simulation.
        
        Args:
            call_volume (dict): Dictionary with time slots as keys and expected calls per minute as values
            staff_levels (dict): Dictionary with time slots as keys and number of staff as values
            call_duration_mean (float): Mean call duration in minutes
            call_duration_std (float): Standard deviation of call duration in minutes
            simulation_duration (int): Total simulation duration in minutes
            time_step (int): Time step in minutes
        """
        self.env = simpy.Environment()
        self.call_volume = call_volume
        self.staff_levels = staff_levels
        self.call_duration_mean = call_duration_mean
        self.call_duration_std = call_duration_std
        self.simulation_duration = simulation_duration
        self.time_step = time_step
        
        # Initialize resources and queues
        self.call_handlers = simpy.Resource(self.env, capacity=staff_levels[0])
        self.call_queue = simpy.Store(self.env)
        
        # Initialize metrics
        self.wait_times = []
        self.queue_lengths = []
        self.times = []
        
    def get_staff_level(self, current_time):
        """Get the appropriate staff level for the current time."""
        for time_slot, staff in self.staff_levels.items():
            if time_slot[0] <= current_time < time_slot[1]:
                return staff
        return self.staff_levels[list(self.staff_levels.keys())[-1]]
    
    def get_call_volume(self, current_time):
        """Get the expected call volume for the current time."""
        for time_slot, volume in self.call_volume.items():
            if time_slot[0] <= current_time < time_slot[1]:
                return volume
        return self.call_volume[list(self.call_volume.keys())[-1]]
    
    def call_process(self, call_id):
        """Process a single call."""
        arrival_time = self.env.now
        
        # Request a call handler
        with self.call_handlers.request() as request:
            yield request
            
            # Calculate wait time
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            self.queue_lengths.append(len(self.call_queue.items))
            self.times.append(self.env.now)
            
            # Generate call duration
            call_duration = np.random.lognormal(
                mean=np.log(self.call_duration_mean),
                sigma=np.log(self.call_duration_std)
            )
            
            # Process the call
            yield self.env.timeout(call_duration)
    
    def run_simulation(self):
        """Run the simulation."""
        call_id = 0
        
        while self.env.now < self.simulation_duration:
            # Update staff level if needed
            current_staff = self.get_staff_level(self.env.now)
            if self.call_handlers.capacity != current_staff:
                self.call_handlers = simpy.Resource(self.env, capacity=current_staff)
            
            # Generate calls based on current volume
            current_volume = self.get_call_volume(self.env.now)
            num_calls = np.random.poisson(current_volume)
            
            for _ in range(num_calls):
                self.env.process(self.call_process(call_id))
                call_id += 1
            
            yield self.env.timeout(self.time_step)
    
    def get_results(self):
        """Get simulation results as a DataFrame."""
        results = pd.DataFrame({
            'time': self.times,
            'wait_time': self.wait_times,
            'queue_length': self.queue_lengths
        })
        
        # Calculate statistics
        stats = {
            'mean_wait_time': results['wait_time'].mean(),
            'max_wait_time': results['wait_time'].max(),
            'mean_queue_length': results['queue_length'].mean(),
            'max_queue_length': results['queue_length'].max(),
            'total_calls': len(results)
        }
        
        return results, stats

def run_multiple_simulations(n_simulations, **simulation_params):
    """
    Run multiple simulations and aggregate results.
    
    Args:
        n_simulations (int): Number of simulations to run
        **simulation_params: Parameters for the simulation
    
    Returns:
        tuple: (aggregated results DataFrame, average statistics)
    """
    all_results = []
    all_stats = []
    
    for _ in range(n_simulations):
        sim = CallCenterSimulation(**simulation_params)
        sim.env.process(sim.run_simulation())
        sim.env.run()
        results, stats = sim.get_results()
        all_results.append(results)
        all_stats.append(stats)
    
    # Aggregate results
    avg_stats = {
        'mean_wait_time': np.mean([s['mean_wait_time'] for s in all_stats]),
        'max_wait_time': np.mean([s['max_wait_time'] for s in all_stats]),
        'mean_queue_length': np.mean([s['mean_queue_length'] for s in all_stats]),
        'max_queue_length': np.mean([s['max_queue_length'] for s in all_stats]),
        'total_calls': np.mean([s['total_calls'] for s in all_stats])
    }
    
    return all_results, avg_stats 