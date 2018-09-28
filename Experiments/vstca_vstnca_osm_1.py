import numpy as np
import math
import time
import csv

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from vst_rs import VST_RS
from link_performance import bpr


def main():

    # Outer bbox.
    # bounds = [-78.51114567859952, -0.22156158994849384, -78.46239384754483, -0.12980902510699335]  # (small) Quito
    bounds = [-78.57160966654635, -0.4180073651030667, -78.36973588724948, -0.06610523586538203]  # (big) Quito
    # bounds = [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727]  # Melbourne
    # bounds = [-74.0326191484375, 40.69502239217181, -73.93236890429688, 40.845827729757275]  # Manhattan
    zone = "Quito"
    delta_meters = 3000.0

    delta = delta_meters / 111111
    num_samples = 100
    nuq = 5

    osm = OsmManager()
    generator = SuitableNodeWeightGenerator()

    results = []
    sample = 0
    initial_seed = 500
    while sample < num_samples:
        #
        np.random.seed(initial_seed)
        initial_seed += 1
        # Compute bbox coords (inner sample bbox of 25 km^2)
        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        # Generate network sample.
        graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                           hotspots=False, cost_type="travel_time")
        N = len(graph.keys())
        num_pois = len(pois)

        if num_pois == 0:
            continue

        # Group POIs by subtype (activity).
        ps_subtype = dict()
        for p in pois:
            ps_subtype.setdefault(graph[p][2]['subtype'], []).append(p)
        # Available nodes for users.
        nq = len(ps_subtype.keys())
        free_nodes = set(graph.keys()).difference(pois)
        if len(free_nodes) < nq * nuq:
            continue
        # Create queries.
        queries = []
        occupied = set()
        for _, pois_ in ps_subtype.iteritems():
            where = set(free_nodes).difference(occupied)
            terminals = np.random.choice(a=list(where), size=nuq, replace=False)
            queries.append((terminals, pois_))
            occupied.update(terminals)
        # Compute capacity for every road segment.
        graph.capacitated = True
        capacity = int(math.ceil((nuq / 4.0 * nq) / 4.0))
        graph.set_capacities({e: capacity for e in graph.get_edges()})
        #
        merge_users = False
        max_iter = 20
        alpha = 1.0
        beta = 4.0

        # VST-NCA ******************************************************************************************************
        vst_rs = VST_RS(graph)
        st = time.clock()
        try:
            _, c, warl, mwrl, mrl1, mrl2, entropy = vst_rs.non_congestion_aware(queries, 4, 8, bpr,
                                                                                merge_users=merge_users, alpha=alpha,
                                                                                beta=beta, verbose=False)
        except:
            continue
        et = time.clock() - st

        line = ["VST-NCA", "N/A", zone, N, capacity, merge_users, sample, nq, nuq, "N/A", num_pois, c, warl, mwrl, mrl1,
                mrl2, 0, et, alpha, beta, entropy]
        print line
        results.append(line)
        # VST-CA  MIXED ************************************************************************************************
        vst_rs = VST_RS(graph)
        st = time.clock()
        try:
            _, c, warl, mwrl, mrl1, mrl2, entropy, ni = vst_rs.congestion_aware(queries, 4, 8, bpr,
                                                                                merge_users=merge_users,
                                                                                max_iter=max_iter, alpha=alpha,
                                                                                beta=beta, verbose=False,
                                                                                randomize=True)
        except:
            continue
        et = time.clock() - st
        ni_ = str(ni)
        if ni == max_iter:
            ni_ += "(*)"
        line = ["VST-CA", "mixed", zone, N, capacity, merge_users, sample, nq, nuq, "N/A", num_pois, c, warl, mwrl,
                mrl1, mrl2, ni_, et, alpha, beta, entropy]
        print line
        results.append(line)
        # VST-CA  PURE *************************************************************************************************
        vst_rs = VST_RS(graph)
        st = time.clock()
        try:
            _, c, warl, mwrl, mrl1, mrl2, entropy, ni = vst_rs.congestion_aware(queries, 4, 8, bpr,
                                                                                merge_users=merge_users,
                                                                                max_iter=max_iter, alpha=alpha,
                                                                                beta=beta, verbose=False,
                                                                                randomize=False)
        except:
            continue
        et = time.clock() - st
        ni_ = str(ni)
        if ni == max_iter:
            ni_ += "(*)"
        line = ["VST-CA", "pure", zone, N, capacity, merge_users, sample, nq, nuq, "N/A", num_pois, c, warl, mwrl, mrl1,
                mrl2, ni_, et, alpha, beta, entropy]
        print line
        results.append(line)

        sample += 1

    result_file = open("files/vstca_vstnca_osm_1_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)

if __name__ == "__main__":
    main()