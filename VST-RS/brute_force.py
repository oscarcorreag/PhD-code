import sys

from utils import comb_upto_n
from dreyfus import Dreyfus


class BruteForce:
    def __init__(self, graph):
        self.__graph = graph.copy()
        self.__solver = Dreyfus(self.__graph)

    def __map_cost_subset(self, users, pois, z):
        map_ = {}
        users_combs = comb_upto_n(users, z)
        for users_ in users_combs:
            min_cost = sys.maxint
            for poi in pois:
                terminals = [poi]
                terminals.extend(users_)
                _, cost = self.__solver.steiner_tree(terminals)
                if cost < min_cost:
                    map_[tuple(users_)] = (cost, poi)
                    min_cost = cost
        return map_

    def steiner_forest(self, users, pois, z):
        print self.__map_cost_subset(users, pois, z)
