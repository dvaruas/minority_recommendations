import json
import logging
import os
import re
import time
import networkx as nx

from code.growth_network.snapshot_explorer.events import (NodeAdditionEvent,
    RecommendationEvent, EdgeAdditionEvent, IterationTypeEvent)
from code.growth_network.snapshot_explorer.snapshot import Snapshot


class EventSnapshots:
    def __init__(self, log_name=None):
        self.logger = logging.getLogger(log_name)
        self.snapshots = []
        self.job_info = {}

    def add_new_snap(self, snap_obj):
        self.snapshots.append(snap_obj)

    def get_job_info(self, name):
        return self.job_info.get(name, None)

    def get_snapshot_at_t(self, t=0):
        s = None
        try:
            s = self.snapshots[t]
        except IndexError:
            self.logger.error("Tried to access an index which does not exist!")
        return s

    def get_snapshots_count(self):
        return len(self.snapshots)

    def clear_snapshots(self):
        while self.snapshots:
            snap = self.snapshots.pop()
            del snap
        self.job_info = {}

    def get_network(self, G0=None, t0=None, t=None):
        events_log = []
        if t == None:
            t = len(self.snapshots) - 1
        if t0 == None:
            t0 = 0
        if G0 == None:
            G0 = nx.Graph()
        if t0 < 0 or t < 0 or len(self.snapshots) == 0: # Invalid
            return G0, events_log
        G = nx.Graph(G0)
        if t < t0:
            # Revert snaps, eg : t0 = 1, t = 0
            while t0 > t:
                s = self.get_snapshot_at_t(t=t0)
                if s:
                    events = s.get_events()
                    for e in events[::-1]:
                        if isinstance(e, NodeAdditionEvent):
                            G.remove_node(e.get_node_added()["node"])
                        elif isinstance(e, EdgeAdditionEvent):
                            G.remove_edge(e.get_node_from()["node"], e.get_node_to()["node"])
                        events_log.append(e)
                t0 -= 1
        elif t > t0:
            # Move forward snaps, eg : t0 = 1, t1 = 2
            while t0 < t:
                t0 += 1
                s = self.get_snapshot_at_t(t=t0)
                if s:
                    events = s.get_events()
                    for e in events:
                        if isinstance(e, NodeAdditionEvent):
                            added_node = e.get_node_added()
                            G.add_node(added_node["node"], type=added_node["type"])
                        elif isinstance(e, EdgeAdditionEvent):
                            G.add_edge(e.get_node_from()["node"], e.get_node_to()["node"])
                        events_log.append(e)
            pass
        return G, events_log

    def create_snapshots_from_log(self, log_file_path):
        self.clear_snapshots()
        job_info_file_path = os.path.join(os.path.dirname(log_file_path), os.pardir, "job_info.json")
        if not os.path.exists(log_file_path) or not os.path.exists(job_info_file_path):
            return
        with open(job_info_file_path, "r") as fr:
            self.job_info = json.load(fr)

        G = nx.Graph()
        s = Snapshot() # Create an empty snapshot to show empty graph
        self.add_new_snap(snap_obj=s)

        with open(log_file_path, "r") as fr:
            line = "something"

            recommendation_pattern = re.compile(r"Recommendation for (.*) : \[(.*)\]")
            node_addition_pattern = re.compile(r"Added Node : (.*), type : (.*)")
            edge_addition_pattern = re.compile(r"Added Edge : (.*), (.*)")
            iteration_info_pattern = re.compile(r"Iteration info > Growth type : (.*)")

            line = fr.readline().strip()
            # First line is the initial node addition line
            node_addition_match = node_addition_pattern.match(line)
            G.add_node(int(node_addition_match.group(1)), type=node_addition_match.group(2))

            e = NodeAdditionEvent(node=int(node_addition_match.group(1)), type=node_addition_match.group(2))
            s = Snapshot(event_objs=[e])
            self.add_new_snap(snap_obj=s)

            events = []
            while line:
                t1 = time.time()
                line = fr.readline().strip()

                # Is it a recommendation line ?
                recommendation_match = recommendation_pattern.match(line)
                if recommendation_match:
                    recomendations_for = int(recommendation_match.group(1))
                    recommendations_nodes_str = recommendation_match.group(2)
                    recommended_nodes = []
                    if recommendations_nodes_str:
                        for ss in recommendations_nodes_str.split(","):
                            s_n = int(ss.strip())
                            recommended_nodes.append((s_n, G.nodes[s_n]["type"]))
                    e = RecommendationEvent(recommendation_for=recomendations_for,
                        recommendation_for_type=G.nodes[recomendations_for]["type"],
                        recommended_nodes=recommended_nodes)
                    events.append(e)
                    continue

                # Is it a node addition line ?
                node_addition_match = node_addition_pattern.match(line)
                if node_addition_match:
                    added_node = int(node_addition_match.group(1))
                    added_node_type = node_addition_match.group(2)
                    G.add_node(added_node, type=added_node_type)
                    e = NodeAdditionEvent(node=added_node, type=added_node_type)
                    events.append(e)
                    continue

                # Is it an edge addition line ?
                edge_addition_match = edge_addition_pattern.match(line)
                if edge_addition_match:
                    node_from = int(edge_addition_match.group(1))
                    node_to = int(edge_addition_match.group(2))
                    G.add_edge(node_from, node_to)
                    e = EdgeAdditionEvent(node_from=node_from, node_from_type=G.nodes[node_from]["type"],
                        node_to=node_to, node_to_type=G.nodes[node_to]["type"])
                    events.append(e)
                    continue

                # Is it the iteration info line ?
                iteration_match = iteration_info_pattern.match(line)
                if iteration_match:
                    e = IterationTypeEvent(type=iteration_match.group(1))
                    events.append(e)
                    s = Snapshot(event_objs=events)
                    self.add_new_snap(snap_obj=s)
                    events = []

                t2 = time.time()
                self.logger.debug("Time taken to process line : {}".format(t2 - t1))
