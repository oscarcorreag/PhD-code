import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus_based_woc import DreyfusBasedWOC

if __name__ == '__main__':

    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)

    terminals = [88, 66, 77, 5, 33, 53, 71]
    pois = [65, 12]

    db_woc = DreyfusBasedWOC(graph)
    start_time = time.clock()
    forest, cost = db_woc.steiner_forest(terminals, pois, 4, method="Voronoi")
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(pois, None, None), (terminals, None, None)],
                   special_subgraphs=[(forest, "#FF0000")],
                   title_1="Dreyfus-based",
                   title_2="Cost: " + str(cost) + ", Elapsed time: " + str(elapsed_time),
                   edge_labels=db_woc.congestion,
                   print_edge_labels=True)
