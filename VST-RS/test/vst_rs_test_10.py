import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from vst_rs import VST_RS
from link_performance import bpr


if __name__ == '__main__':

    m = n = 50

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=True, capacitated=True, capacities_range=(30, 40))

    no_queries = 100
    np.random.seed(0)
    no_users = np.random.choice(a=range(2, 8), size=no_queries, replace=True)
    no_pois = np.random.choice(a=range(1, 5), size=no_queries, replace=True)

    queries = []
    occupied = []
    for i in range(no_queries):
        np.random.seed(i)
        where = set(range(m * n)).difference(occupied)
        nodes = np.random.choice(a=list(where), size=no_users[i] + no_pois[i], replace=False)
        pois = nodes[:no_pois[i]]
        terminals = nodes[no_pois[i]:]
        queries.append((terminals, pois))
        occupied.extend(nodes)

    vst_rs = VST_RS(graph)

    start_time = time.clock()
    plans, cost, warl, mwrl, mrl1, mrl2, entropy = vst_rs.non_congestion_aware(queries, 4, 8, bpr)
    elapsed_time = time.clock() - start_time

    print "Non-congestion-aware:", cost, warl, mwrl, elapsed_time

    vst_rs = VST_RS(graph)

    start_time = time.clock()
    plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
        vst_rs.congestion_aware(queries, 4, 8, bpr, randomize=False, log_history=True)
    elapsed_time = time.clock() - start_time

    print "Congestion-aware:", cost, warl, mwrl, elapsed_time
