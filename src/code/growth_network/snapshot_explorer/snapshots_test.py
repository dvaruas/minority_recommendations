# This file demonstrates how snapshots can be used.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
from code.growth_network.snapshot_explorer.event_snapshots import EventSnapshots
from code.growth_network.growth_data_manager import GrowNetwork
import networkx as nx


if __name__ == "__main__":
    obj = GrowNetwork()
    paths = obj.get_job_paths(all_params={"job_id" : 0})
    path = paths.pop()

    es = EventSnapshots()
    es.create_snapshots_from_log(log_file_path=os.path.join(path, "raw", "logfile.txt"))

    G = nx.Graph()
    G, events = es.get_network(G, 0, 2090)
    print(nx.info(G))
    #print(change_log)
    G, events = es.get_network(G, 2090, 6000)
    print(nx.info(G))
    G, events = es.get_network(G, 6000, 2090)
    print(nx.info(G))
