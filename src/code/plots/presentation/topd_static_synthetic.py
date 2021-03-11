# This plot is to get the top d% minorities for synthetic static networks.
# miority fraction = 0.2
# single plot
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.top_d_nodes import TopDNodesPlotPoints
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    plot_line_colors = ['#854214', '#ed6507', '#1e800d', '#2373fc', '#2716a1'] #dark brown, light brown, green, blue, dark blue
    plt.figure(figsize=(10, 5))

    all_data = {}
    obj = StaticNetwork()

    for h, color in zip(homophilies, plot_line_colors):
        params ={"homophily" : h,
                 "minority_probability" : 0.2,
                 "total_nodes" : 1000}
        paths = obj.get_job_paths(all_params=params)
        comp_jobs = []
        for path in paths:
            cobj = ComputationJob()
            cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
            comp_jobs.append(cobj)
        plot_data = TopDNodesPlotPoints.get_plot_points(job_objs=comp_jobs)
        markers, caps, bars = plt.errorbar(plot_data["x"], plot_data["y"], yerr=plot_data["e"], capsize=4.0, color=color, marker="o", label=f"h = {h}")
        [bar.set_alpha(0.5) for bar in bars]
        [cap.set_alpha(0.5) for cap in caps]

    plt.xticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], fontsize='large')
    plt.yticks(fontsize='large')
    plt.grid(b=True, which='major', axis='x', color='#b3b3b3', linestyle='--')
    plt.plot([0.1, 1.0], [0.2, 0.2], color='black', linestyle="--")
    plt.xlabel("Top d% degree rank", fontsize=12)
    plt.ylabel("Fraction of minorities in top d%", fontsize=12)

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    ax.legend(handles, labels, numpoints=1, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()
