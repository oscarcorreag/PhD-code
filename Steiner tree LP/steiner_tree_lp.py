class SteinerTreeLP:
    def __init__(self, graph, terminals, poi):

        vars_ = []

        b_eq = []
        c = []

        # arcs = graph.get_edges()
        # arcs.update({(j, i): d for (i, j), d in arcs.items()})
        #
        # for (i, j), c_ij in arcs.items():
        #     vars.append((i, j))
        #     c.append(c_ij)
        #     for k in terminals:
        #         vars.append((i, j, k))
        #         c.append(0)

        eq_constraints = []

        for i in graph:
            if not graph.is_node_weighted():
                adj_nodes = graph[i]
            else:
                adj_nodes = graph[i][1]
            coefficients = {}
            for j in adj_nodes:
                for k in terminals:
                    coefficients[(i, j, k)] = 1
                    coefficients[(j, i, k)] = -1


        # node_weighted = graph.is_node_weighted()
        # for v in graph:
        #     if not node_weighted:
        #         adj_nodes = graph[v]
        #     else:
        #         adj_nodes = graph[v][1]
        #     constraint = {}
        #     for w, dist in adj_nodes.items():