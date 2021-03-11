# This plot is to get the degree growth for synthetic growth networks.
# Minority fraction = [0.1, 0.2, 0.3, 0.4, 0.5] (x-axis)
# homophily values = [0.0, 0.2, 0.5, 0.8, 1.0] (y-axis)
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.degree_growth import DegreeGrowthPlotPoints
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    minority_fractions = [0.1, 0.2, 0.3, 0.4, 0.5]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    method = "top_rank" #["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]
    ranking_control = 1.0

    fig, ax = plt.subplots(nrows=len(minority_fractions), ncols=len(homophilies), sharex=True, sharey=True, figsize=(11, 12))
    obj = GrowNetwork()

    for i, f in enumerate(minority_fractions):
        for j, h in enumerate(homophilies):
            params ={"homophily" : h,
                     "minority_probability" : f,
                     "ranking_control" : ranking_control if method in ["ranked_bandit", "top_rank"] else 0.0,
                     "job_type" : method,
                     "parameter_profile" : 0}
            paths = obj.get_job_paths(all_params=params)
            comp_jobs = []
            for path in paths:
                cobj = ComputationJob()
                cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                comp_jobs.append(cobj)
            plot_data = DegreeGrowthPlotPoints.get_plot_points(job_objs=comp_jobs)
            ax[i,j].plot(plot_data["minority"]["x"], plot_data["minority"]["y"], "r", label="minority")
            ax[i,j].plot(plot_data["majority"]["x"], plot_data["majority"]["y"], "b", label="majority")
            ax[i,j].tick_params(labelsize='large')
            if (i == len(minority_fractions) - 1):
                ax[i,j].set_xlabel("$t/t_{0}$", fontsize=12)
            if (j == 0):
                ax[i,j].set_ylabel("$\delta(t) / \delta(t_{0})$", fontsize=12)

    plt.figtext(0.11, 0.97, "h = 0.0", fontsize=12)
    plt.figtext(0.29, 0.97, "h = 0.2", fontsize=12)
    plt.figtext(0.47, 0.97, "h = 0.5", fontsize=12)
    plt.figtext(0.65, 0.97, "h = 0.8", fontsize=12)
    plt.figtext(0.85, 0.97, "h = 1.0", fontsize=12)

    plt.figtext(0.97, 0.13, "f = 0.5", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.3, "f = 0.4", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.48, "f = 0.3", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.66, "f = 0.2", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.84, "f = 0.1", fontsize=12, rotation=-90)

    plt.subplots_adjust(left=0.05, bottom=0.06, right=0.95, top=0.95, wspace=0.1, hspace=0.1)

    plt.show()
