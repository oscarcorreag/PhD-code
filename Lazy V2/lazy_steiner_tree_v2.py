import sys
import pdb

from utils import haversine, comb
from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from graph import dijkstra


class LazySteinerTreeV2:
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

    def steiner_tree(self, qi=10, consider_terminals=False):
        #
        set_c = sorted(self.__terminals[1:])
        #
        for j in self.__nodes:
            self.__steiner_distances[j] = {}
            for t in set_c:
                distance, d_type = self.__distances[tuple(sorted([j, t]))]
                self.__steiner_distances[j][tuple([t])] = [distance, 0, distance, t, (None, None), d_type, d_type,
                                                           d_type, d_type]
        #
        for m in range(2, len(set_c)):
            #
            sets_d = [tuple(c) for c in comb(set_c, m)]
            for set_d in sets_d:
                for i in self.__nodes:
                    self.__steiner_distances[i][set_d] = [sys.maxint, 0, sys.maxint, None, (None, None), None, None,
                                                          None, None]
                #
                sets_e = [tuple([set_d[0]])]
                for x in range(1, m - 1):
                    for y in comb(set_d[1:], x):
                        t = [set_d[0]]
                        t.extend(y)
                        sets_e.append(tuple(t))
                #
                j_subsets_ef = {}
                for j in self.__nodes:
                    j_subsets_ef[j] = []
                    for set_e in sets_e:
                        set_f = tuple(sorted(list(set(set_d) - set(set_e))))
                        u_e = self.__steiner_distances[j][set_e][0]
                        u_f = 0
                        t_e = self.__steiner_distances[j][set_e][5]
                        t_f = 'N'
                        if len(set_f) > 0:
                            u_f = self.__steiner_distances[j][set_f][0]
                            t_f = self.__steiner_distances[j][set_f][5]
                        j_subsets_ef[j].append([set_e, set_f, u_e, u_f, t_e, t_f])
                #
                temp = []
                for i in self.__nodes:
                    dist_to_poi = self.__distances[tuple(sorted([self.__poi, i]))][0]
                    for j in self.__nodes:
                        try:
                            dist, t_dist = self.__distances[tuple(sorted([i, j]))]
                        except KeyError:
                            dist = sys.maxint
                            t_dist = 'N'
                        for j_subset_ef in j_subsets_ef[j]:
                            set_e = j_subset_ef[0]
                            set_f = j_subset_ef[1]
                            u_e = j_subset_ef[2]
                            u_f = j_subset_ef[3]
                            t_e = j_subset_ef[4]
                            t_f = j_subset_ef[5]
                            temp.append([dist_to_poi + dist + u_e + u_f, i, j, set_e, set_f])
                temp.sort()
                print(len(temp))
                print(temp[0:11])
                pdb.set_trace()