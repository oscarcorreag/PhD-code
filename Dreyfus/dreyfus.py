import sys

from graph import Graph
from utils import comb


class Dreyfus:
    def __init__(self, graph):
        self.__graph = graph
        self.__graph.compute_dist_paths(compute_paths=False)
        self.__steiner_distances = {}

    '''

    '''

    def steiner_tree(self, terminals, consider_terminals=True):

        if len(terminals) > 0:
            q = terminals[0]
            set_c = sorted(terminals[1:])
        else:
            return

        for j in self.__graph:
            self.__steiner_distances[j] = {}
            for t in set_c:
                j_t = tuple(sorted(([j, t])))
                try:
                    self.__steiner_distances[j][tuple([t])] = [self.__graph.dist[j_t], t, (None, None)]
                except KeyError:
                    self.__steiner_distances[j][tuple([t])] = [sys.maxint, t, (None, None)]

        for m in range(2, len(set_c)):

            for set_d in comb(set_c, m):
                for i in self.__graph:
                    self.__steiner_distances[i][tuple(set_d)] = [sys.maxint, None, (None, None)]

                sets_e = [[set_d[0]]]
                for x in range(1, m - 1):
                    for y in comb(set_d[1:], x):
                        t = [set_d[0]]
                        t.extend(y)
                        sets_e.append(t)

                for j in self.__graph:
                    u = sys.maxint
                    best_subsets = None
                    for set_e in sets_e:
                        set_f = sorted(list(set(set_d) - set(set_e)))
                        if len(set_f) > 0:
                            s = self.__steiner_distances[j][tuple(set_e)][0] + \
                                self.__steiner_distances[j][tuple(set_f)][0]
                        else:
                            s = self.__steiner_distances[j][tuple(set_e)][0]
                        if s < u:
                            u = s
                            best_subsets = (set_e, set_f)
                    for i in self.__graph:
                        i_j = tuple(sorted(([i, j])))
                        try:
                            dist = self.__graph.dist[i_j]
                        except KeyError:
                            dist = sys.maxint
                        if consider_terminals:
                            if dist + u < self.__steiner_distances[i][tuple(set_d)][0]:
                                self.__steiner_distances[i][tuple(set_d)] = [dist + u, j, best_subsets]
                        else:
                            if dist + u < self.__steiner_distances[i][tuple(set_d)][0] and j not in terminals:
                                self.__steiner_distances[i][tuple(set_d)] = [dist + u, j, best_subsets]

        sets_e = [[set_c[0]]]
        for x in range(1, len(set_c) - 1):
            for y in comb(set_c[1:], x):
                t = [set_c[0]]
                t.extend(y)
                sets_e.append(t)

        cost = sys.maxint
        if q not in self.__steiner_distances:
            self.__steiner_distances[q] = {tuple(set_c): [cost, None, (None, None)]}
        else:
            self.__steiner_distances[q][tuple(set_c)] = [cost, None, (None, None)]
        for j in self.__graph:
            u = sys.maxint
            best_subsets = None
            for set_e in sets_e:
                set_f = sorted(list(set(set_c) - set(set_e)))
                if len(set_f) > 0:
                    s = self.__steiner_distances[j][tuple(set_e)][0] + self.__steiner_distances[j][tuple(set_f)][0]
                else:
                    s = self.__steiner_distances[j][tuple(set_e)][0]
                if s < u:
                    u = s
                    best_subsets = (set_e, set_f)
            q_j = tuple(sorted(([q, j])))
            try:
                dist = self.__graph.dist[q_j]
            except KeyError:
                dist = sys.maxint
            if consider_terminals:
                if dist + u < cost:
                    cost = dist + u
                    self.__steiner_distances[q][tuple(set_c)] = [cost, j, best_subsets]
            else:
                if dist + u < cost and j not in terminals:
                    cost = dist + u
                    self.__steiner_distances[q][tuple(set_c)] = [cost, j, best_subsets]

        # Reconstruct the Steiner by backtracking
        steiner_tree, cost = self.__build_steiner_tree(q, set_c)

        return steiner_tree, cost

    '''

    '''

    def __build_steiner_tree(self, node, subset):
        steiner_tree = Graph()
        next_node = self.__steiner_distances[node][tuple(subset)][1]
        cost = 0
        if next_node is not None:
            self.__graph.compute_dist_paths(origins=[node], destinations=[next_node], recompute=True)
            cost = self.__graph.dist[tuple(sorted([node, next_node]))]
            steiner_tree.append_path(self.__graph.paths[tuple(sorted([node, next_node]))], self.__graph)
        (best_e, best_f) = self.__steiner_distances[node][tuple(subset)][2]
        branch_e = Graph()
        c_1 = c_2 = 0
        if best_e is not None and best_e != [next_node]:
            branch_e, c_1 = self.__build_steiner_tree(next_node, best_e)
        branch_f = Graph()
        if best_f is not None and best_f != [next_node] and len(best_f) > 0:
            branch_f, c_2 = self.__build_steiner_tree(next_node, best_f)
        steiner_tree.append_graph(branch_e)
        steiner_tree.append_graph(branch_f)
        cost += c_1 + c_2
        return steiner_tree, cost
