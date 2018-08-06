import time

from grid_digraph_generator import GridDigraphGenerator
from dreyfus import Dreyfus
from prim import Prim
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 5
    m = n = 10

    gh = GridDigraphGenerator()
    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    # terminals = [654, 288, 315, 231, 312, 111, 609, 645, 434, 469, 186]
    terminals = [12, 88, 66, 77, 5, 33]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    start_time = time.clock()

    terminals_mc = suitability_graph.build_metric_closure(terminals)
    mst_terminals_mc = Prim(terminals_mc).spanning_tree()
    excluded_edges = set(terminals_mc.get_edges()) - set(mst_terminals_mc.get_edges())

    # suitable_nodes = suitability_graph.get_suitable_nodes(generator, excluded_nodes=terminals)
    # closures_edges = set()
    # msts_edges = set()
    # for sn in suitable_nodes:
    #     t_sn = list(terminals)
    #     t_sn.append(sn)
    #     t_sn_mc = suitability_graph.build_metric_closure(t_sn)
    #     mst_t_sn_mc = Prim(t_sn_mc).spanning_tree()
    #     closures_edges.update(t_sn_mc.get_edges())
    #     msts_edges.update(mst_t_sn_mc.get_edges())
    # ee = closures_edges - msts_edges
    # excluded_edges.update(ee)

    suitability_mc = suitability_graph.build_suitability_metric_closure(generator, terminals, excluded_edges)
    dr = Dreyfus(suitability_mc)
    st, cost = dr.steiner_tree(terminals, consider_terminals=False)
    steiner_tree = suitability_graph.build_subgraph_from_metric_closure(st)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.calculate_costs(terminals)

    special_subgraphs = [(r, "#00FF00") for _, (r, _, _, _, _, _) in regions.items()]
    special_subgraphs.append((steiner_tree, "#FF0000"))

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(terminals, None, None)],
                   special_subgraphs=special_subgraphs,
                   title_1="Dreyfus (metric closure), seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=False,
                   print_edge_labels=False)
