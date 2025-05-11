import simpy
import random

def call_center_simulation(env):
    # Create call handler resource (capacity = 2 means 2 calls can be handled simultaneously)
    call_handler = simpy.Resource(env, capacity=2)
    
    # Define what happens when a call comes in
    def handle_call(env, call_id, call_handler):
        print(f'Call {call_id} arrives at {env.now}')
        
        # Request a call handler
        with call_handler.request() as req:
            print(f'Call {call_id} waiting for handler at {env.now}')
            yield req  # Wait until we get a handler
            
            print(f'Call {call_id} being handled at {env.now}')
            # Simulate call duration (random between 2 and 5 minutes)
            call_duration = random.uniform(2, 5)
            yield env.timeout(call_duration)
            
            print(f'Call {call_id} completed at {env.now}')
    
    # Generate some calls
    for i in range(5):
        # Create a new call process
        env.process(handle_call(env, i, call_handler))
        # Wait a random time before next call
        yield env.timeout(random.uniform(0.5, 2))

if __name__ == '__main__':
    # Create environment
    env = simpy.Environment()
    
    # Start the simulation
    env.process(call_center_simulation(env))
    
    # Run the simulation
    env.run(until=20)  # Run for 20 time units

