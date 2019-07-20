from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import CsdpAp
from graph import Graph


def compute_route_cost(route, graph_):
    cost_ = 0
    for i_ in range(len(route) - 1):
        v = route[i_]
        w = route[i_ + 1]
        if v != w:
            cost_ += graph_.get_edges()[tuple(sorted([v, w]))]
    return cost_


def compute_stats_per_driver_type(routes_, graph_):
    #
    pairs = list()
    for route in routes_:
        pairs.append(tuple(sorted([route[0], route[-1]])))
    graph_.compute_dist_paths(pairs=pairs, compute_paths=False)
    #
    no_ad_hoc = 0
    no_dedicated = 0
    total_ad_hoc = 0
    total_dedicated = 0
    total_sd = 0
    costs_ad_hoc = list()
    total_detour = 0
    for route in routes_:
        s = route[0]
        e = route[-1]
        if s == e:
            no_dedicated += 1
            total_dedicated += compute_route_cost(route, graph_)
        else:
            no_ad_hoc += 1
            cost_ = compute_route_cost(route, graph_)
            total_ad_hoc += cost_
            sd = graph_.dist[tuple(sorted([s, e]))]
            total_sd += sd
            costs_ad_hoc.append(cost_)
            total_detour += cost_ / sd
    costs_ad_hoc = [c / total_sd for c in costs_ad_hoc]
    weighted_avg_detour = sum(costs_ad_hoc)
    stats_ = {
        'ad hoc': {
            'no': no_ad_hoc,
            'total': total_ad_hoc,
            'avg': (total_ad_hoc / no_ad_hoc) if no_ad_hoc > 0 else 0,
            'avg detour': (total_detour / no_ad_hoc) if no_ad_hoc > 0 else 0,
            'w avg detour': weighted_avg_detour,
        },
        'dedicated': {
            'no': no_dedicated,
            'total': total_dedicated,
            'avg': (total_dedicated / no_dedicated) if no_dedicated > 0 else 0,
        }
    }
    return stats_


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
    stats = compute_stats_per_driver_type(routes, graph)
    print stats
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
    # SP-based -> Partition='SP-fraction' -> fraction_sd=0.3
    # ------------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(requests, vehicles, method="SP-based", fraction_sd=.3, solve_unserved_method='double-tree')
    stats = compute_stats_per_driver_type(routes, graph)
    print stats
    ss = ngh.special_subgraphs_from_paths(routes)
    ngh.draw_graph(special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 24], None, 65),
                                  ([6, 29, 78, 54], None, 65)],
                   special_subgraphs=ss,
                   title_1="SP-based solution -> fraction: 0.3",
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
    stats = compute_stats_per_driver_type(routes, graph)
    print stats
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
    stats = compute_stats_per_driver_type(routes, graph)
    print stats
    ss = ngh.special_subgraphs_from_paths(routes)
    if routes is not None:
        ngh.draw_graph(
            special_nodes=[([3, 27, 12, 68, 63], None, 65), ([38, 55, 2, 24], None, 65), ([6, 29, 78, 54], None, 65)],
            special_subgraphs=ss,
            title_1="MILP solution",
            title_2="Cost: %f" % cost,
            print_node_labels=True,
            print_edge_labels=False)
