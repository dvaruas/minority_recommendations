import logging
import networkx as nx
import numpy as np


class PAHomophily:
    def __init__(self, G, k, small_value, h_aa, h_bb, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = G
        self.small_value = small_value
        self.h_aa = h_aa
        self.h_bb = h_bb
        self.num_slots = k

    def get_recommendations_list(self, seeker):
        possible_nodes = list(nx.non_neighbors(self.G, seeker))
        conn_probabilities = np.zeros(len(possible_nodes))
        seeker_label = self.G.nodes[seeker]["type"]

        for i, n in enumerate(possible_nodes):
            h_value = None
            if self.G.nodes[n]["type"] == seeker_label:
                if seeker_label == "minority":
                    h_value = self.h_aa
                else:
                    h_value = self.h_bb
            else:
                if seeker_label == "minority":
                    h_value = 1.0 - self.h_aa
                else:
                    h_value = 1.0 - self.h_bb

            conn_probabilities[i] = h_value * (self.G.degree(n) + self.small_value)

        total_sum = np.sum(conn_probabilities)
        recommended_nodes = []
        if total_sum > 0.0:
            conn_probabilities /= total_sum
            positive_count = np.count_nonzero(conn_probabilities)
            if positive_count >= self.num_slots:
                positive_count = self.num_slots
            recommended_nodes = list(np.random.choice(possible_nodes, size=positive_count, replace=False, p=conn_probabilities))

        other_nodes = np.random.permutation([node for node in possible_nodes if node not in recommended_nodes])
        recommended_nodes.extend(other_nodes)

        return list(recommended_nodes[:self.num_slots])
