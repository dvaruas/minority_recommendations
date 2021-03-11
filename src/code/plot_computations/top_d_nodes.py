import networkx as nx


class TopDNodesPlotPoints:
    @staticmethod
    def _compute(job_obj):
        G = job_obj.get_network()

        unique_degrees = []
        for degree, freq in enumerate(nx.degree_histogram(G)):
            if freq > 0:
                unique_degrees.append(degree)

        degree_bounds = []
        each_step = len(unique_degrees) / 10
        for i in range(1, 10):
            degree_bounds.append(unique_degrees[round(each_step * i) - 1])
        degree_bounds.reverse()

        all_nodes = dict(nx.degree(G))
        sorted_nodes = sorted(all_nodes.keys(), key=all_nodes.get, reverse=True)
        num_of_minorities = 0
        nodes_yet = 0
        index = 0
        top_d_values = {}
        for node in sorted_nodes:
            degree = all_nodes[node]
            if index < 9 and degree <= degree_bounds[index]:
                index += 1
                top_d_values[index] = num_of_minorities / nodes_yet
            nodes_yet += 1
            if G.nodes[node]['type'] == "minority":
                num_of_minorities += 1
        top_d_values[10] = num_of_minorities / nodes_yet
        return top_d_values


    @staticmethod
    def get_plot_points(job_objs):
        final_values = {"x" : [x/10 for x in range(1, 11)], "y" : [0.0] * 10}

        all_res = [TopDNodesPlotPoints._compute(job_obj=obj) for obj in job_objs]
        lower_values = [None] * 10
        upper_values = [None] * 10
        total_jobs = len(job_objs)
        for i in range(10):
            all_values = [res[i + 1] for res in all_res]
            final_values["y"][i] = sum(all_values) / total_jobs
            lower_values[i] = final_values["y"][i] - min(all_values)
            upper_values[i] = max(all_values) - final_values["y"][i]

        final_values["e"] = [lower_values, upper_values]

        return final_values
