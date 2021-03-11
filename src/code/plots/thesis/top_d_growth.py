# This plot is to get the top d% minorities for synthetic growth networks.
# minority fraction : x-axis (0.1, 0.2), (0.3, 0.4), (0.5)
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.top_d_nodes import TopDNodesPlotPoints
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    minority_fractions = [[0.1, 0.2],
                          [0.3, 0.4],
                          [0.5, None]]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    plot_line_colors = ['#854214', '#ed6507', '#1e800d', '#2373fc', '#2716a1'] #dark brown, light brown, green, blue, dark blue
    method = "top_rank" #["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]
    ranking_control = 1.0

    fig, ax = plt.subplots(nrows=len(minority_fractions), ncols=len(minority_fractions[0]), sharex=False, sharey=False, figsize=(10, 15))

    all_data = {}
    obj = GrowNetwork()

    for i, f_set in enumerate(minority_fractions):
        for j, f in enumerate(f_set):
            if f == None:
                ax[i, j].axis("off")
                continue
            for h, color in zip(homophilies, plot_line_colors):
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
                plot_data = TopDNodesPlotPoints.get_plot_points(job_objs=comp_jobs)
                markers, caps, bars = ax[i, j].errorbar(plot_data["x"], plot_data["y"], yerr=plot_data["e"], capsize=4.0, color=color, marker="o", label=f"h = {h}")
                [bar.set_alpha(0.5) for bar in bars]
                [cap.set_alpha(0.5) for cap in caps]

                ax[i, j].grid(b=True, which='major', axis='both', color='#b3b3b3', linestyle='--')
                ax[i, j].plot([0.1, 1.0], [f, f], color='black', linestyle="--")
                plt.text(0.9, 0.9, f'f = {f}', horizontalalignment='center',
                    verticalalignment='center', transform = ax[i, j].transAxes,
                    fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

                ax[i, j].set_xlabel(f"Top D% degree rank", fontsize=12)
                if j == 0:
                    ax[i, j].set_ylabel("Fraction of minorities in top D%", fontsize=12)

    plt.xticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], fontsize='large')
    plt.yticks(fontsize='large')
    plt.subplots_adjust(left=0.08, bottom=0.07, right=0.99, top=0.99, wspace=0.2, hspace=0.3)

    handles, labels = ax[0,0].get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    fig.legend(handles, labels, numpoints=1, bbox_to_anchor=(0.8, 0.1), loc='lower center', prop={'size':12})

    plt.show()
