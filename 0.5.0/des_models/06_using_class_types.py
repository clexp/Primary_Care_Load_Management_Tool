import simpy
import random
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SimulationConfig:
    """Configuration parameters for the simulation"""
    # Time parameters
    start_time: int = 0  # minutes since 8:00
    end_time: int = 600  # 10 hours (8:00 to 18:00)
    
    # Resource parameters
    number_of_handlers: int = 2
    
    # Call parameters
    mean_call_duration: float = 4.0  # minutes
    
    # Trial parameters
    number_of_runs: int = 10

class g:
    """Global parameters and environment"""
    def __init__(self):
        # Time parameters
        self.sim_duration = 600  # 10 hours (8:00 to 18:00)
        
        # Resource parameters
        self.number_of_handlers = 2
        
        # Create SimPy environment
        self.env = simpy.Environment()
        self.call_handlers = simpy.Resource(self.env, capacity=self.number_of_handlers)
        
    def get_arrival_rate(self, current_time):
        """Returns mean time between calls based on time of day"""
        if current_time < 60:  # 8:00-9:00
            return 0.5
        elif current_time < 120:  # 9:00-10:00
            return 1.0
        elif current_time < 240:  # 10:00-12:00
            return 2.0
        elif current_time < 360:  # 12:00-14:00
            return 3.0
        elif current_time < 480:  # 14:00-16:00
            return 2.0
        else:  # 16:00-18:00
            return 4.0

class Caller:
    """Entity representing a caller in the system"""
    def __init__(self, caller_id):
        self.id = caller_id
        self.arrival_time = 0
        self.queue_time = 0
        self.service_time = 0
        self.completion_time = 0
        self.abandoned = False

class Model:
    """Main simulation model"""
    def __init__(self, run_number):
        self.run_number = run_number
        self.g = g()
        self.caller_counter = 0
        # Initialize results DataFrame with columns
        self.results_df = pd.DataFrame(columns=[
            'arrival_time', 'queue_time', 'service_time', 
            'completion_time', 'abandoned'
        ])
        
    def handle_call(self, caller):
        """Process a single call"""
        print(f'Call {caller.id} arrives at {self.g.env.now}')
        caller.arrival_time = self.g.env.now
        
        with self.g.call_handlers.request() as req:
            print(f'Call {caller.id} waiting for handler at {self.g.env.now}')
            yield req
            
            # Calculate queue time
            caller.queue_time = self.g.env.now - caller.arrival_time
            
            print(f'Call {caller.id} being handled at {self.g.env.now}')
            caller.service_time = random.uniform(2, 5)
            yield self.g.env.timeout(caller.service_time)
            
            # Record completion
            caller.completion_time = self.g.env.now
            
            # Store results in DataFrame
            self.results_df.loc[caller.id] = {
                'arrival_time': caller.arrival_time,
                'queue_time': caller.queue_time,
                'service_time': caller.service_time,
                'completion_time': caller.completion_time,
                'abandoned': caller.abandoned
            }
            
            print(f'Call {caller.id} completed at {self.g.env.now}')
    
    def generate_calls(self):
        """Generator for call arrivals"""
        while True:
            self.caller_counter += 1
            caller = Caller(self.caller_counter)
            
            self.g.env.process(self.handle_call(caller))
            
            # Get next call arrival time
            mean_time_between_calls = self.g.get_arrival_rate(self.g.env.now)
            next_call = random.expovariate(1.0 / mean_time_between_calls)
            yield self.g.env.timeout(next_call)
    
    def run(self):
        """Run the simulation"""
        self.g.env.process(self.generate_calls())
        self.g.env.run(until=self.g.sim_duration)

class Trial:
    """Manages multiple simulation runs"""
    def __init__(self):
        self.number_of_runs = 10
        self.models = []
        self.trial_results = pd.DataFrame()
        
    def run_trial(self):
        """Run multiple simulations"""
        for run in range(self.number_of_runs):
            print(f"\nStarting Run {run + 1}")
            model = Model(run)
            model.run()
            self.models.append(model)
            
            # Store results
            run_results = {
                'run_number': run,
                'mean_queue_time': model.results_df['queue_time'].mean(),
                'mean_service_time': model.results_df['service_time'].mean(),
                'total_calls': len(model.results_df),
                'abandoned_calls': model.results_df['abandoned'].sum()
            }
            self.trial_results = pd.concat([
                self.trial_results,
                pd.DataFrame([run_results])
            ])

    def get_summary_statistics(self) -> Dict:
        """Get summary statistics across all runs"""
        return {
            'mean_queue_time': self.trial_results['mean_queue_time'].mean(),
            'mean_service_time': self.trial_results['mean_service_time'].mean(),
            'total_calls': self.trial_results['total_calls'].sum(),
            'abandoned_calls': self.trial_results['abandoned_calls'].sum()
        }

if __name__ == '__main__':
    # Create and run a trial
    trial = Trial()
    trial.run_trial()
    
    # Print summary of results
    print("\nTrial Results:")
    print(trial.trial_results)