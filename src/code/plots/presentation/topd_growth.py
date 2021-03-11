# miority fraction = 0.2
# This plot is to get the top d% minorities for synthetic growth networks for non-RL.
# x-axis : ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"] (only r = 1.0 used)
# y-axis : one
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.top_d_nodes import TopDNodesPlotPoints
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    plot_line_colors = ['#854214', '#ed6507', '#1e800d', '#2373fc', '#2716a1'] #dark brown, light brown, green, blue, dark blue
    recommenders = ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]

    fig, ax = plt.subplots(nrows=1, ncols=len(recommenders), sharex=True, sharey=True, figsize=(20, 4))

    obj = GrowNetwork()
    for i, rec in enumerate(recommenders):
        for h, color in zip(homophilies, plot_line_colors):
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
            plot_data = TopDNodesPlotPoints.get_plot_points(job_objs=comp_jobs)
            markers, caps, bars = ax[i].errorbar(plot_data["x"], plot_data["y"], yerr=plot_data["e"], capsize=4.0, color=color, marker="o", label=f"h = {h}")
            [bar.set_alpha(0.5) for bar in bars]
            [cap.set_alpha(0.5) for cap in caps]

        ax[i].set_xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        ax[i].set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax[i].tick_params(labelsize=12)
        ax[i].grid(b=True, which='major', axis='both', color='#b3b3b3', linestyle='--')
        ax[i].plot([0.1, 1.0], [0.2, 0.2], color='black', linestyle="-")

    handles, labels = ax[0].get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    fig.legend(handles, labels, numpoints=1, bbox_to_anchor=(0.35, 1.0), loc='upper left', ncol=5)

    plt.subplots_adjust(left=0.03, bottom=0.07, right=0.99, top=0.85, wspace=0.1, hspace=0.1)

    plt.show()
