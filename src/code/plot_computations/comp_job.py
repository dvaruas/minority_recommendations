import os

from code.common.rebuild_graph import recreate_network
from code.common.synthetic_network import SyntheticNetwork


class ComputationJob:
    def __init__(self):
        self.network_path = None
        self.attributes = {}
        self.log_path = None
        self.graph = SyntheticNetwork()

    def set_network_path(self, path):
        self.network_path = path
        self.graph.load_network_adjlist(file_path=path)

    def set_attribute(self, name, path, modify_func=lambda x : (int(x[0]), x[1])):
        self.attributes[name] = {"path" : path, "modify_func" : modify_func}
        self.graph.load_network_attribute(attribute_name=name, file_path=path,
            modify_func=modify_func)

    def set_log_path(self, path):
        self.log_path = path
        job_path = os.path.join(os.path.dirname(path), os.pardir)
        self.graph.initialize_empty_network()
        recreate_network(job_path=job_path)
        self.set_network_path(path=os.path.join(job_path, "raw", "raw_graph.adjlist"))
        self.set_attribute(name="type", path=os.path.join(job_path, "raw", "raw_graph.type"))

    def get_log_path(self):
        return self.log_path

    def get_network(self):
        return self.graph.get_network()

    def get_job_dir(self):
        return os.path.join(os.path.dirname(self.network_path), os.pardir)
