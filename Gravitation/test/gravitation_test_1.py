from digraph import Digraph
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    gh = GridDigraphGenerator()
    graph = gh.generate(5, 5, edge_weighted=False)

    graph[18][19] = graph[19][18] = 0.5
    graph[1][6] = graph[6][1] = 0.5

    graph.compute_dist_paths()

    subtree_1 = Digraph()
    subtree_1.append_from_path(graph.paths[(0, 12)], graph)

    subtree_2 = Digraph()
    subtree_2.append_from_path(graph.paths[(4, 12)], graph)

    subtree_3 = Digraph()
    subtree_3.append_from_path(graph.paths[(12, 20)], graph)

    subtree_4 = Digraph()
    subtree_4.append_from_path(graph.paths[(12, 24)], graph)

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_subgraphs=[(subtree_1, None), (subtree_2, None), (subtree_3, None), (subtree_4, None)],
                   print_node_labels=True)
