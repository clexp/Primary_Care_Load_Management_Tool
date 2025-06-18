
# Basic Call Center DES model

import simpy
import random
import pandas as pd

class g:
    time_units_between_caller_arrivals = 5
    mean_call_duration = 6
    number_of_handlers = 1
    sim_duration = 1440
    caller_inter = 5
    mean_call_time = 6
    number_of_runs = 10

class Caller:
    def __init__(self, caller_id):
        self.id = caller_id
        self.q_time_handler = 0

class Model:
    def __init__(self, run_number):
        # Create a SimPy environment
        self.env = simpy.Environment()

        # Create a caller counter
        self.caller_counter = 0

        # Create a SimPy resource for call handlers
        self.handler = simpy.Resource(self.env, capacity=g.number_of_handlers)

        # Store the run number
        self.run_number = run_number

        # Create results DataFrame
        self.results_df = pd.DataFrame()
        self.results_df["Caller ID"] = [1]
        self.results_df["Q Time Handler"] = [0.0]
        self.results_df["Time with Handler"] = [0.0]
        self.results_df.set_index("Caller ID", inplace=True)

        # Store mean queuing time
        self.mean_q_time_handler = 0

    def generator_caller_arrivals(self):
        while True:
            # Increment caller counter
            self.caller_counter += 1

            # Create new caller
            c = Caller(self.caller_counter)

            # Start call process
            self.env.process(self.process_call(c))

            # Sample time to next caller
            sampled_inter = random.expovariate(1.0 / g.caller_inter)

            # Wait for next caller
            yield self.env.timeout(sampled_inter)

    def process_call(self, caller):
        # Record queue start time
        start_q_handler = self.env.now

        # Request handler
        with self.handler.request() as req:
            # Wait for handler
            yield req

            # Record queue end time
            end_q_handler = self.env.now

            # Calculate queue time
            caller.q_time_handler = end_q_handler - start_q_handler

            # Sample call duration
            sampled_call_time = random.expovariate(1.0 / g.mean_call_time)

            # Record results
            self.results_df.at[caller.id, "Q Time Handler"] = caller.q_time_handler
            self.results_df.at[caller.id, "Time with Handler"] = sampled_call_time

            # Process call
            yield self.env.timeout(sampled_call_time)

    def calculate_run_results(self):
        self.mean_q_time_handler = self.results_df["Q Time Handler"].mean()

    def run(self):
        # Start caller generator
        self.env.process(self.generator_caller_arrivals())

        # Run simulation
        self.env.run(until=g.sim_duration)

        # Calculate results
        self.calculate_run_results()

        # Print results
        print(f"Run Number {self.run_number}")
        print(self.results_df)

class Trial:
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] = [0]
        self.df_trial_results["Mean Q Time Handler"] = [0.0]
        self.df_trial_results.set_index("Run Number", inplace=True)

    def print_trial_results(self):
        print("Trial Results")
        print(self.df_trial_results)

    def run_trial(self):
        for run in range(g.number_of_runs):
            my_model = Model(run)
            my_model.run()

            self.df_trial_results.loc[run] = [my_model.mean_q_time_handler]

        self.print_trial_results()

if __name__ == "__main__":
    # Create and run trial
    my_trial = Trial()
    my_trial.run_trial() 