# This plot is to get the minority fraction for synthetic static networks.
# single plot
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import matplotlib.pyplot as plt

from code.plot_computations.comp_job import ComputationJob
from code.plot_computations.minority_fraction import MinorityFractionPlotPoints
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    minority_fractions = [0.1, 0.2, 0.3, 0.4, 0.5]
    homophilies = [0.0, 0.2, 0.5, 0.8, 1.0]
    plot_line_colors = ['b', 'g', 'r', 'c', 'm']#, 'y', 'k', 'w']
    plt.figure(figsize=(10, 5))

    all_data = {}
    obj = StaticNetwork()
    for m in minority_fractions:
        job_paths = {}
        for h in homophilies:
            params ={"homophily" : h,
                     "minority_probability" : m,
                     "total_nodes" : 1000}
            paths = obj.get_job_paths(all_params=params)
            comp_jobs = []
            for path in paths:
                cobj = ComputationJob()
                cobj.set_log_path(path=os.path.join(path, "raw", "logfile.txt"))
                comp_jobs.append(cobj)
            job_paths[h] = comp_jobs
        all_data[m] = MinorityFractionPlotPoints.get_plot_points(homophily_job_dict=job_paths)
    for m, color in zip(minority_fractions, plot_line_colors):
        markers, caps, bars = plt.errorbar(all_data[m]["x"], all_data[m]["y"], yerr=all_data[m]["e"], capsize=4.0, color=color, marker='o', label=f"f = {m}")
        [bar.set_alpha(0.5) for bar in bars]
        [cap.set_alpha(0.5) for cap in caps]

    plt.xlabel("homophily $(h)$", fontsize=12)
    plt.ylabel("Fraction of minorities total degree", fontsize=12)
    plt.xticks([0.0, 0.2, 0.5, 0.8, 1.0], fontsize='large')
    plt.yticks(fontsize='large')
    plt.grid(b=True, which='major', axis='y', color='#5c5e5e', linestyle='--')
    plt.grid(b=True, which='major', axis='x', color='#d5dbdb', linestyle='--')

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    handles = [h[0] for h in handles] # remove the errorbars
    ax.legend(handles, labels, numpoints=1, bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size' : 12})

    plt.tight_layout()
    plt.show()
