# This plot is to get the minority fraction for synthetic growth networks for RL.
# x-axis : ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"] (only r = 1.0 used)
# y-axis : one
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.minority_fraction import MinorityFractionPlotPoints
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    minority_fractions = [0.1, 0.2, 0.3, 0.4, 0.5]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    plot_line_colors = ['b', 'g', 'r', 'c', 'm']#, 'y', 'k', 'w']
    recommenders = ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]

    fig, ax = plt.subplots(nrows=1, ncols=len(recommenders), sharex=True, sharey=True, figsize=(20, 4))

    for i, rec in enumerate(recommenders):
        all_data = {}
        obj = GrowNetwork()
        for m in minority_fractions:
            job_paths = {}
            for h in homophilies:
                params ={"homophily" : h,
                         "minority_probability" : m,
                         "ranking_control" : 1.0 if rec in ["ranked_bandit", "top_rank"] else 0.0,
                         "job_type" : rec,
                         "parameter_profile" : 0}
                paths = obj.get_job_paths(all_params=params)
                comp_jobs = []
                for path in paths:
                    cobj = ComputationJob()
                    cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                    comp_jobs.append(cobj)
                job_paths[h] = comp_jobs
            all_data[m] = MinorityFractionPlotPoints.get_plot_points(homophily_job_dict=job_paths)

        for m, color in zip(minority_fractions, plot_line_colors):
            markers, caps, bars = ax[i].errorbar(all_data[m]["x"], all_data[m]["y"], yerr=all_data[m]["e"], capsize=4.0, color=color, marker='o', label=f"f = {m}")
            [bar.set_alpha(0.5) for bar in bars]
            [cap.set_alpha(0.5) for cap in caps]

        ax[i].set_xticks([0.0, 0.2, 0.5, 0.8, 1.0])
        ax[i].tick_params(labelsize=12)
        ax[i].grid(b=True, which='major', axis='y', color='#5c5e5e', linestyle='--')
        ax[i].grid(b=True, which='major', axis='x', color='#d5dbdb', linestyle='--')

    handles, labels = ax[0].get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    fig.legend(handles, labels, numpoints=1, bbox_to_anchor=(0.35, 1.0), loc='upper left', ncol=5)

    plt.subplots_adjust(left=0.03, bottom=0.07, right=0.99, top=0.85, wspace=0.1, hspace=0.1)

    plt.show()
