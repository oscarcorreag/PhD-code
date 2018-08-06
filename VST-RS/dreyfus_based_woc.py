import operator
from dreyfus import Dreyfus
from digraph import Digraph
from helper import assign_users_to_pois


class DreyfusBasedWOC:

    def __init__(self, graph):
        self.__graph = graph
        self.congestion = {e: 0 for e in self.__graph.get_edges()}

        self.__graph.compute_dist_paths(compute_paths=False)

    def __divide_requests_into_groups(self, requests, z):
        groups_ = dict()
        for (u, p) in requests:
            try:
                groups_[p].append(u)
            except KeyError:
                groups_[p] = [u]
        groups = []
        for p, group in groups_.items():
            while len(group) > z:
                # If group size > z, create a new group with the farthest user and their z - 1 nearest neighbours.
                dists = {u: self.__graph.dist[tuple(sorted(([u, p])))] for u in group}
                farthest = max(dists.items(), key=operator.itemgetter(1))[0]
                dists_to_u = {u: self.__graph.dist[tuple(sorted(([u, farthest])))] for u in group}
                new_group = [u for u, _ in sorted(dists_to_u.items(), key=operator.itemgetter(1))[:z]]
                groups.append((p, new_group))
                group = list(set(group).difference(new_group))
            if len(group) > 0:
                groups.append((p, group))
        return groups

    def steiner_forest(self, users, pois, z, method="Voronoi", seed=0):
        steiner_forest = Digraph()
        requests = assign_users_to_pois(self.__graph, users, pois, method, seed)
        groups = self.__divide_requests_into_groups(requests, z)
        d = Dreyfus(self.__graph)
        cost = 0
        for p, group in groups:
            terminals = [p]
            terminals.extend(group)
            steiner_tree, cost_ = d.steiner_tree(terminals)
            steiner_forest.append_from_graph(steiner_tree)
            cost += cost_
            self.__update_congestion(steiner_tree)
        return steiner_forest, cost

    def __update_congestion(self, steiner_tree):
        for e in steiner_tree.get_edges():
            self.congestion[e] += 1
