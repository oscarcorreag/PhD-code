import operator
import sys
import pdb
import numpy as np

from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from utils import id_generator


class HotspotBased:
    def __init__(self, graph, terminals, pois, hot_spots=None):

        # Init some instance variables.
        self.__graph = graph
        self.__terminals = terminals
        self.__pois = pois

        # Temporal list to be excluded when getting suitable nodes.
        temp = list(terminals)
        temp.extend(pois)

        # Get suitable nodes.
        generator = SuitableNodeWeightGenerator()
        self.__hot_spots = self.__graph.get_suitable_nodes(generator, excluded_nodes=temp)
        self.__actual_hs = set(self.__hot_spots)

        if hot_spots is not None:
            self.__hot_spots = hot_spots

        temp.extend(self.__hot_spots)

        # Compute distances between every node within set [temp]
        # if len(self.__graph.pairs_dist_paths) == 0:
        self.__graph.compute_dist_paths(origins=temp, destinations=temp, compute_paths=False)

        # Deal with nodes that are not accessible.
        # print self.__graph.issues_dist_paths

        # Compute P-Voronoi cells.
        _, self.__medoids = self.__graph.get_voronoi_medoids_cells(self.__pois, temp)

        # Subtree-SVs
        self.__leaves_subtree_sv = {}
        self.__inv_subtree_sv = {}

        # Information by terminal / pseudo-terminal
        self.__ind_cost = {}
        self.__cum_loss = {}
        self.__cum_num_terms = {}
        self.__vert_tree = {}
        self.__term_tree = {}
        self.__detour = {}  # Terminals only, i.e. not pseudo-terminals.
        self.__confirmed = {}
        for t in self.__terminals:
            self.__ind_cost[t] = self.__graph.dist[tuple(sorted([t, self.__medoids[t]]))]
            self.__cum_loss[t] = 0
            self.__cum_num_terms[t] = 1
            self.__vert_tree[t] = {t}
            self.__term_tree[t] = {t}
            self.__detour[t] = 0
            self.__confirmed[t] = None

        # Gain ratios.
        self.__gain_ratios = {}

        # Loss ratios.
        self.__loss_ratios = {}

        # Aware terminals.
        self.__aware = []

    def __create_well_formed_subtree_svs(self, terminals, max_dr=sys.maxint):
        self.__leaves_subtree_sv = {}
        self.__inv_subtree_sv = {}
        for h in self.__hot_spots:
            self.__leaves_subtree_sv[h] = []
            dist_h_m = self.__graph.dist[tuple(sorted([h, self.__medoids[h]]))]
            for t in terminals:
                # Dismiss leaf t if it is aware of the inconvenience of meeting anywhere.
                if h not in self.__actual_hs and t in self.__aware:
                    continue
                # Dismiss leaf t if candidate Steiner vertex h is included in the tree whose root is t.
                if h in self.__vert_tree[t] and t != h:
                    continue
                dist_t_h = self.__graph.dist[tuple(sorted([t, h]))]
                # When maximum detour ratio was specified.
                if max_dr < sys.maxint:
                    # Dismiss leaf t (pseudo-terminal) if detour ratio of any of its descendant terminals is exceeded.
                    dr_exceeded = False
                    # for t_ in self.__vert_tree[t].intersection(self.__terminals):
                    for t_ in self.__term_tree[t]:
                        if self.__ind_cost[t_] != 0 \
                                and (self.__detour[t_] + dist_t_h + dist_h_m) / self.__ind_cost[t_] > max_dr:
                            dr_exceeded = True
                            break
                    if dr_exceeded:
                        continue
                # Leaf t is included in Subtree-SV as long as candidate Steiner vertex h is located closer than its
                # corresponding root.
                dist_t_m = self.__graph.dist[tuple(sorted([t, self.__medoids[t]]))]
                if dist_t_h < dist_t_m:
                    self.__leaves_subtree_sv[h].append(t)
                    try:
                        self.__inv_subtree_sv[t].append(h)
                    except KeyError:
                        self.__inv_subtree_sv[t] = [h]
        # Drop hotspots which have less than two terminals (Subtree-SVs with less than two leaves.)
        self.__drop_unsuitable_hotspots()
        # Which terminals will definitely go to their medoids? The ones which do not have any candidate Steiner vertex
        # to go to.
        for t in terminals:
            if t not in self.__inv_subtree_sv or len(self.__inv_subtree_sv[t]) == 0:
                self.__confirmed[t] = self.__medoids[t]
                # For each pseudo-terminal, update detours for its descendant terminals accordingly.
                # for t_ in self.__vert_tree[t].intersection(self.__terminals):
                for t_ in self.__term_tree[t]:
                    self.__detour[t_] += self.__graph.dist[tuple(sorted([t, self.__medoids[t]]))]

    def __drop_unsuitable_hotspots(self):
        # Drop hotspots which have less than two terminals.
        for h in self.__hot_spots:
            if len(self.__leaves_subtree_sv[h]) < 2:
                if len(self.__leaves_subtree_sv[h]) == 1:
                    t = self.__leaves_subtree_sv[h][0]
                    del self.__inv_subtree_sv[t][self.__inv_subtree_sv[t].index(h)]
                del self.__leaves_subtree_sv[h]

    def __compute_gain_ratios(self):
        self.__gain_ratios = {}
        for h, leaves in self.__leaves_subtree_sv.iteritems():
            self.__gain_ratios[h] = self.__compute_gain_ratio(h, leaves)

    def __compute_gain_ratio(self, h, leaves):
        tot_ind_cost = tree = 0
        for t in leaves:
            tot_ind_cost += self.__ind_cost[t]
            tree += self.__cum_loss[t] + self.__graph.dist[tuple(sorted([t, h]))]
        tree += self.__graph.dist[tuple(sorted([h, self.__medoids[h]]))]
        return float(tot_ind_cost) / tree

    def __compute_loss_ratios(self, terminals):
        self.__loss_ratios = {}
        for t in terminals:
            self.__loss_ratios[t] = {}
            # self.__detour_ratios_2[t] = {}
            # self.__detour_ratios_3[t] = {}
            for h in self.__inv_subtree_sv[t]:
                if t == h:
                    self.__loss_ratios[t][h] = 0
                else:
                    dist_t_h = self.__graph.dist[tuple(sorted([t, h]))]
                    self.__loss_ratios[t][h] = float(self.__cum_loss[t] + dist_t_h) / self.__ind_cost[t]
                    # Ts = len(self.__ridesharers_by_hotspot[h])
                    # self.__detour_ratios_2[t][h] = (dist_t_h + dist_h_m / Ts) / OPT
                    # self.__detour_ratios_3[t][h] = dist_t_h / OPT

    # def __compute_densities(self):
    #     for h, ridesharers in self.__ridesharers_by_hotspot.iteritems():
    #         star = sum([self.__graph.dist[tuple(sorted([t, h]))] for t in ridesharers])
    #         star += self.__graph.dist[tuple(sorted([h, self.__medoids[h]]))]
    #         Ts = len(ridesharers)
    #         self.__densities[h] = star / Ts

    # def __compute_remoteness(self):
    #     for poi, p_cell in self.__p_cells.iteritems():
    #         hotspots = set(p_cell).intersection(self.__hotspots)
    #         max_dist = max([self.__graph.dist[tuple(sorted([h, poi]))] for h in hotspots])
    #         temp = {h: self.__graph.dist[tuple(sorted([h, poi]))] / max_dist for h in hotspots}
    #         self.__remoteness.update(temp)

    def __drop_leaf_from_subtree_sv(self, t, h):
        if h in self.__leaves_subtree_sv and t in self.__inv_subtree_sv:
            #
            del self.__leaves_subtree_sv[h][self.__leaves_subtree_sv[h].index(t)]
            del self.__inv_subtree_sv[t][self.__inv_subtree_sv[t].index(h)]
            del self.__loss_ratios[t][h]
            #
            num_leaves_left = len(self.__leaves_subtree_sv[h])
            if num_leaves_left >= 2:
                # Update gain ratio.
                self.__gain_ratios[h] = self.__compute_gain_ratio(h, self.__leaves_subtree_sv[h])
            elif num_leaves_left == 1:
                t_ = self.__leaves_subtree_sv[h][0]
                self.__drop_leaf_from_subtree_sv(t_, h)
            elif num_leaves_left == 0:
                del self.__leaves_subtree_sv[h]
                del self.__gain_ratios[h]
            #
            num_hotspots_left = len(self.__inv_subtree_sv[t])
            if num_hotspots_left == 0:
                del self.__inv_subtree_sv[t]
                del self.__loss_ratios[t]

    def __confirm(self, h, k, clone_hotspots):
        tot_ind_cost = tree = tot_num_terms = 0
        vertices = {h}
        terminals = set()
        for t in self.__leaves_subtree_sv[h]:
            dist_t_h = self.__graph.dist[tuple(sorted([t, h]))]
            tot_ind_cost += self.__ind_cost[t]
            tree += self.__cum_loss[t] + dist_t_h
            tot_num_terms += self.__cum_num_terms[t]
            vertices.update(self.__vert_tree[t])
            terminals.update(self.__term_tree[t])
            # for t_ in self.__vert_tree[t].intersection(self.__terminals):
            for t_ in self.__term_tree[t]:
                self.__detour[t_] += dist_t_h
            self.__confirmed[t] = h
        self.__ind_cost[h] = tot_ind_cost
        self.__cum_loss[h] = tree
        self.__cum_num_terms[h] = tot_num_terms
        self.__vert_tree[h] = set(vertices)
        self.__term_tree[h] = set(terminals)
        if tot_num_terms == k:
            self.__confirmed[h] = self.__medoids[h]
            # for t_ in self.__vert_tree[h].intersection(self.__terminals):
            for t_ in self.__term_tree[h]:
                self.__detour[t_] += self.__graph.dist[tuple(sorted([h, self.__medoids[h]]))]
            if clone_hotspots:
                self.__clone_steiner_vertices(h)
                # self.__hotspots.remove(h)
                # print h, "removed!"
        elif tot_num_terms > k:
            raise (ValueError, "Steiner vertex " + str(h) + " cannot accommodate more than " + str(k))
        else:
            self.__confirmed[h] = None

    def __accommodate_k_terminals(self, h, loss_ratios, k, max_wd):
        Lk_ = []
        tot_num_terms = 0
        gr = 0
        Lk = sorted(loss_ratios.iteritems(), key=operator.itemgetter(1))
        driver_present = False
        for leaf, loss_ratio in Lk:
            if (gr != 0 and 1 / gr <= loss_ratio) or tot_num_terms == k:
                break
            if h not in self.__actual_hs:
                dist_t_h = self.__graph.dist[tuple(sorted([leaf, h]))]
                if driver_present and (leaf not in self.__terminals or dist_t_h > max_wd):
                    break
                else:
                    driver_present = leaf not in self.__terminals or dist_t_h > max_wd
            tot_num_terms += self.__cum_num_terms[leaf]
            if tot_num_terms <= k:
                Lk_.append((leaf, loss_ratio))
                gr = self.__compute_gain_ratio(h, [leaf for leaf, _ in Lk_])
            else:
                tot_num_terms -= self.__cum_num_terms[leaf]
        return gr, [leaf for leaf, _ in Lk_]

    def __max_gain_ratio(self, gr, h, leaves_ord_loss):
        Lk = list(leaves_ord_loss)
        while len(Lk) > 2:
            max_loss = Lk[-1][1]
            if 1 / gr < max_loss:
                Lk.pop()
                gr = self.__compute_gain_ratio(h, [leaf for leaf, _ in Lk])
            else:
                break
        return gr, [leaf for leaf, _ in Lk]

    def __clone_steiner_vertices(self, h):
        new_candidates = []
        for sv in self.__vert_tree[h].intersection(self.__hot_spots):
            new_candidate_id = id_generator()
            self.__graph[new_candidate_id] = \
                (self.__graph[sv][0], self.__graph[sv][1].copy(), self.__graph[sv][2].copy())
            for w, dist in self.__graph[sv][1].iteritems():
                self.__graph[w][1][new_candidate_id] = dist
            self.__hot_spots.append(new_candidate_id)
            self.__medoids.update({new_candidate_id: self.__medoids[sv]})
            new_candidates.append(new_candidate_id)
        self.__graph.update_dist_paths(new_candidates, compute_paths=False)

    def __choose_steiner_vertices(self, k, clone_hotspots, max_wd):
        R = set()
        S = {h: gr for h, gr in self.__gain_ratios.iteritems()}
        while len(S) > 0:
            S_ = dict(S)
            leaves_subtree_svs = {}
            for h, gr in S_.iteritems():
                loss_ratios = {t: self.__loss_ratios[t][h] for t in self.__leaves_subtree_sv[h]}
                S_[h], leaves_subtree_svs[h] = self.__accommodate_k_terminals(h, loss_ratios, k, max_wd)
                # Lk = sorted(loss_ratios.iteritems(), key=operator.itemgetter(1))
                # if k < sys.maxint:
                #     S_[h], leaves_subtree_svs[h] = self.__accommodate_k_terminals(h, Lk, k)
                # else:
                #     S_[h], leaves_subtree_svs[h] = self.__max_gain_ratio(gr, h, Lk)
            S_ord_ = sorted(S_.iteritems(), key=operator.itemgetter(1), reverse=True)
            # while len(S_ord_) > 0 and len(leaves_subtree_svs[S_ord_[0][0]]) == 1:
            while len(S_ord_) > 0 and len(leaves_subtree_svs[S_ord_[0][0]]) < 2:
                del S_ord_[0]
            if len(S_ord_) > 0:
                h = S_ord_[0][0]
                for t in set(self.__leaves_subtree_sv[h]).difference(leaves_subtree_svs[h]):
                    self.__drop_leaf_from_subtree_sv(t, h)
                R.add(h)
                self.__confirm(h, k, clone_hotspots)
                for t in leaves_subtree_svs[h]:
                    hs_affected = set(self.__inv_subtree_sv[t]).intersection(S.keys())
                    hs_affected.remove(h)
                    for ha in hs_affected:
                        self.__drop_leaf_from_subtree_sv(t, ha)
            else:
                break
            S = {h: gr for h, gr in self.__gain_ratios.iteritems() if h not in R}

    def __build_steiner_forest(self):
        forest = SuitabilityGraph()
        dist = cost = occupancy = 0
        for t, dest in self.__confirmed.iteritems():
            if dest is None:
                dest = self.__medoids[t]
                self.__confirmed[t] = dest
                for t_ in self.__term_tree[t]:
                    self.__detour[t_] += self.__graph.dist[tuple(sorted([t, dest]))]
            # # Print groups of terminals that travel together.
            # if dest in self.__pois:
            #     print self.__term_tree[t]
            # print t, dest
            self.__graph.compute_dist_paths(origins=[t], destinations=[dest], recompute=True)
            try:
                forest.append_path(self.__graph.paths[tuple(sorted([t, dest]))], self.__graph)
                dist = self.__graph.dist[tuple(sorted([t, dest]))]
                cost += dist
            except KeyError:
                # pdb.set_trace()
                print 'key error:', t, dest
            # Who is driver?
            # if t in self.__terminals and (dist > max_wd or dest == self.__medoids[t]):
            #     print "Driver:", t, "Meeting point:", dest
            occupancy += len(self.__term_tree[t]) * dist
            # print "Num. terms:", len(self.__term_tree[t]), "Shared distance:", dist
        return forest, cost, occupancy / cost

    # def __num_terminals(self, steiner_vertex):
    #     if steiner_vertex in self.__terminals:
    #         return 1
    #     nt = 0
    #     for l, sv in self.__confirmed.iteritems():
    #         if sv == steiner_vertex:
    #             nt += self.__num_terminals(l)
    #     return nt
    #
    # def __check_k(self, k):
    #     for v, w in self.__confirmed.iteritems():
    #         if w in self.__pois:
    #             nt = self.__num_terminals(v)
    #             if nt > k:
    #                 print "sv:", v, "root:", w, "nt:", nt

    def __get_lowest_steiner_vertices(self):
        steiner_vertices = {}
        for v, w in self.__confirmed.iteritems():
            if v in self.__terminals and w not in self.__pois:
                dist_v_w = self.__graph.dist[tuple(sorted([v, w]))]
                try:
                    steiner_vertices[w][v] = dist_v_w
                except KeyError:
                    steiner_vertices[w] = {v: dist_v_w}
        return steiner_vertices

    def __compute_avg_occupancy_rate(self, k):
        num_trees = 0
        o_rate = 0
        for v, w in self.__confirmed.iteritems():
            if w in self.__pois:
                # print v, self.__cum_num_terms[v]
                o_rate += float(self.__cum_num_terms[v]) / k
                num_trees += 1
        return num_trees, o_rate / num_trees

    def __compute_avg_detour_ratio(self):
        total_ind_cost = 0
        dr = 0
        for t in self.__terminals:
            total_ind_cost += self.__ind_cost[t]
            if self.__ind_cost[t] != 0:
                dr += self.__detour[t] / self.__ind_cost[t]
        return dr / len(self.__terminals), total_ind_cost

    def steiner_forest(self, k=sys.maxint, clone_hotspots=False, max_dr=sys.maxint, max_wd=sys.maxint, get_lsv=True,
                       awareness=0.0, seed=0):
        np.random.seed(seed)
        terminals = list(self.__terminals)
        for t in terminals:
            rnd = np.random.ranf()
            if rnd <= awareness:
                self.__aware.append(t)
        while True:
            self.__create_well_formed_subtree_svs(terminals, max_dr)
            terminals_with_no_dest = [t for t, dest in self.__confirmed.iteritems() if dest is None]
            if len(terminals_with_no_dest) == 0:
                break
            self.__compute_gain_ratios()
            self.__compute_loss_ratios(terminals_with_no_dest)
            self.__choose_steiner_vertices(k, clone_hotspots, max_wd)
            terminals = [t for t, dest in self.__confirmed.iteritems() if dest is None]
            if set(terminals_with_no_dest) == set(terminals):
                break
        forest, cost, avg_oc = self.__build_steiner_forest()
        # Compute some statistics.
        avg_dr, total_ind_cost = self.__compute_avg_detour_ratio()
        num_trees, avg_or = self.__compute_avg_occupancy_rate(k)
        if get_lsv:
            lsv = self.__get_lowest_steiner_vertices()
            return forest, cost, total_ind_cost / cost, avg_dr, num_trees, avg_or, avg_oc, lsv
        else:
            return forest, cost, total_ind_cost / cost, avg_dr, num_trees, avg_or, avg_oc
