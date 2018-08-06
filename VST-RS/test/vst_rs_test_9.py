from digraph import Digraph
from vst_rs import VST_RS
from networkx_graph_helper import NetworkXGraphHelper
from link_performance import bpr, bpr_log


if __name__ == '__main__':
    graph = Digraph(capacitated=True)
    graph.append_edge_2((0, 1), weight=2, capacity=1)
    graph.append_edge_2((0, 3), weight=1, capacity=1)
    graph.append_edge_2((1, 2), weight=1, capacity=1)
    graph.append_edge_2((1, 5), weight=1, capacity=1)
    graph.append_edge_2((2, 17), weight=4, capacity=1)
    graph.append_edge_2((3, 4), weight=1, capacity=1)
    graph.append_edge_2((3, 7), weight=1, capacity=1)
    graph.append_edge_2((4, 5), weight=1, capacity=1)
    graph.append_edge_2((4, 9), weight=2, capacity=1)
    graph.append_edge_2((5, 10), weight=2, capacity=1)
    graph.append_edge_2((6, 7), weight=1, capacity=1)
    graph.append_edge_2((6, 11), weight=2, capacity=1)
    graph.append_edge_2((7, 8), weight=1, capacity=1)
    graph.append_edge_2((8, 9), weight=1, capacity=1)
    graph.append_edge_2((8, 13), weight=1, capacity=1)
    graph.append_edge_2((9, 10), weight=1, capacity=1)
    graph.append_edge_2((10, 16), weight=1, capacity=1)
    graph.append_edge_2((11, 12), weight=0.5, capacity=1)
    graph.append_edge_2((11, 18), weight=1, capacity=1)
    graph.append_edge_2((12, 13), weight=0.5, capacity=1)
    graph.append_edge_2((13, 14), weight=1, capacity=1)
    graph.append_edge_2((13, 19), weight=1, capacity=1)
    graph.append_edge_2((14, 15), weight=0.5, capacity=1)
    graph.append_edge_2((14, 20), weight=1, capacity=1)
    graph.append_edge_2((15, 16), weight=0.5, capacity=1)
    graph.append_edge_2((15, 21), weight=1, capacity=1)
    graph.append_edge_2((16, 17), weight=1, capacity=1)
    graph.append_edge_2((16, 22), weight=1, capacity=1)
    graph.append_edge_2((17, 23), weight=1, capacity=1)
    graph.append_edge_2((18, 19), weight=1, capacity=1)
    graph.append_edge_2((19, 20), weight=1, capacity=1)
    graph.append_edge_2((20, 21), weight=0.5, capacity=1)
    graph.append_edge_2((21, 22), weight=0.5, capacity=1)
    graph.append_edge_2((22, 23), weight=1, capacity=1)

    queries = [([3, 8, 14, 15], [6, 12, 10]), ([20, 21], [1, 9]), ([0, 5, 23], [11])]

    vst_rs = VST_RS(graph)
    # plans, cost, weighted_avg_relative_load, max_relative_load = vst_rs.non_congestion_aware(queries, 4, 8, bpr_log)
    plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
        vst_rs.congestion_aware(queries, 4, 8, bpr, log_history=True, randomize=False)

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[([3, 8, 14, 15], '#000000', 35), ([6, 12, 10], '#000000', 65),
                                  ([20, 21], '#0000FF', 35), ([1, 9], '#0000FF', 65),
                                  ([0, 5, 23], '#13E853', 35), ([11], '#13E853', 65)],
                   special_subgraphs=[(plan, None) for _, plan in plans],
                   title_2="Cost (w. congestion): " + str(round(cost, 2)),
                   edge_labels=vst_rs.load,
                   print_node_labels=True,
                   print_edge_labels=True)
