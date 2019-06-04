import sys

from suitability import SuitableNodeWeightGenerator
from vst_rs import VST_RS

class ExactC_VSF:
    def __init__(self, graph, terminals, pois):

        # Init some instance variables.
        self.__graph = graph
        self.__terminals = terminals
        self.__pois = pois

        # Temporal list to be excluded when getting suitable nodes.
        temp = list(terminals)
        temp.extend(pois)

        # Get suitable nodes.
        generator = SuitableNodeWeightGenerator()
        self.__hotspots = self.__graph.get_suitable_nodes(generator, excluded_nodes=temp)
        temp.extend(self.__hotspots)

        # Compute distances between every node within set [temp]
        if len(self.__graph.nodes_dist_paths) == 0:
            self.__graph.compute_dist_paths(origins=temp, destinations=temp, compute_paths=False)

        # Compute P-Voronoi cells.
        self.__p_cells, self.__medoids = self.__graph.get_voronoi_medoids_cells(self.__pois, temp)

    def __get_candidates_terminal(self, terminal):
        candidates = set()
        for h in self.__hotspots:
            if terminal == h:
                continue
            dist_t_h = self.__graph.dist[tuple(sorted([terminal, h]))]
            dist_t_m = self.__graph.dist[tuple(sorted([terminal, self.__medoids[terminal]]))]
            if dist_t_h < dist_t_m:
                candidates.add(h)
        return candidates

    def __compute_configurations(self, C):
        R = {}
        visited = []
        for t1, cs1 in C.iteritems():
            X1 = self.__get_candidates_terminal(t1)
            visited.append(t1)
            for c1 in cs1:
                C_ = {t: cs for t, cs in C.iteritems() if t not in c1}
                for t2, cs2 in C_.iteritems():
                    if t2 in visited:
                        continue
                    X2 = self.__get_candidates_terminal(t2)
                    X = X1.intersection(X2)
                    if len(X) == 0:
                        continue
                    for c2 in cs2:
                        if len(c1.intersection(c2)) > 0:
                            continue
                        for h in X:
                            c = frozenset(c1.union(c2))
                            if h in C and c in C[h]:
                                continue
                            if h not in R:
                                R[h] = {c}
                            else:
                                R[h].add(c)
        return R

    def __compute_membership(self):
        membership = {}
        C = {}
        for t in self.__terminals:
            membership[t] = set()
            C[t] = {frozenset([t])}
        R = self.__compute_configurations(C)
        while len(R) > 0:
            for h, cs in R.iteritems():
                m = self.__medoids[h]
                for c in cs:
                    for t in c:
                        membership[t].add(m)
                if h not in C:
                    C[h] = set(R[h])
                else:
                    C[h].update(R[h])
            R = self.__compute_configurations(C)
        for t in self.__terminals:
            if len(membership[t]) == 0:
                membership[t] = {self.__medoids[t]}
        return membership

    # def __compute_membership(self):
    #     # groups = {p: set() for p in self.__pois}
    #     membership = {t: set() for t in self.__terminals}
    #     for t1 in self.__terminals:
    #         m1 = self.__medoids[t1]
    #         # groups[m1].add(t1)
    #         membership[t1].add(m1)
    #         c1 = self.__get_candidates_terminal(t1)
    #         i1 = self.__terminals.index(t1)
    #         for i in range(i1 + 1, len(self.__terminals)):
    #             t2 = self.__terminals[i]
    #             m2 = self.__medoids[t2]
    #             # groups[m2].add(t2)
    #             membership[t2].add(m2)
    #             if m1 == m2:
    #                 continue
    #             c2 = self.__get_candidates_terminal(t2)
    #             if len(c1.intersection(c2)) > 0:
    #                 # groups[m1].add(t2)
    #                 # groups[m2].add(t1)
    #                 membership[t1].add(m2)
    #                 membership[t2].add(m1)
    #     # return groups, membership
    #     return membership

    def __compute_branches(self, level, branch, membership):
        if level == len(self.__terminals):
            return [branch]
        res = []
        t = self.__terminals[level]
        medoids = membership[t]
        for m in medoids:
            new_branch = dict(branch)
            new_branch[t] = m
            res.extend(self.__compute_branches(level + 1, new_branch, membership))
        return res

    def steiner_forest(self, k, S):
        forests = {}
        mz = VST_RS(self.__graph)
        membership = self.__compute_membership()
        branches = self.__compute_branches(0, {}, membership)
        print len(branches)
        for b in branches:
            groups = {}
            for t, m in b.iteritems():
                if m in groups:
                    groups[m].append(t)
                else:
                    groups[m] = [t]
            forest, cost = mz.steiner_forest([ts for _, ts in groups.iteritems()], self.__terminals, self.__pois, k, S)
            forests[cost] = forest
        return forests[min(forests)], min(forests)