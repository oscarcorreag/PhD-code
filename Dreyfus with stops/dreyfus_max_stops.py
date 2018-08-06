import sys
import pdb

from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from utils import comb


class DreyfusMaxStops:
    def __init__(self, graph, poi, terminals, max_stops, dist_paths=None, nodes=None):
        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Dreyfus with IMRs algorithm only works with node-weighted graphs.")
        #
        self.__graph = graph
        self.__poi = poi
        self.__terminals = terminals
        self.__max_stops = max_stops
        #
        generator = SuitableNodeWeightGenerator()
        if nodes is not None:
            self.__nodes = list(nodes)
        else:
            self.__nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals)
            if poi not in self.__nodes:
                self.__nodes.append(poi)
        #
        self.__dist = {}
        self.__paths = {}
        if dist_paths is not None:
            self.__dist = dict(dist_paths[0])
            self.__paths = dict(dist_paths[1])
        else:
            temp = list(terminals)  # POI is already included
            temp.extend(self.__nodes)
            self.__dist, self.__paths = self.__graph.get_dist_paths(origins=temp, destinations=temp)
        #
        self.__s_d = {}

    '''
    '''
    def steiner_tree(self):
        #
        set_c = tuple(sorted(self.__terminals))
        t_tuples = [tuple([t]) for t in set_c]
        #
        ms = {t: s - 1 for t, s in self.__max_stops.items()}
        bs = {t: s == 0 for t, s in ms.items()}
        #
        temp_list = list(self.__nodes)
        temp_list.remove(self.__poi)
        for j in temp_list:
            self.__s_d[j] = {}
            for t_ in t_tuples:
                t = t_[0]
                try:
                    self.__s_d[j][t_] = [self.__dist[tuple(sorted([j, t]))], t, (None, None), {t: ms[t]}, bs[t]]
                except KeyError:
                    self.__s_d[j][t_] = [sys.maxint, t, (None, None), {t: ms[t]}, bs[t]]
        #
        j = self.__poi
        self.__s_d[j] = {}
        for t_ in t_tuples:
            t = t_[0]
            try:
                self.__s_d[j][t_] = \
                    [self.__dist[tuple(sorted([j, t]))], t, (None, None), {t: self.__max_stops[t]}, False]
            except KeyError:
                self.__s_d[j][t_] = [sys.maxint, t, (None, None), {t: self.__max_stops[t]}, False]
        #
        for m in range(2, len(set_c) + 1):
            #
            sets_d = [tuple(set_d) for set_d in comb(set_c, m)]
            for set_d in sets_d:
                #
                if m < len(set_c):
                    for i in self.__nodes:
                        self.__s_d[i][set_d] = [sys.maxint, None, (None, None), None, False]
                else:
                    self.__s_d[self.__poi][set_c] = [sys.maxint, None, (None, None), None, False]
                #
                sets_e = self.__create_subsets_e(set_d)
                #
                for j in self.__nodes:
                    u = sys.maxint
                    best_subsets = None
                    burnt = False
                    for set_e in sets_e:
                        set_f = tuple(sorted(list(set(set_d) - set(set_e))))
                        if len(set_f) > 0:
                            s = self.__s_d[j][set_e][0] + self.__s_d[j][set_f][0]
                        else:
                            s = self.__s_d[j][set_e][0]
                        if s < u:
                            burnt = False
                            if self.__s_d[j][set_e][4] or self.__s_d[j][set_f][4]:
                                burnt = True
                            u = s
                            best_subsets = (set_e, set_f)
                    temp_list = list(self.__nodes)
                    ms = None
                    if best_subsets is not None:
                        ms = self.__s_d[j][best_subsets[0]][3].copy()
                        ms.update(self.__s_d[j][best_subsets[1]][3])
                    if m == len(set_c) or j == self.__poi:
                        temp_list = [self.__poi]
                    else:
                        if burnt:
                            temp_list = [self.__poi, j]
                        elif ms is not None:
                            ms = {t: s - 1 for t, s in ms.items()}
                            if 0 in ms.values():
                                burnt = True
                    for i in temp_list:
                        try:
                            dist = self.__dist[tuple(sorted([i, j]))]
                        except KeyError:
                            dist = sys.maxint
                        if dist + u < self.__s_d[i][set_d][0]:
                            self.__s_d[i][set_d] = [dist + u, j, best_subsets, ms, burnt]

        # Reconstruct the Steiner by backtracking
        steiner_tree = self.__build_steiner_tree_bactracking(self.__poi, set_c)

        return steiner_tree

    '''
    '''
    @staticmethod
    def __create_subsets_e(set_):
        sets_e = [tuple([set_[0]])]
        l_set = len(set_)
        for x in range(1, l_set - 1):
            for y in comb(set_[1:], x):
                t = [set_[0]]
                t.extend(y)
                sets_e.append(tuple(t))
        return sets_e

    '''
    '''
    def __build_steiner_tree_bactracking(self, node, subset):
        steiner_tree = SuitabilityDigraph()
        next_node = self.__s_d[node][tuple(subset)][1]
        print(node, self.__s_d[node][tuple(subset)])
        # pdb.set_trace()
        if next_node is not None:
            steiner_tree.append_from_path(self.__paths[tuple(sorted([node, next_node]))], self.__graph)
        (best_e, best_f) = self.__s_d[node][tuple(subset)][2]
        # pdb.set_trace()
        steiner_branch_e = SuitabilityDigraph()
        if best_e is not None and best_e != [next_node]:
            steiner_branch_e = self.__build_steiner_tree_bactracking(next_node, best_e)
        steiner_branch_f = SuitabilityDigraph()
        if best_f is not None and best_f != [next_node] and len(best_f) > 0:
            steiner_branch_f = self.__build_steiner_tree_bactracking(next_node, best_f)
        steiner_tree.append_from_graph(steiner_branch_e)
        steiner_tree.append_from_graph(steiner_branch_f)
        return steiner_tree
