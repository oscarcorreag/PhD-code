from grid_digraph_generator import GridDigraphGenerator
from dreyfus import Dreyfus
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    gh = GridDigraphGenerator()

    seed = 0
    m = 10
    n = 10

    graph = gh.generate(m, n, edge_weighted=False)
    terminals = [12, 88, 66, 77, 5, 33]

    dr = Dreyfus(graph)
    steiner_tree, cost = dr.steiner_tree(terminals, consider_terminals=False)

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[([terminals[0]], None, None), (terminals[1:], None, None)],
                   special_subgraphs=[(steiner_tree, None)],
                   title_1="Dreyfus algorithm (network graph), seed = " + str(seed),
                   title_2="Cost: " + str(cost))
