# This plot is to get the degree distribution for synthetic static networks.
# Minority fraction = [0.1, 0.2, 0.3, 0.4, 0.5] (x-axis)
# homophily values = [0.0, 0.2, 0.5, 0.8, 1.0] (y-axis)
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.degree_distribution import DegreeDistributionPlotPoints
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    minority_fractions = [0.1, 0.2, 0.3, 0.4, 0.5]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]

    fig, ax = plt.subplots(nrows=len(minority_fractions), ncols=len(homophilies), sharex=True, sharey=True, figsize=(11, 12))
    obj = StaticNetwork()

    for i, f in enumerate(minority_fractions):
        for j, h in enumerate(homophilies):
            params ={"homophily" : h,
                     "minority_probability" : f,
                     "total_nodes" : 1000}
            paths = obj.get_job_paths(all_params=params)
            comp_jobs = []
            for path in paths:
                cobj = ComputationJob()
                cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                comp_jobs.append(cobj)
            plot_data = DegreeDistributionPlotPoints.get_plot_points(job_objs=comp_jobs)
            ax[i,j].loglog(plot_data["minority"]["x"], plot_data["minority"]["y"], "ro", markersize=3, label="minority")
            ax[i,j].loglog(plot_data["majority"]["x"], plot_data["majority"]["y"], "bo", markersize=3, label="majority")
            ax[i,j].tick_params(labelsize='large')
            if (i == len(minority_fractions) - 1):
                ax[i,j].set_xlabel("$Degree(k)$", fontsize=12)
            if (j == 0):
                ax[i,j].set_ylabel("$p(k)$", fontsize=12)

    plt.figtext(0.13, 0.97, "h = 0.0", fontsize=12)
    plt.figtext(0.31, 0.97, "h = 0.2", fontsize=12)
    plt.figtext(0.48, 0.97, "h = 0.5", fontsize=12)
    plt.figtext(0.66, 0.97, "h = 0.8", fontsize=12)
    plt.figtext(0.85, 0.97, "h = 1.0", fontsize=12)

    plt.figtext(0.97, 0.13, "f = 0.5", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.3, "f = 0.4", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.48, "f = 0.3", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.66, "f = 0.2", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.84, "f = 0.1", fontsize=12, rotation=-90)

    plt.subplots_adjust(left=0.073, bottom=0.06, right=0.95, top=0.95, wspace=0.1, hspace=0.1)

    plt.show()
