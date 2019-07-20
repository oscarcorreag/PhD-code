import sys

from canditates_list import CandidatesList
from graph import dijkstra
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from utils import haversine, comb


class LazySteinerTree:
    def __init__(self, graph, terminals, hot_spots=None, generator=None, distances=None):
        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Lazy Steiner Tree only works with node-weighted graphs.")
        # Extract POI from the terminals list.
        if len(terminals) > 0:
            self.__poi = terminals[0]
        else:
            return
        # Set object variables.
        self.__graph = SuitabilityGraph()
        self.__graph.append_graph(graph)
        self.__terminals = terminals
        self.__hot_spots = None
        self.__nodes = None
        self.__s_d = {}
        self.__paths = {}
        self.__refs = {}
        # Set hot spots.
        if hot_spots is None:
            if generator is None:
                generator = SuitableNodeWeightGenerator()
            self.__hot_spots = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals)
        else:
            self.__hot_spots = list(hot_spots)
        # Set nodes = hot spots + terminals.
        self.__nodes = list(self.__hot_spots)
        for t in terminals:
            self.__nodes.append(t)
        # Set distances.
        if distances is None:
            len_hot_spots = len(self.__hot_spots)
            self.__distances = {}
            for t in self.__terminals:
                dist, paths = dijkstra(self.__graph, t, self.__nodes)
                for n in self.__nodes:
                    try:
                        self.__distances[tuple(sorted([t, n]))] = (dist[n], 'N')
                        self.__paths[tuple(sorted([t, n]))] = paths[n]
                    except KeyError:
                        self.__distances[tuple(sorted([t, n]))] = (sys.maxint, 'N')
                        self.__paths[tuple(sorted([t, n]))] = []
            for h1 in self.__hot_spots:
                for i in range(self.__hot_spots.index(h1), len_hot_spots):
                    h2 = self.__hot_spots[i]
                    distance = 0
                    d_type = 'E'
                    if h1 == h2:
                        d_type = 'N'
                    else:
                        distance = haversine(self.__graph[h1][2]['lat'], self.__graph[h1][2]['lon'],
                                             self.__graph[h2][2]['lat'], self.__graph[h2][2]['lon'])
                    self.__distances[tuple(sorted([h1, h2]))] = (distance, d_type)
        else:
            self.__distances = dict(distances)

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

    def steiner_tree(self, h_l_sd=20, h_l_hot_spots=3, consider_terminals=False):
        #
        set_c = tuple(sorted(self.__terminals[1:]))
        t_tuples = [tuple([t]) for t in set_c]
        #
        for j in self.__nodes:
            self.__s_d[j] = {}
            for t in t_tuples:
                dist, d_t = self.__distances[tuple(sorted([j, t[0]]))]
                self.__s_d[j][t] = [[dist, 0, dist, t[0], (None, None), d_t, d_t, d_t, d_t, 0]]
        #
        for m in range(2, len(set_c)):
            #
            sets_d = [tuple(set_d) for set_d in comb(set_c, m)]
            for set_d in sets_d:
                # target_hot_spots = CandidatesList(h_l_hot_spots)
                for i in self.__nodes:
                    self.__s_d[i][set_d] = CandidatesList(h_l_sd)
                #
                sets_e = self.__create_subsets_e(set_d)
                #
                for j in self.__nodes:
                    u = sys.maxint
                    sets_e_f = None
                    d_ts = None
                    for set_e in sets_e:
                        set_f = tuple(sorted(list(set(set_d) - set(set_e))))
                        if len(set_f) > 0:
                            s = self.__s_d[j][set_e][0][0] + self.__s_d[j][set_f][0][0]
                        else:
                            s = self.__s_d[j][set_e][0][0]
                        if s < u:
                            u = s
                            sets_e_f = (set_e, set_f)
                            d_ts = (self.__s_d[j][set_e][0][5], self.__s_d[j][set_f][0][5])
                    for i in self.__nodes:
                        try:
                            dist, d_t = self.__distances[tuple(sorted([i, j]))]
                        except KeyError:
                            dist = sys.maxint
                            d_t = 'N'
                        if consider_terminals:
                            cost = dist + u
                            # if cost < self.__steiner_distances[i][set_d][0][0]:
                            if cost < sys.maxint:
                                dd_t = 'E'
                                if d_t == 'N' and d_ts[0] == 'N' and d_ts[1] == 'N':
                                    dd_t = 'N'
                                self.__s_d[i][set_d].append([cost, u, dist, j, sets_e_f, dd_t, d_t, d_ts[0], d_ts[1], 0])
                                # dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                                # target_hot_spots.append([dist_to_poi + cost, i])
                        else:
                            cost = dist + u
                            # if cost < self.__steiner_distances[i][set_d][0][0] and j not in self.__terminals:
                            if j not in self.__terminals and cost < sys.maxint:
                                dd_t = 'E'
                                if d_t == 'N' and d_ts[0] == 'N' and d_ts[1] == 'N':
                                    dd_t = 'N'
                                self.__s_d[i][set_d].append([cost, u, dist, j, sets_e_f, dd_t, d_t, d_ts[0], d_ts[1], 0])
                                # dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                                # target_hot_spots.append([dist_to_poi + cost, i])

                target_hot_spots = CandidatesList(h_l_hot_spots)
                for i in self.__nodes:
                    cost = self.__s_d[i][set_d][0][0]
                    j = self.__s_d[i][set_d][0][3]
                    set_e, set_f = self.__s_d[i][set_d][0][4]
                    dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                    target_hot_spots.append([dist_to_poi + cost, i])
                    if j in self.__refs:
                        if set_e in self.__refs[j]:
                            self.__refs[j][set_e].add((i, set_d))
                        else:
                            self.__refs[j][set_e] = {(i, set_d)}
                        if set_f in self.__refs[j]:
                            self.__refs[j][set_f].add((i, set_d))
                        else:
                            self.__refs[j][set_f] = {(i, set_d)}
                    else:
                        self.__refs[j] = {set_e: {(i, set_d)}, set_f: {(i, set_d)}}

                # which is the best node for steiner tree between terminals in D and POI

                # print('-------------------------------------------------------')
                # print(set_d)
                # print('-------------------------------------------------------')
                # self.__print_target_hot_spots(target_hot_spots, set_d)
                # print('-------------------------------------------------------')
                # pdb.set_trace()
                self.__correct_i_s(target_hot_spots, set_d)
                self.__print_target_hot_spots(target_hot_spots, set_d)
                # print('-------------------------------------------------------')
        #
        sets_e = self.__create_subsets_e(set_c)
        #
        # cost = sys.maxint
        target_hot_spots = CandidatesList(h_l_hot_spots)
        self.__s_d[self.__poi][set_c] = CandidatesList(h_l_sd)
        for j in self.__nodes:
            u = sys.maxint
            sets_e_f = None
            d_ts = None
            for set_e in sets_e:
                set_f = tuple(sorted(list(set(set_c) - set(set_e))))
                if len(set_f) > 0:
                    s = self.__s_d[j][set_e][0][0] + self.__s_d[j][set_f][0][0]
                else:
                    s = self.__s_d[j][set_e][0][0]
                if s < u:
                    u = s
                    sets_e_f = (set_e, set_f)
                    d_ts = (self.__s_d[j][set_e][0][5], self.__s_d[j][set_f][0][5])
            try:
                dist, d_t = self.__distances[tuple(sorted([self.__poi, j]))]
            except KeyError:
                dist = sys.maxint
                d_t = 'N'
            if consider_terminals:
                # if dist + u < cost:
                dd_t = 'E'
                if d_t == 'N' and d_ts[0] == 'N' and d_ts[1] == 'N':
                    dd_t = 'N'
                cost = dist + u
                if cost < sys.maxint:
                    self.__s_d[self.__poi][set_c].append([cost, u, dist, j, sets_e_f, dd_t, d_t, d_ts[0], d_ts[1], 0])
                    target_hot_spots.append([cost, self.__poi])
            else:
                cost = dist + u
                if j not in self.__terminals and cost < sys.maxint:
                    dd_t = 'E'
                    if d_t == 'N' and d_ts[0] == 'N' and d_ts[1] == 'N':
                        dd_t = 'N'
                    self.__s_d[self.__poi][set_c].append([cost, u, dist, j, sets_e_f, dd_t, d_t, d_ts[0], d_ts[1], 0])
                    target_hot_spots.append([cost, self.__poi])

        j = self.__s_d[self.__poi][set_c][0][3]
        set_e, set_f = self.__s_d[self.__poi][set_c][0][4]
        if j in self.__refs:
            if set_e in self.__refs[j]:
                self.__refs[j][set_e].add((self.__poi, set_c))
            else:
                self.__refs[j][set_e] = {(self.__poi, set_c)}
            if set_f in self.__refs[j]:
                self.__refs[j][set_f].add((self.__poi, set_c))
            else:
                self.__refs[j][set_f] = {(self.__poi, set_c)}
        else:
            self.__refs[j] = {set_e: {(self.__poi, set_c)}, set_f: {(self.__poi, set_c)}}

        # print('-------------------------------------------------------')
        # print(set_c)
        # print('-------------------------------------------------------')
        # self.__print_target_hotspots(target_hot_spots, set_c)
        # print('-------------------------------------------------------')
        # pdb.set_trace()
        # self.__print_target_hot_spots(target_hot_spots, set_c)
        # pdb.set_trace()
        self.__correct_i_s(target_hot_spots, set_c)
        # print('-------------------------------------------------------')

        # #
        # while True:
        #     delta_cost = self.__steinerify(self.__poi, set_c)
        #     if delta_cost == 0:
        #         break
        #
        # Reconstruct the Steiner by backtracking
        steiner_tree = self.__build_steiner_tree(self.__poi, set_c)
        #
        return steiner_tree

    # def __correct_i_s(self, target_hot_spots, subset):
    #     while len(target_hot_spots) > 0:
    #         # pdb.set_trace()
    #         i = target_hot_spots[0][1]
    #         dd_t = self.__s_d[i][subset][0][5]
    #         if dd_t == 'E':
    #             self.__correct_j_s(i, subset)
    #         target_hot_spots.pop(0)

    def __correct_i_s(self, target_hot_spots, subset):
        if len(target_hot_spots) > 0:
            #
            target_hot_spots.sort()
            i = target_hot_spots[0][1]
            dd_t = self.__s_d[i][subset][0][5]
            #
            while dd_t == 'E':
                #
                delta = self.__correct_j_s(i, subset)
                target_hot_spots[0][0] += delta
                #
                target_hot_spots.sort()
                i = target_hot_spots[0][1]
                dd_t = self.__s_d[i][subset][0][5]

    def __propagate(self, delta, j, subset):
        try:
            for i, subset_i in self.__refs[j][subset]:
                # if i == 552618963:
                #     print(subset_i, self.__s_d[i][subset_i][0][0], delta, j, subset)
                self.__s_d[i][subset_i][0][0] += delta
                self.__s_d[i][subset_i][0][1] += delta
                self.__propagate(delta, i, subset_i)
        except KeyError:
            pass

    def __correct_j_s(self, i, subset):
        #
        # self.__s_d[i][subset].sort()
        j = self.__s_d[i][subset][0][3]
        old_j = j
        old_set_e, old_set_f = self.__s_d[i][subset][0][4]
        dd_t = self.__s_d[i][subset][0][5]
        count = 0
        #
        while dd_t == 'E':
            # ----------------------------------------------------------------------------------------------------------
            delta_dist = 0
            d_t_1 = self.__s_d[i][subset][0][6]
            if d_t_1 == 'E':
                #
                i_j_tuple = tuple(sorted([i, j]))
                if self.__distances[i_j_tuple][1] == 'N':
                    dist = self.__distances[i_j_tuple][0]
                else:
                    try:
                        distances, _ = dijkstra(self.__graph, i, [j])
                        dist = distances[j]
                        self.__distances[i_j_tuple] = (dist, 'N')
                    except KeyError:
                        dist = sys.maxint
                old_dist = self.__s_d[i][subset][0][2]
                delta_dist = dist - old_dist
                #
                self.__s_d[i][subset][0][0] += delta_dist
                self.__s_d[i][subset][0][2] = dist
                self.__s_d[i][subset][0][6] = 'N'
            # ----------------------------------------------------------------------------------------------------------
            delta_u = 0
            d_t_2 = self.__s_d[i][subset][0][7]
            d_t_3 = self.__s_d[i][subset][0][8]
            if d_t_2 == 'E' or d_t_3 == 'E':
                # if i == 3073194802L and subset == (30287961, 313278858, 1011956802, 1655220587):
                #     pdb.set_trace()
                u, set_e, set_f, delta_e, delta_f = self.__correct_e_f(j, subset)
                self.__s_d[i][subset][0][4] = (set_e, set_f)
                delta_u = delta_e + delta_f
                #
                if u != self.__s_d[i][subset][0][1]:
                    delta_u = u - self.__s_d[i][subset][0][1]
                    self.__s_d[i][subset][0][0] += delta_u
                    self.__s_d[i][subset][0][1] += delta_u
                self.__s_d[i][subset][0][7] = 'N'
                self.__s_d[i][subset][0][8] = 'N'
            # ----------------------------------------------------------------------------------------------------------
            d_t_1 = self.__s_d[i][subset][0][6]
            d_t_2 = self.__s_d[i][subset][0][7]
            d_t_3 = self.__s_d[i][subset][0][8]
            if d_t_1 == 'N' and d_t_2 == 'N' and d_t_3 == 'N':
                self.__s_d[i][subset][0][5] = 'N'
            #
            delta = delta_dist + delta_u
            self.__s_d[i][subset][0][9] = delta
            if delta > 0 and count == 0:
                self.__propagate(delta, i, subset)
                if self.__s_d[i][subset][0][5] == 'N':
                    try:
                        del self.__refs[i][subset]
                    except KeyError:
                        pass
            count += 1
            #
            self.__s_d[i][subset].sort()
            j = self.__s_d[i][subset][0][3]
            dd_t = self.__s_d[i][subset][0][5]

        # Update refs
        j = self.__s_d[i][subset][0][3]
        set_e, set_f = self.__s_d[i][subset][0][4]
        if j != old_j or set_e != old_set_e or set_f != old_set_f:
            #
            try:
                self.__refs[old_j][old_set_e].remove((i, subset))
                self.__refs[old_j][old_set_f].remove((i, subset))
            except KeyError:
                pass
            #
            if j in self.__refs:
                if set_e in self.__refs[j]:
                    self.__refs[j][set_e].add((i, subset))
                else:
                    self.__refs[j][set_e] = {(i, subset)}
                if set_f in self.__refs[j]:
                    self.__refs[j][set_f].add((i, subset))
                else:
                    self.__refs[j][set_f] = {(i, subset)}
            else:
                self.__refs[j] = {set_e: {(i, subset)}, set_f: {(i, subset)}}

        return self.__s_d[i][subset][0][9]

    def __create_subsets_e_f(self, j, set_):
        subsets_e_f = []
        sets_e = self.__create_subsets_e(set_)
        for set_e in sets_e:
            set_f = tuple(sorted(list(set(set_) - set(set_e))))
            if len(set_f) > 0:
                s = self.__s_d[j][set_e][0][0] + self.__s_d[j][set_f][0][0]
            else:
                s = self.__s_d[j][set_e][0][0]
            subsets_e_f.append([s, set_e, set_f, 0, 0])
        return subsets_e_f

    def __correct_e_f(self, j, set_):
        #
        subsets_e_f = self.__create_subsets_e_f(j, set_)
        #
        subsets_e_f.sort()
        set_e = subsets_e_f[0][1]
        set_f = subsets_e_f[0][2]
        dd_t_e = self.__s_d[j][set_e][0][5]
        dd_t_f = self.__s_d[j][set_f][0][5]
        while dd_t_e == 'E' or dd_t_f == 'E':
            #
            delta_e = self.__correct_j_s(j, set_e)
            delta_f = self.__correct_j_s(j, set_f)
            subsets_e_f[0][0] += delta_e + delta_f
            subsets_e_f[0][3] = delta_e
            subsets_e_f[0][4] = delta_f
            #
            subsets_e_f.sort()
            set_e = subsets_e_f[0][1]
            set_f = subsets_e_f[0][2]
            dd_t_e = self.__s_d[j][set_e][0][5]
            dd_t_f = self.__s_d[j][set_f][0][5]
        return subsets_e_f[0]

    def __print_target_hot_spots(self, target_hot_spots, subset):
        for th in target_hot_spots:
            dist_to_poi = th[0]
            i = th[1]
            j = self.__s_d[i][subset][0][3]
            dd_type = self.__s_d[i][subset][0][5]
            d_type_1 = self.__s_d[i][subset][0][6]
            d_type_2 = self.__s_d[i][subset][0][7]
            d_type_3 = self.__s_d[i][subset][0][8]
            print(dist_to_poi, i, j, dd_type, d_type_1, d_type_2, d_type_3)

    def __build_steiner_tree(self, node, subset):
        steiner_tree = SuitabilityGraph()
        next_node = self.__s_d[node][subset][0][3]
        print(node, self.__s_d[node][subset])
        # pdb.set_trace()
        if next_node is not None:
            try:
                steiner_tree.append_path(self.__paths[tuple(sorted([node, next_node]))], self.__graph)
            except KeyError:
                _, paths = dijkstra(self.__graph, node, [next_node])
                steiner_tree.append_path(paths[next_node], self.__graph)
        (set_e, set_f) = self.__s_d[node][subset][0][4]
        steiner_branch_e = SuitabilityGraph()
        if set_e is not None and set_e != [next_node]:
            steiner_branch_e = self.__build_steiner_tree(next_node, set_e)
        steiner_branch_f = SuitabilityGraph()
        if set_f is not None and set_f != [next_node] and len(set_f) > 0:
            steiner_branch_f = self.__build_steiner_tree(next_node, set_f)
        steiner_tree.append_graph(steiner_branch_e)
        steiner_tree.append_graph(steiner_branch_f)
        return steiner_tree
