import sys
from suitability import SuitabilityDigraph
from vst_rs import VST_RS


class Baltz:
    def __init__(self, graph):
        # Init some instance variables.
        self.__graph = SuitabilityDigraph()
        self.__graph.append_from_graph(graph)
        self.__edges = graph.get_edges()
        self.__congestion = {}

        l_G = float(0)
        for e, le in self.__edges.iteritems():
            self.__congestion[e] = 0
            l_G += le
        self.__costs = {e: le / l_G for e, le in self.__edges.iteritems()}

    def steiner_forest(self, requests, k=4):
        lambda_ = 1
        MSTs = {}
        n = len(self.__graph)
        for i, r in enumerate(requests):
            self.__graph.update_edge_weights(
                {e: self.__costs[e] * n ** (self.__congestion[e] / lambda_ - 1) for e in self.__edges})
            mz = VST_RS(self.__graph)
            Ti, l, _, _, _, _, _ = mz.steiner_forest(r[1:], [r[0]], k, sys.maxint)
            MSTs[i] = (Ti, l)
            for e in Ti.get_edges():
                self.__congestion[e] += 1
                lambda_ = max(lambda_, self.__congestion[e])
        iteration = 1
        while iteration <= 100:
            for i, r in enumerate(requests):
                cmax = max(self.__congestion.values())
                E_Ti = MSTs[i][0].get_edges()
                A = len(E_Ti)
                self.__graph.update_edge_weights(
                    {e: self.__costs[e] * A ** (self.__congestion[e] - cmax) for e in self.__edges})
                self.__graph.update_edge_weights({e: le / A for e, le in E_Ti.iteritems()})
                mz = VST_RS(self.__graph)
                Ti_, l, _, _, _, _, _ = mz.steiner_forest(r[1:], [r[0]], k, sys.maxint)
                self.__graph.update_edge_weights({e: le * A for e, le in E_Ti.iteritems()})
                if MSTs[i][1] > l:
                    for e in MSTs[i][0].get_edges():
                        self.__congestion[e] -= 1
                    for e in Ti_.get_edges():
                        self.__congestion[e] += 1
                    MSTs[i] = (Ti_, l)
            iteration += 1
        return MSTs
        # forest = SuitabilityDigraph()
        # for _, (Ti, _) in MSTs.iteritems():
        #     forest.append_from_graph(Ti)
        # return forest
