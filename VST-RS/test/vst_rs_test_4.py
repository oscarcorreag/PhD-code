import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 3
    m = n = 10

    gh = GridDigraphGenerator()
    # node_weights = [generator.weights["VERY_SUITABLE"][0] for _ in range(m * n)]
    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                node_weight_generator=generator,
                                # node_weights=node_weights,
                                seed=seed)

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)
    # suitability_graph.compute_dist_paths()

    terminals = [88, 66, 77, 5, 33, 53, 71]
    pois = [65, 12]

    mz = VST_RS(suitability_graph)
    start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or, _ = mz.steiner_forest(terminals, pois, 5, 8)
    elapsed_time = time.clock() - start_time

    regions = suitability_graph.get_suitable_regions(generator)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(pois, None, None), (terminals, None, None)],
                   special_subgraphs=[(forest, "#FF0000")],
                   title_1="Mustafiz's algorithm, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", Avg. detour ratio: " + str(
                       avg_dr) + ", Num. trees: " + str(num_trees) + ", Avg. occ. rate: " + str(
                       avg_or) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   print_edge_labels=False)
