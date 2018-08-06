import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from vst_rs import VST_RS
from networkx_graph_helper import NetworkXGraphHelper
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    height = width = 30
    padding = 5

    # Generate graph
    gh = GridDigraphGenerator()
    graph = gh.generate(height, width,
                        edge_weighted=False,
                        node_weighted=True,
                        node_weight_generator=generator,
                        seed=seed)

    # Transform graph into a suitability-graph because algorithm needs to know which the suitable nodes are.
    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    # # Compute shortest distances between every pair of nodes.
    # suitability_graph.compute_dist_paths(compute_paths=False)

    # As our goal is to show how Mustafizur's algorithm works, terminals can meet anywhere, thus original suitable nodes
    # are reset and any node in the graph becomes a suitable node (except terminals and POIs).

    # Reset suitable nodes.
    hotspots = suitability_graph.get_suitable_nodes(generator)
    reset_hotspots_weights = {h: generator.weights["WARNING"][0] for h in hotspots}
    suitability_graph.update_node_weights(reset_hotspots_weights)

    # Choose random terminals.

    # Terminals are chosen from a subset of nodes resulting from padding the original graph.
    where = []
    offset = width - 2 * padding - 1
    a = (width + 1) * padding
    for _ in range(0, offset + 1):
        b = a + offset
        where.extend(range(a, b + 1))
        a = b + 2 * padding + 1

    terminals = np.random.choice(a=where, size=35, replace=False)

    # Choose POIs.
    pois = terminals[:10]
    terminals = terminals[10:]

    # Suitable nodes are all nodes except terminals and POIs.
    hotspots = list(set(suitability_graph.keys()).difference(terminals).difference(pois))
    weights = {h: generator.weights["VERY_SUITABLE"][0] for h in hotspots}
    suitability_graph.update_node_weights(weights)

    ngh = NetworkXGraphHelper(suitability_graph)

    # Terminals and POIs are drawn.
    special_nodes = [(terminals, '#000000', 35), (pois, '#0000FF', 65)]
    # ngh.draw_graph(special_nodes=special_nodes, node_weight_generator=generator)

    # Voronoi cells are computed and drawn.
    p_cells, medoids = suitability_graph.get_voronoi_cells(
        list(set(suitability_graph.keys()).difference(terminals).difference(pois)), pois)
    for p in pois:
        # noinspection PyTypeChecker
        special_nodes.append((p_cells[p], None, None))
    ngh.draw_graph(special_nodes=special_nodes)

    #
    mz = VST_RS(suitability_graph)
    # start_time = time.clock()
    forest, cost, gr, avg_dr, num_trees, avg_or, _ = mz.steiner_forest(terminals, pois, 4, 8)
    # elapsed_time = time.clock() - start_time

    # cost2, _ = forest.calculate_costs()

    special_nodes = [(terminals, '#000000', 35), (pois, '#0000FF', 65)]
    ngh.draw_graph(special_nodes=special_nodes)




