from grid_digraph_generator import GridDigraphGenerator
from dreyfus import Dreyfus
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    gh = GridDigraphGenerator()

    seed = 0
    m = 10
    n = 10

    graph = gh.generate(m, n, edge_weighted=False)
    terminals = [64, 75, 56, 7, 35, 20, 49]

    dr = Dreyfus(graph)
    steiner_tree, cost = dr.steiner_tree(terminals, consider_terminals=False)

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(terminals[:5], None, 35), (terminals[5:], None, 65)],
                   special_subgraphs=[(steiner_tree, None)],
                   title_1="Dreyfus algorithm (network graph), seed = " + str(seed),
                   title_2="Cost: " + str(cost))
