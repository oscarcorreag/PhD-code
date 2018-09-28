import time

from grid_digraph_generator import GridDigraphGenerator
from dreyfus_imr import DreyfusIMR
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 9
    m = n = 10

    node_weights = [generator.weights['WARNING'][0] for _ in range(m * n)]
    node_weights[35] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[26] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[721] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[771] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[722] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[772] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2333] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2383] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1573] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1574] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1623] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1624] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1120] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[931] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[930] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n,
                        edge_weighted=True,
                        edge_weights_range=(1, 2),
                        node_weighted=True,
                        node_weight_generator=generator,
                        node_weights=node_weights,
                        seed=seed)

    # terminals = [1226, 1265, 1134, 1482, 1721, 677, 1567, 814, 1879, 635, 838, 2077, 2227, 911]
    # poi = 1226

    # terminals = [1222, 470, 388, 899, 1185, 750, 739, 487, 850, 1299]
    # poi = 1505
    # terminals = [23, 45, 56, 289, 365]
    terminals = [23, 17, 65]

    # terminals = [703, 858, 668, 171, 628, 886, 240, 383, 268, 686]
    # terminals = [3381, 2580, 2655, 3622, 2161, 5247, 5073, 871, 4946, 1017]
    # terminals = [23, 45, 56, 289, 365]

    # terminals = [331, 356, 297]
    # poi = 294

    # terminals = [197, 221]
    # poi = 74

    # terminals = [123, 230, 310, 588, 625, 700]
    # poi = 464

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    # suitability_graph.extend_suitable_regions(seed, generator)
    # suitability_graph.extend_suitable_regions(seed, generator)

    # regions = suitability_graph.get_suitable_regions(generator)

    contract_graph = False
    within_convex_hull = False
    consider_terminals = True

    start_time = time.clock()
    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=contract_graph, within_convex_hull=within_convex_hull)
    steiner_tree = dr.steiner_tree(consider_terminals=consider_terminals)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.calculate_costs(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   # subgraphs_1=[r for _, (r, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Extended Dreyfus, contract = " + str(contract_graph) +
                           ", convex = " + str(within_convex_hull) +
                           ", terminals = " + str(consider_terminals) +
                           ", seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=15,
                   print_edge_labels=False)
