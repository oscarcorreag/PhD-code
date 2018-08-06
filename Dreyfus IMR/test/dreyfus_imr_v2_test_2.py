import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus_imr import DreyfusIMR
from dreyfus_imr_v2 import DreyfusIMRV2


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 3
    m = n = 10

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [28, 56, 72]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    start_time = time.clock()
    # dr = DreyfusIMRV2(suitability_graph, terminals, contract_graph=True)
    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=False)
    steiner_tree = dr.steiner_tree(consider_terminals=False)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.calculate_costs(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.items()],
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Extended Dreyfus, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=15,
                   print_edge_labels=False)