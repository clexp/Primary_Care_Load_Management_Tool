import simpy
import random

def get_arrival_rate(minutes_since_8am: int) -> float:
    """
    Returns the mean time between calls based on minutes since 8:00
    Args:
        minutes_since_8am: int, minutes since 8:00 (0 = 8:00, 60 = 9:00, etc.)
    Returns:
        float: mean time between calls in minutes
    """
    # Define arrival rates for different times of day
    if minutes_since_8am < 60:  # 8:00-9:00 - Very busy
        return 0.5  # Mean time between calls = 30 seconds
    elif minutes_since_8am < 120:  # 9:00-10:00 - Still busy
        return 1.0  # Mean time between calls = 1 minute
    elif minutes_since_8am < 240:  # 10:00-12:00 - Moderate
        return 2.0  # Mean time between calls = 2 minutes
    elif minutes_since_8am < 360:  # 12:00-14:00 - Lunch time
        return 3.0  # Mean time between calls = 3 minutes
    elif minutes_since_8am < 480:  # 14:00-16:00 - Moderate
        return 2.0  # Mean time between calls = 2 minutes
    else:  # 16:00-18:00 - Tapering off
        return 4.0  # Mean time between calls = 4 minutes

def call_center_simulation(env):
    # Create call handler resource
    call_handler = simpy.Resource(env, capacity=2)
    
    def handle_call(env, call_id, call_handler):
        print(f'Call {call_id} arrives at {env.now}')
        
        with call_handler.request() as req:
            print(f'Call {call_id} waiting for handler at {env.now}')
            yield req
            
            print(f'Call {call_id} being handled at {env.now}')
            call_duration = random.uniform(2, 5)
            yield env.timeout(call_duration)
            
            print(f'Call {call_id} completed at {env.now}')
    
    def generate_calls(env, call_handler):
        call_id = 0
        while True:
            # Create a new call
            env.process(handle_call(env, call_id, call_handler))
            call_id += 1
            
            # Get arrival rate for current time (env.now is minutes since 8:00)
            mean_time_between_calls = get_arrival_rate(env.now)
            
            # Generate next call arrival time
            next_call = random.expovariate(1.0 / mean_time_between_calls)
            yield env.timeout(next_call)
    
    # Start the call generator
    env.process(generate_calls(env, call_handler))

if __name__ == '__main__':
    # Create environment
    env = simpy.Environment()
    
    # Start the simulation
    call_center_simulation(env)
    
    # Run the simulation for 10 hours (8:00 to 18:00)
    env.run(until=600)  # 600 minutes = 10 hours