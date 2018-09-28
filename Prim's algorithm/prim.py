import sys

from digraph import Digraph
from priodict import PriorityDictionary


class Prim:
    def __init__(self, graph):
        self.__graph = graph

    def spanning_tree(self):
        marked_nodes = set()
        distances_to = {}
        edges_to = {}
        priority_queue = PriorityDictionary()

        node_weighted = self.__graph.is_node_weighted()

        for n in self.__graph:
            distances_to[n] = sys.maxint
        for n in self.__graph:
            if n in marked_nodes:
                continue
            distances_to[n] = 0
            priority_queue[n] = distances_to[n]
            for v in priority_queue:
                marked_nodes.add(v)
                if not node_weighted:
                    adj_nodes = self.__graph[v]
                else:
                    adj_nodes = self.__graph[v][1]
                for w, edge_cost in adj_nodes.iteritems():
                    if w in marked_nodes:
                        continue
                    if edge_cost < distances_to[w]:
                        distances_to[w] = edge_cost
                        edges_to[w] = (v, w)
                        priority_queue[w] = distances_to[w]
        spanning_tree = Digraph()
        for _, (v, w) in edges_to.iteritems():
            if node_weighted:
                edge_cost = self.__graph[v][1][w]
                if v in spanning_tree:
                    spanning_tree[v][1][w] = edge_cost
                else:
                    spanning_tree[v] = (self.__graph[v][0], {w: edge_cost})
                if w in spanning_tree:
                    spanning_tree[w][1][v] = edge_cost
                else:
                    spanning_tree[w] = (self.__graph[w][0], {v: edge_cost})
            else:
                edge_cost = self.__graph[v][w]
                if v in spanning_tree:
                    spanning_tree[v][w] = edge_cost
                else:
                    spanning_tree[v] = {w: edge_cost}
                if w in spanning_tree:
                    spanning_tree[w][v] = edge_cost
                else:
                    spanning_tree[w] = {v: edge_cost}
        return spanning_tree
