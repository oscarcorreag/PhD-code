import time
import numpy as np

from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from hotspot_based import HotspotBased

if __name__ == '__main__':

    m = 30
    n = 30
    seed = 0

    generator = SuitableNodeWeightGenerator()
    graph = GridDigraphGenerator().generate(m,
                                            n,
                                            node_weighted=True,
                                            node_weight_generator=generator,
                                            seed=seed)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)
    suitability_graph.compute_dist_paths(compute_paths=False)

    pois = [265, 312]
    hot_spots = suitability_graph.get_suitable_nodes(generator, excluded_nodes=pois)
    nodes_left_rh = list(set(suitability_graph.keys()).difference(pois).difference(hot_spots))
    ind = np.random.choice(a=len(nodes_left_rh), size=30, replace=False)
    terminals = [nodes_left_rh[i] for i in ind]

    hot_spots = set(suitability_graph.keys()).difference(terminals).difference(pois)

    for awareness in np.arange(0.0, 1.1, 0.1):
        hb = HotspotBased(suitability_graph, terminals, pois, hot_spots=hot_spots)
        start_time = time.clock()
        forest, cost, gr, avg_dr, num_trees, avg_oc = hb.steiner_forest(get_lsv=False, max_wd=2.5, awareness=awareness)
        elapsed_time = time.clock() - start_time
        line = [awareness, cost, gr, avg_dr, num_trees, avg_oc, elapsed_time]
        print line

    # awareness = 1.0
    # start_time = time.clock()
    # forest, cost, gr, avg_dr, num_trees, avg_oc = hb.steiner_forest(k=5, get_lsv=False, awareness=awareness)
    # elapsed_time = time.clock() - start_time
    # line = [awareness, cost, gr, avg_dr, num_trees, avg_oc, elapsed_time]
    # print line
