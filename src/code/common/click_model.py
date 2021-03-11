import logging
import numpy as np


class ClickModel:
    def __init__(self, c, G, h_aa, h_bb, small_value, ranking_factor, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = G
        self.c = c
        self.h_aa = h_aa
        self.h_bb = h_bb
        self.small_value = small_value
        self.ranking_factor = ranking_factor

    def get_clicks(self, options, query):
        # options are the ranked order of nodes in graph
        # query is the node which is supposed to make the decision.
        option_values = np.zeros(len(options), dtype=np.float16)
        indx = 0
        while indx < len(options):
            graph_node = options[indx]
            if self.G.has_edge(graph_node, query):
                option_values[indx] = 0.0
            else:
                degree_of_node = self.G.degree[graph_node]
                h_value = None
                if self.G.nodes[query]['type'] == self.G.nodes[graph_node]['type']:
                    if self.G.nodes[query]['type'] == "minority":
                        h_value = self.h_aa
                    else:
                        h_value = self.h_bb
                else:
                    if self.G.nodes[query]['type'] == "minority":
                        h_value = 1.0 - self.h_aa
                    else:
                        h_value = 1.0 - self.h_bb
                option_values[indx] = (degree_of_node + self.small_value) * h_value * np.exp((1.0 - indx) * (self.ranking_factor ** 2))
            indx += 1
        total_sum = np.sum(option_values)
        chosen = []
        if total_sum > 0.0:
            option_values /= total_sum
            options_to_choose = np.count_nonzero(option_values)
            if self.c < options_to_choose:
                options_to_choose = self.c
            chosen = np.random.choice(options, size=options_to_choose, replace=False,
                p=option_values)
        return np.isin(options, chosen, assume_unique=True)
