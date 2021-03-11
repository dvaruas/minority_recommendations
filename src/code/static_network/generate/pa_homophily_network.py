import numpy as np

from code.common.synthetic_network import SyntheticNetwork


class GenerateSyntheticNetwork(SyntheticNetwork):
    def __init__(self, log_name):
        super().__init__(log_name)
        self.generating_now = False

    def get_generating_status(self):
        return self.generating_now

    def generate_network(self):
        # Modified version of code from - https://github.com/frbkrm/HomophilicNtwMinorities
        n = self.saved_info["total_nodes"]
        m = self.saved_info["edges_per_iteration"]
        m0 = self.saved_info["initial_nodes"]
        min_fraction = self.saved_info["minority_fraction"]
        h_aa = self.saved_info["homophily_among_minorities"]
        h_bb = self.saved_info["homophily_among_majorities"]
        small_value = 0.00001 # To give boost to 0 degree nodes

        # Starting generation of the graph
        self.generating_now = True
        # Number of nodes which belong to the minority
        num_minority_nodes = int(min_fraction * n)
        # Randomly assign some nodes as minority
        minority_nodes = np.random.choice(a=n, replace=False, size=num_minority_nodes)

        self.initialize_empty_network()
        # Color the nodes and add to graph according to the majority and minority group
        for i in np.arange(n):
            if i in minority_nodes:
                self.G.add_node(i, type="minority")
            else:
                self.G.add_node(i, type="majority")

        # h_values for node pairs
        h_values = []
        for i in np.arange(n):
            i_list = []
            for j in np.arange(i+1, n):
                h_value = 0.0
                if (i in minority_nodes and j in minority_nodes):
                    h_value = h_aa
                elif (i not in minority_nodes and j not in minority_nodes):
                    h_value = h_bb
                elif (i in minority_nodes and j not in minority_nodes):
                    h_value = 1.0 - h_aa
                elif (i not in minority_nodes and j in minority_nodes):
                    h_value = 1.0 - h_bb
                i_list.append(h_value)
            h_values.append(i_list)

        current_node = m0
        for node in range(current_node):
            self.logger.info("Added Node : {}, type : {}".format(node, self.G.nodes[node]["type"]))

        while current_node < n:
            self.logger.info("Added Node : {}, type : {}".format(current_node, self.G.nodes[current_node]["type"]))
            target_nodes_prob = np.zeros(current_node)
            not_done = True
            possible_size = 0
            for t in np.arange(current_node):
                h_value = h_values[t][current_node - t - 1]
                #print("{} - {} : {}".format(t, current_node, h_value))
                # The VERY_SMALL_VALUE is added just to make sure that nodes get an initial boost
                # since initially there will be all initial nodes with zero degree
                insert_value = (h_value * (self.G.degree(t) + small_value))
                if not_done and insert_value > 0.0:
                    possible_size += 1
                    if possible_size == m:
                        not_done = False
                target_nodes_prob[t] = insert_value
            total_target_nodes_prob = np.sum(target_nodes_prob)
            #self.logger.debug("Sum of all target nodes probability : {}".format(total_target_nodes_prob))
            if total_target_nodes_prob > 0.0:
                target_nodes_prob /= total_target_nodes_prob
                temp_targets = np.random.choice(a=current_node, p=target_nodes_prob,
                                                size=possible_size, replace=False)
                for t in temp_targets:
                    self.logger.info("Added Edge : {}, {}".format(current_node, t))
                self.G.add_edges_from(zip([current_node] * possible_size, temp_targets))
            current_node += 1

        # Generation completed
        self.generating_now = False
