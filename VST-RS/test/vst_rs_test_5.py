import time

from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from vst_rs import VST_RS

if __name__ == '__main__':

    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)

    terminals = [88, 66, 77, 5, 33, 53, 71]
    pois = [65, 12]

    vst_rs = VST_RS(graph)
    start_time = time.clock()
    forest, cost, _, _, _, _, _ = vst_rs.steiner_forest(terminals, pois, 4, 8, merge_users=False)
    elapsed_time = time.clock() - start_time

    ngh = NetworkXGraphHelper(graph)
    ngh.draw_graph(special_nodes=[(pois, None, None), (terminals, None, None)],
                   special_subgraphs=[(forest, "#FF0000")],
                   title_1="VST-RS",
                   title_2="Cost: " + str(cost) + ", Elapsed, time: " + str(elapsed_time),
                   edge_labels=vst_rs.load,
                   print_edge_labels=True)
