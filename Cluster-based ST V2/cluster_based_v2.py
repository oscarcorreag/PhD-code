import sys

from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from dreyfus import Dreyfus
from utils import comb


class ClusterBasedV2:
    def __init__(self, graph, terminals):

        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Cluster-based algorithm only works with node-weighted graphs.")
        # Extract POI from the terminals list.
        if len(terminals) > 0:
            self.__poi = terminals[0]
        else:
            return
        #
        generator = SuitableNodeWeightGenerator()
        # Set object variables.
        self.__original_graph = graph
        self.__terminals = terminals
        self.__graph = SuitabilityDigraph()
        self.__graph.append_from_graph(graph)
        self.__graph.contract_suitable_regions(generator, excluded_nodes=terminals)
        self.__regions = self.__graph.contracted_regions
        #
        # self.__dist, self.__paths, self.__regions = self.__graph.get_dist_paths_between_regions(generator,
        #                                                                                         exc_wcr=terminals,
        #                                                                                         inc_wcp=terminals,
        #                                                                                         within_region=True)
        #
        # self.__regions = self.__graph.get_suitable_regions(generator, excluded_nodes=terminals,
        #                                                    get_border_internal_nodes=True, get_centroid_medoid=True)
        #
        self.__pseudo_nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals)
        # self.__pseudo_nodes.extend(self.__regions.keys())
        self.__pseudo_nodes.extend(self.__terminals)
        #
        self.__stats = {}
        for id_r in self.__regions:
            region = self.__regions[id_r][0]
            border_nodes = self.__regions[id_r][1]
            # self.__pseudo_nodes.extend(border_nodes)
            #
            self.__stats[id_r] = {}
            self.__stats[id_r][3] = {}
            self.__stats[id_r][4] = {}
            df = Dreyfus(region)
            for b in border_nodes:
                ecc, inc = region.steiner_n_stats(3, b, df)
                self.__stats[id_r][3][b] = (ecc, inc)
                ecc, inc = region.steiner_n_stats(4, b, df)
                self.__stats[id_r][4][b] = (ecc, inc)
        #
        self.__dist, self.__paths = self.__graph.get_dist_paths(origins=self.__pseudo_nodes,
                                                                destinations=self.__pseudo_nodes)
        #
        self.__s_d = {}

    '''
    '''

    def steiner_tree(self):
        #
        set_c = tuple(sorted(self.__terminals[1:]))
        t_tuples = [tuple([t]) for t in set_c]
        #
        for j in self.__pseudo_nodes:
            self.__s_d[j] = {}
            for t in t_tuples:
                try:
                    d = self.__dist[tuple(sorted([j, t[0]]))]
                    self.__s_d[j][t] = [Interval(d, d), t[0], (None, None), None]
                except KeyError:
                    self.__s_d[j][t] = [Interval(sys.maxint, sys.maxint), t[0], (None, None), None]
        #
        temp_list = list(self.__pseudo_nodes)
        for m in range(2, len(set_c) + 1):
            #
            sets_d = [tuple(set_d) for set_d in comb(set_c, m)]
            for set_d in sets_d:
                #
                if m < len(set_c):
                    for i in self.__pseudo_nodes:
                        self.__s_d[i][set_d] = [Interval(sys.maxint, sys.maxint), None, (None, None), None]
                else:
                    self.__s_d[self.__poi][set_c] = [Interval(sys.maxint, sys.maxint), None, (None, None), None]
                #
                sets_e = self.__create_subsets_e(set_d)
                #
                for j in self.__pseudo_nodes:
                    u = Interval(sys.maxint, sys.maxint)
                    best_subsets = best_border_nodes = None
                    for set_e in sets_e:
                        border_nodes = None
                        set_f = tuple(sorted(list(set(set_d) - set(set_e))))
                        if len(set_f) > 0:
                            s = Interval.add(self.__s_d[j][set_e][0], self.__s_d[j][set_f][0])
                            if j in self.__regions:
                                border_nodes = self.__get_border_nodes(j, set_e, set_f)
                                inner_dist = self.__get_inner_distance(j, list(border_nodes))
                                s = Interval.add(s, inner_dist)
                        else:
                            s = self.__s_d[j][set_e][0]
                        if s.inf < u.inf:
                            u = s
                            best_subsets = (set_e, set_f)
                            best_border_nodes = border_nodes
                    #
                    if m == len(set_c):
                        temp_list = [self.__poi]
                    for i in temp_list:
                        combined_id = tuple(sorted([i, j]))
                        # dist_info = self.__dist[tuple(combined_id)]
                        # dist = dist_info[0]
                        dist = self.__dist[combined_id]
                        inner_dist = Interval(0, 0)
                        border_node = None
                        #
                        if j in self.__regions:
                            dropped_edges = self.__graph[j][2]['dropped_edges']
                            path = self.__paths[combined_id]
                            if len(path) > 1:
                                if path.index(j) == len(path) - 1:
                                    adj_node = path[len(path) - 2]
                                else:
                                    adj_node = path[1]
                                border_node = dropped_edges[adj_node]
                            elif len(path) == 1 and path[0] == j:
                                pass
                            else:
                                raise (RuntimeError, "ClusterBasedV2: empty path")
                            #
                            # x = dist_info[combined_id.index(j) + 1]
                            if border_node is not None:
                                a = set(best_border_nodes)
                                a.add(border_node)
                                inner_dist = self.__get_inner_distance(j, list(a))
                        #
                        temp = Interval.add(u, inner_dist)
                        temp.shift(dist)
                        if temp.intersect(self.__s_d[i][set_d][0]):
                            print(j, self.__s_d[i][set_d][1], temp.inf, temp.sup, self.__s_d[i][set_d][0].inf,
                                  self.__s_d[i][set_d][0].sup, i)
                        if temp.inf < self.__s_d[i][set_d][0].inf and j not in self.__terminals[1:]:
                            self.__s_d[i][set_d] = [temp, j, best_subsets, border_node]

        # Reconstruct the Steiner by backtracking
        steiner_tree = self.__build_steiner_tree_bactracking(self.__poi, set_c)

        return steiner_tree

    def __get_different_next_nodes(self, node, subset):
        next_nodes = []
        next_node = self.__s_d[node][tuple(subset)][1]
        if next_node is not None and next_node != node:
            next_nodes.append(next_node)
        elif next_node == node:
            (best_e, best_f) = self.__s_d[node][tuple(subset)][2]
            if best_e is not None and best_e != [next_node]:
                next_nodes_e = self.__get_different_next_nodes(node, best_e)
                next_nodes.extend(next_nodes_e)
            if best_f is not None and best_f != [next_node] and len(best_f) > 0:
                next_nodes_f = self.__get_different_next_nodes(node, best_f)
                next_nodes.extend(next_nodes_f)
        return next_nodes

    def __get_border_nodes_subset(self, id_region, subset):
        next_nodes = self.__get_different_next_nodes(id_region, subset)
        border_nodes = set()
        dropped_edges = self.__graph[id_region][2]['dropped_edges']
        for next_node in next_nodes:
            combined_id = tuple(sorted([next_node, id_region]))
            # dist_info = self.__dist[tuple(combined_id)]
            path = self.__paths[combined_id]
            if len(path) > 1:
                if path.index(id_region) == len(path) - 1:
                    adj_node = path[len(path) - 2]
                else:
                    adj_node = path[1]
                bn = dropped_edges[adj_node]
                border_nodes.add(bn)
            elif len(path) == 1 and path[0] == id_region:
                pass
            else:
                raise (RuntimeError, "ClusterBasedV2: empty path")
                # bn = dist_info[combined_id.index(id_region) + 1]
        return border_nodes

    def __get_border_nodes(self, id_region, set_e, set_f):
        border_nodes_e = self.__get_border_nodes_subset(id_region, set_e)
        border_nodes_f = self.__get_border_nodes_subset(id_region, set_f)
        return border_nodes_e.union(border_nodes_f)

    def __get_inner_distance(self, id_region, border_nodes):
        if len(border_nodes) == 1:
            return Interval(0, 0)
        elif len(border_nodes) == 2:
            v = border_nodes[0]
            w = border_nodes[1]
            inner_dist = self.__regions[id_region][5][0][tuple(sorted([v, w]))]
            return Interval(inner_dist, inner_dist)
        # else:
        #     df = Dreyfus(self.__regions[id_region][0])
        #     st = df.steiner_tree(border_nodes)
        #     inner_dist, _ = st.calculate_costs(border_nodes)
        #     return Interval(inner_dist, inner_dist)
        elif len(border_nodes) == 3:
            inf, sup = self.__get_inf_sup(3, id_region, border_nodes)
            v = border_nodes[0]
            w = border_nodes[1]
            x = border_nodes[2]
            dd = min(self.__regions[id_region][5][0][tuple(sorted([v, w]))] +
                     self.__regions[id_region][5][0][tuple(sorted([v, x]))],
                     self.__regions[id_region][5][0][tuple(sorted([v, w]))] +
                     self.__regions[id_region][5][0][tuple(sorted([w, x]))],
                     self.__regions[id_region][5][0][tuple(sorted([v, x]))] +
                     self.__regions[id_region][5][0][tuple(sorted([w, x]))])
            if dd < sup:
                sup = dd
            #
            if sup < inf:
                inf = sup
            return Interval(inf, sup)
        elif len(border_nodes) == 4:
            inf, sup = self.__get_inf_sup(4, id_region, border_nodes)
            return Interval(inf, sup)
        else:
            raise (RuntimeError, "ClsuterBasedV2: Inner distance for more than 4 border nodes is not implemented!")

    def __get_inf_sup(self, n, id_region, border_nodes):
        l = []
        u = []
        for bn in border_nodes:
            l.append(self.__stats[id_region][n][bn][1])
            u.append(self.__stats[id_region][n][bn][0])
        return max(l), min(u)

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

    def __build_steiner_tree_bactracking(self, node, subset):
        steiner_tree = SuitabilityDigraph()
        next_node = self.__s_d[node][tuple(subset)][1]
        print(node, self.__s_d[node][tuple(subset)][0].inf, self.__s_d[node][tuple(subset)][0].sup,
              self.__s_d[node][tuple(subset)])
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


class Interval:
    def __init__(self, inf, sup):
        if round(inf - sup, 2) > 0:
            raise (RuntimeError, "Interval: Inf must be <= Sup")
        self.inf = inf
        self.sup = sup

    @staticmethod
    def smaller(interval_1, interval_2):

        if interval_1.inf < interval_2.inf and interval_1.sup <= interval_2.inf:
            return Interval(interval_1.inf, interval_1.sup)
        if interval_2.inf < interval_1.inf and interval_2.sup <= interval_1.inf:
            return Interval(interval_2.inf, interval_2.sup)

        if interval_1.inf < interval_2.inf < interval_1.sup:
            return Interval(interval_2.inf, interval_1.sup)
        if interval_2.inf < interval_1.inf < interval_2.sup:
            return Interval(interval_1.inf, interval_2.sup)

        if interval_1.inf >= interval_2.inf and interval_1.sup <= interval_2.sup:
            return Interval(interval_1.inf, interval_1.sup)
        if interval_2.inf >= interval_1.inf and interval_2.sup <= interval_1.sup:
            return Interval(interval_2.inf, interval_2.sup)

    @staticmethod
    def add(interval_1, interval_2):
        return Interval(interval_1.inf + interval_2.inf, interval_1.sup + interval_2.sup)

    def length(self):
        return self.sup - self.inf

    def shift(self, offset):
        self.inf += offset
        self.sup += offset

    def intersect(self, interval_2):
        if self.inf <= interval_2.inf < self.sup:
            return True
        if interval_2.inf <= self.inf < interval_2.sup:
            return True
