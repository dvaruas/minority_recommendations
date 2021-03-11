import json
import os


class DVStaticPlotPoints:
    @staticmethod
    def _compute(job_obj, method):
        recommendations_file = os.path.join(job_obj.get_job_dir(), "recommendations", f"{method}.json")
        with open(recommendations_file, "r") as fr:
            data = json.load(fr)
        G = job_obj.get_network()
        rec_counter = {}
        minority_nodes, majority_nodes = [], []
        for node, rec_dict in data.items():
            if G.nodes[int(node)]["type"] == "minority":
                minority_nodes.append(int(node))
            else:
                majority_nodes.append(int(node))
            for rec_node in rec_dict.values():
                rec_counter[rec_node] = rec_counter.get(rec_node, 0) + 1

        total_minority_nodes = len(minority_nodes)
        total_majority_nodes = len(majority_nodes)
        total_nodes = total_minority_nodes + total_majority_nodes
        minority_fraction = total_minority_nodes / total_nodes
        majority_fraction = 1.0 - minority_fraction

        minority_visibility = (1 / (5 * total_nodes)) * sum([rec_counter.get(node, 0) for node in minority_nodes])
        majority_visibility = (1 / (5 * total_nodes)) * sum([rec_counter.get(node, 0) for node in majority_nodes])

        return ((minority_visibility / minority_fraction) - (majority_visibility / majority_fraction))

    @staticmethod
    def get_plot_points(homophily_job_dict, method):
        x_values = []
        y_values = []
        lower_err, upper_err = [], []
        for h in sorted(homophily_job_dict):
            all_values = [DVStaticPlotPoints._compute(job_obj=obj, method=method) for obj in homophily_job_dict[h]]
            x_values.append(h)
            agg_y_value = sum(all_values) / len(homophily_job_dict[h])
            lower_err.append(agg_y_value - min(all_values))
            upper_err.append(max(all_values) - agg_y_value)
            y_values.append(agg_y_value)

        return {"x" : x_values, "y" : y_values, "e" : [lower_err, upper_err]}


class DVEmpiricalPlotPoints:
    @staticmethod
    def _compute(job_obj, file_path):
        with open(file_path, "r") as fr:
            data = json.load(fr)
        G = job_obj.get_network()
        rec_counter = {}
        minority_nodes, majority_nodes = [], []
        for node, rec_dict in data.items():
            if G.nodes[int(node)]["type"] == "minority":
                minority_nodes.append(int(node))
            else:
                majority_nodes.append(int(node))
            for rec_node in rec_dict.values():
                rec_counter[rec_node] = rec_counter.get(rec_node, 0) + 1

        total_minority_nodes = len(minority_nodes)
        total_majority_nodes = len(majority_nodes)
        total_nodes = total_minority_nodes + total_majority_nodes
        minority_fraction = total_minority_nodes / total_nodes
        majority_fraction = 1.0 - minority_fraction

        minority_visibility = (1 / (5 * total_nodes)) * sum([rec_counter.get(node, 0) for node in minority_nodes])
        majority_visibility = (1 / (5 * total_nodes)) * sum([rec_counter.get(node, 0) for node in majority_nodes])

        return ((minority_visibility / minority_fraction) - (majority_visibility / majority_fraction))

    @staticmethod
    def get_plot_points(job_obj, methods):
        x_values = []
        y_values = []
        colors = []
        for method_name, params in methods.items():
            recommendations_path = params[0]
            method_color = params[1]
            value = DVEmpiricalPlotPoints._compute(job_obj=job_obj, file_path=recommendations_path)
            x_values.append(method_name)
            y_values.append(value)
            colors.append(method_color)

        return {"x" : x_values, "y" : y_values, "color" : colors}
