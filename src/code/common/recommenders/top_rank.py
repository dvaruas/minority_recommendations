import logging
import networkx as nx
import numpy as np


class Partition:
    def __init__(self, items, k, m, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.items = items
        self.k = k
        self.m = m


class TopRankRecommendation:
    def __init__(self, G, t, k, click_model, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = G
        self.train_iter = t
        self.total_slots = k
        self.click_model = click_model
        self.partitions = []
        self.S = None
        self.N = None
        self.GU = None

    def update_params(self, key, value):
        if key == "t":
            self.train_iter = value

    def train_model(self, seeker):
        n = nx.number_of_nodes(self.G)
        choices = np.zeros(self.total_slots, dtype=np.uint16)
        all_choices = np.zeros(n, dtype=np.int32)

        t = 1
        while t <= self.train_iter:
            for partition in self.partitions:
                partition.items = np.random.permutation(partition.items)
                fill_till = partition.k + partition.m
                choices[partition.k:fill_till] = partition.items[:partition.m]
                if fill_till >= self.total_slots:
                    break

            clicked_options = self.click_model.get_clicks(options=choices,
                query=seeker)
            all_choices[choices] = np.asarray(clicked_options, dtype=np.int32)

            for part in self.partitions:
                for i in np.arange(part.m):
                    item_i = part.items[i]
                    item_j_s = part.items[i+1:]
                    item_j_s_choice = (all_choices[item_i] - all_choices[item_j_s])
                    item_j_s_choice_abs = np.abs(item_j_s_choice)
                    self.S[item_i, item_j_s] += item_j_s_choice
                    self.S[item_j_s, item_i] -= item_j_s_choice
                    self.N[item_i, item_j_s] += item_j_s_choice_abs
                    self.N[item_j_s, item_i] += item_j_s_choice_abs

            updateG = False
            for part in self.partitions:
                for i in np.arange(part.m):
                    item_i = part.items[i]
                    item_j_s = part.items[i+1:]
                    item_j_s = item_j_s[self.N[item_i, item_j_s] > 0]
                    update = self.update_criteria(s_values=self.S[item_i, item_j_s],
                        n_values=self.N[item_i, item_j_s])
                    update_true_indx = np.flatnonzero(update)
                    self.GU[item_i, item_j_s[update_true_indx]] = True
                    if updateG == False:
                        updateG = any(update)

            if updateG == True:
                while self.partitions:
                    p = self.partitions.pop()
                    del p
                remaining_items = np.arange(n)
                k = 0
                while k < self.total_slots:
                    bad_items = np.flatnonzero(np.sum(self.GU[remaining_items, :], axis=0))
                    good_items = np.setdiff1d(remaining_items, bad_items, assume_unique=True)
                    items_length = good_items.size
                    self.partitions.append(Partition(items=good_items, k=k,
                        m=min(items_length, self.total_slots - k)))
                    k += items_length
                    remaining_items = bad_items

            all_choices[choices] = 0
            t += 1

    def update_criteria(self, s_values, n_values):
        return (s_values >= np.sqrt(2 * n_values * np.log(3.43 * self.train_iter * np.sqrt(n_values))))

    def get_recommendations_list(self, seeker):
        n = nx.number_of_nodes(self.G)
        choices = None
        if n <= self.total_slots:
            # If the number of nodes are less than slots, can't train
            choices = np.random.permutation(np.delete(np.arange(n), seeker))
        else:
            # Do training of model
            self.partitions = [Partition(items=np.delete(np.arange(n), seeker),
                k=0, m=self.total_slots)]
            self.S = np.zeros((n, n), dtype=np.int32)
            self.N = np.zeros((n, n), dtype=np.int32)
            self.GU = np.zeros((n, n), dtype=np.bool)
            self.GU[:, seeker] = True
            self.GU[seeker, seeker] = False
            self.train_model(seeker=seeker)

            # Get the choices from the partitions
            fill_till = 0
            choices = np.zeros(self.total_slots, dtype=np.uint16)
            for partition in self.partitions:
                partition.items = np.random.permutation(partition.items)
                fill_till = partition.k + partition.m
                choices[partition.k : fill_till] = partition.items[: partition.m]
                if fill_till >= self.total_slots:
                    break

        choices = list(filter(lambda node: not self.G.has_edge(node, seeker), choices))[:self.total_slots]

        return choices
