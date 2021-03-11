import networkx as nx
import numpy as np

from code.common.synthetic_network import SyntheticNetwork


class GrowthSyntheticNetwork(SyntheticNetwork):
    def get_random_node(self):
        return np.random.choice(nx.number_of_nodes(self.G))

    def preference_monk(self, proposed_nodes_list, seeker_label, rank_options=False):
        h_aa = self.get_info("h_aa")
        h_bb = self.get_info("h_bb")
        small_value = self.get_info("small_value")
        tao = self.get_info("ranking_control")
        conn_probabilities = np.zeros(len(proposed_nodes_list))
        ranking_factor = 1.0
        for i, n in enumerate(proposed_nodes_list):
            h_value = None
            if self.G.nodes[n]["type"] == seeker_label:
                if seeker_label == "minority":
                    h_value = h_aa
                else:
                    h_value = h_bb
            else:
                if seeker_label == "minority":
                    h_value = 1.0 - h_aa
                else:
                    h_value = 1.0 - h_bb

            if rank_options:
                ranking_factor = np.exp((1.0 - i) * (tao ** 2))

            conn_probabilities[i] = h_value * (self.G.degree(n) + small_value) * ranking_factor

        total_target_nodes_prob = np.sum(conn_probabilities)
        other_node = None
        if total_target_nodes_prob > 0.0:
            conn_probabilities /= total_target_nodes_prob
            other_node = np.random.choice(proposed_nodes_list, p=conn_probabilities)
        return other_node

    def get_preferred_node(self, seeker_type):
        total_nodes = nx.number_of_nodes(self.G)
        return self.preference_monk(proposed_nodes_list=np.arange(total_nodes),
            seeker_label=seeker_type)

    def get_recommended_node(self, seeker):
        recommender = self.get_info(key="recommender")
        oho_list = recommender.get_recommendations_list(seeker=seeker)
        self.logger.info("Recommendation for {} : {}".format(seeker, oho_list))
        return self.preference_monk(proposed_nodes_list=oho_list,
            seeker_label=self.G.nodes[seeker]["type"], rank_options=True)
