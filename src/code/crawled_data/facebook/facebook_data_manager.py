import os

from code.common.data_manager import Manager
from code.crawled_data.facebook.globals import FACEBOOK_DATA_PATH


class FacebookNetwork(Manager):
    def __init__(self):
        super().__init__(name="fb_network")
        self.add_field(field_name="project", field_type="string")
        self.add_field(field_name="total_nodes", field_type="int")
        self.add_field(field_name="total_edges", field_type="int")
        self.add_field(field_name="minority", field_type="string")
        self.add_field(field_name="minority_count", field_type="int")
        self.add_field(field_name="majority_count", field_type="int")
        self.add_field(field_name="h_minority", field_type="float")
        self.add_field(field_name="h_majority", field_type="float")
        self.add_field(field_name="minority_fraction", field_type="float")
        self.create_table()

    def get_network_ids(self, all_params):
        answers = self.fetch(values=all_params)
        network_ids = [ans["project"] for ans in answers]
        return network_ids

    def insert_network(self, all_params, defer_commit=False):
        self.insert(values=all_params, defer_commit=defer_commit)

    def delete_network(self, network_name, defer_commit=False):
        self.delete(values={"project" : network_name}, defer_commit=defer_commit)

    def get_network_info(self, all_params):
        network_info = self.fetch(values=all_params)
        network_data = [{"graph" : os.path.join(FACEBOOK_DATA_PATH, "raw_graphs", "{}.adjlist".format(info["project"])),
                          "type" : os.path.join(FACEBOOK_DATA_PATH, "raw_graphs", "{}.gender".format(info["project"])),
                          "recommendations_dir" : os.path.join(FACEBOOK_DATA_PATH, "recommendations", info["project"]),
                          "minority" : info["minority"],
                          "minority_homophily" : info["h_minority"],
                          "majority_homophily" : info["h_majority"],
                          "minority_fraction" : info["minority_fraction"],
                         } for info in network_info]
        return network_data
