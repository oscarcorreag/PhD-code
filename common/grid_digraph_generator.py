import numpy as np

from digraph import Digraph
from suitability import SuitabilityDigraph


class GridDigraphGenerator:
    def __init__(self):
        self.graph = None

    def generate(self, m, n, nodes=None, edge_weighted=True, node_weighted=False, node_weights=None,
                 node_weight_generator=None, capacitated=False, capacities_range=(1, 100), seed=0):
        if m <= 1 or n <= 1:
            return
        if node_weighted:
            self.graph = SuitabilityDigraph(capacitated=capacitated)
        else:
            self.graph = Digraph(capacitated=capacitated)
        if edge_weighted or node_weighted or capacitated:
            np.random.seed(seed)
        for i in range(m * n):
            node = i
            if nodes is not None:
                node = nodes[i]
            if node_weighted:
                if node_weights is not None:
                    self.graph[node] = (node_weights[i], {}, {})
                elif node_weight_generator is not None:
                    self.graph[node] = (node_weight_generator.generate(), {}, {})
                else:
                    raise (RuntimeError,
                           "Grid Digraph: Can't generate a node-weighted grid digraph without a node-weight generator.")
            else:
                self.graph[node] = {}
            if i / n == 0:  # First row
                if nodes is not None:
                    node_b = nodes[i + n]
                else:
                    node_b = i + n
                if node_weighted:
                    if edge_weighted:
                        self.graph[node][1][node_b] = np.random.uniform()
                    else:
                        self.graph[node][1][node_b] = 1
                else:
                    if edge_weighted:
                        self.graph[node][node_b] = np.random.uniform()
                    else:
                        self.graph[node][node_b] = 1
                self.__set_left_right_nodes(node, i, n, nodes, edge_weighted, node_weighted)
            elif i / n == m - 1:  # Last row
                if nodes is not None:
                    node_a = nodes[i - n]
                else:
                    node_a = i - n
                if node_weighted:
                    self.graph[node][1][node_a] = self.graph[node_a][1][node]
                else:
                    self.graph[node][node_a] = self.graph[node_a][node]
                self.__set_left_right_nodes(node, i, n, nodes, edge_weighted, node_weighted)
            else:
                if nodes is not None:
                    node_b = nodes[i + n]
                    node_a = nodes[i - n]
                else:
                    node_b = i + n
                    node_a = i - n
                if node_weighted:
                    self.graph[node][1][node_a] = self.graph[node_a][1][node]
                    if edge_weighted:
                        self.graph[node][1][node_b] = np.random.uniform()
                    else:
                        self.graph[node][1][node_b] = 1
                else:
                    self.graph[node][node_a] = self.graph[node_a][node]
                    if edge_weighted:
                        self.graph[node][node_b] = np.random.uniform()
                    else:
                        self.graph[node][node_b] = 1
                self.__set_left_right_nodes(node, i, n, nodes, edge_weighted, node_weighted)

        if capacitated:
            edges = self.graph.get_edges()
            capacities = {e: np.random.randint(capacities_range[0], capacities_range[1]) for e in edges}
            self.graph.set_capacities(capacities)
        return self.graph

    def __set_left_right_nodes(self, node, i, n, nodes, edge_weighted, node_weighted):
        if i % n == 0:  # First column
            if nodes is not None:
                node_r = nodes[i + 1]
            else:
                node_r = i + 1
            if node_weighted:
                if edge_weighted:
                    self.graph[node][1][node_r] = np.random.uniform()
                else:
                    self.graph[node][1][node_r] = 1
            else:
                if edge_weighted:
                    self.graph[node][node_r] = np.random.uniform()
                else:
                    self.graph[node][node_r] = 1
        elif i % n == n - 1:  # Last column
            if nodes is not None:
                node_l = nodes[i - 1]
            else:
                node_l = i - 1
            if node_weighted:
                self.graph[node][1][node_l] = self.graph[node_l][1][node]
            else:
                self.graph[node][node_l] = self.graph[node_l][node]
        else:
            if nodes is not None:
                node_r = nodes[i + 1]
                node_l = nodes[i - 1]
            else:
                node_r = i + 1
                node_l = i - 1
            if node_weighted:
                self.graph[node][1][node_l] = self.graph[node_l][1][node]
                if edge_weighted:
                    self.graph[node][1][node_r] = np.random.uniform()
                else:
                    self.graph[node][1][node_r] = 1
            else:
                self.graph[node][node_l] = self.graph[node_l][node]
                if edge_weighted:
                    self.graph[node][node_r] = np.random.uniform()
                else:
                    self.graph[node][node_r] = 1