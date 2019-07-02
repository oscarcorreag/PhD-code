import time

from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from networkx_graph_helper import NetworkXGraphHelper
from digraph import dijkstra
from dreyfus_imr import DreyfusIMR


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 40

    # node_weights = [generator.weights['WARNING'][0] for _ in range(m * n)]
    # node_weights[1221] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                # node_weights=node_weights,
                                seed=seed)

    terminals = [742, 870, 776, 578]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    suitable_nodes = suitability_graph.get_suitable_nodes(generator, excluded_nodes=terminals)

    dist, _ = dijkstra(suitability_graph, terminals[0], terminals[1:])
    upper_bound = sum([dist[t] for t in terminals[1:]])

    c = []
    for s in suitable_nodes:
        dist_s, _ = dijkstra(suitability_graph, s, terminals)
        total_s = sum([dist_s[t] for t in terminals])
        if total_s <= upper_bound:
            c.append(s)

    # d = []
    # for s in c:
    #     dist_s, _ = dijkstra(suitability_graph, s, c[c.index(s) + 1:], consider_node_weights=False)
    #     d.extend(dist_s[s1] for s1 in c[c.index(s) + 1:])
    #
    # print(sorted(d, reverse=True)[0:len(terminals) - 2])

    start_time = time.clock()
    dr = DreyfusIMR(suitability_graph, terminals, contract_graph=False, within_convex_hull=False)
    steiner_tree = dr.steiner_tree(consider_terminals=False)
    elapsed_time = time.clock() - start_time

    cost, node_cost = steiner_tree.compute_total_weights(terminals)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=terminals,
                   nodes_2=c,
                   node_weight_generator=generator,
                   subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   subgraphs_2=[steiner_tree],
                   title_1="Extended Dreyfus, seed = " + str(seed),
                   title_2="Cost: " + str(cost - node_cost) + ", Upper bound: " + str(upper_bound),
                   print_node_labels=False,
                   node_size=15)