from graph import dijkstra


class ConvexHull:

    def __init__(self, graph, terminals, poi, dist_paths_suitable_nodes_contracted_graph=None):
        self.__graph = graph
        self.__terminals = terminals
        self.__poi = poi

        terminals_poi = list(terminals)
        terminals_poi.append(poi)

        self.__dist_paths = None
        if dist_paths_suitable_nodes_contracted_graph is not None:
            self.__dist_paths = dict(dist_paths_suitable_nodes_contracted_graph)
            for e in terminals_poi:
                self.__dist_paths[e] = dijkstra(self.__graph, e)

    def compute(self, generator):

        # list_1 = set()
        # list_2 = list(self.__terminals)
        # if self.__poi not in list_2:
        #     list_2.append(self.__poi)
        #
        # while len(list_2) > 0:
        #     temp = set()
        #     for i in list_1:
        #         _, paths = dijkstra(self.__graph, i, list_2, consider_node_weights=False)
        #         paths_ = [paths[j] for j in list_2]
        #         for p in paths_:
        #             for n in p:
        #                 if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
        #                     temp.add(n)
        #     for i in range(len(list_2) - 1):
        #         _, paths = dijkstra(self.__graph, list_2[i], list_2[i + 1:], consider_node_weights=False)
        #         paths_ = [paths[j] for j in list_2[i + 1:]]
        #         for p in paths_:
        #             for n in p:
        #                 if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
        #                     temp.add(n)
        #     list_1.update(list_2)
        #     list_2 = list(temp)
        #
        # return list(list_1)

        list_1 = set()
        list_2 = list(self.__terminals)
        if self.__poi not in list_2:
            list_2.append(self.__poi)

        while len(list_2) > 0:
            temp = set()
            if self.__dist_paths is not None:
                for i in list_1:
                    paths_i_ = [self.__dist_paths[i][1][j] for j in list_2]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
                                temp.add(n)
                for i in range(len(list_2) - 1):
                    paths_i_ = [self.__dist_paths[list_2[i]][1][j] for j in list_2[i + 1:]]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
                                temp.add(n)
            else:
                for i in list_1:
                    _, paths_i = dijkstra(self, i, list_2)
                    paths_i_ = [paths_i[j] for j in list_2]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
                                temp.add(n)
                for i in range(len(list_2) - 1):
                    _, paths_i = dijkstra(self, list_2[i], list_2[i + 1:])
                    paths_i_ = [paths_i[j] for j in list_2[i + 1:]]
                    for p in paths_i_:
                        for n in p:
                            if n not in list_1 and n not in list_2 and self.__graph[n][0] in generator.suitable_weights:
                                temp.add(n)
            list_1.update(list_2)
            list_2 = list(temp)
        return list(list_1)
