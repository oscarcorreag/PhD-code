from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus import Dreyfus


if __name__ == '__main__':

    m = n = 10

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n, edge_weighted=False)

    df = Dreyfus(node_weighted)
    for v in range(m * n):
        ecc, inc = node_weighted.steiner_n_stats(3, v, df)
        print(ecc, inc)

    ngh = NetworkXGraphHelper(node_weighted)
    ngh.draw_graph(print_node_labels=True, node_size=15)
