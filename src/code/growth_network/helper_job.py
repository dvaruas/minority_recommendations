import configparser
import datetime
import json
import logging
import os
import shutil
import sys
import numpy as np

from code.common.recommenders.adamic_adar import AdamicAdarRecommendation
from code.common.recommenders.pa_homophily import PAHomophily
from code.common.recommenders.ranked_bandit import EspGreedy, Exp3, RankedBanditRecommendation
from code.common.recommenders.top_rank import TopRankRecommendation
from code.common.recommenders.twitter_rank import TwitterRankRecommendation
from code.common.click_model import ClickModel
from code.growth_network.globals import GROWTH_DATA_PATH, PARAMETERS_PATH
from code.growth_network.growth_network import GrowthSyntheticNetwork


def grow_network(job_description):
    minority_homophily = job_description["minority_homophily"]
    majority_homophily = job_description["majority_homophily"]
    minority_prob = job_description["minority_prob"]
    simulation = job_description["simulation"]
    job_name = job_description["job_name"]
    method = job_description["method"]
    redo_param = job_description["parser_args"].redo
    job_path = os.path.join(GROWTH_DATA_PATH, job_name)

    rank_control_factor = "NIL"
    if method == "top_rank" or method == "ranked_bandit":
        rank_control_factor = job_description.get("ranking_control", 0.0)
    else:
        # ranking control not really required, ignore useless jobs
        temp_rank_control_factor = job_description.get("ranking_control", 0.0)
        if temp_rank_control_factor != 0.0:
            return

    if os.path.exists(job_path):
        if redo_param == True:
            shutil.rmtree(job_path)
        else:
            return

    unique_name = f"{job_name}_{method}_{rank_control_factor}"

    # -------------------- Setup Logging ---------------------
    job_logger = logging.getLogger(unique_name)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(message)s')
    if job_description["parser_args"].debug:
        job_logger.setLevel(level=logging.DEBUG)
    else:
        job_logger.setLevel(level=logging.INFO)
    if not job_description["parser_args"].silent:
        s_handler = logging.StreamHandler(sys.stdout)
        s_handler.setFormatter(formatter)
        job_logger.addHandler(s_handler)
    #---------------------------------------------------------

    start_time = datetime.datetime.now()
    job_logger.info("Starting Job")

    # create the directories
    os.makedirs(os.path.join(job_path, "raw"))

    # Make log file settings
    logger = logging.getLogger(job_name)
    f_handler = logging.FileHandler(os.path.join(job_path, "raw", "logfile.txt"))
    logger.addHandler(f_handler)
    logger.setLevel(level=logging.INFO)

    # Get configurations
    cfg = configparser.ConfigParser()
    cfg.read(PARAMETERS_PATH)

    total_iterations = job_description.get("total_iterations",
        cfg.getint(section="growth_params", option="total_iterations"))
    job_description["total_iterations"] = total_iterations
    organic_prob = job_description.get("organic_growth_probability",
        cfg.getfloat(section="growth_params", option="organic_growth_probability"))
    job_description["organic_growth_probability"] = organic_prob
    randomness = job_description.get("randomness",
        cfg.getfloat(section="growth_params", option="randomness"))
    job_description["randomness"] = randomness
    small_value = job_description.get("very_small_value",
        cfg.getfloat(section="network", option="very_small_value"))
    job_description["very_small_value"] = small_value
    num_slots = job_description.get("num_slots",
        cfg.getint(section="model_common", option="num_slots"))
    job_description["num_slots"] = num_slots
    num_to_choose = job_description.get("num_to_choose",
        cfg.getint(section="click_model", option="num_to_choose"))
    job_description["num_to_choose"] = num_to_choose
    training_iterations = job_description.get("training_iterations",
        cfg.getint(section="model_common", option="training_iterations"))
    job_description["training_iterations"] = training_iterations
    prob_choosing_random = job_description.get("prob_choosing_random",
        cfg.getfloat(section="model_common", option="prob_choosing_random"))
    job_description["prob_choosing_random"] = prob_choosing_random

    graph = GrowthSyntheticNetwork(log_name=job_name)
    graph.save_info(key="small_value", info=small_value)
    graph.save_info(key="h_aa", info=minority_homophily)
    graph.save_info(key="h_bb", info=majority_homophily)
    graph.save_info(key="ranking_control", info=rank_control_factor)
    graph.initialize_empty_network()
    node_0_type = np.random.choice(a=["minority", "majority"])
    graph.add_new_node(node_name=0, type=node_0_type) # Start with a single node
    logger.info(f"Added Node : 0, type : {node_0_type}")

    # Recommendation strategy
    G = graph.get_network()
    method_obj = None
    if method == "pa_homophily":
        method_obj = PAHomophily(G=G, k=num_slots, small_value=small_value,
            h_aa=minority_homophily, h_bb=majority_homophily, log_name=unique_name)
    elif method == "adamic_adar":
        method_obj = AdamicAdarRecommendation(G=G, k=num_slots, log_name=unique_name)
    elif method == "twitter_rank":
        method_obj = TwitterRankRecommendation(G=G, k=num_slots, log_name=unique_name)
    elif method == "top_rank":
        click_model = ClickModel(c=num_to_choose, G=G, small_value=small_value,
            h_aa=minority_homophily, h_bb=majority_homophily, ranking_factor=rank_control_factor, log_name=unique_name)
        method_obj = TopRankRecommendation(G=G, t=training_iterations, k=num_slots,
            click_model=click_model, log_name=unique_name)
    elif method == "ranked_bandit":
        # using Exp3 method for RL here.
        rl_method_obj = Exp3(gamma=prob_choosing_random, log_name=unique_name)
        click_model = ClickModel(c=num_to_choose, G=G, small_value=small_value,
            h_aa=minority_homophily, h_bb=majority_homophily, ranking_factor=rank_control_factor, log_name=unique_name)
        method_obj = RankedBanditRecommendation(G=G, t=training_iterations,
            k=num_slots, bandit_model_obj=rl_method_obj, click_model=click_model, log_name=unique_name)
        del rl_method_obj

    graph.save_info(key="recommender", info=method_obj)

    node_num = 1
    info_string = None
    while total_iterations > 0:
        job_logger.debug(f"Iteration : {total_iterations}, number of nodes : {node_num}")
        growth_type = np.random.choice(a=[0, 1], p=[organic_prob, 1.0 - organic_prob])
        source_node = node_num
        if growth_type == 0:
            type_label = np.random.choice(a=["minority", "majority"], p=[minority_prob, 1.0 - minority_prob])
            # Organic Growth
            random_choice = np.random.choice(a=[0, 1], p=[randomness, 1.0 - randomness])
            if random_choice == 0:
                info_string = "Growth type : Organic(Random)"
                # Choose a Random Node to add to
                #print("Organic Growth by connecting with random node")
                target_node = graph.get_random_node()
            else:
                info_string = "Growth type : Organic(Preferred)"
                # Use Preferential Attachment to add to
                #print("Organic Growth by connecting with Preferential Attachment")
                target_node = graph.get_preferred_node(seeker_type=type_label)
            graph.add_new_node(node_name=node_num, type=type_label)
            logger.info(f"Added Node : {node_num}, type : {type_label}")
            node_num += 1
        else:
            info_string = "Growth type : Algorithmic"
            # Recommendation
            #s_t = datetime.datetime.now()
            source_node = graph.get_random_node()
            target_node = graph.get_recommended_node(seeker=source_node)
            #e_t = datetime.datetime.now()
            #print("Connection via Recommendation done, took : {} seconds".format((e_t - s_t).seconds))

        if target_node != None and source_node != target_node:
            graph.add_new_edge(node_one=source_node, node_two=target_node)
            logger.info(f"Added Edge : {source_node}, {target_node}")

        logger.info(f"Iteration info > {info_string}")
        total_iterations -= 1

    end_time = datetime.datetime.now()

    job_description["time"] = (end_time - start_time).seconds
    job_logger.info("Ending Job. Time Elapsed : {} seconds".format(job_description["time"]))

    job_description.pop("parser_args")
    # Write down the Job description in the job_info.json file
    with open(os.path.join(job_path, "job_info.json"), "w") as fw:
        json.dump(job_description, fw)
