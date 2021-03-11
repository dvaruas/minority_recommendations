# This plot is to get the degree distribution for empirical network.
# Single plot
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#-------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.degree_distribution import DegreeDistributionPlotPoints
from code.crawled_data.facebook.facebook_data_manager import FacebookNetwork


if __name__ == "__main__":
    obj = FacebookNetwork()
    info = obj.get_network_info(all_params={"project" : "Swarthmore42"})
    info = info.pop()

    cobj = ComputationJob()
    cobj.set_network_path(path=info["graph"])
    cobj.set_attribute(path=info["type"], name="type",
        modify_func=lambda x : (int(x[0]), "minority" if x[1] == info["minority"] else "majority"))

    plot_data = DegreeDistributionPlotPoints.get_plot_points(job_objs=[cobj])
    plt.loglog(plot_data["minority"]["x"], plot_data["minority"]["y"], "ro", markersize=3, label="minority")
    plt.loglog(plot_data["majority"]["x"], plot_data["majority"]["y"], "bo", markersize=3, label="majority")

    plt.xticks(fontsize='large')
    plt.yticks(fontsize='large')
    plt.xlabel("$Degree(k)$", fontsize=12)
    plt.ylabel("$p(k)$", fontsize=12)
    plt.legend(fontsize='large')
    plt.tight_layout()
    plt.show()
