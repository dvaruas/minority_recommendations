import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import networkx as nx
import matplotlib.pyplot as plt

from code.growth_network.growth_data_manager import GrowNetwork
from code.plot_computations.comp_job import ComputationJob

if __name__ == "__main__":
    obj = GrowNetwork()
    info = obj.get_job_paths({"simulation" : 1, "homophily" : 0.2, "minority_probability" : 0.2, "ranking_control" : 0.0, "job_type" : "pa_homophily", "parameter_profile" : 0})
    info = info.pop()

    cobj = ComputationJob()
    cobj.set_log_path(os.path.join(info, "raw", "logfile.txt"))
    G = cobj.graph.get_network()

    node_colors = []
    node_sizes = []
    SIZE_RANGE_MAX, SIZE_RANGE_MIN = 1000, 100
    deg_centrality_dict = nx.degree_centrality(G)
    for n, v in deg_centrality_dict.items():
        node_sizes.append(v)
        node_colors.append("red" if G.nodes[n]['type'] == "minority" else "blue")

    new_range = SIZE_RANGE_MAX - SIZE_RANGE_MIN
    old_range_min = min(node_sizes)
    old_range_max = max(node_sizes)
    old_range = old_range_max - old_range_min
    node_sizes = [(SIZE_RANGE_MIN + (((v - old_range_min) / old_range) * new_range)) for v in node_sizes]

    plt.figure(figsize=(10, 6))
    nx.draw_networkx(G=G,
                     pos=nx.spring_layout(G, k=0.15, iterations=30),
                     node_color=node_colors, # Color the Nodes
                     node_size=node_sizes, # Size of the nodes according to degree centrality
                     with_labels=False, # Do not show the node labels
                     edgecolors='black'
                     )
    plt.axis('off')
    plt.show()
