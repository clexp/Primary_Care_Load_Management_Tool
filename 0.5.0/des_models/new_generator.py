import simpy
import random

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
    
    # Generator function for call arrivals
    def generate_calls(env, call_handler):
        call_id = 0
        while True:  # Keep generating calls indefinitely
            # Create a new call
            env.process(handle_call(env, call_id, call_handler))
            call_id += 1
            
            # Wait for next call
            # Using exponential distribution for inter-arrival times
            next_call = random.expovariate(1.0 / 2.0)  # mean time between calls = 2 minutes
            yield env.timeout(next_call)
    
    # Start the call generator
    env.process(generate_calls(env, call_handler))

if __name__ == '__main__':
    # Create environment
    env = simpy.Environment()
    
    # Start the simulation
    call_center_simulation(env)
    
    # Run the simulation
    env.run(until=20)  # Run for 20 time units