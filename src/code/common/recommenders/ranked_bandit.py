import copy
import logging
import networkx as nx
import numpy as np


# Referenced from book - Reinforcement Learning, an Introduction
class EspGreedy:
    def __init__(self, epsilon, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.epsilon = epsilon
        self.exclude = None
        self.weights = None
        self.num_actions = None
        self.argmax = None
        self.argmax_value = None

    def setup(self, poc, num_actions):
        self.exclude = poc
        self.num_actions = num_actions
        if self.exclude == 0:
            self.argmax = 1
        else:
            self.argmax = 0
        self.argmax_value = 0.0
        internal_mask = np.zeros(num_actions, dtype=np.bool)
        internal_mask[self.exclude] = True
        self.weights = np.ma.array(np.zeros(num_actions), mask=internal_mask, hard_mask=True)

    def choose_action(self):
        type = np.random.choice(1, p=[self.epsilon, 1.0 - self.epsilon])
        choice = None
        if type == 0:
            # Random Explore
            choice = np.random.choice(np.delete(np.arange(self.num_actions), self.exclude))
        else:
            # Exploit
            choice = np.ma.argmax(self.weights, fill_value=np.NINF)
        return choice

    def update(self, choice, reward, t):
        # Average Sum method
        self.weights[choice] += ((1 / t) * (reward - self.weights[choice]))

    def get_next_best(self, mask):
        choice_array = np.ma.array(self.weights, mask=mask)
        return np.ma.argmax(choice_array, fill_value=np.NINF)


# Referenced from - https://jeremykun.com/2013/11/08/adversarial-bandits-and-the-exp3-algorithm/
class Exp3:
    def __init__(self, gamma, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.gamma = gamma
        self.weights = None
        self.prob_dist = None
        self.exclude = None
        self.num_actions = None

    def setup(self, poc, num_actions):
        self.weights = np.ones(num_actions)
        self.prob_dist = np.zeros(num_actions)
        self.exclude = poc
        self.num_actions = num_actions

    def choose_action(self):
        self.prob_dist = ((1.0 - self.gamma) * (self.weights / np.sum(self.weights))) + (self.gamma / self.num_actions)
        choice_prob = np.array(self.prob_dist)
        choice_prob[self.exclude] = 0.0
        choice_prob /= np.sum(choice_prob)
        return np.random.choice(a=self.num_actions, p=choice_prob)

    def update(self, choice, reward, t):
        with np.errstate(over='raise'):
            try:
                self.weights[choice] *= np.exp((reward * self.gamma) / (self.prob_dist[choice] * self.num_actions))
            except FloatingPointError:
                # Overflow must have occured
                if np.isposinf(self.weights[choice]):
                    self.weights[choice] = np.finfo(np.float64).max
                elif np.isneginf(self.weights[choice]):
                    self.weights[choice] = np.finfo(np.float64).min

    def get_next_best(self, mask):
        choice_array = np.ma.array(self.weights, mask=mask)
        return np.ma.argmax(choice_array, fill_value=np.NINF)


class RankedBanditRecommendation:
    def __init__(self, G, t, k, bandit_model_obj, click_model, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = G
        self.train_iter = t
        self.total_slots = k
        self.click_model = click_model
        self.bandits = [copy.deepcopy(bandit_model_obj) for i in range(self.total_slots)]

    def update_params(self, key, value):
        if key == "t":
            self.train_iter = value

    def train_model(self, seeker):
        t = 1
        original_arms = np.zeros(self.total_slots, dtype=np.int16)
        bandit_arms = np.zeros(self.total_slots, dtype=np.int16)
        n = nx.number_of_nodes(self.G)
        while t <= self.train_iter:
            original_arms.fill(-1)
            bandit_arms.fill(-1)
            for i in range(self.total_slots):
                get_arm = self.bandits[i].choose_action()
                original_arms[i] = get_arm
                if get_arm == seeker or get_arm in bandit_arms:
                    get_arm = np.random.choice(np.delete(np.arange(n), bandit_arms[bandit_arms != -1]))
                bandit_arms[i] = get_arm

            clicked_options = self.click_model.get_clicks(options=bandit_arms,
                query=seeker)

            for i in range(self.total_slots):
                reward_value = 0
                if clicked_options[i] == True and bandit_arms[i] == original_arms[i]:
                    reward_value = 1
                self.bandits[i].update(choice=original_arms[i], reward=reward_value, t=t)

            t += 1

    def get_recommendations_list(self, seeker):
        n = nx.number_of_nodes(self.G)
        choices = None
        if n <= self.total_slots:
            # If the number of nodes are less than slots, can't train
            choices = np.random.permutation(np.delete(np.arange(n), seeker))
        else:
            # Do training of model
            for i in range(self.total_slots):
                self.bandits[i].setup(poc=seeker, num_actions=n)
            self.train_model(seeker=seeker)

            # Get the choiced items
            choices = np.zeros(self.total_slots, dtype=np.uint16)
            mask = np.zeros(n, dtype=np.bool)
            mask[seeker] = True
            for i, bandit in enumerate(self.bandits):
                opt = bandit.get_next_best(mask=mask)
                mask[opt] = True
                choices[i] = opt

        choices = list(filter(lambda node: not self.G.has_edge(node, seeker), choices))[:self.total_slots]

        return choices
