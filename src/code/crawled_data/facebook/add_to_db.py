import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import json
import networkx as nx
from collections import Counter

from code.crawled_data.facebook.calculate_homophily import homophily_estimate
from code.crawled_data.facebook.facebook_data_manager import FacebookNetwork
from code.crawled_data.facebook.globals import FACEBOOK_DATA_PATH


if __name__ == "__main__":
    dir_path = os.path.join(FACEBOOK_DATA_PATH, "raw_graphs")
    if not os.path.exists(dir_path):
        print("raw_graphs directory needs to be present to add details to DB")
    else:
        obj = FacebookNetwork()
        for f_name in os.listdir(dir_path):
            if not f_name.endswith(".adjlist"):
                continue

            project_name = f_name[:-len(".adjlist")]
            print(f"Project : {project_name}")
            params = {"project" : project_name}

            with open(os.path.join(dir_path, f"{project_name}.adjlist"), "rb") as fr:
                graph = nx.read_adjlist(fr)
            with open(os.path.join(dir_path, f"{project_name}.gender"), "r") as fr:
                gender = json.load(fr)

            params["total_nodes"] = graph.number_of_nodes()
            params["total_edges"] = graph.number_of_edges()

            count = Counter(gender.values())
            total_male = count["male"]
            total_female = count["female"]

            male_male_edges, male_female_edges, female_female_edges = 0, 0, 0
            for n1, n2 in graph.edges():
                if gender[n1] == gender[n2]:
                    if gender[n1] == "male":
                        male_male_edges += 1
                    elif gender[n1] == "female":
                        female_female_edges += 1
                else:
                    male_female_edges += 1

            if total_female < total_male:
                params["minority"] = "female"
                params["minority_count"] = total_female
                params["majority_count"] = total_male
                params["minority_fraction"] = total_female / (total_male + total_female)
                min_min_edges, maj_maj_edges = female_female_edges, male_male_edges
            else:
                params["minority"] = "male"
                params["minority_count"] = total_male
                params["majority_count"] = total_female
                params["minority_fraction"] = total_male / (total_female + total_male)
                min_min_edges, maj_maj_edges = male_male_edges, female_female_edges
            
            h_aa, h_bb = homophily_estimate(minority_fraction=params["minority_fraction"],
                min_min_edges=min_min_edges, maj_maj_edges=maj_maj_edges, min_maj_edges=male_female_edges)
            if h_aa != None:
                params["h_minority"] = h_aa
            if h_bb != None:
                params["h_majority"] = h_bb

            obj.insert_network(all_params=params, defer_commit=True)

        obj.commit()
