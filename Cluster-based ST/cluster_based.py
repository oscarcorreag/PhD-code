from suitability import SuitabilityGraph, SuitableNodeWeightGenerator
from dreyfus_imr import DreyfusIMR


class ClusterBased:
    def __init__(self, graph, terminals):
        # Check whether graph is node-weighted.
        if not graph.is_node_weighted():
            raise (ValueError, "Cluster-based algorithm only works with node-weighted graphs.")
        # Extract POI from the terminals list.
        if len(terminals) > 0:
            self.__poi = terminals[0]
        else:
            return
        #
        generator = SuitableNodeWeightGenerator()
        # Set object variables.
        self.__graph = SuitabilityGraph()
        self.__graph.append_graph(graph)
        self.__terminals = terminals
        #
        # self.__regions = self.__graph.get_suitable_regions(generator, excluded_nodes=terminals,
        #                                             get_border_internal_nodes=True, get_centroid_medoid=True,
        #                                             get_characteristic_nodes=True)
        self.__regions = self.__graph.get_suitable_regions(generator, excluded_nodes=terminals,
                                                           get_border_internal_nodes=True, get_centroid_medoid=True)
        #
        self.__nodes = []
        for id_r in self.__regions:
            #
            # characteristic_nodes = self.__regions[id_r][6]
            # self.__nodes.extend(characteristic_nodes)
            border_nodes = self.__regions[id_r][1]
            self.__nodes.extend(border_nodes)
            #
            # if len(characteristic_nodes) == 0:
            # medoid = self.__regions[id_r][4]
            # # print(medoid)
            # self.__nodes.append(medoid)
        for t in terminals:
            self.__nodes.append(t)
        #
        self.__dist, self.__paths = self.__graph.get_dist_paths(origins=self.__nodes, destinations=self.__nodes)

    '''

    '''

    def steiner_tree(self, consider_terminals=False):

        dr = DreyfusIMR(graph=self.__graph, terminals=self.__terminals, contract_graph=False, nodes=self.__nodes,
                        dist_paths=(self.__dist, self.__paths))
        if consider_terminals:
            steiner_tree = dr.steiner_tree(consider_terminals=True)
        else:
            steiner_tree = dr.steiner_tree(consider_terminals=False)
        # self.__refine_steiner_tree(steiner_tree)
        return steiner_tree

    '''

    '''

    def __refine_steiner_tree(self, steiner_tree):
        clusters = []
        for id_r in self.__regions:
            region = self.__regions[id_r][0]
            for n in steiner_tree:
                if n in region:
                    clusters.append(id_r)
                    break
        print clusters