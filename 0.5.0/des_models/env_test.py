# test_simpy.py
import simpy
import random

def test_simulation():
    # Create a SimPy environment
    env = simpy.Environment()
    
    # Create a resource (e.g., call handler)
    call_handler = simpy.Resource(env, capacity=1)
    
    # Define a simple process
    def process(env, name, resource):
        print(f'{name} requesting resource at {env.now}')
        with resource.request() as req:
            yield req
            print(f'{name} got resource at {env.now}')
            yield env.timeout(2)
            print(f'{name} released resource at {env.now}')
    
    # Add two processes
    env.process(process(env, 'Process 1', call_handler))
    env.process(process(env, 'Process 2', call_handler))
    
    # Run the simulation
    env.run(until=10)

if __name__ == '__main__':
    test_simulation()