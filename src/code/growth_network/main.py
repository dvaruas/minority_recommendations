import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import argparse
import itertools
from multiprocessing import Pool

from code.growth_network.helper_job import grow_network


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Growing Networks")
    parser.add_argument("--debug", "-d", action="store_true", help="Turn on Debug Mode")
    parser.add_argument("--redo", "-r", action="store_true", help="Redo the Jobs again")
    parser.add_argument("--workers", "-w", type=int, default=1, help="Number of worker processes, default : single process")
    parser.add_argument("--silent", "-s", action="store_true", help="Do not show logs any logs")
    args = parser.parse_args()

    # Total job count - 2250
    simulations = [1] #[1, 2, 3, 4, 5]
    homophily = [0.0, 0.2, 0.5, 0.8, 1.0]
    minority_probability = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
    ranking_control = [0.0, 1.0] #[0.0, 0.5, 1.0]
    job_type = ["adamic_adar", "twitter_rank", "top_rank", "ranked_bandit", "pa_homophily"]

    pool_jobs = []
    job_names_start = {"adamic_adar" : 2250,
                       "twitter_rank" : 2310,
                       "pa_homophily" : 2370,
                       "ranked_bandit" : 2430,
                       "top_rank" : 2490}

    for h, m, s, rc, type in itertools.product(homophily, minority_probability, simulations, ranking_control, job_type):
        # Assign Job Name
        job_name = "Job_{}".format(job_names_start[type])
        job_names_start[type] += 1

        job_description = {"minority_homophily" : h, "majority_homophily" : h,
            "minority_prob" : m, "simulation" : s, "method" : type,
            "ranking_control" : rc, "job_name" : job_name, "parser_args" : args,
            "total_iterations" : 50000}

        pool_jobs.append(job_description)

    # Trim Jobs according to requirement.
    # pool_jobs = list(filter(lambda x : x["method"] == "twitter_rank" and x["simulation"] == 1, pool_jobs))

    # create all the pool jobs
    with Pool(args.workers) as pool:
        pool.map(grow_network, pool_jobs)
