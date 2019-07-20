from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 40

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n,
                        edge_weighted=False,
                        node_weighted=True,
                        node_weight_generator=generator,
                        # node_weights=node_weights,
                        seed=seed)

    terminals = [470, 388, 750, 1185, 1222, 739, 487, 850, 1299, 333]
    poi = 899

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(graph)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    # suitability_graph.contract_suitable_regions(generator)

    # paths = []
    # for t in terminals:
    #     _, paths_t = dijkstra(suitability_graph, t, [poi], consider_node_weights=False)
    #     paths.append(paths_t[poi])

    # _, paths_poi = suitability_graph.compute_shortest(poi, terminals)
    suitability_graph.compute_dist_paths(origins=[poi], destinations=terminals)
    paths = [suitability_graph.paths[tuple(sorted([t, poi]))] for t in terminals]

    tree = SuitabilityGraph()
    for p in paths:
        tree.append_path(p, suitability_graph)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[(terminals, None, None), ([poi], None, None)],
                   # subgraphs_1=[r for _, (r, _, _, _, _, _) in regions.iteritems()],
                   special_subgraphs=[(tree, None)],
                   print_node_labels=False)
