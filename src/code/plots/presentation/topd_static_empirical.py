# This plot is to get the top d% minorities for empirical network.
# single plot
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.top_d_nodes import TopDNodesPlotPoints
from code.crawled_data.facebook.facebook_data_manager import FacebookNetwork


if __name__ == "__main__":
    obj = FacebookNetwork()
    info = obj.get_network_info(all_params={"project" : "Simmons81"})
    info = info.pop()
    minority_fraction = info["minority_fraction"]

    cobj = ComputationJob()
    cobj.set_network_path(path=info["graph"])
    cobj.set_attribute(path=info["type"], name="type",
        modify_func=lambda x : (int(x[0]), "minority" if x[1] == info["minority"] else "majority"))

    plot_data = TopDNodesPlotPoints.get_plot_points(job_objs=[cobj])
    plt.plot(plot_data["x"], plot_data["y"], color='red', marker="o")

    plt.ylim(0.0, 1.0)
    plt.xticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], fontsize='large')
    plt.yticks(fontsize='large')
    plt.grid(b=True, which='major', axis='x', color='#b3b3b3', linestyle='--')
    plt.plot([0.1, 1.0], [minority_fraction, minority_fraction], color='black', linestyle="--")
    plt.xlabel("Top d% degree rank", fontsize=12)
    plt.ylabel("Fraction of minorities in top d%", fontsize=12)

    plt.tight_layout()
    plt.show()
