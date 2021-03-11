import logging
import networkx as nx
import numpy as np


class TwitterRankRecommendation:
    def __init__(self, G, k, log_name=None):
        self.G = G
        self.num_slots = k
        self.logger = logging.getLogger(log_name)

    def get_recommendations_list(self, seeker):
        n = nx.number_of_nodes(self.G)
        choices = None
        if n <= self.num_slots:
            # If the number of nodes are less than slots, can't do anything
            choices = np.random.permutation(np.delete(np.arange(n), seeker))
        else:
            self.logger.debug(f"Recommendation for {seeker}")
            personal_vec = dict.fromkeys(np.arange(n), 0)
            hub_auth_graph = nx.Graph()
            personal_vec[seeker] = 1
            hubs = nx.pagerank_numpy(self.G, personalization=personal_vec)
            hubs.pop(seeker) # Remove the seeker from this rat-race
            hubs = sorted(hubs, key=lambda x:hubs[x], reverse=True)[:self.num_slots]
            all_nodes = set(hubs)
            for node in hubs:
                hub_auth_graph.add_node(f"h_{node}")
                for ng in self.G.neighbors(node):
                    if ng == seeker:
                        # Ignore the seeker from this list
                        continue
                    hub_auth_graph.add_node(f"a_{ng}")
                    all_nodes.add(ng)
                    hub_auth_graph.add_edge(f"h_{node}", f"a_{ng}")

            # Computing SALSA scores, thanks to the book "Google's pageRank and beyond by Amy N."
            # From chapter 12, SALSA example
            all_nodes = list(all_nodes)
            L_matrix = np.zeros(shape=(len(all_nodes), len(all_nodes)))
            for i, node_i in enumerate(all_nodes):
                hub_node = f"h_{node_i}"
                if hub_node in hub_auth_graph.nodes:
                    for j, j_node in enumerate(all_nodes):
                        auth_node = f"a_{j_node}"
                        if hub_auth_graph.has_edge(hub_node, auth_node):
                            L_matrix[i][j] = 1

            row_sums = L_matrix.sum(axis=1, keepdims=True)
            L_r = np.divide(L_matrix, row_sums)
            np.nan_to_num(L_r, copy=False)
            col_sums = L_matrix.sum(axis=0, keepdims=True)
            L_c = np.divide(L_matrix, col_sums)
            np.nan_to_num(L_c, copy=False)
            A_matrix = np.transpose(L_c).dot(L_r)

            total_components = 0
            components = []
            for connected_set in nx.connected_components(hub_auth_graph):
                component_set = []
                for item in connected_set:
                    type, num = item.split("_")
                    if type == "a":
                        component_set.append(int(num))
                        total_components += 1
                components.append(component_set)

            stationary_scores = {}
            for component_set in components:
                set_length = len(component_set)
                if set_length == 0:
                    continue
                Q = np.zeros(shape=(set_length, set_length))
                indexes = []
                for item in component_set:
                    indexes.append(all_nodes.index(item))
                for i, indx1 in enumerate(indexes):
                    for j, indx2 in enumerate(indexes):
                        Q[i][j] = A_matrix[indx1][indx2]
                # Below code taken from StackOverflow --------
                # https://stackoverflow.com/questions/31791728/python-code-explanation-for-stationary-distribution-of-a-markov-chain
                evals, evecs = np.linalg.eig(Q.T)
                evec1 = evecs[:,np.isclose(evals, 1)]
                evec1 = evec1[:,0]
                stationary = evec1 / evec1.sum()
                stationary = stationary.real
                #---------------------------------------------
                for i, item in enumerate(component_set):
                    stationary_scores[item] = (set_length / total_components) * stationary[i]

            choices = sorted(stationary_scores, key=lambda x:stationary_scores[x],
                reverse=True)

        choices = list(filter(lambda node: not self.G.has_edge(node, seeker), choices))[:self.num_slots]

        return choices
