# modelling unavailability of staff


class g:
    # Inter-arrival times
    patient_inter = 5

    # Activity times
    mean_n_consult_time = 6

    # Resource numbers
    number_of_nurses = 1

    unav_time_nurse = 15 ##NEW
    unav_freq_nurse = 120 ##NEW

    # Simulation meta parameters
    sim_duration = 2880
    number_of_runs = 1
    warm_up_period = 1440


  ##NEW
# Generator function to obstruct a nurse resource at specified intervals
# for specified amounts of time
def obstruct_nurse(self):
    while True:
        print (f"{self.env.now:.2f}: The nurse will go on a break at around time",
                f"{(self.env.now + g.unav_freq_nurse):.2f}")

        # The generator first pauses for the frequency period
        yield self.env.timeout(g.unav_freq_nurse)

        # Once elapsed, the generator requests (demands?) a nurse with
        # a priority of -1.  This ensure it takes priority over any patients
        # (whose priority values start at 1).  But it also means that the
        # nurse won't go on a break until they've finished with the current
        # patient
        with self.nurse.request(priority=-1) as req:
            yield req

            print (f"{self.env.now:.2f}: The nurse is now on a break and will be back at",
                    f"{(self.env.now + g.unav_time_nurse):.2f}")

            # Freeze with the nurse held in place for the unavailability
            # time (ie duration of the nurse's break).  Here, both the
            # duration and frequency are fixed, but you could randomly
            # sample them from a distribution too if preferred.
            yield self.env.timeout(g.unav_time_nurse)

def run(self):
    # Start up DES generators
    self.env.process(self.generator_patient_arrivals())
    ##NEW - we also need to start up the obstructor generator now too
    self.env.process(self.obstruct_nurse())

    # Run for the duration specified in g class
    self.env.run(until=(g.sim_duration + g.warm_up_period))

    # Calculate results over the run
    self.calculate_run_results()

    return self.results_df
