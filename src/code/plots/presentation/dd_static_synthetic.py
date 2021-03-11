# This plot is to get the degree distribution for synthetic static networks.
# Minority fraction = 0.2
# homophily values in x-axis
# single y-axis
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.degree_distribution import DegreeDistributionPlotPoints
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]

    fig, ax = plt.subplots(nrows=1, ncols=len(homophilies), sharex=True, sharey=True, figsize=(15, 3))
    obj = StaticNetwork()

    for i, h in enumerate(homophilies):
        params ={"homophily" : h,
                 "minority_probability" : 0.2,
                 "total_nodes" : 1000}
        paths = obj.get_job_paths(all_params=params)
        comp_jobs = []
        for path in paths:
            cobj = ComputationJob()
            cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
            comp_jobs.append(cobj)
        plot_data = DegreeDistributionPlotPoints.get_plot_points(job_objs=comp_jobs)
        ax[i].loglog(plot_data["minority"]["x"], plot_data["minority"]["y"], "ro", markersize=3, label="minority")
        ax[i].loglog(plot_data["majority"]["x"], plot_data["majority"]["y"], "bo", markersize=3, label="majority")
        ax[i].tick_params(labelsize='large')
        ax[i].set_xlabel("$Degree(k)$", fontsize=12)

    ax[0].set_ylabel("$p(k)$", fontsize=12)
    plt.tight_layout()
    plt.show()
