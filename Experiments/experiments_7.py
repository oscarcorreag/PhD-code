import numpy as np
import time
import csv

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from hotspot_based import HotspotBased

if __name__ == '__main__':
    #
    results = []
    osm = OsmManager()
    generator = SuitableNodeWeightGenerator()
    #
    files = {21303: 'maribyrnong'}
    samples = range(3)
    #
    for sa3_code11, file_ in files.items():
        #
        act_dh = {}
        dep_hours = osm.get_departure_hours(file_)
        for dh in dep_hours:
            dest_acts = osm.get_dest_activities(file_, dh)
            for act_desc in dest_acts:
                try:
                    act_dh[act_desc[0]].append(dh)
                except KeyError:
                    act_dh[act_desc[0]] = [dh]
        #
        for act, dhs in act_dh.items():
            graph, hotspots, pois, nodes_by_sa1_code, nodes_by_sa2_code = osm.generate_graph_for_file(file_, act, generator)
            reset_hotspots_weights = {h: generator.weights["WARNING"][0] for h in hotspots}
            graph.compute_dist_paths(compute_paths=False)
            #
            p = len(pois)
            n = len(graph.keys())
            h = len(hotspots)
            #
            graph_rh = graph.copy()
            graph_ch = graph.copy()
            #
            graph_rh.update_node_weights(reset_hotspots_weights)
            graph_ch.update_node_weights(reset_hotspots_weights)
            #
            for dh in dhs:
                for sample in samples:
                    terminals = osm.choose_terminals_according_to_vista(file_, dh, act, nodes_by_sa1_code)
                    t = len(terminals)
                    new_hotspots = set(graph.keys()).difference(terminals).difference(pois)
                    # ORIGINAL hot spots' locations.
                    for awareness in np.arange(0.0, 1.1, 0.1):
                        hb = HotspotBased(graph, terminals, pois, hot_spots=new_hotspots)
                        st = time.clock()
                        forest, cost, gr, avg_dr, nt, avg_or, avg_oc, lsv = hb.steiner_forest(k=5, awareness=awareness)
                        et = time.clock() - st
                        line = ["original", awareness, sa3_code11, dh, act, cost, gr, avg_dr, nt, avg_or, avg_oc, et, h, t, p, n, sample, lsv]
                        results.append(line)
                        print line[:-1]
                    # RANDOM hot spots' locations.
                    nodes_left_rh = list(set(graph_rh.keys()).difference(pois).difference(terminals))
                    ind_rh = np.random.choice(a=len(nodes_left_rh), size=h, replace=False)
                    rh = [nodes_left_rh[i] for i in ind_rh]
                    weights = {h: generator.weights["VERY_SUITABLE"][0] for h in rh}
                    graph_rh.update_node_weights(weights)
                    for awareness in np.arange(0.0, 1.1, 0.1):
                        hb = HotspotBased(graph_rh, terminals, pois, hot_spots=new_hotspots)
                        st = time.clock()
                        forest, cost, gr, avg_dr, nt, avg_or, avg_oc, lsv = hb.steiner_forest(k=5, awareness=awareness)
                        et = time.clock() - st
                        line = ["random", awareness, sa3_code11, dh, act, cost, gr, avg_dr, nt, avg_or, avg_oc, et, h, t, p, n, sample, lsv]
                        results.append(line)
                        print line[:-1]
                    # CLUSTERED hot spots' locations according to population distribution.
                    excluded = list(terminals)
                    excluded.extend(pois)
                    ch = osm.choose_hotspots_according_to_population(sa3_code11, h, nodes_by_sa2_code, excluded)
                    weights = {h: generator.weights["VERY_SUITABLE"][0] for h in ch}
                    graph_ch.update_node_weights(weights)
                    for awareness in np.arange(0.0, 1.1, 0.1):
                        hb = HotspotBased(graph_ch, terminals, pois, hot_spots=new_hotspots)
                        st = time.clock()
                        forest, cost, gr, avg_dr, nt, avg_or, avg_oc, lsv = hb.steiner_forest(k=5, awareness=awareness)
                        et = time.clock() - st
                        line = ["clustered", awareness, sa3_code11, dh, act, cost, gr, avg_dr, nt, avg_or, avg_oc, et, h, t, p, n, sample, lsv]
                        results.append(line)
                        print line[:-1]
    #
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