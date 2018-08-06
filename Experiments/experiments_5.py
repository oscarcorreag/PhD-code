import time
import csv

from osmmanager import OsmManager
# from osmdbmanager import OsmDBManager
from suitability import SuitableNodeWeightGenerator
from hotspot_based import HotspotBased

if __name__ == '__main__':
    osm = OsmManager()
    # osmdbmngr = OsmDBManager("postgres", "anabelle1803!", "osm")
    generator = SuitableNodeWeightGenerator()
    files = {21303: 'maribyrnong'}
    samples = range(5)
    results = []
    for sa3_code11, file_ in files.items():
        act_dh = {}
        dep_hours = osm.get_departure_hours(file_)
        for dh in dep_hours:
            dest_acts = osm.get_dest_activities(file_, dh)
            for act in dest_acts:
                try:
                    act_dh[act].append(dh)
                except KeyError:
                    act_dh[act] = [dh]
        for act, dhs in act_dh.items():
            if act[0] == 805:
                continue
            graph, hotspots, pois, nodes_by_sa1_code, _ = osm.generate_graph_for_file(file_, act[0], generator)
            graph.compute_dist_paths(compute_paths=False)
            #
            h = len(hotspots)
            p = len(pois)
            n = len(graph.keys())
            #
            for dh in dhs:
                for sample in samples:
                    print "sample", sample
                    terminals = osm.choose_terminals_according_to_vista(file_, dh, act[0], nodes_by_sa1_code)
                    t = len(terminals)
                    print dh, act, h, t, p, n
                    #
                    new_hotspots = set(graph.keys()).difference(terminals).difference(pois)
                    hb = HotspotBased(graph, terminals, pois, hot_spots=new_hotspots)
                    start_time = time.clock()
                    forest, cost, gr, avg_dr, num_trees, avg_or, lsv = hb.steiner_forest(k=5, max_wd=500)
                    elapsed_time = time.clock() - start_time
                    line = ["Gr-based", sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h, t,
                            p, n, lsv]
                    results.append(line)
                    print line
                    #
                    hb = HotspotBased(graph, terminals, pois)
                    start_time = time.clock()
                    forest, cost, gr, avg_dr, num_trees, avg_or, lsv = hb.steiner_forest(k=5)
                    elapsed_time = time.clock() - start_time
                    line = ["Gr-based(h)", sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h,
                            t, p, n, lsv]
                    results.append(line)
                    print line

    ts = time.strftime("%d%b%Y_%H%M%S")
    results_f = open("files/results_" + ts + ".csv", 'wb')
    lsv_f = open("files/lsv_" + ts + ".csv", 'wb')
    wr_r = csv.writer(results_f)
    wr_l = csv.writer(lsv_f)
    for i, result in enumerate(results):
        temp = [i]
        temp.extend(result[:-1])
        wr_r.writerow(temp)
        lsv = result[-1]
        for sv, ts in lsv.items():
            for t, d in ts.items():
                wr_l.writerow([i, sv, t, d])
