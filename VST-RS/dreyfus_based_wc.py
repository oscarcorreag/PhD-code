class DreyfusBasedWC:

    def __init__(self, graph):
        self.__graph = graph.copy()
        self.__graph.compute_dist_paths(compute_paths=False)

    def steiner_forest(self, users, pois, z):
        return True
