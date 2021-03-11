import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import argparse
import itertools
from multiprocessing import Pool

from code.static_network.recommendations.helper_job import get_recommendations
from code.static_network.globals import STATIC_DATA_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Growing Networks")
    parser.add_argument("--debug", "-d", action="store_true", help="Turn on Debug Mode")
    parser.add_argument("--redo", "-r", action="store_true", help="Redo the Jobs again")
    parser.add_argument("--workers", "-w", type=int, default=1, help="Number of worker processes, default : single process")
    parser.add_argument("--silent", "-s", action="store_true", help="Do not show logs any logs")
    args = parser.parse_args()

    recommendation_strategies = ["adamic_adar", "twitter_rank", "pa_homophily", "ranked_bandit", "top_rank"]
    ranking_control = [0.0, 0.5, 1.0]

    pool_jobs = []
    for job_id in os.listdir(STATIC_DATA_PATH):
        if not job_id.startswith("Job"):
            continue

        job_path = os.path.join(STATIC_DATA_PATH, job_id)
        recommendations_dir = os.path.join(job_path, "recommendations")
        if not os.path.exists(recommendations_dir):
            os.mkdir(recommendations_dir)

        for strategy, rc in itertools.product(recommendation_strategies, ranking_control):
            pool_jobs.append({"job_path" : job_path, "recommendation_strategy" : strategy,
                "ranking_factor" : rc, "parse_args" : args})

    with Pool(args.workers) as pool:
        pool.map(get_recommendations, pool_jobs)
