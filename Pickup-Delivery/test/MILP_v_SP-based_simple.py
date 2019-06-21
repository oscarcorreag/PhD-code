from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import CsdpAp


if __name__ == '__main__':

    # Generate the graph.
    m = n = 10
    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=True)

    # Setup the requests and vehicles.
    requests = [
        ([(3, 1, 300), (27, 1, 300)], (38, 1, 300)),
        ([(12, 1, 300), (68, 1, 300), (63, 1, 300)], (55, 1, 300)),
        ([(3, 1, 300), (27, 1, 300)], (24, 1, 300))
    ]
    vehicles = [
        ((6, 1, 300), (29, 1, 300)),
        ((78, 1, 300), (54, 1, 300))
    ]
    # requests = [
    #     ([(3, 1, 300)], (6, 1, 300)),
    #     ([(93, 1, 300)], (96, 1, 300)),
    # ]
    # vehicles = [
    #     ((1, 1, 300), (8, 1, 300)),
    #     ((91, 1, 300), (98, 1, 300))
    # ]

    # CSDP-AP and plot objects.
    csdp_ap = CsdpAp(graph)
    ngh = NetworkXGraphHelper(graph)

    # ------------------------------------------------------------------------------------------------------------------
    # MILP solution
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles)
    ss = ngh.special_subgraphs_from_paths(routes)
    # csdp_ap.print_milp_constraints()
    if routes is not None:
        ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 24], None, 65), ([6, 29, 78, 54], None, 65)],
                       special_subgraphs=ss,
                       title_1="MILP solution",
                       title_2="Cost: %f" % cost,
                       print_node_labels=True,
                       print_edge_labels=False)
        # ngh.draw_graph(
        #     special_nodes=[([3, 93], None, 65), ([6, 96], None, 65), ([1, 8, 91, 98], None, 65)],
        #     special_subgraphs=routes,
        #     title_1="MILP solution",
        #     print_node_labels=True,
        #     print_edge_labels=False)

    # ------------------------------------------------------------------------------------------------------------------
    # SP-based solution
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles, method="SP-based", fraction_sd=.5)
    ss = ngh.special_subgraphs_from_paths(routes)
    ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 24], None, 65), ([6, 29, 78, 54], None, 65)],
                   special_subgraphs=ss,
                   title_1="Sp-based solution",
                   title_2="Cost: %f" % cost,
                   print_node_labels=True,
                   print_edge_labels=False)
    # ngh.draw_graph(
    #     special_nodes=[([3, 93], None, 65), ([6, 96], None, 65), ([1, 8, 91, 98], None, 65)],
    #     special_subgraphs=routes,
    #     title_1="Sp-based solution",
    #     print_node_labels=True,
    #     print_edge_labels=False)
