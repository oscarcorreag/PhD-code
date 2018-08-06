from grid_digraph_generator import GridDigraphGenerator
from steiner_forest_lp import SteinerForestLP
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':
    gh = GridDigraphGenerator()
    # graph = gh.generate(10, 10, edge_weighted=False)
    # requests = [[27, 22, 55], [35, 63, 76]]
    graph = gh.generate(5, 5, edge_weighted=False)
    requests = [[21, 11, 18], [4, 3, 6]]

    sf = SteinerForestLP(graph, requests)
    forest = sf.steiner_forest()
    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(requests[0], '#000000', 50),
                                  (requests[1], '#0000FF', 50)],
                   special_subgraphs=[(forest, None)],
                   print_node_labels=True)
