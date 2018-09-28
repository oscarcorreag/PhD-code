import time
import csv

from link_performance import bpr


class STA:
    def __init__(self, graph):
        self.__graph = graph.copy()
        self.__edges = self.__graph.get_edges().copy()
        self.__cap = self.__graph.get_capacities()
        self.load = {e: 0 for e in self.__edges}

        self.__load_h = []
        self.__weights_h = []

        self.__graph.compute_dist_paths()

    def all_or_nothing(self, O_D, max_iter=1000, log_history=False):
        no_iter = 0
        while no_iter <= max_iter:
            self.load = {e: 0 for e in self.__edges}
            for (o, d), no_users in O_D.iteritems():
                if self.__graph.is_undirected():
                    o_d = tuple(sorted([o, d]))
                else:
                    o_d = (o, d)
                path = self.__graph.paths[o_d]
                self.__update_load(path, no_users)
            weights = bpr(self.__graph.get_edges(), self.load, self.__cap)
            self.__graph.update_edge_weights(weights)
            self.__append_to_history()
            no_iter += 1
            print no_iter
            if len(self.__load_h) > 1:
                if self.__load_h[-1] == self.__load_h[-2]:
                    print "No. iter: " + str(no_iter)
                    break
            self.__graph.compute_dist_paths(recompute=True)
        if log_history:
            self.__log_history()
        if no_iter > max_iter:
            print "Max. number of iterations reached!"

    def __append_to_history(self):
        edges = sorted(self.__edges)
        load = []
        weights = []
        for e in edges:
            load.append(self.load[e])
            weights.append(self.__graph.get_edges()[e])
        self.__load_h.append(load)
        self.__weights_h.append(weights)

    def __update_load(self, path, load):
        for i in range(len(path) - 1):
            v = path[i]
            w = path[i + 1]
            self.load[tuple(sorted([v, w]))] += load

    def __log_history(self):
        ts = time.strftime("%d%b%Y_%H%M%S")
        load_f = open("files/load_" + ts + ".csv", 'wb')
        weights_f = open("files/weights_" + ts + ".csv", 'wb')
        load_wr = csv.writer(load_f)
        weights_wr = csv.writer(weights_f)
        for load in self.__load_h:
            load_wr.writerow(load)
        for weights in self.__weights_h:
            weights_wr.writerow(weights)