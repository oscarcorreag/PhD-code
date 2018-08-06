import numpy as np
import sys

from digraph import Digraph
from utils import id_generator, haversine


class SuitableNodeWeightGenerator:
    def __init__(self):

        self.weights = dict(VERY_SUITABLE=(10, '#C2C2C2', 1),  #13E853
                            SUITABLE=(20, '#00994D', 0.5),
                            ALMOST_SUITABLE=(30, '#BED062', 0.5),
                            WARNING=(40, '#FFFFCC', 0.5),
                            POSSIBLE_PROBLEMS=(50, '#FF9933', 0.5),
                            PROBLEMS=(60, '#EA6B66', 0.5),
                            FORGET_IT=(70, '#FF3333', 0.5))

        self.suitable_weights = [self.weights['VERY_SUITABLE'][0],
                                 self.weights['SUITABLE'][0],
                                 self.weights['ALMOST_SUITABLE'][0]]
        # self.suitable_weights = [self.weights['VERY_SUITABLE'][0],
        #                          self.weights['SUITABLE'][0]]

    def generate(self):
        rnd = np.random.ranf()
        # if rnd < 0.05:
        if rnd < 0.01:
            return self.weights['VERY_SUITABLE'][0]
        # elif rnd < 0.1:
        elif rnd < 0.03:
            return self.weights['SUITABLE'][0]
        # elif rnd < 0.15:
        elif rnd < 0.05:
            return self.weights['ALMOST_SUITABLE'][0]
        elif rnd < 0.55:
            return self.weights['WARNING'][0]
        elif rnd < 0.75:
            return self.weights['POSSIBLE_PROBLEMS'][0]
        elif rnd < 0.9:
            return self.weights['PROBLEMS'][0]
        else:
            return self.weights['FORGET_IT'][0]


class SuitabilityDigraph(Digraph):
    def __init__(self, **kwargs):
        super(SuitabilityDigraph, self).__init__(node_weighted=True, **kwargs)
        self.contracted_regions = {}
        self.auxiliary_nodes = set()

    def extend_suitable_regions(self, seed, generator):

        node_weighted = self.is_node_weighted()
        if not node_weighted:
            raise (RuntimeError, "Suitability Digraph: Can't extend suitable regions in a non-node-weighted digraph.")

        np.random.seed(seed)
        for v in self:
            node_weight = self[v][0]
            if node_weight in generator.suitable_weights:
                for w in self[v][1]:
                    if np.random.ranf() <= 0.1:  # probability that neighbour's suitability is changed
                        temp = list(self[w])
                        index = np.random.randint(0, len(generator.suitable_weights))
                        temp[0] = generator.suitable_weights[index]
                        self[w] = tuple(temp)

    def get_suitable_regions(self, generator, excluded_nodes=None, get_border_internal_nodes=True,
                             get_centroid_medoid=False, get_dist_paths_within_region=False):
        #
        node_weighted = self.is_node_weighted()
        if not node_weighted:
            raise (RuntimeError, "Suitability Digraph: Can't get suitable regions in a non-node-weighted digraph.")
        #
        if excluded_nodes is None:
            excluded_nodes = []
        #
        regions = {}
        nodes_in_regions = []
        for v in self:
            if v not in nodes_in_regions and v not in excluded_nodes:
                region = self.__add_node_to_suitable_region(v, SuitabilityDigraph(), generator, excluded_nodes)
                if len(region.keys()) > 1:
                    # if len(region.keys()) > 0:
                    nodes_in_regions.extend(region.keys())
                    #
                    border_nodes = None
                    internal_nodes = None
                    if get_border_internal_nodes:
                        border_nodes = self.__get_border_nodes_region(region)
                        internal_nodes = list(set(region.keys()) - set(border_nodes))
                    #
                    centroid = None
                    medoid = None
                    if get_centroid_medoid:
                        centroid, medoid = self.__get_centroid_medoid_node_region(region)
                    #
                    dist_paths = None
                    if get_dist_paths_within_region:
                        dist_paths = region.get_dist_paths(origins=region.keys(), destinations=region.keys())
                    #
                    id_r = id_generator()
                    regions[id_r] = (region, border_nodes, internal_nodes, centroid, medoid, dist_paths)
        return regions

    def __add_node_to_suitable_region(self, node, region, generator, excluded_nodes):
        if self[node][0] in generator.suitable_weights and node not in region:
            region[node] = (self[node][0], {}, self[node][2].copy())
            for w in self[node][1]:
                if w in excluded_nodes:
                    continue
                region = self.__add_node_to_suitable_region(w, region, generator, excluded_nodes)
                if w in region:
                    region[node][1][w] = self[node][1][w]
                    region[w][1][node] = self[w][1][node]
        return region

    def get_suitable_nodes(self, generator, degree_equals_to=None, degree_more_than=None, excluded_nodes=None):

        node_weighted = self.is_node_weighted()
        if not node_weighted:
            raise (RuntimeError, "Suitability Digraph: Can't get suitable nodes in a non-node-weighted digraph.")

        if excluded_nodes is None:
            excluded_nodes = []

        if degree_equals_to is not None:
            suitable_nodes = [v for v, value in self.items()
                              if value[0] in generator.suitable_weights and
                              len(value[1].keys()) == degree_equals_to and
                              v not in excluded_nodes]
        elif degree_more_than is not None:
            suitable_nodes = [v for v, value in self.items()
                              if value[0] in generator.suitable_weights and
                              len(value[1].keys()) > degree_more_than and
                              v not in excluded_nodes]
        else:
            suitable_nodes = [v for v, value in self.items()
                              if value[0] in generator.suitable_weights and
                              v not in excluded_nodes]

        return suitable_nodes

    def set_suitable_nodes(self, generator, nodes):
        weights = {h: generator.suitable_weights[0] for h in nodes}
        self.update_node_weights(weights)

    def __get_border_nodes_region(self, region):
        border_nodes = []
        for v in region:
            for w in self[v][1]:
                if w not in region:
                    border_nodes.append(v)
                    break
        return border_nodes

    @staticmethod
    def __get_centroid_medoid_node_region(region):
        lat_tot = lon_tot = 0
        for v in region:
            lat_tot += region[v][2]['lat']
            lon_tot += region[v][2]['lon']
        lat_centroid = lat_tot / len(region.keys())
        lon_centroid = lon_tot / len(region.keys())
        min_distance = sys.maxint
        medoid = None
        for v in region:
            dist = haversine(region[v][2]['lat'], region[v][2]['lon'], lat_centroid, lon_centroid)
            if dist < min_distance:
                min_distance = dist
                medoid = v
        return (lat_centroid, lon_centroid), medoid

    def contract_suitable_regions(self, generator, excluded_nodes=None, get_centroid_medoid=False):
        self.contracted_regions = self.get_suitable_regions(generator, excluded_nodes, get_border_internal_nodes=True,
                                                            get_centroid_medoid=get_centroid_medoid,
                                                            get_dist_paths_within_region=True)
        # When an adjacent node to a region has more than one neighbour within the region, an auxiliary node is created
        # for every edge between this adjacent node and the region.
        # For each region...
        for region_id, (region, border_nodes, _, _, _, dist_paths) in self.contracted_regions.items():
            # Create a dictionary of adjacent nodes with their corresponding border nodes of the region.
            adj_nodes_to_region = {}
            for bn in border_nodes:
                for adj_node in self[bn][1].keys():
                    if adj_node not in region:
                        if adj_node not in adj_nodes_to_region:
                            adj_nodes_to_region[adj_node] = [bn]
                        else:
                            adj_nodes_to_region[adj_node].append(bn)
            # Create a new region node in the graph. Distances and paths between the nodes of the region are saved.
            self[region_id] = (
                generator.weights["VERY_SUITABLE"][0], {}, {'contracted': True, 'dist_paths': dist_paths})
            # Wire the adjacent nodes with the new nodes (region nodes or auxiliary nodes).
            dropped_edges = {}
            for adj_node, bns in adj_nodes_to_region.items():
                # When an adjacent node has only one neighbour in the region...
                if len(bns) == 1:
                    # Wire the adjacent node with the new region node and drop the edge between the adjacent node and
                    # the only neighbour in the region.
                    self[adj_node][1][region_id] = self[adj_node][1][bns[0]]
                    self[region_id][1][adj_node] = self[adj_node][1][bns[0]]
                    del self[adj_node][1][bns[0]]
                    dropped_edges[adj_node] = bns[0]
                else:  # When it has more than one...
                    # For each neighbour in the region...
                    for bn in bns:
                        # Auxiliary nodes are needed when an adjacent node has more than one neighbour in the region.
                        new_node_id = id_generator()
                        self[new_node_id] = (generator.weights["WARNING"][0], {}, {})
                        # Wire the adjacent node with the new auxiliary node.
                        self[adj_node][1][new_node_id] = self[adj_node][1][bn]
                        self[new_node_id][1][adj_node] = self[adj_node][1][bn]
                        # Wire the auxiliary node with the region.
                        self[region_id][1][new_node_id] = 0
                        self[new_node_id][1][region_id] = 0
                        # A list of the new created auxiliary nodes is saved.
                        self.auxiliary_nodes.add(new_node_id)
                        # Drop the edge between the adjacent node and this neighbour in the region.
                        del self[adj_node][1][bn]
                        dropped_edges[new_node_id] = bn
            # Save dropped edges in new region node.
            self[region_id][2]['dropped_edges'] = dropped_edges
            # Drop nodes from the graph.
            for w in region:
                del self[w]

    def get_suitable_nodes_within_convex_set(self, convex_set, generator, dist_paths=None):
        list_1 = set()
        list_2 = list(convex_set)

        while len(list_2) > 0:
            temp = set()
            if dist_paths is not None:
                for i in list_1:
                    paths_i_ = [dist_paths[i][1][j] for j in list_2]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self[n][0] in generator.suitable_weights:
                                temp.add(n)
                for i in range(len(list_2) - 1):
                    paths_i_ = [dist_paths[list_2[i]][1][j] for j in list_2[i + 1:]]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self[n][0] in generator.suitable_weights:
                                temp.add(n)
            else:
                for i in list_1:
                    _, paths_i = self.__dijkstra(i, list_2)
                    paths_i_ = [paths_i[j] for j in list_2]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self[n][0] in generator.suitable_weights:
                                temp.add(n)
                for i in range(len(list_2) - 1):
                    _, paths_i = self.__dijkstra(list_2[i], list_2[i + 1:])
                    paths_i_ = [paths_i[j] for j in list_2[i + 1:]]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self[n][0] in generator.suitable_weights:
                                temp.add(n)
            list_1.update(list_2)
            list_2 = list(temp)
        return list(list_1 - set(convex_set))

    def build_suitability_metric_closure(self, generator, included_nodes=None, excluded_edges=None):
        if included_nodes is None:
            included_nodes = []
        nodes = set(self.get_suitable_nodes(generator))
        nodes.update(included_nodes)
        nodes = list(nodes)
        metric_closure = super(SuitabilityDigraph, self).build_metric_closure(nodes, excluded_edges)
        return metric_closure

    def build_subgraph_from_metric_closure(self, metric_closure):
        subgraph = SuitabilityDigraph()
        visited_edges = set()
        node_weighted = metric_closure.is_node_weighted()
        if node_weighted:
            for v in metric_closure:
                ends = []
                for w in metric_closure[v][1]:
                    if tuple(sorted([v, w])) not in visited_edges:
                        ends.append(w)
                _, paths = self.__dijkstra(v, ends)
                for p in [paths[n] for n in ends]:
                    subgraph.append_from_path(p, self)
        else:
            for v in metric_closure:
                ends = []
                for w in metric_closure[v]:
                    if tuple(sorted([v, w])) not in visited_edges:
                        ends.append(w)
                _, paths = self.__dijkstra(v, ends)
                for p in [paths[n] for n in ends]:
                    subgraph.append_from_path(p, self)
        return subgraph

    def get_dist_paths_between_regions(self, generator, method='dijkstra', exc_wcr=None, inc_wcp=None,
                                       within_region=False):
        dist = {}
        paths = {}
        #
        regions = self.get_suitable_regions(generator=generator, excluded_nodes=exc_wcr,
                                            get_dist_paths_within_region=within_region)
        #
        if inc_wcp is None:
            inc_wcp = []
        for n in inc_wcp:
            regions[n] = (None, [n])
        #
        if method == 'dijkstra':
            id_regions = regions.keys()
            no_regions = len(id_regions)
            for i in range(no_regions):
                id_r = id_regions[i]
                bn_0 = regions[id_r][1]
                for other_id in id_regions[i:]:
                    if id_r != other_id:
                        bn_1 = regions[other_id][1]
                        ds_rr = []
                        for v in bn_0:
                            ds, _ = self.__dijkstra(v, bn_1, compute_paths=False, end_mode='first')
                            dm = sys.maxint
                            wm = None
                            for w in bn_1:
                                try:
                                    d = ds[w]
                                except KeyError:
                                    d = sys.maxint
                                if d < dm:
                                    dm = d
                                    wm = w
                            ds_rr.append((dm, v, wm))
                        dmin, vmin, wmin = min(ds_rr)
                        _, p = self.__dijkstra(vmin, [wmin])
                        try:
                            pmin = p[wmin]
                        except KeyError:
                            pmin = []
                        #
                    else:
                        dmin, vmin, wmin, pmin = 0, id_r, id_r, []
                    r0r1_vw = sorted([(id_r, vmin), (other_id, wmin)])
                    id_ = tuple([r0r1_vw[0][0], r0r1_vw[1][0]])
                    dist[id_] = (dmin, r0r1_vw[0][1], r0r1_vw[1][1])
                    paths[id_] = pmin
        else:
            raise (RuntimeError, "Suitability Digraph: No other method except Dijkstra has been implemented!")
        #
        for n in inc_wcp:
            del regions[n]
        #
        return dist, paths, regions

    def copy(self):
        new_graph = super(SuitabilityDigraph, self).copy()
        new_graph.__class__ = SuitabilityDigraph
        new_graph.contracted_regions = self.contracted_regions.copy()
        return new_graph

