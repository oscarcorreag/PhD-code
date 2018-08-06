import sys
import time

from baltz_based import BaltzBased
from vst_rs import VST_RS
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':
    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n)

    b = BaltzBased(graph)

    req_1 = ([22, 55, 43], [27, 99])
    req_2 = ([63, 76], [35, 46])
    req_3 = ([47, 68, 97], [42, 15, 90])
    req_4 = ([64, 23], [56])
    req_5 = ([25, 75], [33])

    requests = [req_1, req_2, req_3, req_4, req_5]
    st = time.clock()
    MSTs = b.steiner_forest(requests)
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
                   edge_labels=b.congestion)

    mz = VST_RS(graph)
    T1, l, _, _, _, _, _ = mz.steiner_forest(req_1[0], req_1[1], 4, sys.maxint)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_1[0], '#000000', 50), (req_1[1], '#000000', 100)],
                   special_subgraphs=[(T1, '#000000')])

    mz = VST_RS(graph)
    T2, l, _, _, _, _, _ = mz.steiner_forest(req_2[0], req_2[1], 4, sys.maxint)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_2[0], '#0000FF', 50), (req_2[1], '#0000FF', 100)],
                   special_subgraphs=[(T2, '#0000FF')])

    mz = VST_RS(graph)
    T3, l, _, _, _, _, _ = mz.steiner_forest(req_3[0], req_3[1], 4, sys.maxint)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_3[0], '#13E853', 50), (req_3[1], '#13E853', 100)],
                   special_subgraphs=[(T3, '#13E853')])

    mz = VST_RS(graph)
    T4, l, _, _, _, _, _ = mz.steiner_forest(req_4[0], req_4[1], 4, sys.maxint)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_4[0], '#FF0000', 50), (req_4[1], '#FF0000', 100)],
                   special_subgraphs=[(T4, '#FF0000')])

    mz = VST_RS(graph)
    T5, l, _, _, _, _, _ = mz.steiner_forest(req_5[0], req_5[1], 4, sys.maxint)
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_5[0], '#E67E22', 50), (req_5[1], '#E67E22', 100)],
                   special_subgraphs=[(T5, '#E67E22')])

    congestion = {}
    ind_forests = [T1, T2, T3, T4, T5]
    for F in ind_forests:
        for e in F.get_edges():
            try:
                congestion[e] += 1
            except KeyError:
                congestion[e] = 1

    special_subgraphs = [(F, None) for F in ind_forests]

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(req_1[0], '#000000', 50), (req_1[1], '#000000', 100),
                                  (req_2[0], '#0000FF', 50), (req_2[1], '#0000FF', 100),
                                  (req_3[0], '#13E853', 50), (req_3[1], '#13E853', 100),
                                  (req_4[0], '#FF0000', 50), (req_4[1], '#FF0000', 100),
                                  (req_5[0], '#E67E22', 50), (req_5[1], '#E67E22', 100)],
                   special_subgraphs=special_subgraphs,
                   print_edge_labels=True,
                   edge_labels=congestion)