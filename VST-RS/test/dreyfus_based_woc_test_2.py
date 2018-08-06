import time
import numpy as np

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from dreyfus_based_woc import DreyfusBasedWOC

if __name__ == '__main__':

    m = n = 30

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)

    np.random.seed(0)
    terminals = np.random.choice(a=m * n, size=35, replace=False)
    pois = terminals[:5]
    terminals = terminals[5:]

    db_woc = DreyfusBasedWOC(graph)
    start_time = time.clock()
    forest, cost = db_woc.steiner_forest(terminals, pois, 4)
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(pois, None, None), (terminals, None, None)],
                   special_subgraphs=[(forest, "#FF0000")],
                   title_1="Dreyfus-based",
                   title_2="Cost: " + str(cost) + ", Elapsed time: " + str(elapsed_time),
                   edge_labels=db_woc.congestion,
                   print_edge_labels=True)
