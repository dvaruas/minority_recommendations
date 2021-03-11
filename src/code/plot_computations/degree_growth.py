import networkx as nx
import re


class DegreeGrowthPlotPoints:
    @staticmethod
    def _compute(job_obj, starting_step, final_step):
        recommendation_pattern = re.compile(r"Recommendation for (.*) : \[(.*)\]")
        node_addition_pattern = re.compile(r"Added Node : (.*), type : (.*)")
        edge_addition_pattern = re.compile(r"Added Edge : (.*), (.*)")

        log_file_path = job_obj.get_log_path()
        degree_counts = []
        G = nx.Graph()

        with open(log_file_path, "r") as fr:
            line = "something"
            min_node, maj_node = None, None

            while line:
                line = fr.readline().strip()
                add_now = False

                recommendation_match = recommendation_pattern.match(line)
                node_addition_match = node_addition_pattern.match(line)
                edge_addition_match = edge_addition_pattern.match(line)

                if recommendation_match:
                    # This line talks about recommendations
                    curr_offset = fr.tell()
                    next_line = fr.readline().strip()
                    if not next_line or not edge_addition_pattern.match(next_line):
                        add_now = True
                    fr.seek(curr_offset)
                elif node_addition_match:
                    # This line talks about adding a new node
                    G.add_node(int(node_addition_match.group(1)), type=node_addition_match.group(2))
                    curr_offset = fr.tell()
                    next_line = fr.readline().strip()
                    if not next_line or not edge_addition_pattern.match(next_line):
                        add_now = True
                    fr.seek(curr_offset)
                elif edge_addition_match:
                    # This line talks about adding a new edge
                    G.add_edge(int(edge_addition_match.group(1)), int(edge_addition_match.group(2)))
                    add_now = True

                if add_now:
                    min_degree, maj_degree = -1, -1
                    if min_node and maj_node:
                        min_degree, maj_degree = G.degree[min_node], G.degree[maj_node]
                    else:
                        for node, type in nx.get_node_attributes(G, 'type').items():
                            if type == "minority" and min_degree < G.degree[node]:
                                min_node, min_degree = node, G.degree[node]
                            elif type == "majority" and maj_degree < G.degree[node]:
                                maj_node, maj_degree = node, G.degree[node]

                    if min_degree > 0 and maj_degree > 0:
                        degree_counts.append({"minority" : min_degree, "majority" : maj_degree})

        final_values = {"minority" : [], "majority" : []}

        if len(degree_counts) > 0:
            step_size = len(degree_counts) // (final_step)

            base_minority, base_majority = degree_counts[step_size * 10]["minority"], degree_counts[step_size * 10]["majority"]


            for i in range(starting_step, final_step + 1):
                try:
                    curr_minority = degree_counts[i * step_size]["minority"] / base_minority
                    curr_majority = degree_counts[i * step_size]["majority"] / base_majority
                except IndexError:
                    pass
                final_values["minority"].append(curr_minority)
                final_values["majority"].append(curr_majority)

        return final_values


    @staticmethod
    def get_plot_points(job_objs, starting_step=10, final_step=40):
        x_values = list(range(starting_step, final_step + 1))
        final_result = {"minority" : {"x" : x_values, "y" : [0.0] * len(x_values)},
                        "majority" : {"x" : x_values, "y" : [0.0] * len(x_values)}}

        for obj in job_objs:
            res = DegreeGrowthPlotPoints._compute(job_obj=obj, starting_step=starting_step, final_step=final_step)
            for type in ["minority", "majority"]:
                for i, value in enumerate(res[type]):
                    final_result[type]["y"][i] += value

        total_jobs = len(job_objs)

        for type in ["minority", "majority"]:
            for i, val in enumerate(final_result[type]["y"]):
                final_result[type]["y"][i] /= total_jobs

        return final_result
