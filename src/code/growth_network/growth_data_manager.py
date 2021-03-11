import os

from code.growth_network.globals import GROWTH_DATA_PATH
from code.common.data_manager import Manager


class ParametersProfile(Manager):
    def __init__(self):
        super().__init__(name="parameters")
        self.add_field(field_name="profile_id", field_type="int")
        self.add_field(field_name="total_iterations", field_type="int")
        self.add_field(field_name="randomness", field_type="float")
        self.add_field(field_name="organic_growth_probability", field_type="float")
        self.add_field(field_name="num_to_choose", field_type="int")
        self.add_field(field_name="training_iterations", field_type="int")
        self.add_field(field_name="num_slots", field_type="int")
        self.add_field(field_name="prob_choosing_random", field_type="float")
        self.create_table()

    def get_parameter_id(self, values, insert_if_not_found=False):
        id = None
        answers = self.fetch(values=values)
        if len(answers) == 0:
            if insert_if_not_found:
                # Not present, first insert
                self.conn.execute("select max(profile_id) from parameters")
                id = self.conn.fetchone()[0]
                if id == None:
                    id = 0
                else:
                    id += 1
                values["profile_id"] = id
                self.insert(values=values)
        elif len(answers) > 1:
            print(f"ERROR : There are multiple profile entries for same parameter values = {values}, check.. check....")
            id = answers[0]["profile_id"]
        else:
            id = answers[0]["profile_id"]
        return id


class GrowNetwork(Manager):
    def __init__(self):
        super().__init__(name="grow_network")
        self.add_field(field_name="job_id", field_type="int")
        self.add_field(field_name="simulation", field_type="int")
        self.add_field(field_name="homophily", field_type="float")
        self.add_field(field_name="minority_probability", field_type="float")
        self.add_field(field_name="ranking_control", field_type="float")
        self.add_field(field_name="job_type", field_type="string")
        self.add_field(field_name="parameter_profile", field_type="int")
        self.create_table()
        self.parameters_obj = ParametersProfile()

    def get_job_ids(self, all_params):
        # all_params should contain the following keys --
        # simulation, homophily, minority_probability, ranking_control, job_type
        # To find the parameter_profile, the following --
        # total_iterations, randomness, organic_growth_probability, num_to_choose,
        # training_iterations, num_slots, prob_choosing_random
        if "job_id" in all_params:
            # Job ID is enough to get the entry
            answers = self.fetch(values=all_params)
            return [f"Job_{ans['job_id']}" for ans in answers]

        if "parameter_profile" not in all_params:
            param_id = self.parameters_obj.get_parameter_id(values=all_params)
        else:
            param_id = all_params["parameter_profile"]
        job_ids = []
        if param_id != None:
            all_params["parameter_profile"] = param_id
            answers = self.fetch(values=all_params)
            for ans in answers:
                job_ids.append(f'Job_{ans["job_id"]}')
        return job_ids

    def insert_new_job(self, all_params, defer_commit=False):
        if all_params["job_id"].startswith("Job"):
            all_params["job_id"] = all_params["job_id"].split("_")[1]
        all_params["parameter_profile"] = self.parameters_obj.get_parameter_id(values=all_params, insert_if_not_found=True)
        self.insert(values=all_params, defer_commit=defer_commit)

    def delete_job(self, job_id, defer_commit=False):
        if job_id.startswith("Job"):
            job_id = job_id.split("_")[1]
        self.delete(values={"job_id" : job_id}, defer_commit=defer_commit)

    def get_job_paths(self, all_params):
        job_ids = self.get_job_ids(all_params=all_params)
        job_paths = []
        for job_id in job_ids:
            job_paths.append(os.path.join(GROWTH_DATA_PATH, str(job_id)))
        return job_paths
