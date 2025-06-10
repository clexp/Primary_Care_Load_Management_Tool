import simpy
import random
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import math

@dataclass
class SimulationConfig:
    """Configuration parameters for the simulation"""
    start_time: int = 0
    end_time: int = 600
    max_queue_size: int = 30
    number_of_handlers: int = 4  # Fixed at 4 handlers
    mean_call_duration: float = 4.0
    retry_probability: float = 0.7
    max_retries: int = 3
    abandonment_threshold: float = 5.0  # minutes

class g:
    def __init__(self):
        self.sim_duration = 600
        self.number_of_handlers = 4  # Fixed at 4 handlers
        self.env = simpy.Environment()
        self.call_handlers = simpy.Resource(self.env, capacity=self.number_of_handlers)
        self.call_queue = simpy.Store(self.env, capacity=30)
        self.sink = simpy.Store(self.env)
        
    def get_arrival_rate(self, current_time):
        """Returns mean time between calls based on time of day"""
        if current_time < 60:  # 8:00-9:00
            return 2.0  # 0.5 calls per minute = 30 calls per hour
        elif current_time < 120:  # 9:00-10:00
            return 1.5  # 0.67 calls per minute = 40 calls per hour
        elif current_time < 240:  # 10:00-12:00
            return 1.0  # 1 call per minute = 60 calls per hour
        elif current_time < 360:  # 12:00-14:00
            return 1.5  # 0.67 calls per minute = 40 calls per hour
        elif current_time < 480:  # 14:00-16:00
            return 2.0  # 0.5 calls per minute = 30 calls per hour
        else:  # 16:00-18:00
            return 3.0  # 0.33 calls per minute = 20 calls per hour

class Caller:
    def __init__(self, caller_id):
        self.id = caller_id
        self.arrival_time = 0
        self.queue_time = 0
        self.service_time = 0
        self.completion_time = 0
        self.abandoned = False
        self.retry_count = 0
        self.bounced = False

class Model:
    def __init__(self, run_number):
        self.run_number = run_number
        self.g = g()
        self.caller_counter = 0
        self.results_df = pd.DataFrame(columns=[
            'arrival_time', 'queue_time', 'service_time', 
            'completion_time', 'abandoned', 'bounced', 'retry_count'
        ]).astype({
            'arrival_time': 'float64',
            'queue_time': 'float64',
            'service_time': 'float64',
            'completion_time': 'float64',
            'abandoned': 'bool',
            'bounced': 'bool',
            'retry_count': 'int64'
        })
        self.queue_length_history = []
        
    def handle_call(self, caller):
        """Process a single call"""
        caller.arrival_time = self.g.env.now
        
        # Record the call immediately when it arrives
        self.results_df.loc[caller.id] = {
            'arrival_time': caller.arrival_time,
            'queue_time': 0.0,
            'service_time': 0.0,
            'completion_time': 0.0,
            'abandoned': False,
            'bounced': False,
            'retry_count': caller.retry_count
        }
        
        # Track queue length before adding new caller
        current_queue_length = len(self.g.call_queue.items)
        self.queue_length_history.append((self.g.env.now, current_queue_length))
        
        # Try to enter queue
        if len(self.g.call_queue.items) < 30:
            yield self.g.call_queue.put(caller)
        else:
            caller.bounced = True
            self.results_df.at[caller.id, 'bounced'] = True
            yield self.g.sink.put(caller)
            return
            
        # Wait for handler
        with self.g.call_handlers.request() as req:
            wait_start_time = self.g.env.now
            yield req
            caller.queue_time = (self.g.env.now - caller.arrival_time) / 60.0  # Convert to minutes
            
            # Now check for abandonment
            if random.random() < (1 - math.exp(-caller.queue_time/5.0)):
                caller.abandoned = True
                self.results_df.at[caller.id, 'abandoned'] = True
                self.g.call_queue.get()
                return
                
            # Service time is just the call duration
            caller.service_time = random.uniform(2, 5)  # Already in minutes
            yield self.g.env.timeout(caller.service_time * 60.0)  # Convert to seconds for timeout
            
            caller.completion_time = self.g.env.now
            
            # Update results for completed calls
            self.results_df.at[caller.id, 'queue_time'] = caller.queue_time
            self.results_df.at[caller.id, 'service_time'] = caller.service_time
            self.results_df.at[caller.id, 'completion_time'] = caller.completion_time
            
            # Handle retries for bounced calls
            if caller.bounced and caller.retry_count < 3:
                if random.random() < 0.7:
                    caller.retry_count += 1
                    retry_delay = random.uniform(5, 30)
                    yield self.g.env.timeout(retry_delay)
                    self.g.env.process(self.handle_call(caller))

    def generate_calls(self):
        """Generator for call arrivals"""
        while True:
            self.caller_counter += 1
            caller = Caller(self.caller_counter)
            self.g.env.process(self.handle_call(caller))
            
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
                'abandoned_calls': model.results_df['abandoned'].sum(),
                'bounced_calls': model.results_df['bounced'].sum(),
                'max_queue_length': max([q[1] for q in model.queue_length_history]),
                'calls_per_hour': len(model.results_df) / 10  # 10-hour day
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
            'abandoned_calls': self.trial_results['abandoned_calls'].sum(),
            'bounced_calls': self.trial_results['bounced_calls'].sum(),
            'max_queue_length': self.trial_results['max_queue_length'].max()
        }

if __name__ == '__main__':
    # Create and run a trial
    trial = Trial()
    trial.run_trial()
    
    # Print summary of results
    print("\nTrial Results:")
    print(trial.trial_results)
    print("\nSummary Statistics:")
    print(trial.get_summary_statistics())
