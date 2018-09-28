import sys
from digraph import Digraph
from vst_rs import VST_RS


class BPRBased:
    def __init__(self, graph):
        # Init some instance variables.
        self.__graph = Digraph(capacitated=True)
        self.__graph.append_from_graph(graph)
        self.__edges = self.__graph.get_edges()
        self.__capacities = self.__graph.get_capacities()
        self.congestion = {e: 0 for e in self.__edges}
        self.__weights = {e: le for e, le in self.__edges.iteritems()}

    def compute_weight(self, e):
        return self.__weights[e] * (1 + 0.15 * (self.congestion[e] / self.__capacities[e])**2)

    def steiner_forest(self, requests, k=4):
        MSTs = {}
        for i, (terminals, pois) in enumerate(requests):
            mz = VST_RS(self.__graph)
            Ti, l, _, _, _, _, _ = mz.steiner_forest(terminals, pois, k, sys.maxint)
            MSTs[i] = (Ti, l)
            weights = dict()
            for e in Ti.get_edges():
                self.congestion[e] += 1
                weights[e] = self.compute_weight(e)
            self.__graph.update_edge_weights(weights)

        iteration = 1
        while iteration <= 100:
            for i, (terminals, pois) in enumerate(requests):
        #         cmax = max(self.congestion.values())
        #         E_Ti = MSTs[i][0].get_edges()
        #         A = len(E_Ti)
        #         self.__graph.update_edge_weights(
        #             {e: self.__weights[e] * A ** (self.congestion[e] - cmax) for e in self.__edges})
        #         self.__graph.update_edge_weights({e: le / A for e, le in E_Ti.iteritems()})
                mz = VST_RS(self.__graph)
                Ti_, l, _, _, _, _, _ = mz.steiner_forest(terminals, pois, k, sys.maxint)
                weights = dict()
                for e in Ti_.get_edges():
                    weights[e] = self.compute_weight(e)
                self.__graph.update_edge_weights(weights)
        #         self.__graph.update_edge_weights({e: le * A for e, le in E_Ti.iteritems()})
                if MSTs[i][1] > l:
                    for e in MSTs[i][0].get_edges():
                        self.congestion[e] -= 1
                    for e in Ti_.get_edges():
                        self.congestion[e] += 1
                    MSTs[i] = (Ti_, l)
            iteration += 1
        return MSTs