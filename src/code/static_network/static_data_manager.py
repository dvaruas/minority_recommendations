import os

from code.static_network.globals import STATIC_DATA_PATH
from code.common.data_manager import Manager


class StaticNetwork(Manager):
    def __init__(self):
        super().__init__(name="static_network")
        self.add_field(field_name="job_id", field_type="int")
        self.add_field(field_name="simulation", field_type="int")
        self.add_field(field_name="homophily", field_type="float")
        self.add_field(field_name="minority_probability", field_type="float")
        self.add_field(field_name="total_nodes", field_type="int")
        self.create_table()

    def get_job_ids(self, all_params):
        job_ids = []
        answers = self.fetch(values=all_params)
        for ans in answers:
            job_ids.append(f'Job_{ans["job_id"]}')
        return job_ids

    def insert_new_job(self, all_params, defer_commit=False):
        if all_params["job_id"].startswith("Job"):
            all_params["job_id"] = all_params["job_id"].split("_")[1]
        self.insert(values=all_params, defer_commit=defer_commit)

    def delete_job(self, job_id, defer_commit=False):
        if job_id.startswith("Job"):
            job_id = job_id.split("_")[1]
        self.delete(values={"job_id" : job_id}, defer_commit=defer_commit)

    def get_job_paths(self, all_params):
        job_ids = self.get_job_ids(all_params=all_params)
        job_paths = []
        for job_id in job_ids:
            job_paths.append(os.path.join(STATIC_DATA_PATH, str(job_id)))
        return job_paths
