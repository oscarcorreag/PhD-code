from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import CsdpAp


if __name__ == '__main__':
    # Generate the graph.
    m = n = 10
    gh = GridDigraphGenerator()
    graph = gh.generate(m, n, edge_weighted=False)
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
    # CSDP-AP and plot objects.
    csdp_ap = CsdpAp(graph)
    ngh = NetworkXGraphHelper(graph)

    # ------------------------------------------------------------------------------------------------------------------
    # MILP
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles)
    ss = ngh.special_subgraphs_from_paths(routes)
    if routes is not None:
        ngh.draw_graph(
            special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 24], None, 65), ([6, 29, 78, 54], None, 65)],
            special_subgraphs=ss,
            title_1="MILP solution",
            title_2="Cost: %f" % cost,
            print_node_labels=True,
            print_edge_labels=False)
    # ------------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles, method="SP-based", fraction_sd=.5)
    ss = ngh.special_subgraphs_from_paths(routes)
    ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 24], None, 65), ([6, 29, 78, 54], None, 65)],
                   special_subgraphs=ss,
                   title_1="SP-based solution -> fraction: 0.5",
                   title_2="Cost: %f" % cost,
                   print_node_labels=True,
                   print_edge_labels=False)

    requests = [
        ([(3, 1, 300), (27, 1, 300)], (38, 1, 300)),
        ([(12, 1, 300), (68, 1, 300), (63, 1, 300)], (55, 1, 300)),
        ([(3, 1, 300), (27, 1, 300)], (2, 1, 300)),
        ([(3, 1, 300), (27, 1, 300)], (24, 1, 300)),
    ]
    # ------------------------------------------------------------------------------------------------------------------
    # MILP
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles)
    ss = ngh.special_subgraphs_from_paths(routes)
    if routes is not None:
        ngh.draw_graph(
            special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 2, 24], None, 65), ([6, 29, 78, 54], None, 65)],
            special_subgraphs=ss,
            title_1="MILP solution",
            title_2="Cost: %f" % cost,
            print_node_labels=True,
            print_edge_labels=False)
    # ------------------------------------------------------------------------------------------------------------------
    # MILP-threshold = 1.5
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles, method='MILP-threshold')
    ss = ngh.special_subgraphs_from_paths(routes)
    if routes is not None:
        ngh.draw_graph(
            special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 2, 24], None, 65), ([6, 29, 78, 54], None, 65)],
            special_subgraphs=ss,
            title_1="MILP solution",
            title_2="Cost: %f" % cost,
            print_node_labels=True,
            print_edge_labels=False)
