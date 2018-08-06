import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from hotspot_based import HotspotBased


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 30

    node_weights = [generator.weights['WARNING'][0] for _ in range(m * n)]
    # node_weights[578] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[437] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[524] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[308] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[371] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[458] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[527] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[348] = generator.weights['VERY_SUITABLE'][0]
    node_weights[252] = generator.weights['VERY_SUITABLE'][0]
    node_weights[433] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                # node_weight_generator=generator,
                                node_weights=node_weights,
                                seed=seed)

    # pois = [634, 496, 310]
    # terminals = [696, 610, 518, 493, 583, 288, 320, 439, 187, 587, 590, 259, 200, 261]

    pois = [133]
    terminals = [220, 250, 190, 285, 461, 491]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    hb = HotspotBased(suitability_graph, terminals, pois)
    start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or, avg_oc = hb.steiner_forest(k=5, get_lsv=False)
    elapsed_time = time.clock() - start_time
    # forest = SuitabilityDigraph()
    # cost = elapsed_time = 0

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(terminals, None, None), (pois, None, None)],
                   special_subgraphs=[(forest, None)],
                   title_1="Hotspot-based, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", Avg. detour ratio: " + str(
                       avg_dr) + ", Num. trees: " + str(num_trees) + ", Avg. occ. rate: " + str(
                       avg_or) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True)
