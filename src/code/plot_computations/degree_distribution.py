import networkx as nx


class DegreeDistributionPlotPoints:
    @staticmethod
    def _compute(job_obj):
        result = {"minority" : {}, "majority" : {}}
        G = job_obj.get_network()
        for node, degree in nx.degree(G):
            if G.nodes[node]['type'] == "minority":
                if degree not in result["minority"]:
                    result["minority"][degree] = 0
                result["minority"][degree] += 1
            elif G.nodes[node]['type'] == "majority":
                if degree not in result["majority"]:
                    result["majority"][degree] = 0
                result["majority"][degree] += 1

        total_nodes = nx.number_of_nodes(G)
        for type in ["minority", "majority"]:
            for degree, count in result[type].items():
                result[type][degree] = count / total_nodes

        return result

    @staticmethod
    def get_plot_points(job_objs):
        final_result = {"minority" : {}, "majority" : {}}
        for obj in job_objs:
            res = DegreeDistributionPlotPoints._compute(job_obj=obj)
            for type in ["minority", "majority"]:
                for degree, p in res[type].items():
                    if degree not in final_result[type]:
                        final_result[type][degree] = 0
                    final_result[type][degree] += p

        consolidated_result = {"minority" : {}, "majority" : {}}
        total_jobs = len(job_objs)
        for type in ["minority", "majority"]:
            for degree, total_p in final_result[type].items():
                final_result[type][degree] = total_p / total_jobs
            all_degrees = sorted(final_result[type].keys())
            consolidated_result[type]["x"] = all_degrees
            consolidated_result[type]["y"] = [final_result[type][d] for d in all_degrees]

        return consolidated_result
