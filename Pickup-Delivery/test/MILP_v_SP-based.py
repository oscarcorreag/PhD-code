from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import CsdpAp, sample
from utils import id_generator


element_colors = ['#000000',
                  '#0000FF',
                  '#13E853',
                  '#FF0000',
                  '#E67E22',
                  '#9B59B6',
                  '#2980B9',
                  '#1ABC9C',
                  '#27AE60',
                  '#F1C40F',
                  '#7F8C8D',
                  '#C0392B',
                  '#E74C3C',
                  '#8E44AD',
                  '#3498DB',
                  '#16A085',
                  '#2ECC71',
                  '#F39C12',
                  '#D35400'
                  ]


def process_requests(requests):
    customers_by_shops = dict()
    for shops_tws, (customer, _, _) in requests:
        ss = tuple(sorted([shop for shop, _, _ in shops_tws]))
        try:
            customers_by_shops[ss].add(customer)
        except KeyError:
            customers_by_shops[ss] = {customer}
    #
    shops_ = set()
    customers_ = set()
    shops_dict = dict()
    customers_dict = dict()
    shops_by_group_id = dict()
    customers_by_group_id = dict()
    for ss, cs in customers_by_shops.iteritems():
        shops_.update(ss)
        customers_.update(cs)
        #
        group_id = id_generator()
        shops_dict.update({shop: group_id for shop in ss})
        customers_dict.update({customer: group_id for customer in cs})
        shops_by_group_id[group_id] = ss
        customers_by_group_id[group_id] = cs
    return shops_, customers_, shops_dict, customers_dict, shops_by_group_id, customers_by_group_id


def format_special_nodes(shops_by_group_id, customers_by_group_id, drivers):
    special_nodes_ = list()
    #
    ec = list(element_colors)
    for ord_, (g, customers) in enumerate(customers_by_group_id.iteritems()):
        shops = shops_by_group_id[g]
        color = ec[ord_ % len(ec)]
        special_nodes_.append((shops, color, 100))
        special_nodes_.append((customers, color, 25))
    #
    starts = list()
    ends = list()
    for (start_v, _, _), (end_v, _, _) in drivers:
        starts.append(start_v)
        ends.append(end_v)
    special_nodes_.extend([(starts, '#00FF00', 75), (ends, '#00FF00', 50)])
    return special_nodes_


if __name__ == '__main__':
    # ------------------------------------------------------------------------------------------------------------------
    # REQUESTS ARE DEFINED
    # ------------------------------------------------------------------------------------------------------------------
    generator = GridDigraphGenerator()
    graph = generator.generate(30, 30, edge_weighted=True)
    helper = NetworkXGraphHelper(graph)
    csdp_ap = CsdpAp(graph)
    # --------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------
    # DETERMINISTIC REQUESTS
    # --------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------
    rs = [
        ([(691, 1, 300), (603, 1, 300)], (398, 1, 300)),
        ([(718, 1, 300)], (445, 1, 300)),
        ([(718, 1, 300)], (576, 1, 300)),
    ]
    ds = [((549, 1, 300), (535, 1, 300))]

    _, _, _, _, ss_by_g, cs_by_g = process_requests(rs)
    special_nodes = format_special_nodes(ss_by_g, cs_by_g, ds)
    # --------------------------------------------------------------------------------------------------------------
    # MILP
    # --------------------------------------------------------------------------------------------------------------
    # routes, cost = csdp_ap.solve(rs, ds)
    # special_subgraphs = helper.special_subgraphs_from_paths(routes)
    # helper.draw_graph(
    #     special_nodes=special_nodes,
    #     special_subgraphs=special_subgraphs,
    #     title_1="MILP",
    #     title_2="Cost: %f" % cost,
    # )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=0.5)
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-fraction' -> fraction_sd=0.5",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-Voronoi'
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-Voronoi'",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------
    # RANDOM REQUESTS
    # --------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------
    rs, ss, cs, ds = sample(nc=10, ng=3, min_s=5, max_s=10, nv=4, vertices=graph.keys(), seed=0)
    _, _, _, _, ss_by_g, cs_by_g = process_requests(rs)
    special_nodes = format_special_nodes(ss_by_g, cs_by_g, ds)
    # --------------------------------------------------------------------------------------------------------------
    # MILP
    # --------------------------------------------------------------------------------------------------------------
    # routes, cost = csdp_ap.solve(rs, ds)
    # special_subgraphs = helper.special_subgraphs_from_paths(routes)
    # helper.draw_graph(
    #     special_nodes=special_nodes,
    #     special_subgraphs=special_subgraphs,
    #     title_1="MILP",
    #     title_2="Cost: %f" % cost,
    # )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=0.5)
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-fraction' -> fraction_sd=0.5",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-Voronoi'
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-Voronoi'",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-threshold' -> threshold_sd=1.5
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-threshold' -> threshold_sd=1.5",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-threshold' -> threshold_sd=1.6
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.6)
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-threshold' -> threshold_sd=1.6",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-threshold' -> threshold_sd=1.9
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.9)
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-threshold' -> threshold_sd=1.9",
        title_2="Cost: %f" % cost,
    )
    # --------------------------------------------------------------------------------------------------------------
    # SP-based -> Partition='SP-threshold' -> threshold_sd=2.0
    # --------------------------------------------------------------------------------------------------------------
    routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=2.0)
    special_subgraphs = helper.special_subgraphs_from_paths(routes)
    helper.draw_graph(
        special_nodes=special_nodes,
        special_subgraphs=special_subgraphs,
        title_1="SP-based -> Partition='SP-threshold' -> threshold_sd=2.0",
        title_2="Cost: %f" % cost,
    )