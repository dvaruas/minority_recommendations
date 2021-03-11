# This plot is to get the Disparate Visibility for synthetic static networks.
# minority fraction : x-axis (0.1, 0.2), (0.3, 0.4), (0.5)
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.disparate_visibility import DVStaticPlotPoints
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    minority_fractions = [[0.1, 0.2],
                          [0.3, 0.4],
                          [0.5, None]]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    method_files = {"Adamic-Adar" : ("adamic_adar_NIL", '#e86127'), # orange
                    "PA-Homophily" : ("pa_homophily_NIL", "#ab580a"), # ochre
                    "Twitter-Rank" : ("twitter_rank_NIL", '#577804'), # green
                    "Ranked-Bandit (r : 0.0)" : ("ranked_bandit_0.0", "#021b4f"), # dark blue
                    "Ranked-Bandit (r : 0.5)" : ("ranked_bandit_0.5", "#06379c"), # ligher blue
                    "Ranked-Bandit (r : 1.0)" : ("ranked_bandit_1.0", "#175ae6"), # lightest blue
                    "Top-Rank (r : 0.0)" : ("top_rank_0.0", "#a30331"), # darker pink
                    "Top-Rank (r : 0.5)" : ("top_rank_0.5", "#c7063d"), # lighter pink
                    "Top-Rank (r : 1.0)" : ("top_rank_1.0", "#fa5282") # lightest pink
                }

    fig, ax = plt.subplots(nrows=len(minority_fractions), ncols=len(minority_fractions[0]), figsize=(10, 15), sharex=True, sharey=True)

    obj = StaticNetwork()

    for i, f_set in enumerate(minority_fractions):
        for j, f in enumerate(f_set):
            if f == None:
                ax[i, j].axis("off")
                continue
            for method, method_params in method_files.items():
                method_file_name = method_params[0]
                method_color = method_params[1]
                homophily_job_dict = {}
                for h in homophilies:
                    params ={"homophily" : h,
                             "minority_probability" : f,
                             "total_nodes" : 1000}
                    paths = obj.get_job_paths(all_params=params)
                    comp_jobs = []
                    for path in paths:
                        cobj = ComputationJob()
                        cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                        comp_jobs.append(cobj)
                    homophily_job_dict[h] = comp_jobs
                plot_data = DVStaticPlotPoints.get_plot_points(homophily_job_dict=homophily_job_dict, method=method_file_name)
                markers, caps, bars = ax[i, j].errorbar(plot_data["x"], plot_data["y"], yerr=plot_data["e"], capsize=4.0, color=method_color, marker="o", label=f"{method}")
                [bar.set_alpha(0.5) for bar in bars]
                [cap.set_alpha(0.5) for cap in caps]

            ax[i, j].yaxis.set_tick_params(labelleft=True)
            ax[i, j].xaxis.set_tick_params(labelbottom=True)
            ax[i,j].tick_params(labelsize='large')

            ax[i, j].set_xticks([0.0, 0.2, 0.5, 0.8, 1.0])
            ax[i, j].grid(b=True, which='major', axis='both', color='#b3b3b3', linestyle='--')

            ax[i, j].plot([0.0, 1.0], [0, 0], color='black', linestyle="-")
            ax[i, j].plot([0.0, 1.0], [(-1.0/(1.0 - f)), (-1.0/(1.0 - f))], color="black", linestyle="--")
            ax[i, j].plot([0.0, 1.0], [(1.0/f), (1.0/f)], color="black", linestyle="--")

            ax[i, j].set_xlabel(f"Homophily (h)", fontsize=12)
            ax[i, j].set_ylabel(f"Disparate Visibility", fontsize=12)

            plt.text(0.9, 0.9, f'f = {f}', horizontalalignment='center',
                verticalalignment='center', transform = ax[i, j].transAxes,
                fontsize=12, bbox=dict(facecolor='white', alpha=1.0))

    plt.xticks([0.0, 0.2, 0.5, 0.8, 1.0], fontsize='large')
    plt.yticks(fontsize='large')
    plt.xticks(fontsize='large')
    plt.subplots_adjust(left=0.08, bottom=0.07, right=0.99, top=0.99, wspace=0.3, hspace=0.3)

    handles, labels = ax[0,0].get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    fig.legend(handles, labels, numpoints=1, bbox_to_anchor=(0.8, 0.05), loc='lower center', prop={'size' : 12})

    plt.show()
