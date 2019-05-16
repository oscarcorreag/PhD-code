from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper
from csdp_ap import sample, CsdpAp
from digraph import Digraph

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
    # Show the initial set up.
    generator = GridDigraphGenerator()
    m = 30
    n = 35
    fraction_sd = .5
    graph = generator.generate(m, n, edge_weighted=False)
    helper = NetworkXGraphHelper(graph)
    # rs, ss, cs, vs = sample(nc=10, ng=1, min_s=10, max_s=10, nv=5, vertices=graph.keys(), seed=0)

    rs = [
        ([(691, 1, 300), (603, 1, 300)], (398, 1, 300)),
        ([(719, 1, 300)], (445, 1, 300)),
        ([(719, 1, 300)], (576, 1, 300)),
    ]
    ss = {691: 1, 603: 1, 719: 2}
    cs = {398: 1, 445: 2, 576: 2}

    vs = [
        ((549, 1, 300), (535, 1, 300))
    ]

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
    for ord_, (g, customers) in enumerate(cs_by_g.iteritems()):
        shops = ss_by_g[g]
        color = element_colors[ord_ % len(element_colors)]
        special_nodes.append((shops, color, 75))
        special_nodes.append((customers, color, 25))
    starts = list()
    ends = list()
    for (start_v, _, _), (end_v, _, _) in vs:
        starts.append(start_v)
        ends.append(end_v)
    special_nodes.extend([(starts, '#00FF00', 75), (ends, '#00FF00', 25)])

    helper.draw_graph(special_nodes=special_nodes, print_node_labels=True)

    # Show the shortest paths of the drivers.
    pairs = [(start_v, end_v) for (start_v, _, _), (end_v, _, _) in vs]
    graph.compute_dist_paths(pairs=pairs)

    special_subgraphs = list()
    for ord_, vehicle in enumerate(vs):
        (start_v, _, _), (end_v, _, _) = vehicle
        route = Digraph()
        path = graph.paths[tuple(sorted([start_v, end_v]))]
        route.append_from_path(path, graph)
        color = element_colors[ord_ % len(element_colors)]
        special_subgraphs.append((route, color))
    helper.draw_graph(special_nodes=special_nodes, special_subgraphs=special_subgraphs)

    # Show the expansion.
    for ord_, vehicle in enumerate(vs):
        (start_v, _, _), (end_v, _, _) = vehicle
        dist = graph.dist[tuple(sorted([start_v, end_v]))]
        path = graph.paths[tuple(sorted([start_v, end_v]))]
        vertices_region = set()
        for n in path:
            dists = graph.explore_upto(n, dist * fraction_sd)
            vertices_region.update(dists.keys())
        color = element_colors[ord_ % len(element_colors)]
        special_nodes.append((vertices_region, color, 15))
    helper.draw_graph(special_nodes=special_nodes)

    # Show a solution with the SP-based approach.
    csdp_ap = CsdpAp(graph)
    routes = csdp_ap.solve(rs, vs, method="SP-based", fraction_sd=fraction_sd)

    special_subgraphs = list()
    for ord_, path in enumerate(routes):
        route = Digraph()
        route.append_from_path(path, graph)
        color = element_colors[ord_ % len(element_colors)]
        special_subgraphs.append((route, color))
    helper.draw_graph(special_nodes=special_nodes, special_subgraphs=special_subgraphs)



    # Show the guarantees given to the driver.
    # Show the excluded customers as serving them may risk the guarantees given to the drivers.
    # Show the excluded shops as there are not customers in the driver's region.
    # Show the exact solution within the driver's region.
    # Show the overlapping case.