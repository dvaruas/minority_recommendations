# This plot is to get the recommendations count for synthetic growth networks.
# Minority fractions : [0.1, 0., 0.3, 0.4, 0.5] (y-axis)
# homophily values : [0.0, 0.2, 0.5, 0.8, 1.0] (x-axis)
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.recommendation_count import RecommendationCount
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    minority_fractions = [0.1, 0.2, 0.3, 0.4, 0.5]
    recommender = "top_rank" # ["pa_homophily", "adamic_adar", "twitter_rank", "ranked_bandit", "top_rank"]
    ranking_control = 1.0
    steps = 100

    fig, ax = plt.subplots(nrows=len(homophilies), ncols=len(minority_fractions), sharex=True, sharey=True, figsize=(13, 13))
    obj = GrowNetwork()

    for i, f in enumerate(minority_fractions):
        for j, h in enumerate(homophilies):
            params ={"homophily" : h,
                     "minority_probability" : f,
                     "ranking_control" : ranking_control if recommender in ["ranked_bandit", "top_rank"] else 0.0,
                     "job_type" : recommender,
                     "parameter_profile" : 0}
            paths = obj.get_job_paths(all_params=params)
            comp_jobs = []
            for path in paths:
                cobj = ComputationJob()
                cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                comp_jobs.append(cobj)

            plot_data = RecommendationCount.get_plot_points(job_objs=comp_jobs, steps=steps)
            ax[i, j].plot(list(range(steps)), plot_data["minority"]["minority"], "#ff0000", label="minority : minority")
            ax[i, j].plot(list(range(steps)), plot_data["minority"]["majority"], "#b00404", label="minority : majority")
            ax[i, j].plot(list(range(steps)), plot_data["majority"]["minority"], "#038a96", label="majority : minority")
            ax[i, j].plot(list(range(steps)), plot_data["majority"]["majority"], "#032896", label="majority : majority")

            # ax[i, j].plot(list(range(50)), [1, 2, 3, 4, 5] * 10, "#ff0000", label="minority : minority")
            # ax[i, j].plot(list(range(50)), [1, 2, 3, 4, 5] * 10, "#b00404", label="minority : majority")
            # ax[i, j].plot(list(range(50)), [1, 2, 3, 4, 5] * 10, "#038a96", label="majority : minority")
            # ax[i, j].plot(list(range(50)), [1, 2, 3, 4, 5] * 10, "#032896", label="majority : majority")

            ax[i, j].tick_params(labelsize='large')
            ax[i, j].set_yticks([0, 1, 2, 3, 4, 5])
            ax[i, j].grid(b=True, which='major', axis='both', color='#b3b3b3', linestyle='--')
            if (i == len(minority_fractions) - 1):
                ax[i,j].set_xlabel("iteration($t$)", fontsize=12)
            if (j == 0):
                ax[i,j].set_ylabel("count", fontsize=12)

    handles, labels = ax[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, numpoints=1, bbox_to_anchor=(0.15, 1.0), loc='upper left', ncol=4, prop={'size' : 12})

    plt.figtext(0.11, 0.935, "h = 0.0", fontsize=12)
    plt.figtext(0.3, 0.935, "h = 0.2", fontsize=12)
    plt.figtext(0.48, 0.935, "h = 0.5", fontsize=12)
    plt.figtext(0.66, 0.935, "h = 0.8", fontsize=12)
    plt.figtext(0.85, 0.935, "h = 1.0", fontsize=12)

    plt.figtext(0.97, 0.13, "f = 0.5", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.3, "f = 0.4", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.47, "f = 0.3", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.64, "f = 0.2", fontsize=12, rotation=-90)
    plt.figtext(0.97, 0.81, "f = 0.1", fontsize=12, rotation=-90)

    plt.subplots_adjust(left=0.05, bottom=0.06, right=0.95, top=0.92, wspace=0.1, hspace=0.1)

    plt.show()
