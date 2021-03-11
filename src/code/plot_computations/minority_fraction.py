import networkx as nx


class MinorityFractionPlotPoints:
    @staticmethod
    def _compute(job_obj):
        total_minority_degree, total_degree = 0, 0
        G = job_obj.get_network()
        for node, degree in nx.degree(G):
            if G.nodes[node]['type'] == "minority":
                total_minority_degree += degree
            total_degree += degree
        return (total_minority_degree / total_degree)

    @staticmethod
    def get_plot_points(homophily_job_dict={}):
        x_values = []
        y_values = []
        lower_err, upper_err = [], []
        for h in sorted(homophily_job_dict.keys()):
            all_values = [MinorityFractionPlotPoints._compute(job_obj=obj) for obj in homophily_job_dict[h]]
            x_values.append(h)
            agg_y_value = sum(all_values) / len(homophily_job_dict[h])
            lower_err.append(agg_y_value - min(all_values))
            upper_err.append(max(all_values) - agg_y_value)
            y_values.append(agg_y_value)

        return {"x" : x_values, "y" : y_values, "e" : [lower_err, upper_err]}
