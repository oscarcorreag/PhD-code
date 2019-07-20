import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from convex_hull import ConvexHull
from graph import dijkstra

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 6
    m = n = 50
    # m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n,
                        edge_weighted=True,
                        node_weighted=True,
                        node_weight_generator=generator,
                        # node_weights=node_weights,
                        seed=seed)

    terminals = [1265, 1134, 1482, 1721, 677, 1567, 814, 1879, 635, 838, 2077, 2227, 911]
    poi = 1226
    # terminals = [25, 85, 33, 67]
    # poi = 55

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(graph)

    # suitability_graph.contract_suitable_regions(generator)
    suitable_nodes = suitability_graph.get_suitable_nodes(generator)
    dist_paths = {n: dijkstra(suitability_graph, n) for n in suitable_nodes}

    start_time = time.clock()
    ch = ConvexHull(suitability_graph, terminals, poi, dist_paths)
    convex_hull = ch.compute(generator)
    print("time elapsed:", time.clock() - start_time)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(nodes_2=terminals,
                   nodes_1=convex_hull,
                   node_weight_generator=generator,
                   print_edge_labels=False,
                   print_node_labels=False)