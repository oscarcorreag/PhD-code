import sys
import operator
import numpy as np

from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator


class VoronoiBased:
    def __init__(self, graph, terminals, pois, use_betweenness=False, seed=0):
        # Init some instance variables.
        self.__graph = graph
        # self.__graph = SuitabilityDigraph()
        # self.__graph.append_from_graph(graph)
        self.__terminals = terminals
        self.__pois = pois
        # Temporal list to be excluded when getting suitable nodes.
        temp = list(terminals)
        temp.extend(pois)
        # Get suitable nodes.
        generator = SuitableNodeWeightGenerator()
        self.__nodes = self.__graph.get_suitable_nodes(generator, excluded_nodes=temp)
        temp.extend(self.__nodes)
        #
        # Compute distances between every node within set [temp]
        if len(self.__graph.pairs_dist_paths) == 0:
            self.__graph.compute_dist_paths(origins=temp, destinations=temp, compute_paths=False)
        # Compute P-Voronoi cells.
        _, self.__nodes_p_medoid = self.__get_voronoi_cells(self.__nodes, self.__pois)
        # Set the upper bound for the number of Steiner points.
        self.__num_medoids_ub = len(terminals) - 2
        # Seed for randomness within this object.
        np.random.seed(seed)
        # Compute vertex betweenness which may be used when computing S-Voronoi cells.
        self.__use_betweenness = use_betweenness
        self.__betweenness = []
        # if use_betweenness:
        #     s_betweenness = {n: 0 for n in temp}
        #     for n1 in temp:
        #         paths = self.__dist_paths[n1][1]
        #         for _, path in paths.iteritems():
        #             if len(path) > 2:
        #                 for n2 in path[1:-1]:
        #                     if n2 in temp:
        #                         s_betweenness[n2] += 1
        #     self.__betweenness = sorted(s_betweenness.iteritems(), key=operator.itemgetter(1), reverse=True)

    '''
    Return the minimal-cost Steiner forest after trying with different number of Steiner points. A Steiner point is the
    medoid of an S-Voronoi cell. The algorithm starts from [number of POIs]. The upper bound for this number is determi-
    ned by the fact that the number of degree-3 Steiner points is equal to the [number of terminals] - 2.
    '''

    def steiner_forest(self):
        forests = {}
        # Compute forests each time with different number of Steiner points and return the one with least cost.
        for sp in range(len(self.__pois), self.__num_medoids_ub + 1):
        # for sp in [3]:
            cost = 0
            forest = SuitabilityDigraph()
            # Compute as many S-Voronoi cells as [sp]
            s_cells = self.__get_s_cells(sp)
            for s, c in s_cells.iteritems():
                poi = self.__nodes_p_medoid[s]
                term_s_cell = set(c).intersection(self.__terminals)
                for t in term_s_cell:
                    k1 = tuple(sorted([t, poi]))
                    k2 = tuple(sorted([t, s]))
                    if self.__graph.dist[k1] < self.__graph.dist[k2] or len(term_s_cell) == 1:
                        self.__graph.compute_dist_paths(origins=[t], destinations=[poi], recompute=True)
                        forest.append_from_path(self.__graph.paths[tuple(sorted([t, poi]))], self.__graph)
                        cost += self.__graph.dist[k1]
                    else:
                        self.__graph.compute_dist_paths(origins=[t], destinations=[s], recompute=True)
                        forest.append_from_path(self.__graph.paths[tuple(sorted([t, s]))], self.__graph)
                        cost += self.__graph.dist[k2]
                k = tuple(sorted([s, poi]))
                self.__graph.compute_dist_paths(origins=[s], destinations=[poi], recompute=True)
                forest.append_from_path(self.__graph.paths[tuple(sorted([s, poi]))], self.__graph)
                cost += self.__graph.dist[k]
            # self.__prune_steiner_forest(forest)
            # cost, _ = forest.calculate_costs()
            forests[cost] = (forest, sp)
        return forests[min(forests)], min(forests)

    '''
    Compute k S-Voronoi cells where the medoids are suitable nodes chosen based on a heuristic.
    '''

    def __get_s_cells(self, k, max_iter=100):
        cells = {}
        # k-medoids are initialised according to the user's selection, i.e. using vertex betweenness or randomly chosen.
        if self.__use_betweenness:
            medoids = [m[0] for m in self.__betweenness[:k]]
        else:
            indices = np.random.choice(a=len(self.__nodes), size=k, replace=False)
            medoids = [self.__nodes[i] for i in indices]
        # Infinite loop until convergence is attained in less than [max_iter].
        while True:
            prev_medoids = []
            # Suitable nodes and terminals are included in the S-Voronoi cells.
            temp = list(self.__nodes)
            temp.extend(self.__terminals)
            iterations = 0
            # Convergence is attained when medoids do not change from the previous iteration after computing them for
            # each Voronoi cell.
            while len(set(prev_medoids).intersection(medoids)) != len(medoids) and iterations < max_iter:
                cells, _ = self.__get_voronoi_cells(temp, medoids)
                prev_medoids = list(medoids)
                medoids = [self.__get_suitable_medoid(c) for _, c in cells.iteritems()]
                iterations += 1
            # print iterations
            # When convergence was attained, loop is broken.
            if iterations < max_iter:
                break
            # Otherwise, the algorithm starts over with k randomly chosen medoids.
            indices = np.random.choice(a=len(self.__nodes), size=k, replace=False)
            medoids = [self.__nodes[i] for i in indices]
        return cells

    '''
    Compute Voronoi cells for a set of nodes and medoids as two dictionaries: (1) nodes by medoids, (2) medoids by node.
    '''

    def __get_voronoi_cells(self, nodes, medoids):
        cells = {m: [] for m in medoids}
        nodes_medoid = {}
        # Each node from the set [nodes] is assigned to its closest medoid.
        for n in nodes:
            dists = {m: self.__graph.dist[tuple(sorted([n, m]))] for m in medoids}
            medoid = min(dists.iteritems(), key=operator.itemgetter(1))[0]
            cells[medoid].append(n)  # Medoids are the keys and the nodes are the elements of the cell.
            nodes_medoid[n] = medoid  # Nodes are the keys and the value is its corresponding medoid.
        return cells, nodes_medoid

    '''
    The "best" suitable medoid will be chosen from the set of suitable nodes that belong to the S-Voronoi cell. This no-
    de will be the one with the least density. Density is the ratio between the cost of the star, formed by a POI, ter-
    minals in the S-Voronoi cell and the suitable node, and the number of these terminals. In a S-Voronoi cell may be
    more than one POI, so the POI that is included in the star is the medoid of the P-Voronoi cell to which the suitable
    node belongs. The terminals are the ones in the S-Voronoi cell whose distance to the suitable node is shorter than
    their distance to the POI (medoid of the P-Voronoi cell to which the suitable node belongs).
    '''

    def __get_suitable_medoid(self, s_cell):
        medoid = None
        set_cell = set(s_cell)
        # Get the suitable nodes and terminals that belong to the S-Voronoi cell.
        suitable_nodes_cell = set_cell.intersection(self.__nodes)
        terminals_cell = set_cell.intersection(self.__terminals)
        # Look for the "best" suitable node as medoid based on its density.
        min_density = sys.maxint
        for s in suitable_nodes_cell:
            # POI which is the medoid of the P-Voronoi cell to which the suitable node belongs.
            poi = self.__nodes_p_medoid[s]
            # Only terminals whose distance to the suitable node is shorter than their distance to the POI are included
            # in the star.
            temp = []
            for t in terminals_cell:
                k1 = tuple(sorted([t, poi]))
                k2 = tuple(sorted([t, s]))
                if self.__graph.dist[k1] > self.__graph.dist[k2]:
                    temp.append(t)
            # The POI is part of the star.
            temp.append(poi)
            if len(temp) == 1:  # It means that only the POI was included.
                continue
            dists = [self.__graph.dist[tuple(sorted([s, t]))] for t in temp]
            # Density is computed with respect to the terminals only, i.e. without POI.
            # density = sum(dists) / (len(temp) - 1)
            density = sum(dists) / len(temp)  # This is yielding less cost!, i.e. including POI.
            # Take the "best" density.
            if density < min_density:
                min_density = density
                medoid = s
        # If there is no such a "best" medoid, return a randomly chosen one.  :(
        if medoid is None:
            ind = np.random.choice(a=len(self.__nodes), size=1, replace=False)
            medoid = self.__nodes[ind]
        return medoid

    '''
    Prune the forest by cutting edges where leaves are not terminals neither POIs.
    '''

    def __prune_steiner_forest(self, forest):
        while True:
            keys_to_prune = []
            for n in forest:
                if n not in self.__terminals and n not in self.__pois:
                    neighbours = forest[n][1].keys()
                    if len(neighbours) == 1:
                        neighbour = neighbours[0]
                        del forest[neighbour][1][n]
                        keys_to_prune.append(n)
            if len(keys_to_prune) == 0:
                break
            for n in keys_to_prune:
                del forest[n]
