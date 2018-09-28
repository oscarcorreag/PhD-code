import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from rayward_smith import RaywardSmith
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    m = n = 30

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469, 186]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    start_time = time.clock()
    suitability_mc = suitability_graph.build_suitability_metric_closure(generator, terminals)
    rs = RaywardSmith(suitability_mc, terminals)
    st = rs.steiner_tree()
    steiner_tree = suitability_graph.build_subgraph_from_metric_closure(st)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.calculate_costs(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   subgraphs_1=[r for _, (r, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Rayward-Smith (metric closure), seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   node_size=15)
