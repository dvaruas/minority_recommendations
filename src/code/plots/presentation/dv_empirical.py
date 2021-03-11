# Single plots for DV, empirical
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.disparate_visibility import DVEmpiricalPlotPoints
from code.crawled_data.facebook.facebook_data_manager import FacebookNetwork


if __name__ == "__main__":
    obj = FacebookNetwork()
    info = obj.get_network_info(all_params={"project" : "Simmons81"})
    info = info.pop()

    cobj = ComputationJob()
    cobj.set_network_path(path=info["graph"])
    cobj.set_attribute(path=info["type"], name="type",
        modify_func=lambda x : (int(x[0]), "minority" if x[1] == info["minority"] else "majority"))

    method_files = {"Adamic-Adar" : (os.path.join(info["recommendations_dir"], "adamic_adar_NIL.json"), '#e86127'), # orange
                    "PA-Homophily" : (os.path.join(info["recommendations_dir"], "pa_homophily_NIL.json"), "#ab580a"), # ochre
                    "Twitter-Rank" : (os.path.join(info["recommendations_dir"], "twitter_rank_NIL.json"), '#577804'), # green
                    "Ranked-Bandit (r : 0.0)" : (os.path.join(info["recommendations_dir"], "ranked_bandit_0.0.json"), "#021b4f"), # dark blue
                    "Ranked-Bandit (r : 0.5)" : (os.path.join(info["recommendations_dir"], "ranked_bandit_0.5.json"), "#06379c"), # ligher blue
                    "Ranked-Bandit (r : 1.0)" : (os.path.join(info["recommendations_dir"], "ranked_bandit_1.0.json"), "#175ae6"), # lightest blue
                    "Top-Rank (r : 0.0)" : (os.path.join(info["recommendations_dir"], "top_rank_0.0.json"), "#a30331"), # darker pink
                    "Top-Rank (r : 0.5)" : (os.path.join(info["recommendations_dir"], "top_rank_0.5.json"), "#c7063d"), # lighter pink
                    "Top-Rank (r : 1.0)" : (os.path.join(info["recommendations_dir"], "top_rank_1.0.json"), "#fa5282") # lightest pink
                }

    plot_data = DVEmpiricalPlotPoints.get_plot_points(job_obj=cobj, methods=method_files)
    plt.grid(b=True, which='major', axis='both', color='#b3b3b3', linestyle='--')
    plt.barh(list(range(len(plot_data["x"]))), plot_data["y"], align='center', color=plot_data["color"], tick_label=plot_data["x"])
    plt.plot([0.0, 0.0], [-1, len(plot_data["x"])], color='black')
    plt.plot([(-1.0/(1.0 - info["minority_fraction"])), (-1.0/(1.0 - info["minority_fraction"]))], [-1, len(plot_data["x"])], color="black", linestyle="--")
    plt.plot([(1.0/info["minority_fraction"]), (1.0/info["minority_fraction"])], [-1, len(plot_data["x"])], color="black", linestyle="--")

    plt.xticks(fontsize='large')
    plt.yticks(fontsize='large')
    plt.xlabel("Disparate Visibility", fontsize=12)
    plt.tight_layout()

    plt.show()
