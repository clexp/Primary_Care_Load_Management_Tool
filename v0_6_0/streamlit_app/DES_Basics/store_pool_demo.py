"""
    Simple demo of a pool of riders delivering packages where the 
    number of riders can change over time

    Idel riders are keep in a store that is wrapped in a class
    to manage the number of riders

    Programmer Michael R. Gibbs
"""

import simpy
import random

class Rider():
    """
        quick class to track the riders that deliver packages
    """

    # tracks the next id to be assigned to a rider
    next_id = 1

    def __init__(self):

        self.id = Rider.next_id
        Rider.next_id += 1

class Pack():
    """
        quick class to track the packages
    """

    # tracks the next id to be assigned to a pack
    next_id = 1

    def __init__(self):

        self.id = Pack.next_id
        Pack.next_id += 1

class RiderPool():
    """
        Pool of riders where the number of riders can be changed
    """

    def __init__(self, env, start_riders=10):

        self.env = env

        # tracks the number of riders we need
        self.target_cnt = start_riders

        # tracks the number of riders we have
        self.curr_cnt = start_riders

        # the store idle riders
        self.riders = simpy.Store(env)

        # stores do not start with objects like resource pools do.
        # need to add riders yourself as part of set up
        self.riders.items = [Rider() for _ in range(start_riders)]
 

    def add_rider(self):
        """
            Add a rider to the pool
        """

        self.target_cnt += 1


        if self.curr_cnt < self.target_cnt:
            # need to add a rider to the pool to get to the target
            rider = Rider()
            self.riders.put(rider)
            self.curr_cnt += 1
            print(f'{env.now:0.2f} rider {rider.id} added')

        else:
            # already have enough riders,
            # must have tried to reduce the rider pool while all riders were busy
            # In effect we are cancelling a previous remove rider call
            print(f'{env.now:0.2f} keeping rider scheduled to be removed instead of adding')

    def remove_rider(self):
        """
            Remove a rider from the pool

            If all the riders are busy, the actual removal of a rider
            will happen when a that rider finishes it current task and is
            tried to be put/returned back into the pool
        """

        self.target_cnt -= 1

        if self.curr_cnt > self.target_cnt:
            if len(self.riders.items) > 0:
                # we have a idle rider that we can remove now

                rider = yield self.riders.get()
                self.curr_cnt -= 1
                print(f'{env.now:0.2f} rider {rider.id} removed from store')

            else:
                # wait for a rider to be put back to the pool
                pass
        

    def get(self):
        """
            Get a rider from the pool

            returns a get request that can be yield to, not a rider
        """

        rider_req = self.riders.get()

        return rider_req

    def put(self, rider):
        """
            put a rider pack into the pool
        """

        if self.curr_cnt <= self.target_cnt:
            # still need the rider
            self.riders.put(rider)
        else:
            # have tool many riders, do not add back to pool
            self.curr_cnt -= 1
            print(f'{env.now:0.2f} rider {rider.id} removed on return to pool')

def gen_packs(env, riders):
    """
        generates the arrival of packages to be delivered by riders
    """

    while True:

        yield env.timeout(random.randint(1,4))
        pack = Pack()

        env.process(ship_pack(env, pack, riders))

def ship_pack(env, pack, riders):
    """
        The process of a rider delivering a packages
    """

    print(f'{env.now:0.2f} pack {pack.id} getting rider')

    rider = yield riders.get()

    print(f'{env.now:0.2f} pack {pack.id} has rider {rider.id}')

    # trip time
    yield env.timeout(random.randint(5,22))

    riders.put(rider)

    print(f'{env.now:0.2f} pack {pack.id} delivered')

def rider_sched(env, riders):
    """
        Changes the number of riders in rider pool over time
    """


    yield env.timeout(30)
    # time to remove a few riders

    print(f'{env.now:0.2f} -- reducing riders')
    print(f'{env.now:0.2f} -- request queue len {len(riders.riders.get_queue)}')
    print(f'{env.now:0.2f} -- rider store len {len(riders.riders.items)}')

    for _ in range(5):
        env.process(riders.remove_rider())

    yield env.timeout(60)
    # time to add back some riders

    print(f'{env.now:0.2f} -- adding riders ')
    for _ in range(2):
        riders.add_rider()


# run the model
env = simpy.Environment()
riders = RiderPool(env, 10)

env.process(gen_packs(env, riders))
env.process(rider_sched(env, riders))

env.run(100)

print(f'{env.now:0.2f} -- end rider count {riders.target_cnt}')