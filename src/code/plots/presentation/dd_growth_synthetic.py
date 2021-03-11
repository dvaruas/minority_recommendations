# This plot is to get the degree distribution for synthetic growth networks.
# Minority fraction = 0.2
# homophily values in 0.2, 0.8 in y-axis
# x-axis : [pa_homophily, adamic_adar, twitter_rank, ranked_bandits, top_rank]
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.degree_distribution import DegreeDistributionPlotPoints
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    homophilies = [0.2, 0.8]
    recommenders = ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]

    fig, ax = plt.subplots(nrows=len(homophilies), ncols=len(recommenders), sharex=True, sharey=True, figsize=(15, 5))
    obj = GrowNetwork()

    for i, h in enumerate(homophilies):
        for j, rec in enumerate(recommenders):
            params ={"homophily" : h,
                     "minority_probability" : 0.2,
                     "ranking_control" : 1.0 if rec in ["ranked_bandit", "top_rank"] else 0.0,
                     "job_type" : rec,
                     "parameter_profile" : 0}
            paths = obj.get_job_paths(all_params=params)
            comp_jobs = []
            for path in paths:
                cobj = ComputationJob()
                cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                comp_jobs.append(cobj)
            plot_data = DegreeDistributionPlotPoints.get_plot_points(job_objs=comp_jobs)
            ax[i, j].loglog(plot_data["minority"]["x"], plot_data["minority"]["y"], "ro", markersize=3, label="minority")
            ax[i, j].loglog(plot_data["majority"]["x"], plot_data["majority"]["y"], "bo", markersize=3, label="majority")
            ax[i, j].tick_params(labelsize='large')

    plt.tight_layout()
    plt.show()
