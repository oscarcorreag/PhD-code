import sys
# from suitability import SuitabilityDigraph
from digraph import Digraph
from vst_rs import VST_RS


class BaltzBased:
    def __init__(self, graph):
        # Init some instance variables.
        self.__graph = Digraph()
        self.__graph.append_from_graph(graph)
        self.__edges = self.__graph.get_edges()
        self.congestion = {}

        l_G = float(0)
        for e, le in self.__edges.items():
            self.congestion[e] = 0
            l_G += le
        self.__weights = {e: le / l_G for e, le in self.__edges.items()}

    def steiner_forest(self, requests, k=4):
        lambda_ = 1
        MSTs = {}
        n = len(self.__graph)
        for i, (terminals, pois) in enumerate(requests):
            self.__graph.update_edge_weights(
                {e: self.__weights[e] * n ** (self.congestion[e] / lambda_ - 1) for e in self.__edges})
            mz = VST_RS(self.__graph)
            Ti, l, _, _, _, _, _ = mz.steiner_forest(terminals, pois, k, sys.maxint)
            MSTs[i] = (Ti, l)
            for e in Ti.get_edges():
                self.congestion[e] += 1
                lambda_ = max(lambda_, self.congestion[e])
        iteration = 1
        while iteration <= 100:
            for i, (terminals, pois) in enumerate(requests):
                cmax = max(self.congestion.values())
                E_Ti = MSTs[i][0].get_edges()
                A = len(E_Ti)
                self.__graph.update_edge_weights(
                    {e: self.__weights[e] * A ** (self.congestion[e] - cmax) for e in self.__edges})
                self.__graph.update_edge_weights({e: le / A for e, le in E_Ti.items()})
                mz = VST_RS(self.__graph)
                Ti_, l, _, _, _, _, _ = mz.steiner_forest(terminals, pois, k, sys.maxint)
                self.__graph.update_edge_weights({e: le * A for e, le in E_Ti.items()})
                if MSTs[i][1] > l:
                    for e in MSTs[i][0].get_edges():
                        self.congestion[e] -= 1
                    for e in Ti_.get_edges():
                        self.congestion[e] += 1
                    MSTs[i] = (Ti_, l)
            iteration += 1
        return MSTs