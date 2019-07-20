import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from dreyfus_imr import DreyfusIMR


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 30

    node_weights = [generator.weights['WARNING'][0] for _ in range(m * n)]
    node_weights[644] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[401] = generator.weights['VERY_SUITABLE'][0]
    node_weights[405] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                # node_weight_generator=generator,
                                node_weights=node_weights,
                                seed=seed)

    terminals = [200, 760, 763, 766, 499]

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)

    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=False, within_convex_hull=False)
    start_time = time.clock()
    steiner_tree = dr.steiner_tree(consider_terminals=False)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=terminals,
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Extended Dreyfus, seed = " + str(seed),
                   title_2="Cost: " + str(cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   node_size=15)
