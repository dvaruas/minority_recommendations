# This is a throw-away code to figure out all the confusing names. Can delete it later.
# This might not be updated according to the currecnt code structure.
import itertools
import os
import json


simulations = [1, 2, 3, 4, 5]
homophily = [0.0, 0.2, 0.5, 0.8, 1.0]
minority_probability = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
ranking_control = [0.0, 0.5, 1.0]
job_type = ["adamic_adar", "twitter_rank", "top_rank", "ranked_bandit", "pa_homophily"]

pool_jobs = []
job_names_start = {"adamic_adar" : 0,
                   "twitter_rank" : 450,
                   "pa_homophily" : 900,
                   "ranked_bandit" : 1350,
                   "top_rank" : 1800}
remaining_jobs = []

# for h, m, s, rc, type in remaining_jobs:
for h, m, s, rc, type in itertools.product(homophily, minority_probability, simulations, ranking_control, job_type):
    # Assign Job Name
    job_name = "Job_{}".format(job_names_start[type])
    job_names_start[type] += 1

    job_description = {"minority_homophily" : h, "majority_homophily" : h,
        "minority_prob" : m, "simulation" : s, "method" : type,
        "ranking_control" : rc, "job_name" : job_name}

    pool_jobs.append(job_description)

changes = {}

data_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "data", "synthetic", "growth")
for job in pool_jobs:
    if not os.path.exists(os.path.join(data_path, job["job_name"])):
        continue
    with open(os.path.join(data_path, job["job_name"], "job_info.json")) as fr:
        info = json.load(fr)
    mismatches = []
    copy_info = dict(info)
    for k, v in info.items():
        if k not in job.keys():
            copy_info.pop(k)
        elif v != job[k]:
            mismatches.append(f"{k} : {job[k]} <-> {v}")

    if mismatches:
        actual_job = []
        for check_job in pool_jobs:
            if all([copy_info[k] == v for k, v in check_job.items() if k != "job_name"]):
                actual_job.append(check_job["job_name"])
        if len(actual_job) == 1:
            changes[job["job_name"]] = actual_job[0]
        else:
            print("Found more than one actual job, something is wrong ... {} : {}".format(job["job_name"], actual_job))
        print("{} : {}. Actual Job : {}".format(job["job_name"], " ; ".join(mismatches), actual_job))

def make_change(change_this):
    print(f"Working on : {change_this}")
    if change_this not in changes:
        return
    changed_to = changes[change_this]
    if changed_to in changes:
        make_change(change_this=changed_to)
    with open(os.path.join(data_path, change_this, "job_info.json"), "r") as fr:
        info = json.load(fr)
    info["job_name"] = changed_to
    with open(os.path.join(data_path, change_this, "job_info.json"), "w") as fw:
        json.dump(info, fw)
    os.rename(os.path.join(data_path, change_this), os.path.join(data_path, changed_to))
    print(f"Changed {change_this} to {changed_to}")
    changes.pop(change_this)

jobs_to_change = list(changes.keys())
for j in jobs_to_change:
    make_change(change_this=j)
