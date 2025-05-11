class g:
    time_units_between_customer_arrivals = 5
    mean_customer_service_time = 6
    number_of_customer_support_agents = 1
    sim_duration = 1440
    number_of_runs = 10

class Customer:
    def __init__(self, p_id):
        self.id = p_id
        self.queue_time_customer_support_agent = 0


class Model:
    # Constructor to set up the model for a run.  We pass in a run number when
    # we create a new model.
    def __init__(self, run_number):
        # Create a SimPy environment in which everything will live
        self.env = simpy.Environment()

        # Create a customer counter (which we'll use as a customer ID)
        self.customer_counter = 0

        # Create a SimPy resource to represent a customer support agent, that will live in the
        # environment created above.  The number of this resource we have is
        # specified by the capacity, and we grab this value from our g class.
        self.customer_support_agent = simpy.Resource(self.env, capacity=number_of_customer_support_agents)

        # Store the passed in run number
        self.run_number = run_number

        # Create a new Pandas DataFrame that will store some results against
        # the customer ID (which we'll use as the index).
        self.results_df = pd.DataFrame()
        self.results_df["Customer ID"] = [1]
        self.results_df["Queue Time"] = [0.0]
        self.results_df["Time with Customer Support Agent"] = [0.0]
        self.results_df.set_index("Customer ID", inplace=True)

        # Create an attribute to store the mean queuing time for the support agents
        # across this run of the model
        self.mean_queue_time_support_agent = 0

    # A generator function that represents the DES generator for customer
    # arrivals
    def generator_customer_arrivals(self):
        # We use an infinite loop here to keep doing this indefinitely whilst
        # the simulation runs
        while True:
            # Increment the customer counter by 1 (this means our first customer
            # will have an ID of 1)
            self.customer_counter += 1

            # Create a new customer - an instance of the customer Class we
            # defined above.  Remember, we pass in the ID when creating a
            # customer - so here we pass the customer counter to use as the ID.
            c = Customer(self.customer_counter)

            # Tell SimPy to start up the use_customer_service_helpline generator function with
            # this customer (the generator function that will model the
            # customer's journey through the system)
            self.env.process(self.use_customer_service_helpline (c))

            # Randomly sample the time to the next customer arriving.  Here, we
            # sample from an exponential distribution (common for inter-arrival
            # times), and pass in a lambda value of 1 / mean.  The mean
            # inter-arrival time is stored in the g class.
            sampled_inter_arrival_time = random.expovariate(1.0 / g.time_units_between_customer_arrivals)

            # Freeze this instance of this function in place until the
            # inter-arrival time we sampled above has elapsed.  Note - time in
            # SimPy progresses in "Time Units", which can represent anything
            # you like (just make sure you're consistent within the model)
            yield self.env.timeout(sampled_inter_arrival_time)

    # A generator function that represents the pathway for a customer calling our helpline
    # Here the pathway is extremely simple - a customer
    # arrives in the call system, waits to be connected to a customer support agent,
    # spends a varying amount of time being helped by the agent, and then leaves,
    # meaning the agent is free to help the next person.
    # The customer object is passed in to the generator function so we can
    # extract information from / record information to it
    def use_customer_service_helpline(self, customer):
        # Record the time the patient started queuing for a nurse
        start_q_customer_support_agent = self.env.now

        # This code says request a customer support agent resource, and do all of the following
        # block of code with that nurse resource held in place (and therefore
        # not usable by another patient)
        with self.customer_support_agent.request() as req:
            # Freeze the function until the request for a customer support agent can be met.
            # The customer is currently queuing.
            yield req

            # When we get to this bit of code, control has been passed back to
            # the generator function, and therefore the request for a customer support agent has
            # been met.  We now have the customer support agent, and have stopped queuing, so we
            # can record the current time as the time we finished queuing.
            end_q_customer_support_agent = self.env.now

            # Calculate the time this patient was queuing for the customer support agent, and
            # record it in the customer's attribute for this.
            customer.queue_time_customer_support_agent = end_q_customer_support_agent - start_q_customer_support_agent

            # Now we'll randomly sample the time this customer with the customer support agent.
            # Here, we use an Exponential distribution for simplicity, but you
            # would typically use a Log Normal distribution for a real model
            # (we'll come back to that).  As with sampling the inter-arrival
            # times, we grab the mean from the g class, and pass in 1 / mean
            # as the lambda value.
            sampled_customer_support_agent_activity_time = random.expovariate(1.0 /
                                                        g.mean_customer_service_time)

            # Here we'll store the queuing time for the customer support agent and the sampled
            # time to spend with the nurse in the results DataFrame against the
            # ID for this customer.
            #
            # In real world models, you may not want to
            # bother storing the sampled activity times - but as this is a
            # simple model, we'll do it here.
            #
            # We use a handy property of pandas called .at, which works a bit
            # like .loc.  .at allows us to access (and therefore change) a
            # particular cell in our DataFrame by providing the row and column.
            # Here, we specify the row as the patient ID (the index), and the
            # column for the value we want to update for that patient.
            self.results_df.at[customer.id, "Queue Time"] = (
                customer.queue_time_customer_support_agent)
            self.results_df.at[customer.id, "Time with Customer Support Agent"] = (
                sampled_customer_support_agent_activity_time)

            # Freeze this function in place for the activity time we sampled
            # above.  This is the patient spending time with the customer support
            # agent.
            yield self.env.timeout(sampled_customer_support_agent_activity_time)

            # When the time above elapses, the generator function will return
            # here.  As there's nothing more that we've written, the function
            # will simply end.  This is a sink.  We could choose to add
            # something here if we wanted to record something - e.g. a counter
            # for number of patients that left, recording something about the
            # patients that left at a particular sink etc.

    # This method calculates results over a single run.  Here we just calculate
    # a mean, but in real world models you'd probably want to calculate more.
    def calculate_run_results(self):
        # Take the mean of the queuing times for the nurse across patients in
        # this run of the model.
        self.mean_queue_time_support_agent = self.results_df["Time with Customer Support Agent"].mean()

    # The run method starts up the DES entity generators, runs the simulation,
    # and in turns calls anything we need to generate results for the run
    def run(self):
        # Start up our DES entity generators that create new customers.  We've
        # only got one in this model, but we'd need to do this for each one if
        # we had multiple generators.
        self.env.process(self.generator_customer_arrivals())

        # Run the model for the duration specified in g class
        self.env.run(until=g.sim_duration)

        # Now the simulation run has finished, call the method that calculates
        # run results
        self.calculate_run_results()

        # Print the run number with the customer-level results from this run of
        # the model
        print (f"Run Number {self.run_number}")
        print (self.results_df)

class Trial:
    # The constructor sets up a pandas dataframe that will store the key
    # results from each run (just the mean queuing time for the nurse here)
    # against run number, with run number as the index.
    def  __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] = [0]
        self.df_trial_results["Mean Queue Time Customer Supoprt Agent"] = [0.0]
        self.df_trial_results.set_index("Run Number", inplace=True)

    # Method to print out the results from the trial.  In real world models,
    # you'd likely save them as well as (or instead of) printing them
    def print_trial_results(self):
        print ("Trial Results")
        print (self.df_trial_results)

    # Method to run a trial
    def run_trial(self):
        # Run the simulation for the number of runs specified in g class.
        # For each run, we create a new instance of the Model class and call its
        # run method, which sets everything else in motion.  Once the run has
        # completed, we grab out the stored run results (just mean queuing time
        # here) and store it against the run number in the trial results
        # dataframe.
        for run in range(g.number_of_runs):
            my_model = Model(run)
            my_model.run()

            self.df_trial_results.loc[run] = [my_model.mean_queue_time_support_agent]

        # Once the trial (ie all runs) has completed, print the final results
        self.print_trial_results()