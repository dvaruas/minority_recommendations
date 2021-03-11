class Node:
    def __init__(self, n, t):
        self.n = n
        self.t = t

    def get_node(self):
        return {"node" : self.n, "type" : self.t}


class NodeAdditionEvent:
    def __init__(self, node, type):
        self.node = Node(n=node, t=type)

    def get_node_added(self):
        return self.node.get_node()

    def change_log(self, reverting=False):
        change = ""
        node_info = self.get_node_added()
        if reverting:
            change = f"Removed node {node_info['node']}({node_info['type']})"
        else:
            change = f"Added node {node_info['node']}({node_info['type']})"
        return change


class RecommendationEvent:
    def __init__(self, recommendation_for, recommendation_for_type, recommended_nodes=[]):
        self.r_for = Node(n=recommendation_for, t=recommendation_for_type)
        self.r_nodes = [Node(n=n, t=t) for (n, t) in recommended_nodes]

    def change_log(self, reverting=False):
        if reverting:
            return ""
        prime_node = self.r_for.get_node()
        recommendations_list = [(node.get_node()["node"], node.get_node()["type"]) for node in self.r_nodes]
        change = f"Node {prime_node['node']}({prime_node['type']}) received recommendations : {recommendations_list}"
        return change


class EdgeAdditionEvent:
    def __init__(self, node_from, node_from_type, node_to, node_to_type):
        self.n_from = Node(n=node_from, t=node_from_type)
        self.n_to = Node(n=node_to, t=node_to_type)

    def get_node_from(self):
        return self.n_from.get_node()

    def get_node_to(self):
        return self.n_to.get_node()

    def change_log(self, reverting=False):
        change = ""
        node_from_info = self.get_node_from()
        node_to_info = self.get_node_to()
        if reverting:
            change = f"Removing edge between {node_to_info['node']}({node_to_info['type']}) and {node_from_info['node']}({node_from_info['type']})"
        else:
            change = f"Adding edge between {node_to_info['node']}({node_to_info['type']}) and {node_from_info['node']}({node_from_info['type']})"
        return change


class IterationTypeEvent:
    def __init__(self, type):
        self.type = type

    def change_log(self, reverting=False):
        if reverting:
            return ""
        return f"Iteration type : {self.type}"
