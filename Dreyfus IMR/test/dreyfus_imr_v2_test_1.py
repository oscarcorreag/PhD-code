import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus_imr_v2 import DreyfusIMRV2


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 5
    m = n = 30
    # m = n = 10

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469, 186]
    # terminals = [36, 78, 28, 11]

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    start_time = time.clock()
    dr = DreyfusIMRV2(suitability_graph, terminals, contract_graph=True, within_convex_hull=False)
    steiner_tree = dr.steiner_tree(consider_terminals=False)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Extended Dreyfus, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=15,
                   print_edge_labels=False)