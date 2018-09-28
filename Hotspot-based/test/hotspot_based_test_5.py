import time

from grid_digraph_generator import GridDigraphGenerator
from hotspot_based import HotspotBased
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 3
    m = n = 20

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False, node_weighted=True, node_weight_generator=generator, seed=seed)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    terminals = [88, 66, 77, 5, 33, 53, 71]
    pois = [65, 12]
    #
    hb = HotspotBased(suitability_graph, terminals, pois)

    start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or, _ = hb.steiner_forest(k=5, get_lsv=False)
    elapsed_time = time.clock() - start_time

    regions = suitability_graph.get_suitable_regions(generator)

    special_nodes = [(pois, "#0000FF", 45), (terminals, "#000000", 45)]
    special_subgraphs = [(r, "#00FF00") for _, (r, _, _, _, _, _) in regions.iteritems()]

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=special_nodes,
                   special_subgraphs=special_subgraphs,
                   node_weight_generator=generator,
                   title_1="Hotspot-based algorithm, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", Avg. detour ratio: " + str(
                       avg_dr) + ", Num. trees: " + str(num_trees) + ", Avg. occ. rate: " + str(
                       avg_or) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   print_edge_labels=False)
