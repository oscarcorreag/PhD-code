import sys
import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from hotspot_based import HotspotBased

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 10
    m = n = 50

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    # suitability_graph.extend_suitable_regions(seed, generator)

    hotspots = suitability_graph.get_suitable_nodes(generator)

    terminals = np.random.choice(a=m * n, size=30, replace=False)
    while set(hotspots).intersection(terminals) != set():
        terminals = np.random.choice(a=m * n, size=30, replace=False)

    pois = terminals[:3]
    terminals = terminals[3:]

    regions = suitability_graph.get_suitable_regions(generator)

    cap = 5
    max_dr = sys.maxint
    last_mile = sys.maxint

    hb = HotspotBased(suitability_graph, terminals, pois)
    start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or = hb.steiner_forest(k=cap, max_dr=max_dr, max_wd=last_mile)
    elapsed_time = time.clock() - start_time

    # cost2, _ = forest.calculate_costs()

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=pois,
                   nodes_2=terminals,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   subgraphs_2=[forest],
                   title_1="Hotspot-based, seed: " + str(seed) + ", Capacity: " + str(
                       cap) + ", Max. Detour ratio: " + str(max_dr) + ", Last mile: " + str(last_mile),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", Avg. detour ratio: " + str(
                       avg_dr) + ", Num. trees: " + str(num_trees) + ", Avg. occ. rate: " + str(
                       avg_or) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=45,
                   print_edge_labels=False)
