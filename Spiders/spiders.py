import operator
import sys
import utils

from digraph import dijkstra
from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator


# from networkx_graph_helper import NetworkXGraphHelper


class Spiders:
    def __init__(self, graph, terminals, poi, contract_graph=True, contracted_graph=None, within_convex_hull=False,
                 dist_paths_suitable_nodes=None):

        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Spiders algorithm only works with node-weighted graphs.")

        # Store class variables for future references.
        self.__original_graph = graph
        self.__terminals = terminals
        self.__poi = poi
        self.__contract_graph = contract_graph

        terminals_poi = list(terminals)
        terminals_poi.append(poi)

        generator = SuitableNodeWeightGenerator()

        # Contracted graph...
        if contract_graph:
            if contracted_graph is not None:
                self.__graph = contracted_graph.copy()
            else:
                self.__graph = SuitabilityDigraph()
                self.__graph.append_from_graph(graph)
                self.__graph.contract_suitable_regions(generator, excluded_nodes=terminals_poi)
        else:
            self.__graph = SuitabilityDigraph()
            self.__graph.append_from_graph(graph)

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
        # POI will be included in this list.
        self.__suitable_nodes.append(poi)

        # Calculate distances and paths between nodes. IMPORTANT: Only suitable nodes are regarded as start nodes.
        self.__dist_paths_node_node = {}
        # self.__dist_paths_node_within_region_node = {}

        if dist_paths is not None:
            self.__dist_paths_node_node = {n: dist_paths[n] for n in self.__suitable_nodes}
            # for n in self.__suitable_nodes:
            #     self.__dist_paths_node_node[n] = dist_paths[n]
            #     if n in self.__graph.contracted_regions:
            #         region = self.__graph.contracted_regions[n][0]
            #         for w in region:
            #             self.__dist_paths_node_within_region_node[w] = \
            #                 dijkstra(self.__original_graph, w, consider_node_weights=False)
        else:
            self.__dist_paths_node_node = \
                {n: dijkstra(self.__graph, n) for n in self.__suitable_nodes}
            # for n in self.__suitable_nodes:
            #     self.__dist_paths_node_node[n] = dijkstra(self.__graph, n, consider_node_weights=False)
            #     if n in self.__graph.contracted_regions:
            #         region = self.__graph.contracted_regions[n][0]
            #         for w in region:
            #             self.__dist_paths_node_within_region_node[w] = \
            #                 dijkstra(self.__original_graph, w, consider_node_weights=False)
        for e in terminals_poi:
            if e not in self.__dist_paths_node_node:
                self.__dist_paths_node_node[e] = dijkstra(self.__graph, e)

        # For every terminal create a subtree which has such terminal as the only node. Each subtree is digraph.
        self.__subtrees = {}
        for s in terminals:
            subtree = SuitabilityDigraph()
            subtree[s] = (self.__graph[s][0], {})
            self.__subtrees[s] = subtree

        # IMPORTANT: This method calculates the distances and paths from suitable nodes only.
        self.__calculate_distances_paths_to_subtrees()

    '''
    Calculate the distances and paths from every suitable node to every subtree. It also calculates the sorted list of
    subtrees by distance. It is called every time merging operations are performed.
    '''

    def __calculate_distances_paths_to_subtrees(self):
        # Distances and paths node-to-subtree
        self.__dist_paths_node_subtree = {}
        self.__ordered_subtrees = {}
        # For every suitable node, get the tuple (distances, paths) to every subtree and store it as the value for
        # the entry ->  node: (distances, paths)  in a dictionary which is a class variable.
        # distances: dictionary with entries ->  subtree: distance_to_nearest_node_in_the_subtree
        # paths: dictionary with entries ->  subtree: path_to_nearest_node_in_the_subtree
        # path: list of nodes ordered from node to nearest node in the subtree
        for n in self.__suitable_nodes:
            for s in self.__subtrees:
                dist, nearest = self.__calculate_distance_node_subtree(n, s)
                if n not in self.__dist_paths_node_subtree:
                    self.__dist_paths_node_subtree[n] = ({}, {})
                self.__dist_paths_node_subtree[n][0][s] = dist
                try:
                    self.__dist_paths_node_subtree[n][1][s] = self.__dist_paths_node_node[n][1][nearest]
                except KeyError:
                    self.__dist_paths_node_subtree[n][1][s] = []
            # Once the distances dictionary is ready for the current node, a list of tuples (subtree, distance) ordered
            # by distance is calculated and stored as a value for the entry -> node: sorted_list_of_subtrees_by_distance
            # The entry is stored in a dictionary which is a class variable.
            ordering = sorted(self.__dist_paths_node_subtree[n][0].iteritems(), key=operator.itemgetter(1))
            self.__ordered_subtrees[n] = ordering

    '''
    Calculate the distance from node to subtree. It also returns the nearest node within the subtree that is a suitable
    node, or the terminal if it is the only node within the subtree.
    '''

    def __calculate_distance_node_subtree(self, node, subtree):
        min_dist = sys.maxint
        nearest_n = None
        # Get the distance from the node to every node in the subtree that is a suitable node (or is the only node that
        # is a terminal) and return the nearest.
        for n in self.__subtrees[subtree]:
            if (len(self.__subtrees[subtree].keys()) == 1 and n in self.__terminals) or n in self.__suitable_nodes:
                try:
                    d = self.__dist_paths_node_node[node][0][n]
                except KeyError:
                    d = sys.maxint
                if d < min_dist:
                    min_dist = self.__dist_paths_node_node[node][0][n]
                    nearest_n = n
        return min_dist, nearest_n

    '''
    Evaluate a ratio similar to Klein and Ravi paper. However, when a node is within a subtree, i.e. its distance to
    this subtree is zero, the number of subtrees, which acts as divisor in the ratio, is also affected. A fraction of
    this subtree is taken into account instead of it as a whole. In this way, I prevent this node having advantage over
    the others.
    '''

    def __evaluate_ratio(self, node, i):
        dist_subtrees = 0
        cont = 0
        for j in range(i + 1):
            if self.__ordered_subtrees[node][j][1] != 0:
                dist_subtrees += self.__ordered_subtrees[node][j][1]
            else:
                cont += 1
        return float(self.__graph[node][0] + dist_subtrees) / (i + 1 - cont / 2.)

    '''
    Clever way to get the minimum ratio for a node.
    '''

    def __get_quotient_cost(self, node):
        i = 1
        k = len(self.__subtrees)
        ratio = self.__evaluate_ratio(node, i)
        while i < k - 1:
            if self.__ordered_subtrees[node][i + 1][1] < ratio:
                i += 1
                ratio = self.__evaluate_ratio(node, i)
            else:
                break
        return ratio, i

    '''
    Get the best node amongst the suitable nodes, i.e. the node with the minimum ratio.
    '''

    def __get_best_node(self, min_threshold=None):

        best_avg = sys.maxint
        best_node = None
        best_r = None
        best_checked = False  # Useful to prevent unnecessary double-check whether a node already belongs to a subtree
        best_found = False  # Indicates whether the best node, so far, has been found within a subtree

        # For every suitable node, get the minimum value of the heuristic function. The goal is to obtain the node
        # with the minimum minimum value. If the nodes that are being compared have the same minimum value, other
        # heuristics are taken into account. See V. J. Rayward-Smith paper.
        for n in self.__suitable_nodes:

            min_by_node, r = self.__get_quotient_cost(n)

            if min_threshold < min_by_node < best_avg:
                best_avg = min_by_node
                best_node = n
                best_r = r
                best_checked = False  # A new best node is likely not having been checked yet
                best_found = False  # A new best node is likely not having been found within a subtree

            elif min_by_node == best_avg:  # In case two nodes have the same minimum value

                dist_0 = self.__dist_paths_node_node[best_node][0][self.__poi]
                dist_1 = self.__dist_paths_node_node[n][0][self.__poi]

                # a) The best is the one with minimum distance to the POI.
                if dist_1 < dist_0:
                    best_node = n
                    best_r = r
                    best_checked = False  # A new best node is likely not having been checked yet
                    best_found = False  # A new best node is likely not having been found within a subtree

                    continue

                # b) The best is the one that is not within a subtree.
                if not best_checked or (best_checked and best_found):
                    if not best_checked:  # To prevent checking again
                        # Check if the best node is within any subtree.
                        for i in range(best_r + 1):
                            subtree = self.__ordered_subtrees[best_node][i][0]
                            if best_node in self.__subtrees[subtree]:
                                best_found = True
                                break
                        best_checked = True
                    # Check id the current node is within any subtree.
                    cur_found = False
                    for i in range(r + 1):
                        subtree = self.__ordered_subtrees[n][i][0]
                        if n in self.__subtrees[subtree]:
                            cur_found = True
                            break
                    # This corresponds to the (i) heuristic proposed in the paper when two nodes have the same value.
                    # Only if the best node is within a subtree whereas the current node not, the latter becomes the new
                    # best node.
                    if best_found and not cur_found:
                        best_node = n
                        best_r = r
                        best_checked = True  # This new best node has been already checked
                        best_found = False  # This new best node is not within a subtree

        return best_node, best_avg

    '''
    Merge the first two nearest subtrees of the node and the node as well.
    '''

    def __merge_subtrees_and_node(self, node):
        # Get the first two nearest subtrees to the node.
        subtree_0 = self.__ordered_subtrees[node][0][0]
        subtree_1 = self.__ordered_subtrees[node][1][0]
        # Generate a random id for the new subtree.
        new_subtree_id = "s_" + utils.id_generator()
        # Init the new subtree with the nodes of the first nearest subtree.
        new_subtree = self.__subtrees[subtree_0].copy()
        # Append the nodes of the second nearest subtree to the new subtree.
        new_subtree.append_from_graph(self.__subtrees[subtree_1])
        # Get the paths from the node to the first two nearest subtrees.
        path_0 = self.__dist_paths_node_subtree[node][1][subtree_0]
        path_1 = self.__dist_paths_node_subtree[node][1][subtree_1]
        # Append these paths to the new subtree.
        for path in [path_0, path_1]:
            new_subtree.append_from_path(path, self.__graph)
        # Remove the first two nearest subtrees from the list of subtrees.
        del self.__subtrees[subtree_0]
        del self.__subtrees[subtree_1]
        # Add the new subtree to the list of subtrees.
        self.__subtrees[new_subtree_id] = new_subtree
        # Calculate distances and paths for the new list of subtrees.
        self.__calculate_distances_paths_to_subtrees()

    '''
    Merge a node with a subtree and append the subtree to the list of subtrees.
    '''

    def __merge_subtree_and_node(self, subtree, node):
        # Generate a random id for the new subtree.
        new_subtree_id = "s_" + utils.id_generator()
        # Init the new subtree with the nodes of the subtree.
        new_subtree = self.__subtrees[subtree].copy()
        # Get the path from the node to the subtree.
        path = self.__dist_paths_node_subtree[node][1][subtree]
        # Append this path to the new subtree.
        new_subtree.append_from_path(path, self.__graph)
        # Remove the subtree from the list of subtrees.
        del self.__subtrees[subtree]
        # Add the new subtree to the list of subtrees.
        self.__subtrees[new_subtree_id] = new_subtree
        # Calculate distances and paths for the new list of subtrees.
        self.__calculate_distances_paths_to_subtrees()

    def __merge_subtrees_through_poi(self, subtree_with_poi, subtree):
        # Generate a random id for the new subtree.
        new_subtree_id = "s_" + utils.id_generator()
        # Init the new subtree with the nodes of the subtree with the POI.
        new_subtree = self.__subtrees[subtree_with_poi].copy()
        # Append the nodes of the second subtree to the new subtree.
        new_subtree.append_from_graph(self.__subtrees[subtree])
        # Find the path through the POI between these two subtrees.
        min_dist = sys.maxint
        nearest_n = None
        if len(self.__subtrees[subtree].keys()) == 1:
            nearest_n = self.__subtrees[subtree].keys()[0]
        else:
            for n in self.__subtrees[subtree]:
                if n in self.__suitable_nodes:
                    if self.__dist_paths_node_node[n][0][self.__poi] < min_dist:
                        min_dist = self.__dist_paths_node_node[n][0][self.__poi]
                        nearest_n = n
        if nearest_n is None:
            raise (RuntimeError, "__merge_subtrees_through_poi: couldn't find the nearest point within the subtree.")
        path = self.__dist_paths_node_node[self.__poi][1][nearest_n]
        # Append this path to the new subtree.
        new_subtree.append_from_path(path, self.__graph)
        # Remove the two subtrees from the list of subtrees.
        del self.__subtrees[subtree_with_poi]
        del self.__subtrees[subtree]
        # Add the new subtree to the list of subtrees.
        self.__subtrees[new_subtree_id] = new_subtree
        # Calculate distances and paths for the new list of subtrees.
        self.__calculate_distances_paths_to_subtrees()

        return path

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
                    s = Spiders(region, new_terminals[1:], new_terminals[0], contract_graph=False)
                    st, _ = s.steiner_tree()
                    trees.append(st)
        for r in regions:
            del steiner_tree[r]
        for p in paths:
            steiner_tree.append_from_path(p, self.__original_graph)
        for st in trees:
            steiner_tree.append_from_graph(st)

    # def __find_closest_node_to_poi_within_region(self, region_id):
    #     region = self.__graph.contracted_regions[region_id][0]
    #     min_dist = sys.maxint
    #     closest_node = None
    #     distances, _ = dijkstra(self.__original_graph, self.__poi, region.keys(), consider_node_weights=False)
    #     for n in region:
    #         if distances[n] < min_dist:
    #             closest_node = n
    #             min_dist = distances[n]
    #     return closest_node
    #
    # def __decontract_steiner_tree(self, steiner_tree):
    #     regions = []
    #     paths = []
    #     for r in steiner_tree:
    #         if r in self.__graph.contracted_regions:
    #             regions.append(r)
    #             closest_node = self.__find_closest_node_to_poi_within_region(r)
    #             neighbors = steiner_tree[r][1].keys()
    #             _, paths_closest = dijkstra(self.__original_graph, closest_node, neighbors, consider_node_weights=False)
    #             for v in steiner_tree[r][1]:
    #                 paths.append(paths_closest[v])
    #                 del steiner_tree[v][1][r]
    #     for r in regions:
    #         del steiner_tree[r]
    #     for p in paths:
    #         steiner_tree.append_from_path(p, self.__original_graph)

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

    '''
    The minimum Steiner tree will be the last tree after merging all the subtrees.
    '''

    def steiner_tree(self):
        # ngh = NetworkXGraphHelper(self.__graph)
        meeting_nodes = []

        while len(self.__subtrees) > 1:

            # Get the best node according to the heuristic function.
            best_node, best_avg = self.__get_best_node()

            # Get the two subtrees that might be merged.
            subtree_0 = self.__ordered_subtrees[best_node][0][0]
            subtree_1 = self.__ordered_subtrees[best_node][1][0]

            # After the best node has been found, there are four possibilities:

            # a) If the two subtrees are the last ones and any of them contains the POI, I do not need an intermediary
            # node since there is not chance this meeting node will be used by other subtrees. Thus, I merge the
            # subtrees through the POI.
            if len(self.__subtrees) == 2:
                if self.__poi in self.__subtrees[subtree_0] or self.__poi in self.__subtrees[subtree_1]:
                    if self.__poi in self.__subtrees[subtree_0]:
                        self.__merge_subtrees_through_poi(subtree_0, subtree_1)
                    else:
                        self.__merge_subtrees_through_poi(subtree_1, subtree_0)
                    # meeting_nodes.append((self.__poi, self.__terminals))
                    continue

            # b) If one of the subtrees that might be merged contains the POI and there are more than two subtrees,
            # I avoid merging this subtree and search for another couple.
            while (self.__poi in self.__subtrees[subtree_0] or self.__poi in self.__subtrees[subtree_1]) \
                    and best_node != self.__poi:

                best_node, best_avg = self.__get_best_node(best_avg)

                if best_node is None:
                    best_node, best_avg = self.__get_best_node()
                    subtree_0 = self.__ordered_subtrees[best_node][0][0]
                    subtree_1 = self.__ordered_subtrees[best_node][1][0]
                    break

                subtree_0 = self.__ordered_subtrees[best_node][0][0]
                subtree_1 = self.__ordered_subtrees[best_node][1][0]

            # c) If one of them is closer to the POI than to the best node, I merge this subtree with the POI instead of
            # using the best node as an intermediary meeting node.
            dist_0 = sys.maxint
            dist_1 = sys.maxint
            # If the POI is within any of the subtrees, it does not make sense to check for convenience.
            if self.__poi not in self.__subtrees[subtree_0]:
                dist_0 = self.__dist_paths_node_subtree[self.__poi][0][subtree_0]
            if self.__poi not in self.__subtrees[subtree_1]:
                dist_1 = self.__dist_paths_node_subtree[self.__poi][0][subtree_1]
            # If one of them is closer to the POI...
            if dist_0 < self.__ordered_subtrees[best_node][0][1] or dist_1 < self.__ordered_subtrees[best_node][1][1]:
                # Merge the POI with the subtree.
                if dist_0 < self.__ordered_subtrees[best_node][0][1]:
                    # meeting_nodes.append((self.__poi, [t for t in self.__subtrees[subtree_0] if t in self.__terminals]))
                    self.__merge_subtree_and_node(subtree_0, self.__poi)
                if dist_1 < self.__ordered_subtrees[best_node][1][1]:
                    # meeting_nodes.append((self.__poi, [t for t in self.__subtrees[subtree_1] if t in self.__terminals]))
                    self.__merge_subtree_and_node(subtree_1, self.__poi)

                continue

            # d) The "best node" is in fact the best node.
            # nodes = [t for t in self.__subtrees[subtree_0] if t in self.__terminals]
            # nodes.extend([t for t in self.__subtrees[subtree_1] if t in self.__terminals])
            # meeting_nodes.append((best_node, nodes))
            self.__merge_subtrees_and_node(best_node)

            # legend = [str(counter + 1) + ". imp->" + str(mn[0]) + " for: " + str(mn[1]) for counter, mn in
            #           enumerate(meeting_nodes)]
            #
            # ngh.draw_graph(nodes_2=[self.__poi], nodes_1=self.__terminals,
            #                subgraphs_2=[subtree for _, subtree in self.__subtrees.iteritems()],
            #                node_weight_generator=SuitableNodeWeightGenerator(),
            #                legend=legend,
            #                node_labels=True)

        # At the end, if the POI is not part of the Steiner tree, merge the POI with the Steiner tree because the POI is
        # a compulsory meeting node.
        if self.__poi not in self.__subtrees[self.__subtrees.keys()[0]]:
            # meeting_nodes.append(
            #     (self.__poi, [t for t in self.__subtrees[self.__subtrees.keys()[0]] if t in self.__terminals]))
            self.__merge_subtree_and_node(self.__subtrees.keys()[0], self.__poi)

        steiner_tree = self.__subtrees[self.__subtrees.keys()[0]]
        self.__prune_steiner_tree(steiner_tree)

        if self.__contract_graph:
            self.__decontract_steiner_tree(steiner_tree)

        return steiner_tree, meeting_nodes
