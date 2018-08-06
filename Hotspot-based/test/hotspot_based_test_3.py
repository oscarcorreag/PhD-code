import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from hotspot_based import HotspotBased


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 30

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    # pois = [359, 834, 520, 378, 755, 616, 1, 435]
    # pois = [359, 834]
    # terminals = [123, 456, 463, 897, 506, 639, 343, 232, 564, 766, 138, 469, 800]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    # suitability_graph.extend_suitable_regions(seed, generator)
    # suitability_graph.extend_suitable_regions(seed, generator)
    # suitability_graph.extend_suitable_regions(seed, generator)

    hotspots = suitability_graph.get_suitable_nodes(generator)

    terminals = np.random.choice(a=m * n, size=60, replace=False)
    while set(hotspots).intersection(terminals) != set():
        terminals = np.random.choice(a=m * n, size=60, replace=False)

    # temp = list(terminals)
    # temp.extend(hotspots)
    #
    # pois_ = np.random.binomial(n=m * n, p=0.7, size=5)
    # pois = set(pois_)
    # while set(temp).intersection(pois) != set() or len(pois) < 5:
    #     pois_ = np.random.binomial(n=m * n, p=0.7, size=5)
    #     pois.update(pois_)

    pois = terminals[:5]
    terminals = terminals[5:]

    regions = suitability_graph.get_suitable_regions(generator)

    hb = HotspotBased(suitability_graph, terminals, pois)
    start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or = hb.steiner_forest(k=5)
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=pois,
                   nodes_2=terminals,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.items()],
                   subgraphs_2=[forest],
                   title_1="Hotspot-based, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", Avg. detour ratio: " + str(
                       avg_dr) + ", Num. trees: " + str(num_trees) + ", Avg. occ. rate: " + str(
                       avg_or) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   node_size=15,
                   print_edge_labels=False)
