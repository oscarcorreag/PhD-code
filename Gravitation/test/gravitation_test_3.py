import operator

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from graph import dijkstra


def __calculate_mass_suitable_node(g, ts, p, dp, node):

        hits = 0
        for t in ts:
            path = dp[p][1][t]
            if node in path:
                hits += 10

        m = 0
        if node in g.contracted_regions:
            region = g.contracted_regions[node][0]
            for n in region:
                m += 1. / region[n][0] * 100
        else:
            m = 1. / g[node][0] * 100

        return m + hits


def __calculate_adjusted_edge_cost(max_d, edge_cost, mass_attracting_node, distance_from_attracting_node):
    if max_d > 0:
        scaled_dist = float(distance_from_attracting_node) / max_d
    else:
        scaled_dist = 1
    return edge_cost * scaled_dist / mass_attracting_node


def __attract_nodes_to(g, dp, max_d, attracting_node, mass_attracting_node, current_node, level_attraction,
                       distance_so_far, already_affected_edges):
    if level_attraction < 1:
        return
    for neighbour in g[current_node][1]:
        edge = tuple(sorted([current_node, neighbour]))
        distance_from_attracting_node = dp[attracting_node][0][neighbour]
        edge_cost = g[current_node][1][neighbour]
        if distance_so_far + edge_cost == distance_from_attracting_node and edge not in already_affected_edges:
            adjusted_edge_cost = \
                __calculate_adjusted_edge_cost(max_d, edge_cost, mass_attracting_node, distance_from_attracting_node)
            g[current_node][1][neighbour] = adjusted_edge_cost
            g[neighbour][1][current_node] = adjusted_edge_cost
            already_affected_edges.append(edge)
            __attract_nodes_to(g, dp, max_d, attracting_node, mass_attracting_node, neighbour, level_attraction - 1,
                               distance_so_far + edge_cost, already_affected_edges)

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0

    node_weights = [generator.weights['WARNING'][0] for _ in range(20 * 20)]

    suitable_nodes = [167, 274]
    for s in suitable_nodes:
        node_weights[s] = generator.weights['VERY_SUITABLE'][0]

    # node_weights[584] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[720] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[721] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[771] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[722] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[772] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2333] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[2383] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1573] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1574] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1623] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1624] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[1120] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[931] = generator.weights['VERY_SUITABLE'][0]
    # node_weights[930] = generator.weights['VERY_SUITABLE'][0]

    gh = GridDigraphGenerator()
    graph = gh.generate(20, 20,
                        edge_weighted=False,
                        node_weighted=True,
                        node_weight_generator=generator,
                        node_weights=node_weights,
                        seed=seed)

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(graph)

    terminals = [82, 182]
    poi = 173

    terminals_poi = list(terminals)
    terminals_poi.append(poi)

    dist_paths_node_node = {n: dijkstra(suitability_graph, n) for n in suitable_nodes}
    for e in terminals_poi:
        dist_paths_node_node[e] = dijkstra(suitability_graph, e)

    # suitable_nodes = suitability_graph.get_suitable_nodes_within_convex_set(terminals_poi, generator)
    # dist_paths_node_node = {n: dijkstra(suitability_graph, n, consider_node_weights=False) for n in suitable_nodes}
    # for e in terminals_poi:
    #     dist_paths_node_node[e] = dijkstra(suitability_graph, e, consider_node_weights=False)

    # max_distances = [max(dist_paths_node_node[n][0].values()) for n in suitable_nodes
    #                  if len(dist_paths_node_node[n][0].values()) > 0]
    # if len(max_distances) > 0:
    #     max_dist = max(max_distances)
    # else:
    #     max_dist = 0
    max_dist = 2

    dist_to_poi = {n: dist_paths_node_node[n][0][poi] for n in suitable_nodes}
    ord_suit_nodes = sorted(dist_to_poi.iteritems(), key=operator.itemgetter(1))
    for n, _ in ord_suit_nodes:
        mass = __calculate_mass_suitable_node(suitability_graph, terminals, poi, dist_paths_node_node, n)
        __attract_nodes_to(suitability_graph, dist_paths_node_node, max_dist, n, mass, n, 2, 0, [])

    subtrees = []
    # for e in terminals_poi:
    #     _, pt = dijkstra(suitability_graph, e, [poi], consider_node_weights=False)
    #     subtree = SuitabilityDigraph()
    #     subtree.append_from_path(pt[poi], suitability_graph)
    #     subtrees.append(subtree)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_1=terminals,
                   nodes_2=[poi],
                   subgraphs_2=subtrees,
                   node_weight_generator=generator,
                   print_edge_labels=True,
                   print_node_labels=False,
                   node_size=25)
