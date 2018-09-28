import operator
import sys
import utils

from digraph import Digraph


# from networkx_graph_helper import NetworkxGraphHelper


class RaywardSmith:
    def __init__(self, graph, terminals):

        # An edge-weighted graph is represented by a dictionary with entries ->  node: adjacent_nodes
        # adjacent_nodes: dictionary with entries ->  adjacent_node: edge_weight
        self.__graph = graph

        # self.__terminals = terminals

        # Distances and paths node-to-node
        self.__dist_paths_node_node = {}
        # For every node in the graph, get the tuple (distances, paths) to every other node and store it as the value
        # for the entry ->  node: (distances, paths)  in a dictionary which is a class variable.
        # distances: dictionary with entries ->  target_node: distance_to_target
        # paths: dictionary with entries ->  target_node: path
        # path: list of nodes ordered from node to target
        for n in self.__graph:
            distances, paths = self.__graph.compute_shortest(n)
            self.__dist_paths_node_node[n] = (distances, paths)

        # Subtrees
        self.__subtrees = {}
        # For every terminal create a subtree which has such terminal as the only node. Each subtree is a digraph.
        for s in terminals:
            subtree = Digraph()
            subtree[s] = {}
            self.__subtrees[s] = subtree
        self.__calculate_distances_paths_to_subtrees()

    '''
    Calculate the distances and paths from every node to each subtree. It also calculates the sorted list of subtrees by
    distance from every node to every subtree. It is called every time subtrees are merged.
    '''

    def __calculate_distances_paths_to_subtrees(self):

        # Distances and paths node-to-subtree
        self.__dist_paths_node_subtree = {}
        self.__ordered_subtrees = {}
        # For every node in the graph, get the tuple (distances, paths) to every subtree and store it as the value for
        # the entry ->  node: (distances, paths)  in a dictionary which is a class variable.
        # distances: dictionary with entries ->  subtree: distance_to_nearest_node_in_the_subtree
        # paths: dictionary with entries ->  subtree: path_to_nearest_node_in_the_subtree
        # path: list of nodes ordered from node to nearest node in the subtree
        for n in self.__graph:
            for s in self.__subtrees:
                dist, nearest = self.__calculate_distance_node_subtree(n, s)
                if n not in self.__dist_paths_node_subtree:
                    self.__dist_paths_node_subtree[n] = ({}, {})
                self.__dist_paths_node_subtree[n][0][s] = dist
                self.__dist_paths_node_subtree[n][1][s] = self.__dist_paths_node_node[n][1][nearest]
            # Once the distances dictionary is ready for the current node, a list of tuples (subtree, distance) ordered
            # by distance is calculated and stored as a value for the entry -> node: sorted_list_of_subtrees_by_distance
            # The entry is stored in a dictionary which is a class variable.
            ordering = sorted(self.__dist_paths_node_subtree[n][0].iteritems(), key=operator.itemgetter(1))
            self.__ordered_subtrees[n] = ordering

    '''
    Calculate the distance from node to subtree. It also returns the nearest node within the subtree.
    '''

    def __calculate_distance_node_subtree(self, node, subtree):
        min_dist = sys.maxint
        nearest_n = None
        # Get the distance from the node to every node in the subtree and return the nearest.
        for n in self.__subtrees[subtree]:
            if self.__dist_paths_node_node[node][0][n] < min_dist:
                min_dist = self.__dist_paths_node_node[node][0][n]
                nearest_n = n
        return min_dist, nearest_n

    '''
    Recursive evaluation of the heuristic function according to V. J. Rayward-Smith paper.
    '''

    def __evaluate_f_r(self, node, r):
        # When r == 1, the function returns the sum of the distances to the first two nearest subtrees.
        if r == 1:
            return self.__ordered_subtrees[node][0][1] + self.__ordered_subtrees[node][1][1]
        else:
            # Otherwise, when r >= 2, it returns an "average" of the distances up to the r subtree. It is not an actual
            # average since the sum is divided by [number_of_summands - 1]
            return float((r - 1) * self.__evaluate_f_r(node, r - 1) + self.__ordered_subtrees[node][r][1]) / r

    '''
    Clever way to get the minimum value of the heuristic function for a node.
    '''

    def __get_min_f(self, node):
        r = 1
        k = len(self.__subtrees)
        f_r = self.__evaluate_f_r(node, r)
        while r < k - 1:
            # If the distance to the next subtree is less than the "average" of the distances up to the r subtree, then
            # a lower bound is still possible.
            if self.__ordered_subtrees[node][r + 1][1] < f_r:
                r += 1
                f_r = self.__evaluate_f_r(node, r)
            else:
                break
        return f_r, r

    '''
    Get the best node, i.e. the node with the minimum heuristic function value.
    '''

    def __get_best_node(self):

        best_avg = sys.maxint
        best_node = None
        best_r = None
        best_checked = False  # Useful to prevent unnecessary double-check whether a node already belongs to a subtree
        best_found = False  # Indicates whether the best node, so far, has been found within a subtree

        # For every node in the graph, get the minimum value of the heuristic function. The goal is to obtain the node
        # with the minimum minimum value. If the nodes that are being compared have the same minimum value, other
        # heuristics are taken into account. See V. J. Rayward-Smith paper.
        for n in self.__graph:

            min_by_node, r = self.__get_min_f(n)

            if min_by_node < best_avg:
                best_avg = min_by_node
                best_node = n
                best_r = r
                best_checked = False  # A new best node is likely not having been checked yet
                best_found = False  # A new best node is likely not having been found within a subtree

            elif min_by_node == best_avg:  # In case two nodes have the same minimum value
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
        return best_node

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
    The minimum Steiner tree will be the last tree after merging all the subtrees.
    '''

    def steiner_tree(self):
        # ngh = NetworkxGraphHelper(self.__graph)
        # best_nodes = []
        while len(self.__subtrees) > 1:
            best_node = self.__get_best_node()
            # best_nodes.append(best_node)
            self.__merge_subtrees_and_node(best_node)
            # ngh.draw_graph(self.__terminals, [subtree for _, subtree in self.__subtrees.iteritems()],
            # best_nodes=best_nodes)
        steiner_tree = self.__subtrees[self.__subtrees.keys()[0]]
        # return steiner_tree, self.__calculate_tree_cost(steiner_tree), best_nodes
        return steiner_tree
