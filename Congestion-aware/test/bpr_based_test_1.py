import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from bpr_based import BPRBased


if __name__ == '__main__':
    m = n = 10

    gg = GridDigraphGenerator()
    graph = gg.generate(m, n, capacitated=True, capacities_range=(1, 2))

    bpr = BPRBased(graph)

    req_1 = ([22, 55, 43], [27, 99])
    req_2 = ([63, 76], [35, 46])
    req_3 = ([47, 68, 97], [42, 15, 90])
    req_4 = ([64, 23], [56])
    req_5 = ([25, 75], [33])

    requests = [req_1, req_2, req_3, req_4, req_5]
    st = time.clock()
    MSTs = bpr.steiner_forest(requests)
    et = time.clock() - st

    print et

    special_subgraphs = [(MST, None) for _, (MST, cost) in MSTs.items()]

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_1[0], '#000000', 50), (req_1[1], '#000000', 100),
                                  (req_2[0], '#0000FF', 50), (req_2[1], '#0000FF', 100),
                                  (req_3[0], '#13E853', 50), (req_3[1], '#13E853', 100),
                                  (req_4[0], '#FF0000', 50), (req_4[1], '#FF0000', 100),
                                  (req_5[0], '#E67E22', 50), (req_5[1], '#E67E22', 100)],
                   special_subgraphs=special_subgraphs,
                   print_edge_labels=True,
                   edge_labels=bpr.congestion)
