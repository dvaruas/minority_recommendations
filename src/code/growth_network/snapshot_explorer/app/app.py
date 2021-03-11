import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))
#------------------------------------------------------------------------------------------------------
import networkx as nx
from flask import Flask, render_template, jsonify, make_response, request

from code.growth_network.snapshot_explorer.event_snapshots import EventSnapshots
from code.growth_network.snapshot_explorer.events import (NodeAdditionEvent,
    RecommendationEvent, EdgeAdditionEvent, IterationTypeEvent)
from code.growth_network.growth_data_manager import GrowNetwork


obj = GrowNetwork()
paths = obj.get_job_paths(all_params={"job_id" : 30})
path = paths.pop()
es = EventSnapshots()
es.create_snapshots_from_log(log_file_path=os.path.join(path, "raw", "logfile.txt"))
max_snapshots = es.get_snapshots_count()
G = None

app = Flask(__name__)

@app.route('/get_next')
def get_next_change():
    t0 = request.args.get('t0', default=0, type=int)
    t = request.args.get('t', default=0, type=int)
    changes = {"network" : [], "events" : [], "finished" : False, "min_change" : 0, "maj_change" : 0}
    if t < max_snapshots and t >= 0:
        global G
        G, events = es.get_network(G0=G, t0=t0, t=t)
        for e in events:
            if isinstance(e, NodeAdditionEvent):
                node_added = e.get_node_added()
                color = None
                if node_added["type"] == "minority":
                    color = "red"
                    changes["min_change"] += 1
                else:
                    color = "blue"
                    changes["maj_change"] += 1
                changes["network"].append({
                    "id" : node_added["node"],
                    "label" : str(node_added["node"]),
                    "color" : {"background" : color},
                    "shape" : "circle",
                    "font" : "14 arial #FFFFFF",
                })
                change = e.change_log()
                changes["events"].append(change)
            elif isinstance(e, EdgeAdditionEvent):
                node_from, node_to = e.get_node_from(), e.get_node_to()
                changes["network"].append({
                    "from" : node_from["node"],
                    "to" : node_to["node"]
                })
                change = e.change_log()
                changes["events"].append(change)
            elif isinstance(e, RecommendationEvent) or isinstance(e, IterationTypeEvent):
                change = e.change_log()
                if change:
                    changes["events"].append(change)

    else:
        changes["finished"] = True

    return make_response(jsonify(changes), 200)

@app.route('/')
def display_network():
    return render_template('visualizer.html', f=es.get_job_info("minority_prob"),
        h=es.get_job_info("minority_homophily"), r=es.get_job_info("ranking_control"),
        method=es.get_job_info("method"), af=None)


if __name__ == '__main__':
    app.run()
