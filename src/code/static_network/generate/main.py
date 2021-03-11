import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import argparse
import itertools
from multiprocessing import Pool

from code.static_network.generate.helper_job import generate_pa_homophily_network


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Growing Networks")
    parser.add_argument("--debug", "-d", action="store_true", help="Turn on Debug Mode")
    parser.add_argument("--redo", "-r", action="store_true", help="Redo the Jobs again")
    parser.add_argument("--workers", "-w", type=int, default=1, help="Number of worker processes, default : single process")
    parser.add_argument("--silent", "-s", action="store_true", help="Do not show logs any logs")
    args = parser.parse_args()

    simulations = [1]#[1, 2, 3, 4, 5]
    homophily = [0.0, 0.2, 0.5, 0.8, 1.0]
    minority_probability = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]

    total_nodes = 5000
    edges_per_iteration = 2
    initial_nodes = 2

    job_name_start = 150
    pool_jobs = []
    for (h, m_frac, s) in itertools.product(homophily, minority_probability, simulations):
        job_name = f"Job_{job_name_start}"
        job_name_start += 1

        pool_jobs.append({"simulation" : s, "homophily" : h, "minority_probability" : m_frac,
            "total_nodes" : total_nodes, "edges_per_iteration" : edges_per_iteration,
            "initial_nodes" : initial_nodes, "job_name" : job_name, "parse_args" : args})

    with Pool(args.workers) as pool:
        pool.map(generate_pa_homophily_network, pool_jobs)
