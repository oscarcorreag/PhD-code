import numpy as np
import time
import csv

from grid_digraph_generator import GridDigraphGenerator
from vst_rs import VST_RS
from link_performance import bpr

if __name__ == '__main__':

    num_samples = 10
    num_queries = [16, 32, 64]
    # num_queries = [64]
    num_users_query = [8, 12, 16, 24, 32]
    # num_users_query = [16]
    prop_pois_users = 0.25
    # off_net = 4
    # net_size = off_net * num_queries[-1] * (1 + prop_pois_users) * num_users_query[-1]
    # m = n = int(math.sqrt(net_size))
    m = n = 100
    N = m * n
    graph = GridDigraphGenerator().generate(m, n, edge_weighted=False, capacitated=True, capacities_range=(16, 64))

    merge_users = False
    max_iter = 100
    alpha = 0.15
    beta = 4.0
    results = []
    for nq in num_queries:
        for nu in num_users_query:
            num_pois = max(int(prop_pois_users * nu), 1)
            print "(nq, nu, np):", (nq, nu, num_pois)
            for sample in range(num_samples):
                print "\tsample:", sample
                queries = []
                occupied = []
                for i in range(nq):
                    np.random.seed(sample * i)
                    where = set(range(m * n)).difference(occupied)
                    nodes = np.random.choice(a=list(where), size=num_pois + nu, replace=False)
                    pois = nodes[:num_pois]
                    terminals = nodes[num_pois:]
                    queries.append((terminals, pois))
                    occupied.extend(nodes)
                # VST-NCA
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy = \
                    vst_rs.non_congestion_aware(queries, 4, 8, bpr, merge_users=merge_users, alpha=alpha, beta=beta,
                                                verbose=False)
                et = time.clock() - st
                line = ["VST-NCA", "N/A", "uniform", N, "(16, 64)", merge_users, sample, nq, nu, prop_pois_users,
                        num_pois, c, warl, mwrl, 0, et, alpha, beta]
                print line
                results.append(line)
                # VST-CA
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
                    vst_rs.congestion_aware(queries, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter, alpha=alpha,
                                            beta=beta, verbose=False)
                et = time.clock() - st
                ni_ = str(ni)
                if ni == max_iter:
                    ni_ += "(*)"
                line = ["VST-CA", "mixed", "uniform", N, "(16, 64)", merge_users, sample, nq, nu, prop_pois_users,
                        num_pois, c, warl, mwrl, ni_, et, alpha, beta]
                print line
                results.append(line)

    result_file = open("files/vstca_vstnca_1_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
