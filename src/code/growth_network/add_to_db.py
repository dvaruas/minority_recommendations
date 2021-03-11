import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import json

from code.growth_network.globals import GROWTH_DATA_PATH
from code.growth_network.growth_data_manager import GrowNetwork


if __name__ == "__main__":
    grow_obj = GrowNetwork()
    default_params = {"total_iterations" : 10000,
                      "randomness" : 0.1,
                      "organic_growth_probability" : 0.1,
                      "num_to_choose" : 1,
                      "training_iterations" : 10000,
                      "num_slots" : 5,
                      "prob_choosing_random" : 0.1}

    misc_mapping = {"minority_homophily" : "homophily",
                    "minority_prob" : "minority_probability",
                    "method" : "job_type"}

    for dir_name in os.listdir(GROWTH_DATA_PATH):
        job_path = os.path.join(GROWTH_DATA_PATH, dir_name)
        if not os.path.exists(os.path.join(job_path, "job_info.json")):
            continue

        with open(os.path.join(job_path, "job_info.json"), "r") as fr:
            data = json.load(fr)

        params = dict(data)
        params["job_id"] = dir_name
        for key in data.keys():
            if key in misc_mapping:
                value = params.pop(key)
                params[misc_mapping[key]] = value

        for key, value in default_params.items():
            params[key] = data.get(key, value)
            data[key] = value

        grow_obj.insert_new_job(all_params=params, defer_commit=True)

    grow_obj.commit()
