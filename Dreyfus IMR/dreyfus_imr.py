import sys
import pdb

from graph import dijkstra
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from utils import comb


class DreyfusIMR:
    def __init__(self, graph, terminals, contract_graph=True, contracted_graph=None, within_convex_hull=False,
                 dist_paths=None, nodes=None):

        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Dreyfus with IMRs algorithm only works with node-weighted graphs.")
        # Extract POI from the terminals list.
        if len(terminals) > 0:
            self.__poi = terminals[0]
        else:
            return
        # Set object variables.
        generator = SuitableNodeWeightGenerator()
        self.__original_graph = graph
        self.__terminals = terminals
        self.__contract_graph = contract_graph
        # Contracted graph...
        if contract_graph:
            if contracted_graph is not None:
                self.__graph = contracted_graph.copy()
            else:
                self.__graph = SuitabilityGraph()
                self.__graph.append_graph(graph)
                self.__graph.contract_suitable_regions(generator, excluded_nodes=terminals)
        else:
            self.__graph = SuitabilityGraph()
            self.__graph.append_graph(graph)
        #
        if nodes is not None:
            self.__nodes = list(nodes)
        else:
            if within_convex_hull:
                pass
                # self.__nodes = self.__graph.get_suitable_nodes_within_convex_set(terminals, generator, dist_paths)
            else:
                self.__nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals)
            #
            for t in terminals:
                self.__nodes.append(t)
        # print(self.__nodes)
        #
        self.__dist = {}
        self.__paths = {}
        if dist_paths is not None:
            self.__dist = dict(dist_paths[0])
            self.__paths = dict(dist_paths[1])
        else:
            self.__dist, self.__paths = self.__graph.get_dist_paths(origins=self.__nodes, destinations=self.__nodes)
        #
        self.__s_d = {}

    '''

    '''

    def steiner_tree(self, consider_terminals=False):
        #
        set_c = tuple(sorted(self.__terminals[1:]))
        t_tuples = [tuple([t]) for t in set_c]
        #
        for j in self.__nodes:
            self.__s_d[j] = {}
            for t in t_tuples:
                try:
                    self.__s_d[j][t] = [self.__dist[tuple(sorted([j, t[0]]))], t[0], (None, None)]
                except KeyError:
                    self.__s_d[j][t] = [sys.maxint, t[0], (None, None)]
        #
        for m in range(2, len(set_c)):
            #
            sets_d = [tuple(set_d) for set_d in comb(set_c, m)]
            for set_d in sets_d:
                #
                for i in self.__nodes:
                    self.__s_d[i][set_d] = [sys.maxint, None, (None, None)]
                #
                sets_e = self.__create_subsets_e(set_d)
                #
                for j in self.__nodes:
                    u = sys.maxint
                    best_subsets = None
                    for set_e in sets_e:
                        set_f = tuple(sorted(list(set(set_d) - set(set_e))))
                        if len(set_f) > 0:
                            s = self.__s_d[j][set_e][0] + self.__s_d[j][set_f][0]
                        else:
                            s = self.__s_d[j][set_e][0]
                        if s < u:
                            u = s
                            best_subsets = (set_e, set_f)
                    for i in self.__nodes:
                        try:
                            dist = self.__dist[tuple(sorted([i, j]))]
                        except KeyError:
                            dist = sys.maxint
                        if consider_terminals:
                            if dist + u < self.__s_d[i][set_d][0]:
                                self.__s_d[i][set_d] = [dist + u, j, best_subsets]
                        else:
                            if dist + u < self.__s_d[i][set_d][0] and j not in self.__terminals[1:]:
                                self.__s_d[i][set_d] = [dist + u, j, best_subsets]
        #
        sets_e = self.__create_subsets_e(set_c)
        #
        cost = sys.maxint
        if self.__poi not in self.__s_d:
            self.__s_d[self.__poi] = {set_c: [cost, None, (None, None)]}
        else:
            self.__s_d[self.__poi][set_c] = [cost, None, (None, None)]
        #
        for j in self.__nodes:
            u = sys.maxint
            best_subsets = None
            for set_e in sets_e:
                set_f = tuple(sorted(list(set(set_c) - set(set_e))))
                if len(set_f) > 0:
                    s = self.__s_d[j][set_e][0] + self.__s_d[j][set_f][0]
                else:
                    s = self.__s_d[j][set_e][0]
                if s < u:
                    u = s
                    best_subsets = (set_e, set_f)
            try:
                dist = self.__dist[tuple(sorted([self.__poi, j]))]
            except KeyError:
                dist = sys.maxint
            if consider_terminals:
                if dist + u < cost:
                    cost = dist + u
                    self.__s_d[self.__poi][set_c] = [cost, j, best_subsets]
            else:
                if dist + u < cost and j not in self.__terminals[1:]:
                    cost = dist + u
                    self.__s_d[self.__poi][set_c] = [cost, j, best_subsets]

        # Reconstruct the Steiner by backtracking
        steiner_tree = self.__build_steiner_tree_bactracking(self.__poi, set_c)

        if self.__contract_graph:
            self.__decontract_steiner_tree(steiner_tree)

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
        steiner_tree = SuitabilityGraph()
        next_node = self.__s_d[node][tuple(subset)][1]
        print(node, self.__s_d[node][tuple(subset)])
        # pdb.set_trace()
        if next_node is not None:
            steiner_tree.append_path(self.__paths[tuple(sorted([node, next_node]))], self.__graph)
        (best_e, best_f) = self.__s_d[node][tuple(subset)][2]
        # pdb.set_trace()
        steiner_branch_e = SuitabilityGraph()
        if best_e is not None and best_e != [next_node]:
            steiner_branch_e = self.__build_steiner_tree_bactracking(next_node, best_e)
        steiner_branch_f = SuitabilityGraph()
        if best_f is not None and best_f != [next_node] and len(best_f) > 0:
            steiner_branch_f = self.__build_steiner_tree_bactracking(next_node, best_f)
        steiner_tree.append_graph(steiner_branch_e)
        steiner_tree.append_graph(steiner_branch_f)
        return steiner_tree

    '''

    '''

    def __find_closest_node_to_node_within_region(self, node, region_id):
        region = self.__graph.contracted_regions[region_id][0]
        min_dist = sys.maxint
        closest_node = None
        distances, paths = dijkstra(self.__original_graph, node, region.keys())
        for n in region:
            if distances[n] < min_dist:
                closest_node = n
                min_dist = distances[n]
        return closest_node, paths[closest_node]

    '''

    '''

    def __decontract_steiner_tree(self, steiner_tree):
        regions = []
        paths = []
        trees = []
        for n in steiner_tree:
            try:
                if n in self.__graph.contracted_regions:
                    dropped_edges = steiner_tree[n][2]['dropped_edges']
                    neighbors = steiner_tree[n][1].keys()
                    new_terminals = set()
                    for b in neighbors:
                        t = dropped_edges[b]
                        new_terminals.add(t)
                        if b in self.__graph.auxiliary_nodes:
                            bb = [cc for cc in steiner_tree[b][1] if cc != n][0]
                            paths.append([t, bb])
                        else:
                            paths.append([t, b])
                    if len(new_terminals) > 1:
                        region = self.__graph.contracted_regions[n][0]
                        d = DreyfusIMR(region, list(new_terminals), contract_graph=False)
                        st = d.steiner_tree()
                        trees.append(st)
                    regions.append(n)
            except KeyError:
                pass
        for r in regions:
            del steiner_tree[r]
        for p in paths:
            steiner_tree.append_path(p, self.__original_graph)
        for st in trees:
            steiner_tree.append_graph(st)

        # for r in steiner_tree:
        #     if r in self.__graph.contracted_regions:
        #         regions.append(r)
        #         neighbors = steiner_tree[r][1].keys()
        #         new_terminals = set()
        #         for n in neighbors:
        #             closest_node_to_n, path = self.__find_closest_node_to_node_within_region(n, r)
        #             paths.append(path)
        #             new_terminals.add(closest_node_to_n)
        #             del steiner_tree[n][1][r]
        #         if len(new_terminals) > 1:
        #             region = self.__graph.contracted_regions[r][0]
        #             d = DreyfusIMR(region, list(new_terminals), contract_graph=False)
        #             st = d.steiner_tree()
        #             trees.append(st)
        # for r in regions:
        #     del steiner_tree[r]
        # for p in paths:
        #     steiner_tree.append_from_path(p, self.__original_graph)
        # for st in trees:
        #     steiner_tree.append_from_graph(st)
