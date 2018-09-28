from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from networkx_graph_helper import NetworkXGraphHelper
from digraph import dijkstra

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 40

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [870, 902, 776, 578, 585]

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

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

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(terminals, None, None), (c, None, None)],
                   special_subgraphs=[(r, "#00FF00") for _, (r, _, _, _, _, _) in regions.iteritems()],
                   print_node_labels=False)
