from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import CsdpAp

if __name__ == '__main__':
    m = n = 10
    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=True)
    ngh = NetworkXGraphHelper(graph)
    # graph.perturb_edge_weights()
    requests = [([(3, 1, 300), (27, 1, 300)], (38, 1, 300)), ([(12, 1, 300), (68, 1, 300), (63, 1, 300)], (45, 1, 300))]
    vehicles = [((6, 1, 300), (29, 1, 300)), ((78, 1, 300), (54, 1, 300))]
    csdp_ap = CsdpAp(graph)
    # routes = csdp_ap.solve(requests, vehicles)
    # csdp_ap.print_milp_constraints()
    # if routes is not None:
    #     ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 45], None, 65), ([6, 29, 78, 54], None, 65)],
    #                    special_subgraphs=[(routes, None)],
    #                    title_1="Exact solution",
    #                    # title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", elapsed time: " + str(elapsed_time),
    #                    print_node_labels=True,
    #                    print_edge_labels=False)
    routes = csdp_ap.solve(requests, vehicles, method="SP-based")
    ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 45], None, 65), ([6, 29, 78, 54], None, 65)],
                   special_subgraphs=[(routes, None)],
                   title_1="Exact solution",
                   # title_2="Cost: " + str(cost) + ", Gain ratio: " + str(gr) + ", elapsed time: " + str(elapsed_time),
                   print_node_labels=True,
                   print_edge_labels=False)
