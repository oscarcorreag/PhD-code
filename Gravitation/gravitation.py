import sys
import operator

from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from graph import dijkstra
from networkx_graph_helper import NetworkXGraphHelper


class Gravitation:
    def __init__(self, graph, terminals, poi, max_level_attraction=2, contract_graph=True, contracted_graph=None,
                 within_convex_hull=False, dist_paths_suitable_nodes=None):

        if not graph.is_node_weighted():
            raise (ValueError, "Gravitation algorithm only works with node-weighted graphs.")

        # Store class variables for future references.
        self.__original_graph = graph
        self.__terminals = terminals
        self.__poi = poi
        self.__contract_graph = contract_graph

        #
        terminals_poi = list(terminals)
        terminals_poi.append(poi)

        generator = SuitableNodeWeightGenerator()

        # Contracted graph...
        if contract_graph:
            if contracted_graph is not None:
                self.__graph = contracted_graph.copy()
            else:
                self.__graph = SuitabilityGraph()
                self.__graph.append_graph(graph)
                self.__graph.contract_suitable_regions(generator, excluded_nodes=terminals_poi)
        else:
            self.__graph = SuitabilityGraph()
            self.__graph.append_graph(graph)

        # #
        # ngh = NetworkXGraphHelper(self.__original_graph)
        # ngh.draw_graph(nodes_1=terminals,
        #                nodes_2=[poi],
        #                subgraphs_1=[r for _, (r, _, _) in self.__graph.contracted_regions.iteritems()],
        #                node_weight_generator=generator,
        #                node_size=25)
        # #
        # ngh = NetworkXGraphHelper(self.__graph)
        # ngh.draw_graph(node_weight_generator=generator, node_size=25, node_labels=True)

        # Copy distances and paths dictionary since it will be changed.
        dist_paths = None
        if dist_paths_suitable_nodes is not None:
            dist_paths = dict(dist_paths_suitable_nodes)
            for e in terminals_poi:
                dist_paths[e] = dijkstra(self.__graph, e)

        # Get the suitable nodes.
        if within_convex_hull:
            self.__suitable_nodes = self.__graph.get_suitable_nodes_within_convex_set(terminals_poi, generator, dist_paths)
        else:
            self.__suitable_nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=terminals_poi)
        # print(self.__suitable_nodes)

        #
        self.__dist_paths_node_node = {}
        if dist_paths is not None:
            self.__dist_paths_node_node = {n: dist_paths[n] for n in self.__suitable_nodes}
        else:
            self.__dist_paths_node_node = \
                {n: dijkstra(self.__graph, n) for n in self.__suitable_nodes}
        for e in terminals_poi:
            if e not in self.__dist_paths_node_node:
                self.__dist_paths_node_node[e] = dijkstra(self.__graph, e)

        #
        max_distances = [max(self.__dist_paths_node_node[n][0].values()) for n in self.__suitable_nodes
                         if len(self.__dist_paths_node_node[n][0].values()) > 0]
        if len(max_distances) > 0:
            self.__max_dist = max(max_distances)
        else:
            self.__max_dist = 0

        # #
        # max_level_attraction_poi = 0
        # for t in terminals:
        #     max_level_attraction_poi = max(max_level_attraction_poi, len(self.__dist_paths_node_node[poi][1][t]))
        # mass = self.__calculate_mass_suitable_node(poi)
        # self.__attract_nodes_to(poi, mass, poi, max_level_attraction_poi, 0, [])

        #
        dist_to_poi = {}
        for n in self.__suitable_nodes:
            try:
                dist_to_poi[n] = self.__dist_paths_node_node[n][0][poi]
            except KeyError:
                dist_to_poi[n] = sys.maxint
        # dist_to_poi = {n: self.__dist_paths_node_node[n][0][poi] for n in self.__suitable_nodes}
        # ord_suit_nodes = sorted(dist_to_poi.iteritems(), key=operator.itemgetter(1), reverse=True)
        ord_suit_nodes = sorted(dist_to_poi.iteritems(), key=operator.itemgetter(1))
        for n, _ in ord_suit_nodes:
            mass = self.__calculate_mass_suitable_node(n)
            self.__attract_nodes_to(n, mass, n, max_level_attraction, 0, [])

        # #
        # ngh = NetworkXGraphHelper(self.__graph)
        # ngh.draw_graph(node_weight_generator=generator, node_size=25, node_labels=False)

    '''
    '''

    def __calculate_mass_suitable_node(self, node):

        hits = 0
        for t in self.__terminals:
            p = self.__dist_paths_node_node[self.__poi][1][t]
            if node in p:
                hits += 10

        mass = 0
        if node in self.__graph.contracted_regions:
            region = self.__graph.contracted_regions[node][0]
            for n in region:
                mass += 1. / region[n][0] * 100
        else:
            mass = 1. / self.__graph[node][0] * 100

        return mass + hits

    '''
    '''

    def __calculate_adjusted_edge_cost(self, edge_cost, mass_attracting_node, distance_from_attracting_node):
        if self.__max_dist > 0:
            scaled_dist = float(distance_from_attracting_node) / self.__max_dist
        else:
            scaled_dist = 1
        return edge_cost * scaled_dist / mass_attracting_node

    '''
    '''

    def __attract_nodes_to(self, attracting_node, mass_attracting_node, current_node, level_attraction, distance_so_far,
                           already_affected_edges):
        if level_attraction < 1:
            return
        for neighbour in self.__graph[current_node][1]:
            edge = tuple(sorted([current_node, neighbour]))
            distance_from_attracting_node = self.__dist_paths_node_node[attracting_node][0][neighbour]
            edge_cost = self.__graph[current_node][1][neighbour]
            if distance_so_far + edge_cost == distance_from_attracting_node and edge not in already_affected_edges:
                adjusted_edge_cost = \
                    self.__calculate_adjusted_edge_cost(edge_cost, mass_attracting_node, distance_from_attracting_node)
                self.__graph[current_node][1][neighbour] = adjusted_edge_cost
                self.__graph[neighbour][1][current_node] = adjusted_edge_cost
                already_affected_edges.append(edge)
                self.__attract_nodes_to(attracting_node, mass_attracting_node, neighbour, level_attraction - 1,
                                        distance_so_far + edge_cost, already_affected_edges)

    def __find_closest_node_to_node_within_region(self, node, region_id):
        region = self.__graph.contracted_regions[region_id][0]
        min_dist = sys.maxint
        closest_node = None
        distances, paths = dijkstra(self.__original_graph, node, region.keys())
        for n in region:
            if distances[n] < min_dist:
                closest_node = n
                min_dist = distances[n]
        return closest_node, paths[closest_node]

    def __decontract_steiner_tree(self, steiner_tree):
        regions = []
        paths = []
        trees = []
        for r in steiner_tree:
            if r in self.__graph.contracted_regions:
                regions.append(r)
                neighbors = steiner_tree[r][1].keys()
                new_terminals = []
                for n in neighbors:
                    closest_node_to_n, path = self.__find_closest_node_to_node_within_region(n, r)
                    paths.append(path)
                    new_terminals.append(closest_node_to_n)
                    del steiner_tree[n][1][r]
                if len(new_terminals) > 1:
                    region = self.__graph.contracted_regions[r][0]
                    g = Gravitation(region, new_terminals[1:], new_terminals[0], contract_graph=False)
                    st = g.steiner_tree()
                    trees.append(st)
        for r in regions:
            del steiner_tree[r]
        for p in paths:
            steiner_tree.append_path(p, self.__original_graph)
        for st in trees:
            steiner_tree.append_graph(st)

        # Fix the edge costs.
        for v in steiner_tree:
            for w in steiner_tree[v][1]:
                steiner_tree[v][1][w] = self.__original_graph[v][1][w]

    @staticmethod
    def __merge_subtrees(subtrees):
        result = SuitabilityGraph()
        for subtree in subtrees:
            result.append_graph(subtree)
        return result

    def __prune_steiner_tree(self, steiner_tree):
        while True:
            keys_to_prune = []
            for n in steiner_tree:
                if n not in self.__terminals and n != self.__poi:
                    neighbours = steiner_tree[n][1].keys()
                    if len(neighbours) == 1:
                        neighbour = neighbours[0]
                        del steiner_tree[neighbour][1][n]
                        keys_to_prune.append(n)
            if len(keys_to_prune) == 0:
                break
            for n in keys_to_prune:
                del steiner_tree[n]

    def steiner_tree(self):
        subtrees = []
        _, paths = dijkstra(self.__graph, self.__poi, self.__terminals)
        for t in self.__terminals:
            path = paths[t]
            subtree = SuitabilityGraph()
            # j = 0
            # for i in range(len(path_to_poi)):
            #     if path_to_poi[i] in self.__graph.contracted_regions:
            #         region_id = path_to_poi[i]
            #         subtree.append_from_path(path_to_poi[j:i], self.__original_graph)
            #         closest_node = self.__find_closest_node_to_poi_within_region(region_id)
            #         path_endpoint_1 = self.__dist_paths_node_within_region_node[closest_node][1][path_to_poi[i - 1]]
            #         subtree.append_from_path(path_endpoint_1, self.__original_graph)
            #         path_endpoint_2 = self.__dist_paths_node_within_region_node[closest_node][1][path_to_poi[i + 1]]
            #         subtree.append_from_path(path_endpoint_2, self.__original_graph)
            #         j = i + 1
            # subtree.append_from_path(path_to_poi[j:], self.__original_graph)
            subtree.append_path(path, self.__graph)
            subtrees.append(subtree)

        steiner_tree = self.__merge_subtrees(subtrees)
        self.__prune_steiner_tree(steiner_tree)

        if self.__contract_graph:
            self.__decontract_steiner_tree(steiner_tree)

        return steiner_tree
