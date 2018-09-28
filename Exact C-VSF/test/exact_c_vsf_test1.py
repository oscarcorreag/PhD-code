import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from exact_c_vsf import ExactC_VSF


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

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    # suitability_graph.extend_suitable_regions(seed, generator)

    hotspots = suitability_graph.get_suitable_nodes(generator)

    terminals = np.random.choice(a=m * n, size=20, replace=False)
    while set(hotspots).intersection(terminals) != set():
        terminals = np.random.choice(a=m * n, size=20, replace=False)

    pois = terminals[:5]
    terminals = terminals[5:]

    regions = suitability_graph.get_suitable_regions(generator)

    e = ExactC_VSF(suitability_graph, list(terminals), list(pois))
    start_time = time.clock()
    forest, cost = e.steiner_forest(k=5, S=10)
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=pois,
                   nodes_2=terminals,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   subgraphs_2=[forest],
                   title_1="Exact C-VSF, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=45,
                   print_edge_labels=False)