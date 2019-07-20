import time

from grid_digraph_generator import GridDigraphGenerator
from dreyfus_imr import DreyfusIMR
from suitability import SuitableNodeWeightGenerator, SuitabilityGraph
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 5
    m = n = 30

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469, 186]

    terminals = [654, 315, 288, 434]
    terminals = [654, 315, 288]
    terminals = [654, 288, 434]
    terminals = [654, 315, 434]

    terminals = [654, 315, 288]
    terminals = [654, 315]
    terminals = [654, 288]


    terminals = [654, 288, 315, 645, 434]
    terminals = [654, 288, 315, 645]
    terminals = [654, 288, 315, 434]

    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469, 186]
    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 469]
    terminals = [288, 315, 231, 312, 111, 609, 645, 434, 654, 186]

                 # terminals = [654, 315, 288, 434, 111]
    # terminals = [654, 315, 288, 434, 645]
    # terminals = [654, 111, 288]


    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    start_time = time.clock()
    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=False, within_convex_hull=False)
    steiner_tree = dr.steiner_tree(consider_terminals=True)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   subgraphs_1=[r for _, (r, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   node_weight_generator=generator,
                   title_1="Extended Dreyfus, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   node_size=15,
                   print_edge_labels=False)
