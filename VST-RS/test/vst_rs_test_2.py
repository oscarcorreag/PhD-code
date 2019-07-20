import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS

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

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)

    # suitability_graph.extend_suitable_regions(seed, generator)

    hotspots = suitability_graph.get_suitable_nodes(generator)

    terminals = np.random.choice(a=m * n, size=30, replace=False)
    while set(suitability_graph.keys()).intersection(terminals) != set(terminals) or set(hotspots).intersection(
            terminals) != set():
        terminals = np.random.choice(a=m * n, size=30, replace=False)

    pois = terminals[:3]
    terminals = terminals[3:]

    regions = suitability_graph.get_suitable_regions(generator)

    mz = VST_RS(suitability_graph)
    start_time = time.clock()
    forest, cost, gr, _, _, _, _ = mz.steiner_forest(terminals, pois, 5, 8, merge_users=False)
    elapsed_time = time.clock() - start_time

    # cost2, _ = forest.calculate_costs()

    special_nodes = [(terminals, '#000000', 35), (pois, '#0000FF', 65)]

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=special_nodes,
                   special_subgraphs=[(forest, None)],
                   title_1="Mustafiz's algorithm, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   print_edge_labels=False)
