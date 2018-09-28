import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus_max_stops import DreyfusMaxStops


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

    poi = 586
    terminals = [359, 123, 456, 463, 897]
    max_stops = {359: 1, 123: 1, 456: 1, 463: 1, 897: 1}
    # terminals = [440, 439, 438, 407, 377, 348]
    # max_stops = {440: 1, 439: 1, 438: 1, 407: 1, 377: 1, 348: 1}

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    dr = DreyfusMaxStops(suitability_graph, poi, terminals, max_stops)
    start_time = time.clock()
    steiner_tree = dr.steiner_tree()
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.calculate_costs(terminals)

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
