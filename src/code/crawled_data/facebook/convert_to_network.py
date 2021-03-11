import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import json
import logging
import scipy
import scipy.io
import shutil
import networkx as nx

from code.crawled_data.facebook.globals import FACEBOOK_DATA_PATH


def create_network_file(file_path):
    logger = logging.getLogger("facebook100")
    file_name = os.path.basename(file_path)
    data_name = file_name[:-len(".mat")]

    logger.info(f"\nWorking on File : {file_name}")

    G = nx.Graph()
    write_network_file = os.path.join(FACEBOOK_DATA_PATH, "raw_graphs", f"{data_name}.adjlist")
    write_gender_file = os.path.join(FACEBOOK_DATA_PATH, "raw_graphs", f"{data_name}.gender")

    content = scipy.io.loadmat(file_path)
    count, original_count, missed = 0, 0, 0
    mapping = {}
    try:
        for node_info in content["local_info"]:
            if node_info[1] == 0:
                missed += 1
            elif node_info[1] == 1:
                G.add_node(count, gender="female")
                mapping[count] = original_count
                original_count += 1
            elif node_info[1] == 2:
                G.add_node(count, gender="male")
                mapping[count] = original_count
                original_count += 1
            else:
                logger.info(f"Another group found! {node_info[1]}")
            count += 1
    except KeyError:
        logger.info(f"Could not find the key : local_info, CHECK!")
        return
    else:
        if missed > 0:
            logger.info(f"no gender information for {missed} nodes")

    try:
        row, col, _ = scipy.sparse.find(content["A"])
    except KeyError:
        logger.info(f"Could not find the key : A, CHECK!")
        return

    missed = 0
    for r, c in zip(row, col):
        if G.has_node(r) and G.has_node(c):
            G.add_edge(r, c)
        else:
            missed += 1
    logger.info(f"Missed {missed} connections due to no Gender information")

    G = nx.relabel_nodes(G, mapping)
    with open(write_network_file, "wb") as fw:
        nx.write_adjlist(G, fw)
    with open(write_gender_file, "w") as fw:
        json.dump(nx.get_node_attributes(G, "gender"), fw)


if __name__ == "__main__":
    if not os.path.exists(os.path.join(FACEBOOK_DATA_PATH, "facebook100_zip")):
        print("The data for Facebook does not exist! Download data from https://archive.org/download/oxford-2005-facebook-matrix/facebook100.zip")
        print("Unzip it and rename facebook100 folder to facebook100_zip")
        print("re-run the code then.")
        sys.exit(0)

    if os.path.exists(os.path.join(FACEBOOK_DATA_PATH, "run_details.txt")):
        os.remove(os.path.join(FACEBOOK_DATA_PATH, "run_details.txt"))

    if os.path.exists(os.path.join(FACEBOOK_DATA_PATH, "raw_graphs")):
        shutil.rmtree(os.path.join(FACEBOOK_DATA_PATH, "raw_graphs"))
    os.mkdir(os.path.join(FACEBOOK_DATA_PATH, "raw_graphs"))

    f_handler = logging.FileHandler(os.path.join(FACEBOOK_DATA_PATH, "run_details.txt"))
    logger = logging.getLogger("facebook100")
    logger.addHandler(f_handler)
    s_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(s_handler)
    logger.setLevel(level=logging.INFO)

    for file_name in os.listdir(os.path.join(FACEBOOK_DATA_PATH, "facebook100_zip")):
        if file_name.endswith(".mat"):
            create_network_file(file_path=os.path.join(FACEBOOK_DATA_PATH, "facebook100_zip", file_name))
