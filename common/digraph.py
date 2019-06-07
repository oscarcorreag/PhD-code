import itertools
import operator
import sys

import numpy as np

from priodict import PriorityDictionary
from utils import comb_v


class Digraph(dict):
    def __init__(self, node_weighted=False, undirected=True, capacitated=False, **kwargs):
        super(Digraph, self).__init__(**kwargs)
        self.node_weighted = node_weighted
        self.undirected = undirected
        self.capacitated = capacitated
        self.__edges = dict()
        self.__capacities = dict()
        self.__edges_in_sp = dict()
        self.dist = dict()
        self.paths = dict()
        self.pairs_dist_paths = set()
        self.issues_dist_paths = set()

    def is_node_weighted(self):
        return self.node_weighted

    def is_undirected(self):
        return self.undirected

    def is_capacitated(self):
        return self.capacitated

    def drop_node_weights(self):
        if self.node_weighted:
            for v in self:
                self[v] = self[v][1]

    def update_node_weights(self, weights):
        if self.node_weighted:
            for v, weight in weights.iteritems():
                l_value = list(self[v])
                l_value[0] = weight
                self[v] = tuple(l_value)

    def update_edge_weights(self, weights):
        od_to_recompute = set()
        for (v, w), weight in weights.iteritems():
            # Check whether the edge is present.
            if self.undirected:
                v_w = tuple(sorted([v, w]))
            else:
                v_w = (v, w)
            if v_w not in self.get_edges():
                continue
            # Update the adjacency lists.
            if self.node_weighted:
                self[v][1][w] = weight
                if self.undirected:
                    self[w][1][v] = weight
            else:
                self[v][w] = weight
                if self.undirected:
                    self[w][v] = weight
            # Update the edge.
            self.get_edges()[v_w] = weight
            # Update list of O-D pairs that are to be recomputed.
            if v_w in self.__edges_in_sp:
                od_to_recompute.update(self.__edges_in_sp[v_w])
        # Recompute shortest distances|paths.
        if len(od_to_recompute) > 0:
            self.compute_dist_paths(pairs=od_to_recompute, compute_paths=len(self.paths) > 0, recompute=True,
                                    track_edges=True)

    def perturb_edge_weights(self):
        perturbed = set()
        od_to_recompute = set(self.pairs_dist_paths)
        for v, val in self.iteritems():
            if self.node_weighted:
                for w in val[1]:
                    if (v, w) in perturbed:
                        continue
                    if np.random.ranf() < 0.5:
                        weight = self[v][1][w] + np.random.ranf() / 100
                    else:
                        weight = self[v][1][w] - np.random.ranf() / 100
                    self[v][1][w] = weight
                    if self.undirected:
                        self[w][1][v] = weight
                        perturbed.add((w, v))
                        self.get_edges()[tuple(sorted([v, w]))] = weight
                    else:
                        self.get_edges()[(v, w)] = weight
            else:
                for w in val:
                    if (v, w) in perturbed:
                        continue
                    if np.random.ranf() < 0.5:
                        weight = self[v][w] + np.random.ranf() / 100
                    else:
                        weight = self[v][w] - np.random.ranf() / 100
                    self[v][w] = weight
                    if self.undirected:
                        self[w][v] = weight
                        perturbed.add((w, v))
                        self.get_edges()[tuple(sorted([v, w]))] = weight
                    else:
                        self.get_edges()[(v, w)] = weight
        # Recompute shortest distances|paths.
        self.compute_dist_paths(pairs=od_to_recompute, compute_paths=len(self.paths) > 0, recompute=True)

    def append_edge_1(self, edge, source_graph):  # This DOES NOT recompute shortest distances|paths.
        path = [edge[0], edge[1]]
        self.append_from_path(path, source_graph)

    def append_edge_2(self, edge, weight=1, capacity=0, nodes_weights=(0, 0), nodes_info=({}, {}), check_exists=True):
        v = edge[0]
        w = edge[1]
        # First of all, the edge tuple is created to check whether it already exists.
        if self.undirected:
            v_w = tuple(sorted([v, w]))
        else:
            v_w = (v, w)
        # If that is the case, do nothing.
        if check_exists:
            if v_w in self.get_edges():
                return
        # (A) Let us take care of the adjacency list.
        # If the first node exists, just update its adjacency list.
        if v in self:
            if self.node_weighted:
                self[v][1][w] = weight
            else:
                self[v][w] = weight
        # If not, create that node with the relevant information provided.
        else:
            if self.node_weighted:
                self[v] = (nodes_weights[0], {w: weight}, nodes_info[0])
            else:
                self[v] = {w: weight}
        # To reach a consistent state, check whether the second node exists.
        # If not, create it.
        if w not in self:
            if self.node_weighted:
                self[w] = (nodes_weights[1], {}, nodes_info[1])
            else:
                self[w] = {}
        # (B) Now, let us worry about the collateral information, i.e., edges and capacities.
        self.get_edges()[v_w] = weight
        if self.capacitated:
            self.get_capacities()[v_w] = capacity
        # (C) If the graph is undirected, update the adjacency list of the second node.
        # It is not needed to worry about collateral information when the graph is undirected.
        if self.undirected:
            if self.node_weighted:
                self[w][1][v] = weight
            else:
                self[w][v] = weight

    def append_from_path(self, path, source_graph):
        source_weighted = source_graph.is_node_weighted()
        # If this graph is node-weighted, the source graph MUST be node-weighted.
        if self.node_weighted and not source_weighted:
            raise (ValueError, "Graph: Can't append a source graph which is not node-weighted.")
        for i in range(len(path)):
            if i + 1 < len(path):
                v = path[i]
                w = path[i + 1]
                if source_graph.is_undirected():
                    v_w = tuple(sorted([v, w]))
                else:
                    v_w = (v, w)
                weight = source_graph.get_edges()[v_w]
                capacity = 0
                if source_graph.is_capacitated():
                    capacity = source_graph.get_capacities()[v_w]
                if source_graph.is_node_weighted():
                    nodes_weights = (source_graph[v][0], source_graph[w][0])
                    nodes_info = (source_graph[v][2], source_graph[w][2])
                    self.append_edge_2(v_w, weight, capacity, nodes_weights=nodes_weights, nodes_info=nodes_info)
                else:
                    self.append_edge_2(v_w, weight, capacity)

    def append_from_graph(self, source_graph):
        source_weighted = source_graph.is_node_weighted()
        # If this graph is node-weighted, the source graph MUST be node-weighted.
        if self.node_weighted and not source_weighted:
            raise (ValueError, "Graph: Can't append a source graph which is not node-weighted.")
        source_capacitated = source_graph.is_capacitated()
        # If this graph is capacitated, the source graph MUST be capacitated.
        if self.capacitated and not source_capacitated:
            raise (ValueError, "Graph: Can't append a source graph which is not capacitated.")
        source_capacities = source_graph.get_capacities()
        # Start iterating the nodes in the source graph.
        for v, val in source_graph.iteritems():
            # When v (source graph's node) is present in this graph...
            if v in self:
                if self.node_weighted:
                    # Iterate v's neighbourhood.
                    for w, weight in val[1].iteritems():
                        # When w is NOT present in this graph, an edge is added.
                        if w not in self[v][1]:
                            self[v][1][w] = weight
                            if self.undirected:
                                edge = tuple(sorted([v, w]))
                            else:
                                edge = (v, w)
                            self.get_edges()[edge] = weight
                            # Edge capacity is copied from the source.
                            if self.capacitated:
                                self.get_capacities()[edge] = source_capacities[edge]
                else:
                    # Only the source graph is node-weighted.
                    if source_weighted:
                        adj_nodes = val[1]
                    # Neither is node-weighted.
                    else:
                        adj_nodes = val
                    # Iterate v's neighbourhood.
                    for w, weight in adj_nodes.iteritems():
                        # When w is NOT present in this graph, an edge is added.
                        if w not in self[v]:
                            self[v][w] = weight
                            if self.undirected:
                                edge = tuple(sorted([v, w]))
                            else:
                                edge = (v, w)
                            self.get_edges()[edge] = weight
                            # Edge capacity is copied from the source.
                            if self.capacitated:
                                self.get_capacities()[edge] = source_capacities[edge]
            # When v (source graph's node) is NOT present in this graph, the whole neighbourhood and extra info are
            # copied from the source.
            else:
                if self.node_weighted:
                    adj_nodes = val[1]
                    self[v] = (val[0], adj_nodes.copy(), val[2].copy())
                else:
                    # Only the source graph is node-weighted.
                    if source_weighted:
                        adj_nodes = val[1]
                    # Neither is node-weighted.
                    else:
                        adj_nodes = val
                    self[v] = adj_nodes.copy()
                # Add edges corresponding to the whole neighbourhood.
                for w, weight in adj_nodes.iteritems():
                    if self.undirected:
                        edge = tuple(sorted([v, w]))
                    else:
                        edge = (v, w)
                    self.get_edges()[edge] = weight
                    # Edge capacity is copied from the source.
                    if self.capacitated:
                        self.get_capacities()[edge] = source_capacities[edge]

    def copy(self):
        new_graph = Digraph()
        for v, val in self.iteritems():
            if self.node_weighted:
                new_graph[v] = (val[0], val[1].copy(), val[2].copy())
            else:
                new_graph[v] = val.copy()
        #
        new_graph.node_weighted = self.node_weighted
        new_graph.undirected = self.undirected
        new_graph.capacitated = self.capacitated
        new_graph.__edges = self.get_edges().copy()
        new_graph.set_capacities(self.get_capacities())
        new_graph.dist = self.dist.copy()
        new_graph.paths = self.paths.copy()
        new_graph.pairs_dist_paths = self.pairs_dist_paths.copy()
        new_graph.issues_dist_paths = self.issues_dist_paths.copy()
        #
        return new_graph

    def calculate_costs(self, excluded_nodes=None, compute_node_cost=False):
        cost = 0
        node_cost = 0
        for v in self:
            if self.node_weighted:
                if compute_node_cost:
                    if excluded_nodes is None or v not in excluded_nodes:
                        node_cost += self[v][0]
                cost += sum(self[v][1].values())
            else:
                cost += sum(self[v].values())
        cost = cost / 2. + node_cost  # Divided by two since it is digraph.
        return cost, node_cost

    def extract_node_induced_subgraph(self, nodes):
        subgraph = Digraph()
        if self.node_weighted:
            for n in nodes:
                adj = {w: edge_weight for w, edge_weight in self[n][1].iteritems() if w in nodes}
                subgraph[n] = (self[n][0], adj, self[n][2].copy())
        else:
            for n in nodes:
                subgraph[n] = {w: edge_weight for w, edge_weight in self[n].iteritems() if w in nodes}
        return subgraph

    def build_metric_closure(self, nodes, excluded_edges=None):
        metric_closure = Digraph()
        if excluded_edges is None:
            excluded_edges = set()
        for i in range(len(nodes) - 1):
            nodes_ = []
            for w in nodes[i + 1:]:
                if tuple(sorted([nodes[i], w])) in excluded_edges:
                    continue
                nodes_.append(w)
            dist, _ = self.__dijkstra(nodes[i], nodes_)
            neighbourhood = {}
            for n in nodes_:
                try:
                    neighbourhood[n] = dist[n]
                except KeyError:
                    neighbourhood[n] = sys.maxint
            if nodes[i] in metric_closure:
                temp = list(metric_closure[nodes[i]])
                temp[1].update(neighbourhood)
            else:
                metric_closure[nodes[i]] = (self[nodes[i]][0], neighbourhood, self[nodes[i]][2].copy())
            for n, edge_weight in neighbourhood.iteritems():
                if n in metric_closure:
                    temp = list(metric_closure[n])
                    temp[1][nodes[i]] = edge_weight
                else:
                    metric_closure[n] = (self[n][0], {nodes[i]: edge_weight}, self[n][2].copy())
        return metric_closure

    def get_edges(self):
        if len(self.__edges) != 0:
            return self.__edges
        # Generate edges from scratch only in the case of an undirected graph.
        if self.undirected:
            if self.node_weighted:
                for n in self:
                    for w, edge_weight in self[n][1].iteritems():
                        edge = tuple(sorted([n, w]))
                        if edge not in self.__edges:
                            self.__edges[edge] = edge_weight
            else:
                for n in self:
                    for w, edge_weight in self[n].iteritems():
                        edge = tuple(sorted([n, w]))
                        if edge not in self.__edges:
                            self.__edges[edge] = edge_weight
        return self.__edges

    def get_capacities(self):
        # if self.__capacitated:
        #     missing = set(self.get_edges().keys()).difference(self.__capacities.keys())
        #     if len(missing) != 0:
        #         raise (RuntimeError, "Digraph: Capacities have not been set for all edges!")
        return self.__capacities

    def set_capacities(self, capacities, replace=False):
        non_existent = set(capacities.keys()).difference(self.get_edges().keys())
        if len(non_existent) != 0:
            raise (RuntimeError, "Digraph: Edges corresponding to capacities do not exist!")
        if replace:
            self.__capacities = dict(capacities)
        else:
            self.__capacities.update(capacities)

    def get_dist_paths(self, origins, destinations, method='dijkstra'):
        if len(self.pairs_dist_paths) == 0:
            self.compute_dist_paths(origins=origins, destinations=destinations, method=method)
        return self.dist, self.paths

    def set_dist_path(self, origin, destination, dist, path=None):
        if self.undirected:
            v_w = tuple(sorted([origin, destination]))
        else:
            v_w = (origin, destination)
        try:
            self.dist[v_w] = dist
            if path:
                self.paths[v_w] = path
            self.pairs_dist_paths.add(v_w)
        except KeyError:
            self.dist[v_w] = sys.maxint
            if path:
                self.paths[v_w] = []
            self.issues_dist_paths.add(v_w)

    def compute_missing_pairs_dist_paths(self, pairs):
        if self.undirected:
            pairs_dict = {tuple(sorted([o, d])): (o, d) for (o, d) in pairs}
        else:
            pairs_dict = {(o, d): (o, d) for (o, d) in pairs}
        missing = set(pairs_dict.keys()).difference(self.pairs_dist_paths)
        return [pairs_dict[p] for p in missing]

    def compute_dist_paths(self, origins=None, destinations=None, pairs=None, end_mode='all', compute_paths=True,
                           track_edges=False, recompute=False, method='dijkstra'):
        # Both origins and destinations are indicated or none.
        if (origins is not None and destinations is None) or (destinations is not None and origins is None):
            raise (RuntimeError, "Digraph: Wrong parameters when computing distances!")
        origins_ = []
        destinations_ = []
        # When None is indicated, the graph nodes are the default.
        if origins is None and destinations is None and pairs is None:
            origins_ = self.keys()
            destinations_ = self.keys()
        # Cartesian product.
        if origins is not None and destinations is not None:
            origins_ = list(origins)
            destinations_ = list(destinations)
        pairs_ = set(itertools.product(origins_, destinations_))
        # Final set of pairs.
        if pairs is not None:
            pairs_ = pairs_.union(pairs)
        # Compute missing pairs in set of pairs already computed.
        if len(self.pairs_dist_paths) != 0:
            missing = self.compute_missing_pairs_dist_paths(pairs_)
            if recompute:
                pairs_.update(missing)
            else:
                pairs_ = set(missing)
        # Shortest distance algorithm: Dijkstra
        if method == 'dijkstra':
            # Create dict from pairs which is more appropriate for use with Dijkstra.
            requests = dict()
            for (o, d) in pairs_:
                try:
                    requests[o].append(d)
                except KeyError:
                    requests[o] = [d]
            for v, ds in requests.iteritems():
                dist, p = self.__dijkstra(v, ds, end_mode=end_mode, compute_paths=compute_paths,
                                          track_edges=track_edges)
                for w in ds:
                    if compute_paths:
                        self.set_dist_path(v, w, dist[w], list(p[w]))
                    else:
                        self.set_dist_path(v, w, dist[w])
        elif method == 'meet-in-the-middle':
            # Only one origin and one destination are expected for this method.
            if len(pairs_) != 1:
                raise (RuntimeError, "Only one origin and one destination are expected when 'Meet-in-the-middle' "
                                     "method is used.")
            (pair,) = pairs_
            v = pair[0]
            w = pair[1]
            dist, path = self.__meet_in_the_middle(v, w, compute_path=compute_paths, track_edges=track_edges)
            if compute_paths:
                self.set_dist_path(v, w, dist, path)
            else:
                self.set_dist_path(v, w, dist)
        else:
            raise (RuntimeError, "Digraph: No other method but Dijkstra has been implemented!")
        return len(pairs_)  # number of computed pairs.

    def steiner_n_stats(self, n, v, mst_alg):
        ecc = inc = 0
        powerset_n_terminals = comb_v(self.keys(), n, v)
        costs = []
        for terminals in powerset_n_terminals:
            st = mst_alg.steiner_tree(terminals)
            cost, _ = st.calculate_costs(terminals)
            costs.append(cost)
        if len(costs) > 0:
            ecc = max(costs)
            inc = min(costs)
        return ecc, inc

    '''
    Compute Voronoi cells for a set of nodes and medoids as two dictionaries: (1) nodes by medoids, (2) medoids by node.
    '''

    def get_voronoi_medoids_cells(self, medoids, nodes):
        cells = {m: [] for m in medoids}    # Medoids are the keys and the nodes are the elements of the cell.
        generator_by_node = dict()          # Nodes are the keys and the value is its corresponding closest medoid.
        self.compute_dist_paths(origins=nodes, destinations=medoids, compute_paths=False)
        # Each node from the set [nodes] is assigned to its closest medoid.
        for n in nodes:
            dists = dict()
            for m in medoids:
                if self.undirected:
                    n_m = tuple(sorted([n, m]))
                else:
                    n_m = (n, m)
                dists[m] = self.dist[n_m]
            medoid = min(dists.iteritems(), key=operator.itemgetter(1))[0]
            cells[medoid].append(n)
            generator_by_node[n] = medoid
        return cells, generator_by_node

    def get_voronoi_paths_cells(self, paths, nodes=None):
        cells = dict()              # Paths are the keys and the nodes are the elements of the cell.
        generator_by_node = dict()  # Nodes are the keys and the value is its corresponding closest path.
        # When None is indicated, the graph nodes are the default.
        if nodes is None:
            nodes_ = set(self.keys())
        else:
            nodes_ = set(nodes)
        # A priority queue is created. It will help retrieve the next farthest node to any shortest path.
        priority_dict = PriorityDictionary()
        # Paths are traversed in no specific order.
        # TODO: Perhaps a smarter way of traversing, e.g., based on distance, may be needed.
        for p in paths:
            if len(p) == 0:
                continue
            origin = p[0]
            destination = p[-1]
            # Cells are initialized.
            # A cell is identified by the path's origin and destination.
            cells[(origin, destination)] = list()
            for node in p:
                # Check whether the node is of interest.
                # In that case, since the node is part of the path, the distance is zero and the generator is such path.
                if node in nodes_:
                    priority_dict[node] = 0
                    generator_by_node[node] = (origin, destination)
        #
        distances = dict()
        for node in priority_dict:
            origin, destination = generator_by_node[node]
            # The closest path has been found for the current node.
            cells[(origin, destination)].append(node)
            # Store the associated shortest distance.
            distances[node] = priority_dict[node]
            # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
            if not self.node_weighted:
                adj_nodes = self[node]
            else:
                adj_nodes = self[node][1]
            # Traverse the adjacency list.
            for w, dist in adj_nodes.iteritems():
                vw_length = distances[node] + dist
                # In case w is of interest and has not been visited before...
                if w in nodes_ and w not in distances:
                    # If w's distance is improved, this distance and generator are updated.
                    if w not in priority_dict or vw_length < priority_dict[w]:
                        priority_dict[w] = vw_length
                        generator_by_node[w] = (origin, destination)

        return cells, generator_by_node

    def get_medoid(self, nodes):
        self.compute_dist_paths(origins=nodes, destinations=nodes, compute_paths=False)
        sums = dict()
        for v in nodes:
            sum_ = 0
            for w in nodes:
                if self.undirected:
                    sum_ += self.dist[tuple(sorted([v, w]))]
                else:
                    sum_ += self.dist[(v, w)]
            sums[v] = sum_
        return min(sums.iteritems(), key=operator.itemgetter(1))[0]

    def get_k_closest_destinations(self, n, k, destinations=None):
        if destinations is None:
            destinations_ = self.keys()
        else:
            destinations_ = list(destinations)
        distances = dict()
        for d in destinations_:
            if self.undirected:
                n_d = tuple(sorted([n, d]))
            else:
                n_d = (n, d)
            distances[d] = self.dist[n_d]
        sorted_dist = sorted(distances.iteritems(), key=operator.itemgetter(1))
        if k > len(sorted_dist):
            return sorted_dist
        return sorted_dist[:k]

    def __track_edges(self, path):
        origin = path[0]
        destination = path[-1]
        for i in range(len(path) - 1):
            x = path[i]
            y = path[i + 1]
            if self.undirected:
                x_y = tuple(sorted([x, y]))
            else:
                x_y = (x, y)
            try:
                self.__edges_in_sp[x_y].append((origin, destination))
            except KeyError:
                self.__edges_in_sp[x_y] = [(origin, destination)]

    def __dijkstra(self, origin, destinations=None, consider_node_weights=False, end_mode='all', compute_paths=True,
                   track_edges=False):

        distances = {}  # dictionary of final distances
        predecessors = {}  # dictionary of predecessors
        paths = {}  # dictionary of paths
        priority_queue = PriorityDictionary()  # est.dist. of non-final vert.
        priority_queue[origin] = 0

        if destinations is None:
            destinations = []
        reached_nodes = []

        for v in priority_queue:

            # When a node is retrieved from the priority queue, means that there is no shortest way to get to it.
            # Therefore, this distance is the final.
            distances[v] = priority_queue[v]

            if compute_paths or track_edges:
                if v in destinations:
                    path = []
                    w = v
                    while 1:
                        path.append(w)
                        if w == origin:
                            break
                        w = predecessors[w]
                    path.reverse()
                    paths[v] = path
                    if track_edges:
                        self.__track_edges(path)

            # if v == end:
            #     break
            if v in destinations:
                reached_nodes.append(v)
                if end_mode == 'all':
                    # When all the destinations have been reached...
                    if len(set(destinations) - set(reached_nodes)) == 0:
                        # Trim distances to nodes which are not in the list of destinations.
                        distances = {u: dist for u, dist in distances.iteritems() if u in destinations}
                        break
                elif end_mode == 'first':
                    # Trim distances to nodes which are not the first-reached destination.
                    distances = {u: dist for u, dist in distances.iteritems() if u == v}
                    break
                else:
                    raise (RuntimeError, "dijkstra: End mode has not been implemented!")

            # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
            if not self.node_weighted:
                adj_nodes = self[v]
            else:
                adj_nodes = self[v][1]

            # Traverse the adjacency list.
            for w, dist in adj_nodes.iteritems():
                vw_length = distances[v] + dist
                if self.node_weighted:
                    # In case node v is 'contracted', i.e., if v were telescoped, it would be a set of nodes instead,
                    # retrieves the shortest distance from one end to the other in the set of nodes represented by v.
                    # Both ends are the neighbour nodes of v and w that are within v.
                    internal_dist = 0
                    try:
                        if self[v][2]['contracted'] and v != origin:
                            dist_paths = self[v][2]['dist_paths']
                            dropped_edges = self[v][2]['dropped_edges']
                            n1 = dropped_edges[predecessors[v]]
                            n2 = dropped_edges[w]
                            try:
                                internal_dist = dist_paths[0][tuple(sorted([n1, n2]))]
                            except KeyError:
                                print "Something is wrong"
                    except KeyError:
                        pass
                    # When the graph is weighted, the weights of the nodes may be taken into account as part of the
                    # shortest distance computation.
                    if consider_node_weights:
                        vw_length += self[w][0]
                    vw_length += internal_dist
                # In case v-w shortest distance has already been computed.
                if w in distances:
                    if vw_length < distances[w]:
                        raise (ValueError, "Dijkstra: found better path to already-final vertex")
                # In case w has not been visited before or the current computed distance is better than the one computed
                # before.
                elif w not in priority_queue or vw_length < priority_queue[w]:
                    priority_queue[w] = vw_length
                    predecessors[w] = v

        if self.node_weighted and consider_node_weights:
            for v in distances:
                if v != origin:
                    distances[v] -= self[v][0]

        return distances, paths

    def __meet_in_the_middle(self, origin, destination, consider_node_weights=False, compute_path=True,
                             track_edges=False):

        distances = {0: {}, 1: {}}  # dictionary of final distances
        predecessors = {0: {}, 1: {}}  # dictionary of predecessors

        priority_dict = PriorityDictionary()  # est.dist. of non-final vert.

        # One priority queue where each entry's key informs which node the estimated distance is computed from.
        priority_dict[(0, origin)] = 0  # 0: from origin
        priority_dict[(1, destination)] = 0  # 1: from destination

        distance = sys.maxint
        path = []
        middle = None

        for end, v in priority_dict:

            # If the next node's distance is bigger than 1/2 the candidate shortest distance then such candidate is the
            # final shortest distance.
            if priority_dict[(end, v)] >= distance / 2.:
                if compute_path or track_edges:
                    # Build the path from the origin to the middle node.
                    w = middle
                    while 1:
                        path.append(w)
                        if w == origin:
                            break
                        w = predecessors[0][w]
                    path.reverse()
                    # Append the second half of the path, i.e., from the middle to the destination.
                    w = predecessors[1][middle]
                    while 1:
                        path.append(w)
                        if w == destination:
                            break
                        w = predecessors[1][w]
                    if track_edges:
                        self.__track_edges(path)
                break
            distances[end][v] = priority_dict[(end, v)]

            # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
            if not self.node_weighted:
                adj_nodes = self[v]
            else:
                adj_nodes = self[v][1]

            # Traverse the adjacency list.
            for w, dist in adj_nodes.iteritems():
                vw_length = distances[end][v] + dist
                # When a node from the other end has been reached, store the whole distance, i.e., distance from one end
                # plus distance from the other end, as candidate shortest distance.
                if w in distances[1 - end]:
                    temp = vw_length + distances[1 - end][w]
                    if temp < distance:
                        distance = temp
                        middle = w
                # In case v-w shortest distance has already been computed.
                if w in distances[end]:
                    if vw_length < distances[end][w]:
                        raise (ValueError, "Meet-in-the-middle: found better path to already-final vertex")
                # In case w has not been visited before or the current computed distance is better than the one computed
                # before.
                elif (end, w) not in priority_dict or vw_length < priority_dict[(end, w)]:
                    priority_dict[(end, w)] = vw_length
                    predecessors[end][w] = v
        return distance, path

    def explore_upto(self, starting, upper_bound):

        distances = {}  # dictionary of final distances
        priority_queue = PriorityDictionary()  # est.dist. of non-final vert.
        priority_queue[starting] = 0

        for v in priority_queue:
            if priority_queue[v] > upper_bound:
                break
            distances[v] = priority_queue[v]

            # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
            if not self.node_weighted:
                adj_nodes = self[v]
            else:
                adj_nodes = self[v][1]

            # Traverse the adjacency list.
            for w, dist in adj_nodes.iteritems():
                vw_length = distances[v] + dist
                # In case v-w shortest distance has already been computed.
                if w in distances:
                    if vw_length < distances[w]:
                        raise (ValueError, "Explore upto: found better path to already-final vertex")
                # In case w has not been visited before or the current computed distance is better than the one computed
                # before.
                elif w not in priority_queue or vw_length < priority_queue[w]:
                    priority_queue[w] = vw_length
        return distances

    # def nodes_within_ellipse_opt(self, focal_1, focal_2, constant):
    #
    #     ellipse = dict()
    #
    #     distances = {focal_1: {}, focal_2: {}}
    #     predecessors = {focal_1: {}, focal_2: {}}
    #
    #     priority_dict = PriorityDictionary()
    #     priority_dict[(focal_1, focal_1)] = 0
    #     priority_dict[(focal_2, focal_2)] = 0
    #
    #     iterations = 0
    #     flag = False
    #     discarded = set()
    #     for focal, v in priority_dict:
    #
    #         iterations += 1
    #
    #         if priority_dict[(focal, v)] > constant:
    #             break
    #         # if not flag and priority_dict[(focal, v)] > constant / 2.:
    #         #     for f, x in priority_dict.keys():
    #         #         if predecessors[f][x] not in ellipse:
    #         #             discarded.add((f, x))
    #         #     flag = True
    #
    #         # if priority_dict[(focal, v)] > constant / 2.:
    #         #     if predecessors[focal][v] not in ellipse:
    #         #         continue
    #
    #         # if flag and (focal, v) in discarded:
    #         #     continue
    #
    #         distances[focal][v] = priority_dict[(focal, v)]
    #
    #         other_focal = focal_1 if focal == focal_2 else focal_2
    #         if v in distances[other_focal]:
    #             if distances[focal][v] + distances[other_focal][v] <= constant:
    #                 ellipse[v] = {focal: distances[focal][v],
    #                               other_focal: distances[other_focal][v]
    #                               }
    #
    #         # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
    #         if not self.node_weighted:
    #             adj_nodes = self[v]
    #         else:
    #             adj_nodes = self[v][1]
    #
    #         for w, dist in adj_nodes.iteritems():
    #             vw_length = distances[focal][v] + dist
    #             if w not in distances[focal]:
    #                 if distances[focal][v] > constant / 2.:
    #                     if predecessors[focal][v] in ellipse:
    #                         if (focal, w) not in priority_dict or vw_length < priority_dict[(focal, w)]:
    #                             priority_dict[(focal, w)] = vw_length
    #                             predecessors[focal][w] = v
    #                     elif (focal, w) in priority_dict and vw_length < priority_dict[(focal, w)]:
    #                         priority_dict[(focal, w)] = vw_length
    #                         predecessors[focal][w] = v
    #                 elif (focal, w) not in priority_dict or vw_length < priority_dict[(focal, w)]:
    #                     priority_dict[(focal, w)] = vw_length
    #                     predecessors[focal][w] = v
    #
    #     return ellipse, iterations

    def nodes_within_ellipse(self, focal_1, focal_2, constant):

        ellipse = dict()

        distances = {focal_1: {}, focal_2: {}}

        priority_dict = PriorityDictionary()
        priority_dict[(focal_1, focal_1)] = 0
        priority_dict[(focal_2, focal_2)] = 0

        # iterations = 0
        for focal, v in priority_dict:

            # iterations += 1

            if priority_dict[(focal, v)] > constant:
                break

            distances[focal][v] = priority_dict[(focal, v)]

            other_focal = focal_1 if focal == focal_2 else focal_2

            if v in distances[other_focal]:
                if distances[focal][v] + distances[other_focal][v] <= constant:
                    ellipse[v] = {
                        focal: distances[focal][v],
                        other_focal: distances[other_focal][v]
                    }

            # How the adjacency list is retrieved depends upon whether the graph is node-weighted or not.
            if not self.node_weighted:
                adj_nodes = self[v]
            else:
                adj_nodes = self[v][1]

            for w, dist in adj_nodes.iteritems():
                vw_length = distances[focal][v] + dist
                if w not in distances[focal]:
                    if (focal, w) not in priority_dict or vw_length < priority_dict[(focal, w)]:
                        priority_dict[(focal, w)] = vw_length
        # return ellipse, iterations
        return ellipse