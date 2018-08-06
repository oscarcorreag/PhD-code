import sys
# import numpy as np

from utils import haversine, comb
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from canditates_list import CandidatesList
from digraph import dijkstra


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
        self.__graph = SuitabilityDigraph()
        self.__graph.append_from_graph(graph)
        self.__terminals = terminals
        self.__hot_spots = None
        self.__nodes = None
        self.__steiner_distances = {}
        self.__paths = {}
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
        # len_hot_spots = len(self.__hot_spots)
        if distances is None:
            # np.random.seed(1)
            # len_nodes = len(self.__nodes)
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

                    # for n1 in self.__nodes:
                    #     for i in range(self.__nodes.index(n1), len_nodes):
                    #         n2 = self.__nodes[i]
                    #         # rnd = np.random.ranf()
                    #         # if rnd <= 0.1:
                    #         #     dist, paths = dijkstra(self.__graph, n1, [n2], consider_node_weights=False)
                    #         #     try:
                    #         #         distance = dist[n2]
                    #         #     except KeyError:
                    #         #         distance = sys.maxint
                    #         #     self.__distances[tuple(sorted([n1, n2]))] = (distance, 'N')
                    #         # else:
                    #         distance = calculate_distance(self.__graph[n1][2]['lat'], self.__graph[n1][2]['lon'],
                    #                                       self.__graph[n2][2]['lat'], self.__graph[n2][2]['lon'])
                    #         self.__distances[tuple(sorted([n1, n2]))] = (distance, 'E')
        else:
            self.__distances = dict(distances)

    '''
    '''

    def steiner_tree(self, history_length=10, consider_terminals=False):
        #
        set_c = sorted(self.__terminals[1:])
        #
        for j in self.__nodes:
            self.__steiner_distances[j] = {}
            for t in set_c:
                # self.__steiner_distances[j][tuple([t])] = CandidatesList(history_length)
                distance, d_type = self.__distances[tuple(sorted([j, t]))]
                # self.__steiner_distances[j][tuple([t])].append([distance, t, (None, None), distance, 0, d_type])
                self.__steiner_distances[j][tuple([t])] = [distance, 0, distance, t, (None, None), d_type, d_type,
                                                           d_type, d_type]
        #
        for m in range(2, len(set_c)):
            #
            for set_d in comb(set_c, m):
                candidates = CandidatesList(history_length)
                for i in self.__nodes:
                    self.__steiner_distances[i][tuple(set_d)] = [sys.maxint, 0, sys.maxint, None, (None, None), None,
                                                                 None, None, None]
                    # self.__steiner_distances[i][tuple(set_d)] = CandidatesList(history_length)
                #
                sets_e = [[set_d[0]]]
                for x in range(1, m - 1):
                    for y in comb(set_d[1:], x):
                        t = [set_d[0]]
                        t.extend(y)
                        sets_e.append(t)
                #
                # Do it with nodes j \in best hotspots for subsets of D
                for j in self.__nodes:
                    u = sys.maxint
                    best_subsets = None
                    d_types = None
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
                            d_types = (self.__steiner_distances[j][tuple(set_e)][5],
                                       self.__steiner_distances[j][tuple(set_f)][5])
                    for i in self.__nodes:
                        try:
                            dist, d_type = self.__distances[tuple(sorted([i, j]))]
                        except KeyError:
                            dist = sys.maxint
                            d_type = 'N'
                        if consider_terminals:
                            cost = dist + u
                            if cost < self.__steiner_distances[i][tuple(set_d)][0]:
                                dd_type = 'E'
                                if d_type == 'N' and d_types[0] == 'N' and d_types[1] == 'N':
                                    dd_type = 'N'
                                self.__steiner_distances[i][tuple(set_d)] = [cost, u, dist, j, best_subsets, dd_type,
                                                                             d_type, d_types[0], d_types[1]]
                                dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                                candidates.append(
                                    [dist_to_poi + cost, cost, dist, i, j, dd_type, d_type, d_types[0], d_types[1],
                                     best_subsets])
                        else:
                            cost = dist + u
                            if cost < self.__steiner_distances[i][tuple(set_d)][0] and j not in self.__terminals:
                                dd_type = 'E'
                                if d_type == 'N' and d_types[0] == 'N' and d_types[1] == 'N':
                                    dd_type = 'N'
                                self.__steiner_distances[i][tuple(set_d)] = [cost, u, dist, j, best_subsets, dd_type,
                                                                             d_type, d_types[0], d_types[1]]
                                dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                                candidates.append(
                                    [dist_to_poi + cost, cost, dist, i, j, dd_type, d_type, d_types[0], d_types[1],
                                     best_subsets])

                # which is the best node for steiner tree between terminals in D and POI
                # pdb.set_trace()
                print('-------------------------------------------------------')
                print(set_d)
                print('-------------------------------------------------------')
                print(candidates)
                print('-------------------------------------------------------')
                self.__stabilize_candidates_set(candidates, set_d)

        sets_e = [[set_c[0]]]
        for x in range(1, len(set_c) - 1):
            for y in comb(set_c[1:], x):
                t = [set_c[0]]
                t.extend(y)
                sets_e.append(t)
        #
        cost = sys.maxint
        candidates = CandidatesList(history_length)
        if self.__poi not in self.__steiner_distances:
            self.__steiner_distances[self.__poi] = {
                tuple(set_c): [cost, 0, cost, None, (None, None), None, None, None, None]}
        else:
            self.__steiner_distances[self.__poi][tuple(set_c)] = [cost, 0, cost, None, (None, None), None,
                                                                  None, None, None]
        #
        for j in self.__nodes:
            u = sys.maxint
            best_subsets = None
            d_types = None
            for set_e in sets_e:
                set_f = sorted(list(set(set_c) - set(set_e)))
                if len(set_f) > 0:
                    s = self.__steiner_distances[j][tuple(set_e)][0] + \
                        self.__steiner_distances[j][tuple(set_f)][0]
                else:
                    s = self.__steiner_distances[j][tuple(set_e)][0]
                if s < u:
                    u = s
                    best_subsets = (set_e, set_f)
                    d_types = (self.__steiner_distances[j][tuple(set_e)][5],
                               self.__steiner_distances[j][tuple(set_f)][5])
            try:
                dist, d_type = self.__distances[tuple(sorted([self.__poi, j]))]
            except KeyError:
                dist = sys.maxint
                d_type = 'N'
            if consider_terminals:
                if dist + u < cost:
                    dd_type = 'E'
                    if d_type == 'N' and d_types[0] == 'N' and d_types[1] == 'N':
                        dd_type = 'N'
                    cost = dist + u
                    self.__steiner_distances[self.__poi][tuple(set_c)] = [cost, u, dist, j, best_subsets, dd_type,
                                                                          d_type, d_types[0], d_types[1]]
                    candidates.append(
                        [dist + cost, cost, dist, self.__poi, j, dd_type, d_type, d_types[0], d_types[1], best_subsets])
            else:
                if dist + u < cost and j not in self.__terminals:
                    dd_type = 'E'
                    if d_type == 'N' and d_types[0] == 'N' and d_types[1] == 'N':
                        dd_type = 'N'
                    cost = dist + u
                    self.__steiner_distances[self.__poi][tuple(set_c)] = [cost, u, dist, j, best_subsets, dd_type,
                                                                          d_type, d_types[0], d_types[1]]
                    candidates.append(
                        [dist + cost, cost, dist, self.__poi, j, dd_type, d_type, d_types[0], d_types[1], best_subsets])

        # pdb.set_trace()
        print('-------------------------------------------------------')
        print(set_c)
        print('-------------------------------------------------------')
        print(candidates)
        print('-------------------------------------------------------')
        self.__stabilize_candidates_set(candidates, set_c)

        # #
        # while True:
        #     delta_cost = self.__steinerify(self.__poi, set_c)
        #     if delta_cost == 0:
        #         break
        #
        # Reconstruct the Steiner by backtracking
        steiner_tree = self.__build_steiner_tree_bactracking(self.__poi, set_c)
        #
        return steiner_tree

    def __stabilize_candidates_set(self, candidates, subset):
        candidates.sort()
        candidate = candidates[0]
        while candidate[5] == 'E':
            d_type_1 = candidate[6]
            d_type_2 = candidate[7]
            d_type_3 = candidate[8]
            n1 = candidate[3]
            n2 = candidate[4]
            # pdb.set_trace()
            if d_type_1 == 'E' and d_type_2 == 'N' and d_type_3 == 'N':
                dist_poi_and_cost = candidate[0]
                cost = candidate[1]
                dist = candidate[2]
                if self.__distances[tuple(sorted([n1, n2]))][1] == 'N':
                    dist_n2 = self.__distances[tuple(sorted([n1, n2]))][0]
                else:
                    distances, _ = dijkstra(self.__graph, n1, [n2])
                    try:
                        dist_n2 = distances[n2]
                    except KeyError:
                        print("Distance couldn't be found between:", n1, n2)
                        break

                self.__steiner_distances[n1][tuple(subset)][0] = cost - dist + dist_n2
                self.__steiner_distances[n1][tuple(subset)][2] = dist_n2
                self.__steiner_distances[n1][tuple(subset)][5] = 'N'
                self.__steiner_distances[n1][tuple(subset)][6] = 'N'

                candidates[0][0] = dist_poi_and_cost - dist + dist_n2
                candidates[0][2] = dist_n2
                candidates[0][5] = 'N'
                candidates[0][6] = 'N'

                candidates.sort()
                candidate = candidates[0]

            elif not(d_type_1 == 'N' and d_type_2 == 'N' and d_type_3 == 'N'):
                # pdb.set_trace()
                best_e, best_f = candidate[9]

                print('----BEST E----')
                print(self.__steiner_distances[n2][tuple(best_e)])

                # hold_e = False
                # hold_f = False

                j_e = self.__steiner_distances[n2][tuple(best_e)][3]
                d_typ_1_e = self.__steiner_distances[n2][tuple(best_e)][6]
                d_typ_2_e = self.__steiner_distances[n2][tuple(best_e)][7]
                d_typ_3_e = self.__steiner_distances[n2][tuple(best_e)][8]

                if d_typ_1_e == 'E' and d_typ_2_e == 'N' and d_typ_3_e == 'N':
                    if self.__distances[tuple(sorted([n2, j_e]))][1] == 'N':
                        dist_j_e = self.__distances[tuple(sorted([n2, j_e]))][0]
                    else:
                        distances, _ = dijkstra(self.__graph, n2, [j_e])
                        try:
                            dist_j_e = distances[j_e]
                        except KeyError:
                            break

                    u_e = self.__steiner_distances[n2][tuple(best_e)][1]
                    self.__steiner_distances[n2][tuple(best_e)][0] = u_e + dist_j_e
                    self.__steiner_distances[n2][tuple(best_e)][2] = dist_j_e
                    self.__steiner_distances[n2][tuple(best_e)][5] = 'N'
                    self.__steiner_distances[n2][tuple(best_e)][6] = 'N'

                    hold_e = True

                elif d_typ_1_e == 'N' and d_typ_2_e == 'N' and d_typ_3_e == 'N':
                    hold_e = True
                else:
                    print('Bad news!', n2, j_e, best_e)
                    break

                print('----BEST F----')
                print(self.__steiner_distances[n2][tuple(best_f)])

                j_f = self.__steiner_distances[n2][tuple(best_f)][3]
                d_typ_1_f = self.__steiner_distances[n2][tuple(best_f)][6]
                d_typ_2_f = self.__steiner_distances[n2][tuple(best_f)][7]
                d_typ_3_f = self.__steiner_distances[n2][tuple(best_f)][8]

                if d_typ_1_f == 'E' and d_typ_2_f == 'N' and d_typ_3_f == 'N':
                    if self.__distances[tuple(sorted([n2, j_f]))][1] == 'N':
                        dist_j_f = self.__distances[tuple(sorted([n2, j_f]))][0]
                    else:
                        distances, _ = dijkstra(self.__graph, n2, [j_f])
                        try:
                            dist_j_f = distances[j_f]
                        except KeyError:
                            break

                    u_f = self.__steiner_distances[n2][tuple(best_f)][1]
                    self.__steiner_distances[n2][tuple(best_f)][0] = u_f + dist_j_f
                    self.__steiner_distances[n2][tuple(best_f)][2] = dist_j_f
                    self.__steiner_distances[n2][tuple(best_f)][5] = 'N'
                    self.__steiner_distances[n2][tuple(best_f)][6] = 'N'

                    hold_f = True

                elif d_typ_1_f == 'N' and d_typ_2_f == 'N' and d_typ_3_f == 'N':
                    hold_f = True
                else:
                    print('Bad news!', n2, j_f, best_f)
                    break

                # Update every node that is pointing to n2
                if hold_e and hold_f:
                    new_u = self.__steiner_distances[n2][tuple(best_e)][0] + \
                            self.__steiner_distances[n2][tuple(best_f)][0]
                    for i in self.__nodes:
                        if self.__steiner_distances[i][tuple(subset)][3] == n2 and \
                                        self.__steiner_distances[i][tuple(subset)][4][0] == best_e and \
                                        self.__steiner_distances[i][tuple(subset)][4][1] == best_f:
                            # pdb.set_trace()
                            dist = self.__steiner_distances[i][tuple(subset)][2]
                            self.__steiner_distances[i][tuple(subset)][0] = dist + new_u
                            self.__steiner_distances[i][tuple(subset)][1] = new_u
                            self.__steiner_distances[i][tuple(subset)][7] = 'N'
                            self.__steiner_distances[i][tuple(subset)][8] = 'N'

                    # Update candidates
                    for i in range(len(candidates)):
                        c = candidates[i]
                        if c[3] == n1 and c[4] == n2 and candidate[9][0] == best_e and candidate[9][1] == best_f:
                            # pdb.set_trace()
                            dist_poi_and_cost = candidates[i][0]
                            cost = candidates[i][1]
                            candidates[i][0] = dist_poi_and_cost - cost + new_u
                            candidates[i][1] = new_u
                            candidates[i][7] = 'N'
                            candidates[i][8] = 'N'

            elif d_type_1 == 'N' and d_type_2 == 'N' and d_type_3 == 'N':
                candidates[0][5] = 'N'

        print(candidates)

    '''
    '''

    def __steinerify(self, parent_node, subset):

        # pdb.set_trace()

        # child_node = self.__steiner_distances[parent_node][tuple(subset)][0][1]
        initial_cost = self.__steiner_distances[parent_node][tuple(subset)][0][0]
        self.__stabilize_children(parent_node, subset)
        delta_cost = self.__steiner_distances[parent_node][tuple(subset)][0][0] - initial_cost
        new_child_node = self.__steiner_distances[parent_node][tuple(subset)][0][1]
        # if parent_node != self.__poi and (child_node != new_child_node or delta_cost > 0):
        #     if delta_cost < 0:
        #         delta_cost = 0
        #     return delta_cost
        if parent_node != self.__poi and delta_cost > 0:
            return delta_cost

        best_e, best_f = self.__steiner_distances[parent_node][tuple(subset)][0][2]
        delta_cost_e = delta_cost_f = 0
        if best_e is not None and best_e != [new_child_node]:
            delta_cost_e = self.__steinerify(new_child_node, best_e)
        if best_f is not None and best_f != [new_child_node] and len(best_f) > 0:
            delta_cost_f = self.__steinerify(new_child_node, best_f)

        self.__steiner_distances[parent_node][tuple(subset)][0][4] += delta_cost_e + delta_cost_f  # Update u
        dist = self.__steiner_distances[parent_node][tuple(subset)][0][3]
        u = self.__steiner_distances[parent_node][tuple(subset)][0][4]
        self.__steiner_distances[parent_node][tuple(subset)][0][0] = dist + u  # Update total cost

        if delta_cost_e + delta_cost_f > 0:
            return delta_cost_e + delta_cost_f

        return 0

    '''
    '''

    def __stabilize_children(self, parent_node, subset):
        self.__steiner_distances[parent_node][tuple(subset)].sort()
        child = self.__steiner_distances[parent_node][tuple(subset)][0]
        while child[5] == 'E':
            child_node = child[1]
            distances, paths = dijkstra(self.__graph, parent_node, [child_node])
            # for k, v in distances.items():
            #     self.__distances[tuple(sorted([parent_node, k]))] = (v, 'N')
            # for k, v in paths.items():
            #     self.__paths[tuple(sorted([parent_node, k]))] = v
            # try:
            #     self.__paths[tuple(sorted([parent_node, child_node]))] = paths[child_node]
            # except KeyError:
            #     pass
            #     # print("KeyError!")
            try:
                # Update total cost of the parent node for this candidate child.
                self.__steiner_distances[parent_node][tuple(subset)][0][0] = child[4] + distances[child_node]
                # Update distance between the parent and this candidate child.
                self.__steiner_distances[parent_node][tuple(subset)][0][3] = distances[child_node]
            except KeyError:
                self.__steiner_distances[parent_node][tuple(subset)][0][0] = sys.maxint
                self.__steiner_distances[parent_node][tuple(subset)][0][3] = sys.maxint
            # Advise the distance between nodes is a network distance.
            self.__steiner_distances[parent_node][tuple(subset)][0][5] = 'N'
            # Sort the candidates list to check if priorities have changed.
            self.__steiner_distances[parent_node][tuple(subset)].sort()
            # Retrieve new best candidate.
            child = self.__steiner_distances[parent_node][tuple(subset)][0]

    '''
    '''

    def __build_steiner_tree_bactracking(self, node, subset):
        steiner_tree = SuitabilityDigraph()
        next_node = self.__steiner_distances[node][tuple(subset)][3]
        # pdb.set_trace()
        if next_node is not None:
            try:
                steiner_tree.append_from_path(self.__paths[tuple(sorted([node, next_node]))], self.__graph)
            except KeyError:
                _, paths = dijkstra(self.__graph, node, [next_node])
                steiner_tree.append_from_path(paths[next_node], self.__graph)
        (best_e, best_f) = self.__steiner_distances[node][tuple(subset)][4]
        steiner_branch_e = SuitabilityDigraph()
        if best_e is not None and best_e != [next_node]:
            steiner_branch_e = self.__build_steiner_tree_bactracking(next_node, best_e)
        steiner_branch_f = SuitabilityDigraph()
        if best_f is not None and best_f != [next_node] and len(best_f) > 0:
            steiner_branch_f = self.__build_steiner_tree_bactracking(next_node, best_f)
        steiner_tree.append_from_graph(steiner_branch_e)
        steiner_tree.append_from_graph(steiner_branch_f)
        return steiner_tree
