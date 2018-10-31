import operator
import sys
import time
import csv
import numpy as np
import math
import pp
import pdb

import priodict
import digraph
import utils


class VST_RS:
    def __init__(self, graph, nodes=None):
        self.graph = graph.copy()
        if nodes is not None:
            self.nodes = list(nodes)
        else:
            self.nodes = self.graph.keys()
        self.edges = self.graph.get_edges().copy()
        self.sum_weights = float(sum(self.edges.values()))
        self.cap = self.graph.get_capacities().copy()
        self.load = {e: 0 for e in self.edges}

        self.U = []  # Users
        self.pois = []
        self.z = 0  # Car capacity
        self.S = 0  # Group size
        self.p_cells = dict()
        self.medoids = dict()

        self.load_h = []
        self.weights_h = []
        self.stats_h = []

        # # Get suitable nodes (potential meeting points), except users and POIs.
        # temp = list(U_)
        # temp.extend(pois)
        # if self.__graph.is_node_weighted():
        #     generator = SuitableNodeWeightGenerator()
        #     self.__nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=temp)
        # else:
        #     self.__nodes = set(self.__graph.keys()).difference(temp)

    def find_nimp(self, M, cost):
        p = None
        min_cost = sys.maxint
        Q = priodict.PriorityDictionary()
        J = {}
        visited = set()
        for m in M:
            Q[m] = cost[m]
            J[m] = m
            visited.add(m)
        X = []
        for u in Q:
            visited.add(u)
            if u in self.nodes:
                X.append(u)
            if u in self.pois:
                p = u
                min_cost = cost[u]
                break
            if self.graph.is_node_weighted():
                adj_nodes = self.graph[u][1]
            else:
                adj_nodes = self.graph[u]
            for v, length in adj_nodes.iteritems():
                if v not in visited:
                    cost[v] = sys.maxint
                temp = cost[u] + length
                if cost[v] > temp:
                    cost[v] = temp
                    J[v] = J[u]
                    Q[v] = cost[v]
        return X, cost, J, p, min_cost

    def plan_subgroups(self, group):
        gs = len(group)
        if gs > self.S:
            raise (ValueError, "Group size must be at most S.")
        X = {}
        cost = {}
        J = {}
        OptPOI = {}
        OptCost = {}
        bestSubgrouping = {}
        bestDiv = {}
        for u in group:
            t_u = tuple([u])
            X[t_u], cost[t_u], J[t_u], OptPOI[t_u], OptCost[t_u] = self.find_nimp([u], {u: 0})

        for j in range(2, self.z + 1):
            for cmb in utils.comb(group, j):
                cmb = sorted(cmb)
                t_cmb = tuple(cmb)
                M = {t_cmb: []}
                OptCost[t_cmb] = sys.maxint
                OptPOI[t_cmb] = None
                bestDiv[t_cmb] = {}
                bestSubgrouping[t_cmb] = [None, None]
                cost[t_cmb] = {}
                for v in self.nodes:
                    cost[t_cmb][v] = sys.maxint
                combs1 = [[cmb[0]]]
                for x in range(1, j - 1):
                    for y in utils.comb(cmb[1:], x):
                        t = [cmb[0]]
                        t.extend(y)
                        combs1.append(t)
                for comb1 in combs1:
                    comb2 = sorted(list(set(cmb) - set(comb1)))
                    temp = OptCost[tuple(comb1)] + OptCost[tuple(comb2)]
                    if OptCost[t_cmb] > temp:
                        OptCost[t_cmb] = temp
                        bestSubgrouping[t_cmb] = [comb1, comb2]
                    XX = list(set(X[tuple(comb1)]).intersection(X[tuple(comb2)]))
                    for m in XX:
                        if m not in M[t_cmb]:
                            M[t_cmb].append(m)
                        temp = cost[tuple(comb1)][m] + cost[tuple(comb2)][m]
                        if cost[t_cmb][m] > temp:
                            cost[t_cmb][m] = temp
                            bestDiv[t_cmb][m] = [comb1, comb2]
                X[t_cmb], cost[t_cmb], J[t_cmb], p, temp = self.find_nimp(M[t_cmb], cost[t_cmb])
                if OptCost[t_cmb] > temp:
                    # It is better to ride-share than going independently.
                    OptCost[t_cmb] = temp
                    OptPOI[t_cmb] = p
                    bestSubgrouping[t_cmb] = [cmb, None]
        return OptCost, OptPOI, J, bestDiv, bestSubgrouping

    def divide_group_into_subgroups(self, group, OptCost):
        gs = len(group)
        if gs > self.S:
            raise (ValueError, "Group size must be at most S.")
        bestSubgrouping = {}
        for j in range(self.z + 1, gs + 1):
            for cmb in utils.comb(group, j):
                cmb = sorted(cmb)
                t_cmb = tuple(cmb)
                OptCost[t_cmb] = sys.maxint
                combs1 = [[cmb[0]]]
                bestSubgrouping[t_cmb] = [None, None]
                for x in range(1, j - 1):
                    for y in utils.comb(cmb[1:], x):
                        t = [cmb[0]]
                        t.extend(y)
                        combs1.append(t)
                for comb1 in combs1:
                    comb2 = sorted(list(set(cmb) - set(comb1)))
                    temp = OptCost[tuple(comb1)] + OptCost[tuple(comb2)]
                    if OptCost[t_cmb] > temp:
                        OptCost[t_cmb] = temp
                        bestSubgrouping[t_cmb] = [comb1, comb2]
        return OptCost, bestSubgrouping

    def divide_users_into_groups(self, merge_users=True, initial_seed=0):
        groups = []
        remaining_users = []
        for p, group in self.p_cells.iteritems():
            while len(group) > self.S:
                dists = {u: self.graph.dist[tuple(sorted(([u, p])))] for u in group}
                # If group size > S, create a new group with the S farthest users from the medoid.
                new_group = [u for u, _ in sorted(dists.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.S]]
                groups.append(new_group)
                group = list(set(group).difference(new_group))
            if len(group) > 0:
                if merge_users:
                    remaining_users.extend(group)
                else:
                    groups.append(group)
        if merge_users:
            if len(remaining_users) > self.S:
                k = int(math.ceil(float(len(remaining_users)) / self.S))
                merged = self.merge_remaining_users(k, remaining_users, initial_seed=initial_seed)
                groups.extend(merged)
            else:
                groups.append(remaining_users)
        return groups

    def merge_remaining_users(self, k, users, initial_seed=0):
        groups = []
        merged = self.get_merged_groups(k, users, initial_seed=initial_seed)
        for m, group in merged.iteritems():
            while len(group) > self.S:
                dists = {u: self.graph.dist[tuple(sorted(([u, m])))] for u in group}
                # If group size > S, create a new group with the S closest users from the medoid.
                new_group = [u for u, _ in sorted(dists.iteritems(), key=operator.itemgetter(1))[:self.S]]
                groups.append(new_group)
                group = list(set(group).difference(new_group))
            if len(group) > 0:
                groups.append(group)
        return groups

    def get_merged_groups(self, k, users, max_iter=100, initial_seed=0):
        groups = []
        np.random.seed(initial_seed)
        medoids = np.random.choice(a=users, size=k, replace=False)
        # Infinite loop until convergence is attained in less than [max_iter].
        while True:
            prev_medoids = []
            iterations = 0
            # Convergence is attained when medoids do not change from the previous iteration after computing them for
            # each Voronoi cell.
            while set(prev_medoids) != set(medoids) and iterations < max_iter:
                groups, _ = self.graph.get_voronoi_cells(users, medoids)
                prev_medoids = list(medoids)
                medoids = [self.graph.get_medoid(g) for _, g in groups.iteritems()]
                iterations += 1
            # print iterations
            # When convergence was attained, loop is broken.
            if iterations < max_iter:
                break
            # Otherwise, the algorithm starts over with k randomly chosen medoids.
            initial_seed += 1
            np.random.seed(initial_seed)
            medoids = np.random.choice(a=users, size=k, replace=False)
        return groups

    def steiner_forest(self, U, pois, z, S, merge_users=True, groups=None, initial_seed=0):
        self.U = U
        self.pois = pois
        self.z = z
        self.S = S
        # Compute P-Voronoi cells.
        self.p_cells, self.medoids = self.graph.get_voronoi_cells(self.U, self.pois)
        # Compute distances between users as they are used when grouping them.
        for _, cell in self.p_cells.iteritems():
            self.graph.compute_dist_paths(origins=cell, destinations=cell, compute_paths=False)
        #
        cost = num_trees = 0
        steiner_forest = digraph.Digraph()
        detours = {}
        occupancy_rates = []
        steiner_trees = []
        if groups is None:
            groups = self.divide_users_into_groups(merge_users, initial_seed=initial_seed)
        for group in groups:
            OptCost, OptPOI, J, bestDiv, bestSubgrouping = self.plan_subgroups(group)
            subgroups = []
            if len(group) > self.z:
                oc, bs = self.divide_group_into_subgroups(group, OptCost)
                OptCost.update(oc)
                bestSubgrouping.update(bs)
                subgroups = self.get_subgroups(group, bestSubgrouping)
            else:
                subgroups.append(group)
            for subgroup in subgroups:
                if len(subgroup) > 0:
                    forest, c, detours_, nt, ocr, sts = \
                        self.build_steiner_forest(subgroup, OptCost, OptPOI, J, bestDiv, bestSubgrouping)
                    steiner_trees.extend(sts)
                    steiner_forest.append_from_graph(forest)
                    cost += c
                    detours.update(detours_)
                    occupancy_rates.extend(ocr)
                    num_trees += nt
        # Compute some statistics.
        tot_ic = 0
        tot_dr = 0
        for u in self.U:
            m = self.medoids[u]
            ic = self.graph.dist[tuple(sorted([u, m]))]
            tot_ic += ic
            if ic != 0:
                tot_dr += detours[u] / ic
        gain_ratio = 0
        avg_detour_ratio = 0
        avg_occupancy_rate = 0
        if cost > 0 and len(self.U) > 0 and num_trees > 0:
            gain_ratio = tot_ic / cost
            avg_detour_ratio = tot_dr / len(self.U)
            avg_occupancy_rate = sum(occupancy_rates) / num_trees
        load = {e: l for e, l in self.load.iteritems() if l > 0}

        return steiner_forest, cost, gain_ratio, avg_detour_ratio, num_trees, avg_occupancy_rate, steiner_trees, load

    def compute_multiq_plans(self, queries, z, S, f=None, merge_users=True, alpha=0.15, beta=4.0, no_iter=0,
                             previous=None, randomise=False, seed=0, parallelise=True, p_method="pp", job_server=None):
        plans = dict()
        if randomise:
            np.random.seed(seed)
        parallelise_ = parallelise and len(queries) > 1
        # If parallelise, which method is going to be used?
        if parallelise_:
            # pp: Parallel Python ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if p_method == "pp":
                # Functions that are called to retrieve the result of the job are store in this variable.
                results = []
                for ord_, (U, pois) in enumerate(queries):
                    rnd = 0.0
                    if randomise:
                        rnd = np.random.ranf()
                    if rnd < 1. / (no_iter + 1) or previous is None:
                        vst_rs = VST_RS(self.graph)
                        # Submit the job.
                        res = job_server.submit(vst_rs.steiner_forest, (U, pois, z, S, merge_users), globals=globals())
                        results.append((ord_, res))
                    else:
                        plans[ord_] = previous[ord_]
                # Functions with the results are called.
                for ord_, res in results:
                    plan, _, _, _, _, _, sts, load = res()
                    # Update plan only if its new cost is better.
                    if previous is not None:
                        weights_0 = f(self.edges, previous[ord_][2], self.cap, alpha=alpha, beta=beta)
                        weights_1 = f(self.edges, load, self.cap, alpha=alpha, beta=beta)
                        cost_0 = sum([l * weights_0[e] for e, l in previous[ord_][2].iteritems()])
                        cost_1 = sum([l * weights_1[e] for e, l in load.iteritems()])
                        #
                        if cost_1 < cost_0:
                            plans[ord_] = (plan, sts, load)
                        else:
                            plans[ord_] = previous[ord_]
                    else:
                        plans[ord_] = (plan, sts, load)
                        # # MPI ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        # elif p_method == "mpi":
                        #     # Create as many lists of queries as processors exist.
                        #     if rank == 0:
                        #         queries_proc = dict()
                        #         for ord_, q in enumerate(queries):
                        #             try:
                        #                 queries_proc[ord_ % size].append((ord_, q))
                        #             except KeyError:
                        #                 queries_proc[ord_ % size] = [(ord_, q)]
                        #     else:
                        #         queries_proc = None
                        #     queries_ = comm.scatter(queries_proc.values(), root=0)
                        #     plans_ = dict()
                        #     for ord_, (U, pois) in queries_:
                        #         rnd = 0.0
                        #         if randomise:
                        #             rnd = np.random.ranf()
                        #         if rnd < 1. / (no_iter + 1):
                        #             vst_rs = VST_RS(self.graph)
                        #             plan, _, _, _, _, _, _, load = vst_rs.steiner_forest(U, pois, z, S, merge_users)
                        #             plans_[ord_] = (plan, load)
                        #         else:
                        #             plans_[ord_] = previous[ord_]
                        #     plans_ = comm.gather(plans_, root=0)
                        #     if rank == 0:
                        #         for i in range(size):
                        #             for ord_, (plan, load) in plans_[i].iteritems():
                        #                 plans[ord_] = (plan, load)
        else:  # No parallel processing ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            for ord_, (U, pois) in enumerate(queries):
                vst_rs = VST_RS(self.graph)
                plan, _, _, _, _, _, sts, load = vst_rs.steiner_forest(U, pois, z, S, merge_users)
                # Update plan only if its new cost is better.
                if previous is not None:
                    weights_0 = f(self.edges, previous[ord_][1], self.cap, alpha=alpha, beta=beta)
                    weights_1 = f(self.edges, load, self.cap, alpha=alpha, beta=beta)
                    cost_0 = sum([l * weights_0[e] for e, l in previous[ord_][1].iteritems()])
                    cost_1 = sum([l * weights_1[e] for e, l in load.iteritems()])
                    #
                    if cost_1 < cost_0:
                        plans[ord_] = (plan, sts, load)
                    else:
                        plans[ord_] = previous[ord_]
                else:
                    plans[ord_] = (plan, sts, load)
        return plans

    def congestion_aware(self, queries, z, S, f, merge_users=True, alpha=0.15, beta=4.0, max_iter=100, randomize=True,
                         log_history=False, parallelise=True, p_method="pp", verbose=True):
        plans = dict()
        previous = None
        no_iter = 0
        job_server = None
        parallelise_ = parallelise and len(queries) > 1
        # In the case of parallelisation, some initialisation is done.
        if parallelise_ and p_method == "pp":
            ppservers = ("*",)
            job_server = pp.Server(ppservers=ppservers)
        while no_iter < max_iter:
            # Compute the plans for the queries (it can be in parallel).
            plans = self.compute_multiq_plans(queries, z, S, f, merge_users=merge_users, alpha=alpha, beta=beta,
                                              no_iter=no_iter, previous=previous, randomise=randomize, seed=no_iter,
                                              parallelise=parallelise, p_method=p_method, job_server=job_server)
            # Aggregate the loads.
            self.load = {e: 0 for e in self.edges}
            for _, (plan, _, load) in plans.iteritems():
                for e, l in load.iteritems():
                    self.load[e] += l
            # Store the previous plan as it is needed with a mixed strategy.
            previous = dict(plans)
            # Compute new weights based on the current load and the WEIGHTS OF THE PREVIOUS ITERATION.
            weights = f(self.graph.get_edges(), self.load, self.cap, alpha=alpha, beta=beta)
            self.graph.update_edge_weights(weights)
            # Store the history of loads as they are needed to check convergence.
            self.append_to_history(f, log_history=log_history, alpha=alpha, beta=beta)
            # Check stop condition. Either convergence or maximum number of iterations reached.
            no_iter += 1
            if verbose:
                print no_iter
            if len(self.load_h) > 1:
                if self.load_h[-1] == self.load_h[-2]:
                    if verbose:
                        print "No. iter: " + str(no_iter)
                    break
        if verbose and no_iter > max_iter:
            print "Max. number of iterations reached!"
        if log_history:
            self.log_history()
        # Compute congestion statistics.
        cost, warl, mwrl, mrl1, mrl2, entropy = self.compute_congestion_statistics(f, alpha=alpha, beta=beta)
        # In the case of parallelisation, some cleaning is done.
        if parallelise_ and p_method == "pp":
            if verbose:
                job_server.print_stats()
            job_server.destroy()
        # TODO: sts correspond to the collection of Steiner Trees (individual vehicles). This is not needed here yet. It is used in VST-CA (mobile app)
        return [(ord_, plan) for ord_, (plan, sts, _) in
                plans.iteritems()], cost, warl, mwrl, mrl1, mrl2, entropy, no_iter

    def non_congestion_aware(self, queries, z, S, f, merge_users=True, alpha=0.15, beta=4.0, parallelise=True,
                             p_method="pp", verbose=True):
        job_server = None
        parallelise_ = parallelise and len(queries) > 1
        # In the case of parallelisation, some initialisation is done.
        if parallelise_ and p_method == "pp":
            ppservers = ("*",)
            job_server = pp.Server(ppservers=ppservers)
        # Compute the plans for the queries (it can be in parallel).
        plans = self.compute_multiq_plans(queries, z, S, merge_users=merge_users, parallelise=parallelise,
                                          p_method=p_method, job_server=job_server)
        # Aggregate the loads.
        for _, (_, _, load) in plans.iteritems():
            for e, l in load.iteritems():
                self.load[e] += l
        # Compute congestion statistics.
        cost, warl, mwrl, mrl1, mrl2, entropy = self.compute_congestion_statistics(f, alpha=alpha, beta=beta)
        # In the case of parallelisation, some cleaning is done.
        if parallelise_ and p_method == "pp":
            if verbose:
                job_server.print_stats()
            job_server.destroy()
        return [(ord_, plan, sts) for ord_, (plan, sts, _) in plans.iteritems()], cost, warl, mwrl, mrl1, mrl2, entropy

    def append_to_history(self, f, log_history=False, alpha=0.15, beta=4.0):
        edges = sorted(self.edges)
        load = []
        weights = []
        for e in edges:
            load.append(self.load[e])
            if log_history:
                weights.append(self.graph.get_edges()[e])
        self.load_h.append(load)
        if log_history:
            self.weights_h.append(weights)
            cost, warl, mwrl, mrl1, mrl2, entropy = self.compute_congestion_statistics(f, alpha=alpha, beta=beta)
            self.stats_h.append([cost, warl, mwrl, mrl1, mrl2, entropy])

    def log_history(self):
        ts = time.strftime("%d%b%Y_%H%M%S")
        #
        load_f = open("files/load_" + ts + ".csv", 'wb')
        load_wr = csv.writer(load_f)
        for load in self.load_h:
            load_wr.writerow(load)
        #
        weights_f = open("files/weights_" + ts + ".csv", 'wb')
        weights_wr = csv.writer(weights_f)
        for weights in self.weights_h:
            weights_wr.writerow(weights)
        #
        stats_f = open("files/stats_" + ts + ".csv", 'wb')
        stats_wr = csv.writer(stats_f)
        for stats in self.stats_h:
            stats_wr.writerow(stats)

    def compute_congestion_statistics(self, f, alpha=0.15, beta=4.0):
        # Compute new weights regarding the current loads.
        weights = f(self.edges, self.load, self.cap, alpha=alpha, beta=beta)
        # Initialise statistics.
        cost = 0.0
        warl = 0.0
        mwrl = 0.0
        mrl1 = 0.0
        mrl2 = 0.0
        rls = []
        # Compute statistics.
        for e, weight in self.edges.iteritems():
            if self.load[e] > 0:
                cost += self.load[e] * weights[e]  # With new weights
                prop = weight / self.sum_weights  # "Importance" of the edge (based on original weights)
                rl = float(self.load[e]) / self.cap[e]
                rls.append(rl)
                weighted_rl = rl * prop
                warl += weighted_rl  # (based on original weights)
                if weighted_rl > mwrl:
                    mwrl = weighted_rl
                    mrl1 = rl
                if rl > mrl2:
                    mrl2 = rl
            else:
                rls.append(0)
        entropy = utils.entropy(rls)
        return cost, warl, mwrl, mrl1, mrl2, entropy

    def get_subgroups(self, cmb, bestSubgrouping):
        subgroups = []
        t_cmb = tuple(sorted(cmb))
        comb1, comb2 = bestSubgrouping[t_cmb]
        # TODO: At least comb1 SHOULD have value
        if comb1 is not None:
            if len(comb1) <= self.z:
                subgroups.append(comb1)
            else:
                sg = self.get_subgroups(comb1, bestSubgrouping)
                subgroups.extend(sg)
        if comb2 is not None:
            if len(comb2) <= self.z:
                subgroups.append(comb2)
            else:
                sg = self.get_subgroups(comb2, bestSubgrouping)
                subgroups.extend(sg)
        return subgroups

    def build_steiner_forest(self, cmb, OptCost, OptPOI, J, bestDiv, bestSubgrouping):
        cost = 0
        num_trees = 0
        steiner_trees = []
        steiner_forest = digraph.Digraph()
        t_cmb = tuple(sorted(cmb))
        detours = {t: 0 for t in t_cmb}
        occupancy_rates = []
        p = OptPOI[t_cmb]
        if p is not None:
            steiner_tree, cost = self.build_steiner_tree(p, cmb, J, bestDiv, detours)
            steiner_forest.append_from_graph(steiner_tree)
            num_trees += 1
            steiner_trees.append((cmb, steiner_tree))
            # self.__update_load(steiner_tree)
            occupancy_rates.append(float(len(t_cmb)) / self.z)
        else:
            if t_cmb in bestSubgrouping:
                comb1, comb2 = bestSubgrouping[t_cmb]
                c_1 = c_2 = nt_1 = nt_2 = 0
                # TODO: At least comb1 SHOULD have value
                if comb1 is not None:
                    if len(comb1) > 0:
                        forest_1, c_1, detours_1, nt_1, ocr_1, sts_1 = \
                            self.build_steiner_forest(comb1, OptCost, OptPOI, J, bestDiv, bestSubgrouping)
                        steiner_forest.append_from_graph(forest_1)
                        steiner_trees.extend(sts_1)
                        detours.update(detours_1)
                        occupancy_rates.extend(ocr_1)
                if comb2 is not None:
                    if len(comb2) > 0:
                        forest_2, c_2, detours_2, nt_2, ocr_2, sts_2 = \
                            self.build_steiner_forest(comb2, OptCost, OptPOI, J, bestDiv, bestSubgrouping)
                        steiner_forest.append_from_graph(forest_2)
                        steiner_trees.extend(sts_2)
                        detours.update(detours_2)
                        occupancy_rates.extend(ocr_2)
                cost += c_1 + c_2
                num_trees += nt_1 + nt_2
        return steiner_forest, cost, detours, num_trees, occupancy_rates, steiner_trees

    def build_steiner_tree(self, node, cmb, J, bestDiv, detours):
        steiner_tree = digraph.Digraph()
        t_cmb = tuple(sorted(cmb))
        m = J[t_cmb][node]
        self.graph.compute_dist_paths(origins=[node], destinations=[m], recompute=True)
        cost = self.graph.dist[tuple(sorted([node, m]))]
        #
        if m in t_cmb:
            detours[m] += cost
        else:
            for t in t_cmb:
                detours[t] += cost
        #
        path = self.graph.paths[tuple(sorted([node, m]))]
        steiner_tree.append_from_path(path, self.graph)
        self.update_load(path)
        if t_cmb in bestDiv:
            comb1, comb2 = bestDiv[t_cmb][m]
            branch_1 = digraph.Digraph()
            c_1 = c_2 = 0
            if comb1 is not None and comb1 != [m]:
                branch_1, c_1 = self.build_steiner_tree(m, comb1, J, bestDiv, detours)
            branch_2 = digraph.Digraph()
            if comb2 is not None and comb2 != [m]:
                branch_2, c_2 = self.build_steiner_tree(m, comb2, J, bestDiv, detours)
            steiner_tree.append_from_graph(branch_1)
            steiner_tree.append_from_graph(branch_2)
            cost += c_1 + c_2
        return steiner_tree, cost

    def update_load(self, path):
        for i in range(len(path) - 1):
            v = path[i]
            w = path[i + 1]
            self.load[tuple(sorted([v, w]))] += 1
