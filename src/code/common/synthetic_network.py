import json
import logging
import networkx as nx


class SyntheticNetwork:
    def __init__(self, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.G = nx.Graph()
        self.saved_info = {}

    def save_info(self, key, info):
        self.saved_info[key] = info

    def get_info(self, key):
        return self.saved_info.get(key, None)

    def initialize_empty_network(self):
        self.G = nx.Graph()

    def get_network(self):
        return self.G

    def add_new_node(self, node_name, **node_attrs):
        self.G.add_node(node_name, **node_attrs)

    def add_new_edge(self, node_one, node_two, **edge_attrs):
        self.G.add_edge(node_one, node_two, **edge_attrs)

    def save_network_adjlist(self, file_path):
        with open(file_path, "wb") as fw:
            nx.write_adjlist(self.G, fw)

    def save_network_attribute(self, attribute_name, file_path):
        attrs = nx.get_node_attributes(self.G, attribute_name)
        if attrs:
            with open(file_path, "w") as fw:
                json.dump(attrs, fw)

    def load_network_adjlist(self, file_path):
        with open(file_path, "rb") as fr:
            self.G = nx.read_adjlist(fr, nodetype=int)

    def load_network_attribute(self, attribute_name, file_path,
        modify_func=lambda x : (int(x[0]), x[1])):
        with open(file_path, "r") as fr:
            attr_data = json.load(fr)
        attr_data = dict(map(modify_func, attr_data.items()))
        nx.set_node_attributes(self.G, attr_data, attribute_name)
