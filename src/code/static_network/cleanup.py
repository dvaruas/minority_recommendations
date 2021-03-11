import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import json
import shutil

from code.static_network.globals import STATIC_DATA_PATH


if __name__ == "__main__":
    delete_generated_network_files = False

    checked, deleted = 0, 0
    for dir_name in os.listdir(STATIC_DATA_PATH):
        if not dir_name.startswith("Job"):
            continue

        dir_path = os.path.join(STATIC_DATA_PATH, dir_name)

        # Cleanup the dirs which don't have the job_info.json
        if not os.path.exists(os.path.join(dir_path, "job_info.json")):
            shutil.rmtree(dir_path)
            deleted += 1
        else:
            if delete_generated_network_files:
                try:
                    os.remove(os.path.join(dir_path, "raw", "raw_graph.adjlist"))
                except FileNotFoundError:
                    pass
                try:
                    os.remove(os.path.join(dir_path, "raw", "raw_graph.type"))
                except FileNotFoundError:
                    pass

            # Check additionaly the recommendation folder
            recommendation_dir = os.path.join(dir_path, "recommendations")
            if os.path.exists(recommendation_dir):
                for file_name in os.listdir(recommendation_dir):
                    remove = False
                    with open(os.path.join(recommendation_dir, file_name), "r") as fr:
                        try:
                            file_data = json.load(fr)
                        except json.JSONDecodeError as e:
                            remove = True
                    if remove:
                        os.remove(os.path.join(recommendation_dir, file_name))

        checked += 1

    print(f"Checked {checked} directories | Deleted {deleted} directories")
