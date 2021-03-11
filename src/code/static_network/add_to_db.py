import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import json

from code.static_network.globals import STATIC_DATA_PATH
from code.static_network.static_data_manager import StaticNetwork


if __name__ == "__main__":
    static_obj = StaticNetwork()

    for dir_name in os.listdir(STATIC_DATA_PATH):
        job_path = os.path.join(STATIC_DATA_PATH, dir_name)
        if not os.path.exists(os.path.join(job_path, "job_info.json")):
            continue

        with open(os.path.join(job_path, "job_info.json"), "r") as fr:
            data = json.load(fr)

        data["job_id"] = dir_name

        static_obj.insert_new_job(all_params=data, defer_commit=True)

    static_obj.commit()
