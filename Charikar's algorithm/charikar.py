import sys
import operator

from digraph import dijkstra
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph

class Charikar:

    def __init__(self, graph, root, terminals):
        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Dreyfus with IMRs algorithm only works with node-weighted graphs.")
        #
        self.__graph = graph
        self.__root = root
        self.__terminals = terminals
        self.__root_term = list(terminals)
        self.__root_term.append(root)
        #
        generator = SuitableNodeWeightGenerator()
        self.__nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals)
        if root not in self.__nodes:
            self.__nodes.append(root)
        #
        self.__dist = {}
        self.__paths = {}
        temp = list(terminals)  # root is already included
        temp.extend(self.__nodes)
        self.__dist, self.__paths = self.__graph.get_dist_paths(origins=temp, destinations=temp)

    def Ai(self, k, r, X, i):
        T = SuitabilityDigraph()
        while k > 0:
            TBEST = SuitabilityDigraph()
            for kprime in range(1, k + 1):
                for v in self.__nodes:
                    if i > 1:
                        Tprime = self.Ai(kprime, v, X, i - 1)
                        p = self.__paths[tuple(sorted([r, v]))]
                        Tprime.append_from_path(p, self.__graph)
                    else:
                        dists = {}
                        for t in self.__terminals:
                            dists[t] = self.__dist[tuple(sorted([v, t]))]
                        ord_term = sorted(dists.items(), key=operator.itemgetter(1))
                        Tprime = SuitabilityDigraph()
                        for j in range(kprime):
                            p = self.__paths[tuple(sorted([v, ord_term[j][0]]))]
                            Tprime.append_from_path(p, self.__graph)
                    if self.d(TBEST) > self.d(Tprime):
                        TBEST = Tprime
            T.append_from_graph(TBEST)
            k -= len(set(TBEST.keys()).intersection(X))
            X = set(X).difference(TBEST.keys())
        return T

    def d(self, T):
        cost, _ = T.calculate_costs(self.__root_term)
        k = len(set(T.keys()).intersection(self.__terminals))
        density = sys.maxint
        if k > 0:
            density = cost / k
        return density
