import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS
from link_performance import bpr


if __name__ == '__main__':

    m = n = 20

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False, capacitated=True, capacities_range=(1, 10))

    queries = []

    np.random.seed(0)
    terminals = np.random.choice(a=m * n, size=15, replace=False)
    pois_1 = terminals[:2]
    terminals_1 = terminals[2:]
    queries.append((terminals_1, pois_1))

    occupied = list(terminals_1)
    occupied.extend(pois_1)

    np.random.seed(1)
    where = set(range(m * n)).difference(occupied)
    terminals = np.random.choice(a=list(where), size=15, replace=False)
    pois_2 = terminals[:2]
    terminals_2 = terminals[2:]
    queries.append((terminals_2, pois_2))

    occupied.extend(terminals_2)
    occupied.extend(pois_2)

    np.random.seed(2)
    where = set(range(m * n)).difference(occupied)
    terminals = np.random.choice(a=list(where), size=15, replace=False)
    pois_3 = terminals[:2]
    terminals_3 = terminals[2:]
    queries.append((terminals_3, pois_3))

    occupied.extend(terminals_3)
    occupied.extend(pois_3)

    np.random.seed(3)
    where = set(range(m * n)).difference(occupied)
    terminals = np.random.choice(a=list(where), size=15, replace=False)
    pois_4 = terminals[:2]
    terminals_4 = terminals[2:]
    queries.append((terminals_4, pois_4))

    vst_rs = VST_RS(graph)

    start_time = time.clock()
    plans, cost, warl, mwrl, mrl1, mrl2, entropy, ni = \
        vst_rs.congestion_aware(queries, 4, 8, bpr, randomize=False, max_iter=20)
    elapsed_time = time.clock() - start_time

    print cost, warl, mwrl, elapsed_time

    ngh = NetworkXGraphHelper(graph)
    # labels = graph.get_capacities()
    # labels = {e: round(float(vst_rs.load[e]) / graph.get_capacities()[e], 2) for e in graph.get_edges()}
    labels = {e: vst_rs.load[e] for e in graph.get_edges()}

    ngh.draw_graph(
        special_subgraphs=[(plan, None) for _, plan in plans],
        special_nodes=[(terminals_1, '#000000', 25), (pois_1, '#000000', 65),
                       (terminals_2, '#0000FF', 25), (pois_2, '#0000FF', 65),
                       (terminals_3, '#13E853', 25), (pois_3, '#13E853', 65),
                       (terminals_4, '#FF0000', 25), (pois_4, '#FF0000', 65)
        ],
        edge_labels=labels,
        print_edge_labels=True,
        print_node_labels=False,
        title_1="Congestion-aware",
        title_2="Cost (w. congestion): " + str(round(cost, 2)) +
                ", Avg. Congestion: " + str(round(warl, 2)) +
                ", Elapsed time: " + str(round(elapsed_time, 2))
    )
