from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import sample, CsdpAp
from random import shuffle


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


if __name__ == '__main__':
    # # ------------------------------------------------------------------------------------------------------------------
    # # REQUESTS ARE DEFINED
    # # ------------------------------------------------------------------------------------------------------------------
    # Show the initial set up.
    generator = GridDigraphGenerator()
    m = 40
    n = 40
    fraction_sd = .5
    graph = generator.generate(m, n, edge_weighted=True)
    helper = NetworkXGraphHelper(graph)
    #
    # rs = [
    #     ([(691, 1, 300), (603, 1, 300)], (398, 1, 300)),
    #     # ([(719, 1, 300)], (445, 1, 300)),
    #     ([(718, 1, 300)], (445, 1, 300)),
    #     # ([(719, 1, 300)], (576, 1, 300)),
    #     ([(718, 1, 300)], (576, 1, 300)),
    # ]
    # # ss = {691: 1, 603: 1, 719: 2}
    # ss = {691: 1, 603: 1, 718: 2}
    # cs = {398: 1, 445: 2, 576: 2}
    # # cs = {398: 1, 410: 2, 576: 2}
    #
    # vs = [
    #     ((549, 1, 300), (535, 1, 300))
    # ]
    #
    # ss_by_g = {1: [691, 603], 2: [718]}
    # cs_by_g = {1: [398], 2: [445, 576]}
    #
    # special_nodes = list()
    # ec = list(element_colors)
    # shuffle(ec)
    # for ord_, (g, customers) in enumerate(cs_by_g.iteritems()):
    #     shops = ss_by_g[g]
    #     color = ec[ord_ % len(ec)]
    #     special_nodes.append((shops, color, 75))
    #     special_nodes.append((customers, color, 25))
    # starts = list()
    # ends = list()
    # for (start_v, _, _), (end_v, _, _) in vs:
    #     starts.append(start_v)
    #     ends.append(end_v)
    # special_nodes.extend([(starts, '#00FF00', 75), (ends, '#00FF00', 25)])
    #
    # helper.draw_graph(special_nodes=special_nodes, print_node_labels=True)
    #
    # # Show the shortest paths of the drivers.
    # pairs = [(start_v, end_v) for (start_v, _, _), (end_v, _, _) in vs]
    # graph.compute_dist_paths(pairs=pairs)
    #
    # paths = list()
    # for ord_, vehicle in enumerate(vs):
    #     (start_v, _, _), (end_v, _, _) = vehicle
    #     path = graph.paths[tuple(sorted([start_v, end_v]))]
    #     paths.append(path)
    # special_subgraphs = helper.special_subgraphs_from_paths(paths)
    # helper.draw_graph(special_nodes=special_nodes, special_subgraphs=special_subgraphs)
    #
    # # Show the expansion.
    # special_nodes_and_expansion = list(special_nodes)
    # shuffle(ec)
    # for ord_, vehicle in enumerate(vs):
    #     (start_v, _, _), (end_v, _, _) = vehicle
    #     dist = graph.dist[tuple(sorted([start_v, end_v]))]
    #     path = graph.paths[tuple(sorted([start_v, end_v]))]
    #     vertices_region = set()
    #     for n in path:
    #         dists = graph.explore_upto(n, dist * fraction_sd)
    #         vertices_region.update(dists.keys())
    #     color = ec[ord_ % len(ec)]
    #     special_nodes_and_expansion.insert(0, (vertices_region, color, 15))
    # helper.draw_graph(special_nodes=special_nodes_and_expansion)
    #
    # # Show a solution with the SP-based approach.
    # csdp_ap = CsdpAp(graph)
    # routes, cost = csdp_ap.solve(rs, vs, method="SP-based", fraction_sd=fraction_sd)
    # # routes, cost = csdp_ap.solve(rs, vs, method="SP-based", partition_method='SP-Voronoi')
    #
    # special_subgraphs = helper.special_subgraphs_from_paths(routes)
    # helper.draw_graph(special_nodes=special_nodes, special_subgraphs=special_subgraphs)

    # ------------------------------------------------------------------------------------------------------------------
    # REQUESTS ARE RANDOM
    # ------------------------------------------------------------------------------------------------------------------
    # Show the initial set up.
    rs, ss, cs, vs = sample(nc=5, ng=2, min_s=10, max_s=10, nv=10, vertices=graph.keys(), seed=0)

    ss_by_g = dict()
    for s, g in ss.iteritems():
        try:
            ss_by_g[g].append(s)
        except KeyError:
            ss_by_g[g] = [s]

    cs_by_g = dict()
    for c, g in cs.iteritems():
        try:
            cs_by_g[g].append(c)
        except KeyError:
            cs_by_g[g] = [c]

    special_nodes = list()
    # ec = list(element_colors)
    # shuffle(ec)
    # for ord_, (g, customers) in enumerate(cs_by_g.iteritems()):
    #     shops = ss_by_g[g]
    #     color = ec[ord_ % len(ec)]
    #     special_nodes.append((shops, color, 75))
    #     special_nodes.append((customers, color, 25))
    starts = list()
    ends = list()
    for (start_v, _, _), (end_v, _, _) in vs:
        starts.append(start_v)
        ends.append(end_v)
    special_nodes.extend([(starts, '#00FF00', 75), (ends, '#00FF00', 25)])

    helper.draw_graph(special_nodes=special_nodes)

    # Show the shortest paths of the drivers.
    pairs = [(start_v, end_v) for (start_v, _, _), (end_v, _, _) in vs]
    graph.compute_dist_paths(pairs=pairs)

    paths = list()
    for ord_, vehicle in enumerate(vs):
        (start_v, _, _), (end_v, _, _) = vehicle
        path = graph.paths[tuple(sorted([start_v, end_v]))]
        paths.append(path)

    cells, _ = graph.get_voronoi_paths_cells(paths)
    special_nodes_and_expansion = list(special_nodes)
    for (start_v, end_v), vertices in cells.iteritems():
        # color = ec[ord_ % len(ec)]
        special_nodes_and_expansion.insert(0, (vertices, None, 15))

    special_subgraphs = helper.special_subgraphs_from_paths(paths)
    helper.draw_graph(special_nodes=special_nodes_and_expansion, special_subgraphs=special_subgraphs)

    # # Show the expansion.
    # cells, _ = graph.get_voronoi_paths_cells(paths)
    # special_nodes_and_expansion = list(special_nodes)
    # shuffle(ec)
    # for ord_, vehicle in enumerate(vs):
    #     (start_v, _, _), (end_v, _, _) = vehicle
    #     dist = graph.dist[tuple(sorted([start_v, end_v]))]
    #     path = graph.paths[tuple(sorted([start_v, end_v]))]
    #     vertices_region = set()
    #     for n in path:
    #         dists = graph.explore_upto(n, dist * fraction_sd)
    #         vertices_region.update(dists.keys())
    #     color = ec[ord_ % len(ec)]
    #     special_nodes_and_expansion.insert(0, (vertices_region, color, 15))
    # helper.draw_graph(special_nodes=special_nodes_and_expansion)
    #
    # # Show a solution with the SP-based approach.
    # csdp_ap = CsdpAp(graph)
    # routes, cost = csdp_ap.solve(rs, vs, method="SP-based", fraction_sd=fraction_sd)
    #
    # special_subgraphs = helper.special_subgraphs_from_paths(routes)
    # helper.draw_graph(special_nodes=special_nodes, special_subgraphs=special_subgraphs)
