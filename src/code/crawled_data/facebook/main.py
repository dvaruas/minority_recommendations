# Make recommendations for the Facebook Networks
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import argparse
import itertools
from multiprocessing import Pool

from code.crawled_data.facebook.facebook_data_manager import FacebookNetwork
from code.crawled_data.facebook.globals import FACEBOOK_DATA_PATH
from code.crawled_data.facebook.helper_job import get_all_recommendations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Recommendations")
    parser.add_argument("--debug", "-d", action="store_true", help="Turn on Debug Mode")
    parser.add_argument("--redo", "-r", action="store_true", help="Redo the Jobs again")
    parser.add_argument("--workers", "-w", type=int, default=1, help="Number of worker processes, default : single process")
    parser.add_argument("--silent", "-s", action="store_true", help="Do not show logs any logs")
    args = parser.parse_args()

    chosen_projects = ["Caltech36", "Reed98", "Haverford76", "Simmons81", "Swarthmore42"]

    recommendation_strategies = ["adamic_adar", "twitter_rank", "top_rank", "ranked_bandit", "pa_homophily"]
    ranking_control = [0.0, 0.5, 1.0]

    recommendations_dir = os.path.join(FACEBOOK_DATA_PATH, "recommendations")
    if not os.path.exists(recommendations_dir):
        os.mkdir(recommendations_dir)

    pool_jobs = []
    obj = FacebookNetwork()
    for project in chosen_projects:
        info = obj.get_network_info(all_params={"project" : project})
        if len(info) == 0:
            print(f"Project {project} entry not found in DB.")
            break
        elif len(info) > 1:
            print(f"Project {project} has multiple entries in DB, please check DB!")
            break
        else:
            info = info[0]
            if not os.path.exists(info["graph"]):
                print(f"Project {project} does not have adjlist file in data path")
                break
            if not os.path.exists(info["type"]):
                print(f"Project {project} does not have gender file in data path")
                break
            if not os.path.exists(info["recommendations_dir"]):
                os.mkdir(info["recommendations_dir"])

            for strategy, rc in itertools.product(recommendation_strategies, ranking_control):
                job_info = {"job" : project,
                            "recommendation_strategy" : strategy,
                            "ranking_factor" : rc,
                            "minority" : info["minority"],
                            "minority_homophily" : round(info["minority_homophily"], 2),
                            "majority_homophily" : round(info["majority_homophily"], 2),
                            "recommendations_dir" : info["recommendations_dir"],
                            "graph_path" : info["graph"],
                            "type_path" : info["type"],
                            "parser_args" : args}
                pool_jobs.append(job_info)
    else:
        with Pool(args.workers) as pool:
            pool.map(get_all_recommendations, pool_jobs)
