import logging
import networkx as nx


class AdamicAdarRecommendation:
    def __init__(self, G, k, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = G
        self.num_slots = k

    def get_recommendations_list(self, seeker):
        edges_to_test = []
        for u, v in nx.non_edges(self.G):
            if u == seeker:
                edges_to_test.append(tuple([u, v]))
            elif v == seeker:
                edges_to_test.append(tuple([v, u]))
        aa_index_sorted = sorted(nx.adamic_adar_index(self.G, ebunch=edges_to_test),
            key=lambda x:x[2], reverse=True)
        return [couplet[1] for couplet in aa_index_sorted][:self.num_slots]
