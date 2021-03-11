import os
import re

from code.common.synthetic_network import SyntheticNetwork


def recreate_network(job_path):
    # This function can recreate and save a networkx graph from the log file entries of a static/growth Job
    log_file_path = os.path.join(job_path, "raw", "logfile.txt")
    if not os.path.exists(log_file_path):
        return

    adjlist_path = os.path.join(job_path, "raw", "raw_graph.adjlist")
    type_path = os.path.join(job_path, "raw", "raw_graph.type")

    if os.path.exists(adjlist_path) and os.path.exists(type_path):
        # The recreated network already exists
        return

    obj = SyntheticNetwork()

    #recommendation_pattern = re.compile(r"Recommendation for (.*) : \[(.*)\]")
    node_addition_pattern = re.compile(r"Added Node : (.*), type : (.*)")
    edge_addition_pattern = re.compile(r"Added Edge : (.*), (.*)")

    with open(log_file_path, "r") as fr:
        for line in fr:
            line = line.rstrip()
            #recommendation_match = recommendation_pattern.match(line)
            node_addition_match = node_addition_pattern.match(line)
            edge_addition_match = edge_addition_pattern.match(line)

            if node_addition_match:
                # This line talks about adding a new node
                obj.add_new_node(int(node_addition_match.group(1)), type=node_addition_match.group(2))
            elif edge_addition_match:
                # This line talks about adding a new edge
                obj.add_new_edge(int(edge_addition_match.group(1)), int(edge_addition_match.group(2)))

    obj.save_network_adjlist(file_path=adjlist_path)
    obj.save_network_attribute(file_path=type_path, attribute_name="type")
