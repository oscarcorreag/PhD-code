import time

from osmmanager import OsmManager
from osmdbmanager import OsmDBManager
from suitability import SuitableNodeWeightGenerator
from vst_rs import VST_RS
from hotspot_based import HotspotBased

if __name__ == '__main__':
    osm = OsmManager()
    osmdbmngr = OsmDBManager("postgres", "anabelle1803!", "osm")
    generator = SuitableNodeWeightGenerator()
    files = {21303: 'maribyrnong'}
    samples = range(5)
    for sa3_code11, file_ in files.iteritems():
        dep_hours = osm.get_departure_hours(file_)
        for dh in dep_hours:
            dest_acts = osm.get_dest_activities(file_, dh)
            for act in dest_acts:
                if act[0] == 805:
                    continue
                for sample in samples:
                    print sample
                    graph, hotspots, pois, nodes_by_sa1_code, _ = osm.generate_graph_for_file(file_, act[0], generator)
                    terminals = osm.choose_terminals_according_to_vista(file_, dh, act[0], nodes_by_sa1_code)
                    temp = list(hotspots)
                    temp.extend(pois)
                    temp.extend(terminals)
                    graph.compute_dist_paths(origins=temp, destinations=temp, compute_paths=False)
                    # print graph.issues_dist_paths
                    #
                    h = len(hotspots)
                    t = len(terminals)
                    p = len(pois)
                    n = len(graph.keys())
                    print dh, act, h, t, p, n
                    experiment = {}
                    #
                    mz = VST_RS(graph, terminals, pois, 5, 8)
                    try:
                        start_time = time.clock()
                        forest, cost, gr, avg_dr, num_trees, avg_or = mz.steiner_forest()
                        elapsed_time = time.clock() - start_time
                    except KeyError as err:
                        print err
                        continue
                    hs_r = set(forest.keys()).intersection(hotspots)
                    experiment['mVST-RS'] = ([sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h,
                                             t, p, n], hs_r)
                    print 'mVST-RS', sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h, t, p, n
                    #
                    hb = HotspotBased(graph, terminals, pois)
                    start_time = time.clock()
                    forest, cost, gr, avg_dr, num_trees, avg_or, lsv = hb.steiner_forest(k=5)
                    elapsed_time = time.clock() - start_time
                    hs_c = set(forest.keys()).intersection(hotspots)
                    experiment['Gr-based'] = ([sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h,
                                             t, p, n], hs_c)
                    print 'Gr-based', sa3_code11, dh, act[0], cost, gr, avg_dr, num_trees, avg_or, elapsed_time, h, t, p, n
                    #
                    osmdbmngr.save_experiment(experiment, save_details=False)
