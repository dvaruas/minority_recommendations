from code.growth_network.snapshot_explorer.event_snapshots import EventSnapshots
from code.growth_network.snapshot_explorer.events import RecommendationEvent


class RecommendationCount:
    @staticmethod
    def compute(job_obj, steps):
        es = EventSnapshots()
        es.create_snapshots_from_log(log_file_path=job_obj.get_log_path())
        step = int(10000 / steps)
        #print(step)
        G = None
        counts = {}
        i = 0
        step_now = 0
        while step_now < 10000:
            G, events = es.get_network(G, step_now, step_now + step)
            step_now += step
            min_min, min_maj = 0, 0
            maj_min, maj_maj = 0, 0
            minority_chosen, majority_chosen = 0, 0
            for e in events:
                if isinstance(e, RecommendationEvent):
                    if e.r_for.t == "minority":
                        minority_chosen += 1
                        for n in e.r_nodes:
                            if n.t == "minority":
                                min_min += 1
                            else:
                                min_maj += 1
                    else:
                        majority_chosen += 1
                        for n in e.r_nodes:
                            if n.t == "minority":
                                maj_min += 1
                            else:
                                maj_maj += 1

            counts[i] = {"minority" : {"minority" : 0, "majority" : 0},
                         "majority" : {"minority" : 0, "majority" : 0}}
            if minority_chosen > 0:
                counts[i]["minority"]["minority"] = min_min / minority_chosen
                counts[i]["minority"]["majority"] = min_maj / minority_chosen
            if majority_chosen > 0:
                counts[i]["majority"]["minority"] = maj_min / majority_chosen
                counts[i]["majority"]["majority"] = maj_maj / majority_chosen
            i += 1

        return counts

    @staticmethod
    def get_plot_points(job_objs, steps):
        all_counts = [RecommendationCount.compute(obj, steps) for obj in job_objs]
        com_counts = {"minority" : {"minority" : [0] * steps, "majority" : [0] * steps},
                      "majority" : {"minority" : [0] * steps, "majority" : [0] * steps}}
        for count in all_counts:
            for k in sorted(count.keys()):
                for type in ["minority", "majority"]:
                    for inner_type in ["minority", "majority"]:
                        com_counts[type][inner_type][k] += count[k][type][inner_type]
        for type in ["minority", "majority"]:
            for inner_type in ["minority", "majority"]:
                for k in range(steps):
                    com_counts[type][inner_type][k] /= len(job_objs)
        return com_counts
