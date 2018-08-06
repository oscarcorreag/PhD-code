from digraph import Digraph
from vst_rs import VST_RS
from networkx_graph_helper import NetworkXGraphHelper
from link_performance import bpr


if __name__ == '__main__':
    graph = Digraph(capacitated=True)
    no_queries = 100
    # Meeting points: {0, 1}, POI: {2}
    # Edges between meeting points and POI.
    graph.append_edge_2((0, 1), weight=0.5, capacity=no_queries)
    graph.append_edge_2((1, 2), weight=0.5, capacity=no_queries)
    graph.append_edge_2((0, 2), weight=0.5749, capacity=no_queries)
    # First group of users:     range(3, no_queries + 3)
    # An edge connects each user of this group with the first meeting point: 0
    for i in range(3, no_queries + 3):
        graph.append_edge_2((i, 0), weight=0, capacity=1)
    # Second group of users:    range(no_queries + 3, 2 * no_queries + 3)
    # An edge connects each user of this group with the second meeting point: 1
    for i in range(no_queries + 3, 2 * no_queries + 3):
        graph.append_edge_2((i, 1), weight=0, capacity=1)
    # Queries.
    queries = [([i, i + no_queries], [2]) for i in range(3, no_queries + 3)]
    # Optimal travel plans.
    vst_rs = VST_RS(graph)
    plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
        vst_rs.congestion_aware(queries, 4, 8, bpr, randomize=True, log_history=True)

    # ngh = NetworkXGraphHelper(graph)
    # ngh.draw_graph(print_node_labels=True, print_edge_labels=True)
