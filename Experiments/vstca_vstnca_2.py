import csv
import getopt
import sys
import time
import numpy as np
import math

from mpi4py import MPI

from grid_digraph_generator import GridDigraphGenerator
from link_performance import bpr
from utils import distribute_pois_in_queries
from vst_rs import VST_RS

MASTER_RANK = 0


def print_usage():
    print ('usage is: vstca_vstnca_2.py -m <parallelisation_method> where:')
    print ('          <parallelisation_method> can be: [pp|mpi|n]')
    print ('          pp:   Parallel Python')
    print ('          mpi:  MPI')
    print ('          n:    No parallelization')


def main(argv):

    p_method = "pp"

    try:
        opts, args = getopt.getopt(argv, "hm:")
    except getopt.GetoptError as error:
        print(error)
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit(0)
        elif opt == "-m":
            p_method = arg
            break

    comm = None
    rank = MASTER_RANK
    if p_method == "mpi":
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()

    if rank != MASTER_RANK:
        while True:
            res = comm.recv(source=MASTER_RANK)
            print res

    num_samples = 5
    num_queries = [16, 32]
    num_users_query = [16]
    prop_pois_users = 0.1

    m = n = 30
    N = m * n
    graph = GridDigraphGenerator().generate(m, n, edge_weighted=True)

    merge_users = False
    max_iter = 50
    alpha = 1.0
    beta = 4.0
    results = []
    for nq in num_queries:
        for nu in num_users_query:
            num_pois = max(int(prop_pois_users * nu), 1)
            graph.capacitated = True
            capacity = int(math.ceil((nu / 4.0 * nq) / 12.0))
            graph.set_capacities({e: capacity for e in graph.get_edges()})
            print "(nq, nu, np, cap):", (nq, nu, num_pois, capacity)
            for sample in range(num_samples):
                print "\tsample:", sample
                ppq = distribute_pois_in_queries((m, n), nq, num_pois, seed=0)
                queries_u = []
                queries_z = []
                #
                all_pois = []
                for ps in ppq.values():
                    all_pois.extend(ps)
                free_nodes = set(range(m * n)).difference(all_pois)
                #
                occupied_t = set()
                occupied_p = set()
                for i, pois_z in ppq.iteritems():
                    np.random.seed(sample * i)
                    #
                    where_t = set(free_nodes).difference(occupied_t)
                    terminals = np.random.choice(a=list(where_t), size=nu, replace=False)
                    queries_z.append((terminals, pois_z))
                    occupied_t.update(terminals)
                    occupied_p.update(terminals)
                    #
                    where_p = set(range(m * n)).difference(occupied_p)
                    pois_u = np.random.choice(a=list(where_p), size=num_pois, replace=False)
                    queries_u.append((terminals, pois_u))
                    occupied_p.update(pois_u)
                #
                # VST-NCA **********************************************************************************************
                # POIs Zipfian distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy = \
                    vst_rs.non_congestion_aware(queries_z, 4, 8, bpr, merge_users=merge_users, alpha=alpha, beta=beta,
                                                p_method=p_method, verbose=False)
                et = time.clock() - st

                line = ["VST-NCA", "N/A", "zipfian", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, 0, et, alpha, beta, entropy]
                print line
                results.append(line)

                # POIs Uniformly distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy = \
                    vst_rs.non_congestion_aware(queries_u, 4, 8, bpr, merge_users=merge_users, alpha=alpha, beta=beta,
                                                p_method=p_method, verbose=False)
                et = time.clock() - st

                line = ["VST-NCA", "N/A", "uniform", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, 0, et, alpha, beta, entropy]
                print line
                results.append(line)
                # VST-NCA **********************************************************************************************

                # VST-CA ***********************************************************************************************
                # MIXED
                # POIs Zipfian distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
                    vst_rs.congestion_aware(queries_z, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter,
                                            alpha=alpha, beta=beta, verbose=False, randomize=True, p_method=p_method)
                et = time.clock() - st
                ni_ = str(ni)
                if ni == max_iter:
                    ni_ += "(*)"
                line = ["VST-CA", "mixed", "zipfian", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, ni_, et, alpha, beta, entropy]
                print line
                results.append(line)

                # POIs Uniformly distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
                    vst_rs.congestion_aware(queries_u, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter,
                                            alpha=alpha, beta=beta, verbose=False, randomize=True, p_method=p_method)
                et = time.clock() - st
                ni_ = str(ni)
                if ni == max_iter:
                    ni_ += "(*)"
                line = ["VST-CA", "mixed", "uniform", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, ni_, et, alpha, beta, entropy]
                print line
                results.append(line)

                # PURE
                # POIs Zipfian distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
                    vst_rs.congestion_aware(queries_z, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter,
                                            alpha=alpha, beta=beta, verbose=False, randomize=False, p_method=p_method)
                et = time.clock() - st
                ni_ = str(ni)
                if ni == max_iter:
                    ni_ += "(*)"
                line = ["VST-CA", "pure", "zipfian", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, ni_, et, alpha, beta, entropy]
                print line
                results.append(line)

                # POIs Uniformly distributed.
                vst_rs = VST_RS(graph)
                st = time.clock()
                _, c, warl, mwrl, mrl1, mrl2, entropy, ni = \
                    vst_rs.congestion_aware(queries_u, 4, 8, bpr, merge_users=merge_users, max_iter=max_iter,
                                            alpha=alpha, beta=beta, verbose=False, randomize=False, p_method=p_method)
                et = time.clock() - st
                ni_ = str(ni)
                if ni == max_iter:
                    ni_ += "(*)"
                line = ["VST-CA", "pure", "uniform", N, capacity, merge_users, sample, nq, nu,
                        prop_pois_users, num_pois, c, warl, mwrl, mrl1, mrl2, ni_, et, alpha, beta, entropy]
                print line
                results.append(line)

                # VST-CA ***********************************************************************************************

    result_file = open("files/vstca_vstnca_2_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)


if __name__ == "__main__":
    main(sys.argv[1:])
