import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from cluster_based_v2 import ClusterBasedV2
from networkx_graph_helper import NetworkXGraphHelper


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

    terminals = [678, 359, 123, 456, 463, 897]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    cb = ClusterBasedV2(suitability_graph, terminals)
    start_time = time.clock()
    steiner_tree = cb.steiner_tree()
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=terminals,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.items()],
                   subgraphs_2=[steiner_tree],
                   title_2="elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   node_size=15)
