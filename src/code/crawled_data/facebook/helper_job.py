import configparser
import datetime
import json
import logging
import os
import sys

from code.common.recommenders.adamic_adar import AdamicAdarRecommendation
from code.common.recommenders.pa_homophily import PAHomophily
from code.common.recommenders.ranked_bandit import EspGreedy, Exp3, RankedBanditRecommendation
from code.common.recommenders.top_rank import TopRankRecommendation
from code.common.recommenders.twitter_rank import TwitterRankRecommendation
from code.common.click_model import ClickModel
from code.common.synthetic_network import SyntheticNetwork
from code.crawled_data.facebook.globals import PARAMETERS_PATH


def get_all_recommendations(job_description):
    method = job_description["recommendation_strategy"]
    redo_job = job_description["parser_args"].redo
    project_name = job_description["job"]
    minority_homophily = job_description["minority_homophily"]
    majority_homophily = job_description["majority_homophily"]
    rc = "NIL"
    if method == "top_rank" or method == "ranked_bandit":
        rc = job_description.get("ranking_factor", 0.0)
    else:
        # ranking control not really required, ignore useless jobs
        temp_rc = job_description.get("ranking_factor", 0.0)
        if temp_rc != 0.0:
            return

    unique_name = f"{project_name}_{method}_{rc}"

    # -------------------- Setup Logging ---------------------
    logger = logging.getLogger(unique_name)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(message)s')
    if job_description["parser_args"].debug:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)
    if not job_description["parser_args"].silent:
        s_handler = logging.StreamHandler(sys.stdout)
        s_handler.setFormatter(formatter)
        logger.addHandler(s_handler)
    #---------------------------------------------------------

    strategy_file_path = os.path.join(job_description["recommendations_dir"], f"{method}_{rc}.json")
    if os.path.exists(strategy_file_path):
        if redo_job:
            os.remove(strategy_file_path)
        else:
            return

    start_time = datetime.datetime.now()
    logger.info("Starting Job")

    # Get configurations
    cfg = configparser.ConfigParser()
    cfg.read(PARAMETERS_PATH)

    small_value = job_description.get("very_small_value",
        cfg.getfloat(section="network", option="very_small_value"))
    num_slots = job_description.get("num_slots",
        cfg.getint(section="model_common", option="num_slots"))
    num_to_choose = job_description.get("num_to_choose",
        cfg.getint(section="click_model", option="num_to_choose"))
    training_iterations = job_description.get("training_iterations",
        cfg.getint(section="model_common", option="training_iterations"))
    prob_choosing_random = job_description.get("prob_choosing_random",
        cfg.getfloat(section="model_common", option="prob_choosing_random"))

    graph = SyntheticNetwork()
    graph.load_network_adjlist(file_path=job_description["graph_path"])
    graph.load_network_attribute(file_path=job_description["type_path"], attribute_name="type",
        modify_func=lambda x : (int(x[0]), "minority" if x[1] == job_description["minority"] else "majority"))
    G = graph.get_network()

    # Recommendation strategy
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
            h_aa=minority_homophily, h_bb=majority_homophily, ranking_factor=rc, log_name=unique_name)
        method_obj = TopRankRecommendation(G=G, t=training_iterations, k=num_slots,
            click_model=click_model, log_name=unique_name)
    elif method == "ranked_bandit":
        # using Exp3 method for RL here.
        rl_method_obj = Exp3(gamma=prob_choosing_random, log_name=unique_name)
        click_model = ClickModel(c=num_to_choose, G=G, small_value=small_value,
            h_aa=minority_homophily, h_bb=majority_homophily, ranking_factor=rc, log_name=unique_name)
        method_obj = RankedBanditRecommendation(G=G, t=training_iterations,
            k=num_slots, bandit_model_obj=rl_method_obj, click_model=click_model, log_name=unique_name)
        del rl_method_obj

    complete_r_list = {}
    for node in G.nodes:
        r_list = method_obj.get_recommendations_list(seeker=node)
        complete_r_list[node] = {}
        for indx, r_node in enumerate(r_list, 1):
            complete_r_list[node][indx] = int(r_node)

    with open(strategy_file_path, "w") as fw:
        json.dump(complete_r_list, fw)

    end_time = datetime.datetime.now()

    logger.info("Ending Job. Time Elapsed : {} seconds".format((end_time - start_time).seconds))
