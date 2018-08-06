import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from hotspot_based import HotspotBased


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    m = n = 50

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
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    hotspots = suitability_graph.get_suitable_nodes(generator)

    terminals = np.random.choice(a=m * n, size=60, replace=False)
    while set(suitability_graph.keys()).intersection(terminals) != set(terminals) or set(hotspots).intersection(terminals) != set():
        terminals = np.random.choice(a=m * n, size=60, replace=False)

    pois = terminals[:15]
    terminals = terminals[15:]

    regions = suitability_graph.get_suitable_regions(generator)

    hb = HotspotBased(suitability_graph, terminals, pois)
    start_time = time.clock()
    forest, cost, _, _, _, _, _ = hb.steiner_forest(clone_hotspots=True, get_lsv=False)
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(pois, None, None), (terminals, None, None)],
                   special_subgraphs=[(forest, None)],
                   title_1="Hotspot-based, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False)