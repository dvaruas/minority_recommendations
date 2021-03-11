import datetime
import json
import logging
import os
import shutil
import sys

from code.static_network.globals import STATIC_DATA_PATH
from code.static_network.generate.pa_homophily_network import GenerateSyntheticNetwork


def generate_pa_homophily_network(all_params):
    job_name = all_params["job_name"]
    redo_job = all_params["parse_args"].redo

    job_path = os.path.join(STATIC_DATA_PATH, job_name)

    if os.path.exists(job_path):
        if redo_job:
            shutil.rmtree(job_path)
        else:
            return

    # -------------------- Setup Logging ---------------------
    job_logger = logging.getLogger(f"{job_name}_slog")
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(message)s')
    if all_params["parse_args"].debug:
        job_logger.setLevel(level=logging.DEBUG)
    else:
        job_logger.setLevel(level=logging.INFO)
    if not all_params["parse_args"].silent:
        s_handler = logging.StreamHandler(sys.stdout)
        s_handler.setFormatter(formatter)
        job_logger.addHandler(s_handler)
    #---------------------------------------------------------

    start_time = datetime.datetime.now()

    job_logger.info("Starting Job")

    # create the raw dump dir
    os.makedirs(os.path.join(job_path, "raw"))

    # Make log file settings
    f_handler = logging.FileHandler(os.path.join(job_path, "raw", "logfile.txt"))
    logger = logging.getLogger(job_name)
    logger.addHandler(f_handler)
    logger.setLevel(level=logging.INFO)

    syn_network = GenerateSyntheticNetwork(log_name=job_name)
    syn_network.save_info("total_nodes", all_params["total_nodes"])
    syn_network.save_info("edges_per_iteration", all_params["edges_per_iteration"])
    syn_network.save_info("initial_nodes", all_params["initial_nodes"])
    syn_network.save_info("minority_fraction", all_params["minority_probability"])
    syn_network.save_info("homophily_among_minorities", all_params["homophily"])
    syn_network.save_info("homophily_among_majorities", all_params["homophily"])
    syn_network.generate_network()

    end_time = datetime.datetime.now()

    all_params["time"] = (end_time - start_time).seconds
    job_logger.info("Ending Job. Time Elapsed : {} seconds".format(all_params["time"]))

    all_params.pop("parse_args")
    # Write down the Job description in the job_info.json file
    with open(os.path.join(job_path, "job_info.json"), "w") as fw:
        json.dump(all_params, fw)
