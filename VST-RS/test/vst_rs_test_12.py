import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS
from link_performance import bpr
from utils import distribute_pois_in_queries


if __name__ == '__main__':

    m = n = 30
    capacities = (7, 8)
    nq = 16
    npq = 1
    nuq = 8

    gh = GridDigraphGenerator()
    graph = GridDigraphGenerator().generate(m, n, edge_weighted=True, capacitated=True, capacities_range=capacities)

    ppq = distribute_pois_in_queries((m, n), nq, npq, seed=0)
    # queries_u = []
    queries_z = []
    #
    all_pois = []
    for ps in ppq.values():
        all_pois.extend(ps)
    free_nodes = set(range(m * n)).difference(all_pois)
    #
    # special = []
    occupied_t = set()
    # occupied_p = set()
    for i, pois_z in ppq.items():
        np.random.seed(0)
        #
        where_t = set(free_nodes).difference(occupied_t)
        terminals = np.random.choice(a=list(where_t), size=nuq, replace=False)
        queries_z.append((terminals, pois_z))
        occupied_t.update(terminals)
        # occupied_p.update(terminals)
        # special.append((terminals, None, 25))
        # special.append((pois_z, None, 65))
        #
        # where_p = set(range(m * n)).difference(occupied_p)
        # pois_u = np.random.choice(a=list(where_p), size=1, replace=False)
        # queries_u.append((terminals, pois_u))
        # occupied_p.update(pois_u)

    # np.random.shuffle(queries_z)

    merge_users = False
    max_iter = 50
    alpha = 1.0
    beta = 4.0

    # NCA ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    vst_rs = VST_RS(graph)
    st = time.clock()
    plans, c, warl, mwrl, mrl1, mrl2, entropy = \
        vst_rs.non_congestion_aware(queries_z, 4, 8, bpr, merge_users=merge_users, alpha=alpha, beta=beta, verbose=True)
    et = time.clock() - st

    print c, warl, mwrl, mrl1, mrl2, entropy, et

    # ngh = NetworkXGraphHelper(graph)
    # # labels = {e: vst_rs.load[e] for e in graph.get_edges()}
    # ngh.draw_graph(special_subgraphs=[(plan, None) for _, plan in plans], special_nodes=special)

    # CA +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    vst_rs = VST_RS(graph)
    st = time.clock()
    plans, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
        vst_rs.congestion_aware(queries_z, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter, alpha=alpha,
                                beta=beta, verbose=True, randomize=False)
    et = time.clock() - st

    print c, warl, mwrl, mrl1, mrl2, entropy, et

    # ngh = NetworkXGraphHelper(graph)
    # # labels = {e: vst_rs.load[e] for e in graph.get_edges()}
    # ngh.draw_graph(special_subgraphs=[(plan, None) for _, plan in plans], special_nodes=special)
