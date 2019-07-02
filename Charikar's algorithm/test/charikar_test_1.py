import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from charikar import Charikar


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

    root = 586
    terminals = [359, 123, 456, 463, 897]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    ch = Charikar(suitability_graph, root, terminals)
    start_time = time.clock()
    steiner_tree = ch.Ai(5, root, terminals, 2)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   title_1="Dreyfus max stops, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   node_size=15,
                   print_edge_labels=False)
