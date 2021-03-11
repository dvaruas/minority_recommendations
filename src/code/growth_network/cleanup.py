import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#--------------------------------------------------------------------------------
import shutil

from code.growth_network.globals import GROWTH_DATA_PATH


if __name__ == "__main__":
    delete_generated_network_files = False

    checked, deleted = 0, 0
    for dir_name in os.listdir(GROWTH_DATA_PATH):
        if not dir_name.startswith("Job"):
            continue

        dir_path = os.path.join(GROWTH_DATA_PATH, dir_name)

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
        checked += 1

    print(f"Checked {checked} directories | Deleted {deleted} directories")
