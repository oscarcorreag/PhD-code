import networkx as nx
import matplotlib.pyplot as plt

from graph import Graph
from numpy.random import RandomState


class NetworkXGraphHelper:
    def __init__(self, graph, layout="spring"):

        self.__graph = Graph()
        self.__graph.append_graph(graph)

        self.element_colors = ['#000000',
                               '#0000FF',
                               '#13E853',  # Subgraphs 1's color
                               '#FF0000',  # Subgraphs 2's color
                               '#E67E22',
                               '#9B59B6',
                               '#2980B9',
                               '#1ABC9C',
                               '#27AE60',
                               '#F1C40F',
                               '#7F8C8D',
                               '#C0392B',
                               '#E74C3C',
                               '#8E44AD',
                               '#3498DB',
                               '#16A085',
                               '#2ECC71',
                               '#F39C12',
                               '#D35400']

        self.default_node_size = 15
        self.default_color = '#C2C2C2'

        self.__graph_x = nx.Graph()

        # self.__node_weighted = graph.is_node_weighted()

        if graph.is_node_weighted():
            for node in graph:
                self.__graph_x.add_node(node, weight=graph[node][0])
                for adj_node, weight in graph[node][1].iteritems():
                    self.__graph_x.add_edge(node, adj_node, weight=weight)
        else:
            for node in graph:
                self.__graph_x.add_node(node)
                for adj_node, weight in graph[node].iteritems():
                    self.__graph_x.add_edge(node, adj_node, weight=weight)

        if layout == "spectral":
            # Spectral layout looks better for grid graphs.
            self.pos = nx.spectral_layout(self.__graph_x)
        elif layout == "kamada_kawai":
            self.pos = nx.kamada_kawai_layout(self.__graph_x)
        else:
            self.pos = nx.spring_layout(self.__graph_x)

    '''
    '''

    def draw_graph(self, special_nodes=None, special_subgraphs=None, title_1=None, title_2=None, legend=None,
                   edge_labels=None, print_edge_labels=False, node_labels=None, print_node_labels=False):

        # Create list of node colors and sizes.
        node_colors = [self.default_color] * self.__graph_x.number_of_nodes()
        node_sizes = [self.default_node_size] * self.__graph_x.number_of_nodes()

        # Modify the list of colors and sizes if there are special nodes. Color of a sub-list may overlap color of a
        # previous sub-list.
        if special_nodes is not None:
            node_idx_map = {node: idx for idx, node in enumerate(self.__graph_x.nodes())}
            for ord_, (nodes, color, size) in enumerate(special_nodes):
                for n in nodes:
                    # n MUST BE the actual index of the node within node_colors
                    color = self.element_colors[ord_ % len(self.element_colors)] if color is None else color
                    node_colors[node_idx_map[n]] = color
                    if size is not None:
                        node_sizes[node_idx_map[n]] = size

        # Create list of default edge colors.
        edge_colors = [self.default_color for _ in self.__graph_x.edges()]
        edge_widths = [1.0 for _ in self.__graph_x.edges()]

        # Modify the list of edge colors if there are special subgraphs (subgraphs can be overlapped)
        # if special_subgraphs:
        #     if isinstance(special_subgraphs, list):
        #         special_subgraphs = \
        #             self.special_subgraphs_from_paths(special_subgraphs, random_colors=random_colors, seed=seed)
        # else:
        #     special_subgraphs = []
        special_subgraphs = [] if special_subgraphs is None else special_subgraphs
        for ord_, (subgraph, color) in enumerate(special_subgraphs):
            i = 0
            node_weighted = subgraph.is_node_weighted()
            color = self.element_colors[ord_ % len(self.element_colors)] if color is None else color
            for v, w in self.__graph_x.edges():
                if v in subgraph:
                    if (node_weighted and w in subgraph[v][1]) or (not node_weighted and w in subgraph[v]):
                        edge_colors[i] = color
                        edge_widths[i] = 2.0
                i += 1

        nx.draw_networkx_nodes(self.__graph_x, self.pos, node_size=node_sizes, node_color=node_colors, linewidths=0)
        nx.draw_networkx_edges(self.__graph_x, self.pos, edge_color=edge_colors, width=edge_widths)

        if print_edge_labels:
            if edge_labels is None:
                labels = dict([((u, v,), format(d['weight'], '.3f')) for u, v, d in self.__graph_x.edges(data=True)])
            else:
                labels = dict(edge_labels)
            nx.draw_networkx_edge_labels(self.__graph_x, self.pos, edge_labels=labels, font_size=7)

        if print_node_labels:
            if node_labels is None:
                labels = {n: n for n, _ in self.__graph_x.nodes(data=True)}
            else:
                labels = dict(node_labels)
            nx.draw_networkx_labels(self.__graph_x, self.pos, labels, font_size=10)

        if title_1 is not None:
            plt.title(title_1)

        if title_2 is not None:
            plt.text(0.5, 1.1, title_2, horizontalalignment='center')

        if legend is not None:
            y = 1.1
            for label in legend:
                plt.text(x=1, y=y, s=label, fontdict={'size': 8})
                y -= .03

        # show graph
        plt.show()

    def get_node_induced_subgraph(self, nodes):
        return self.__graph_x.subgraph(nodes)

    def special_subgraphs_from_paths(self, paths, random_colors=False, seed=None):
        special_subgraphs = list()
        #
        rnd = RandomState()
        if seed is not None:
            rnd = RandomState(seed)
        #
        ec = list(self.element_colors)
        if random_colors:
            rnd.shuffle(ec)
        for ord_, path in enumerate(paths):
            route = Graph()
            route.append_path(path, self.__graph)
            color = ec[ord_ % len(ec)]
            special_subgraphs.append((route, color))
        return special_subgraphs
