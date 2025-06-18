import simpy

def staff_blocker(env, resource, num_to_block, until_time):
    # Block num_to_block slots by requesting and holding them until until_time
    reqs = [resource.request() for _ in range(num_to_block)]
    for req in reqs:
        yield req
    yield env.timeout(until_time - env.now)  # Hold until desired time

env = simpy.Environment()
staff = simpy.Resource(env, capacity=5)

# At time 0, all 5 staff are available
# At time 240 (e.g., 4 hours in), block 2 staff for the rest of the day
env.process(staff_blocker(env, staff, num_to_block=2, until_time=480))  # Simulate 8-hour day

# Add your call handling processes here

env.run(until=480)