import operator
import gmplot
import time

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState
from csdp_ap import CsdpAp
from graph import Graph


element_colors = ['#13E853',
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


def get_routes_map(routes_, graph_):
    routes_map_ = list()
    for i_, route in enumerate(routes_):
        lats_ = list()
        lons_ = list()
        for v in route:
            lats_.append(graph_[v][2]['lat'])
            lons_.append(graph_[v][2]['lon'])
        routes_map_.append((lats_, lons_))
    return routes_map_


if __name__ == '__main__':
    #
    osm = OsmManager()
    generator = SuitableNodeWeightGenerator()
    #
    regions = {
        'MEL': (
            [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727],
            {'COLES': 0.326, 'WOOLWORTHS': 0.39, 'ALDI': 0.164, 'IGA': 0.12}
        ),
        # 'UIO': (
        #     [-78.57160966654635, -0.4180073651030667, -78.36973588724948, -0.06610523586538203],
        #     ['LA FAVORITA', 'SANTA MARIA', 'MI COMISARIATO']
        # ),
        # 'MHT': (
        #     [-74.0326191484375, 40.69502239217181, -73.93236890429688, 40.845827729757275],
        #     ['WALMART', 'TARGET', 'COSTCO']
        # ),
    }
    #
    delta_meters = 10000.0
    delta = delta_meters / 111111
    num_samples = 1
    # num_customers_r = [10, 100, 1000]
    num_customers_r = [256]
    # ratios = [1.5, 2.0, 2.5, 3.0]
    ratios = [4.0]
    fractions = [0.1]
    # thresholds = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    thresholds = []
    driver_locations = ['Z-U']
    max_loads = [8]
    bounds = 'both'
    approaches = ['IRB-BB']
    #
    results = []
    sample = 0
    seed = 200
    for region, info in regions.iteritems():
        while sample < num_samples:
            #
            seed += 1
            rnd = RandomState(seed)
            # Compute bbox coordinates.
            min_lon = rnd.uniform(info[0][0], info[0][2] - delta)
            min_lat = rnd.uniform(info[0][1], info[0][3] - delta)
            max_lon = min_lon + delta
            max_lat = min_lat + delta
            bbox = (min_lon, min_lat, max_lon, max_lat)
            #
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            gmap = gmplot.GoogleMapPlotter(center_lat, center_lon, 13, apikey='AIzaSyApAatZz85dsgZSWQD_L59EmeBt5enPPDE')
            # Generate network sample.
            graph, _, stores, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                                 hotspots=False, poi_names=info[1].keys())
            #
            components = graph.get_components()
            if len(components) > 1:
                sizes = {component: len(nodes) for component, nodes in components.iteritems()}
                nodes = components[max(sizes.iteritems(), key=operator.itemgetter(1))[0]]
                graph = graph.extract_node_induced_subgraph(nodes)
                stores = set(graph.keys()).intersection(stores)
            #
            num_stores = len(stores)
            if num_stores == 0:
                continue
            #
            stores_per_ret = dict()
            for store in stores:
                retailer = graph[store][2]['name']
                try:
                    stores_per_ret[retailer].append(store)
                except KeyError:
                    stores_per_ret[retailer] = [store]
            #
            num_retailers = len(stores_per_ret.keys())
            # if num_retailers < len(info[1]):
            #     continue
            #
            free = set(graph.keys()).difference(stores)
            for num_customers in num_customers_r:
                customers = rnd.choice(a=list(free), size=num_customers, replace=False)
                rs = list()
                idx = 0
                for i, (retailer, stores_retailer) in enumerate(stores_per_ret.iteritems()):
                    #
                    lats = list()
                    lons = list()
                    for store_retailer in stores_retailer:
                        lats.append(graph[store_retailer][2]['lat'])
                        lons.append(graph[store_retailer][2]['lon'])
                    gmap.scatter(lats, lons, element_colors[i % len(element_colors)], size=75, marker=False)
                    #
                    num_customers_retailer = int(round(num_customers * info[1][retailer]))
                    if i < num_retailers - 1:
                        cust_ret = customers[idx:idx + num_customers_retailer]
                    else:
                        cust_ret = customers[idx:num_customers]
                    #
                    lats = list()
                    lons = list()
                    for customer in cust_ret:
                        lats.append(graph[customer][2]['lat'])
                        lons.append(graph[customer][2]['lon'])
                        rs.append(([(store_retailer, 1, 300)
                                    for store_retailer in stores_retailer], (customer, 1, 300)))
                    idx += num_customers_retailer
                    gmap.scatter(lats, lons, element_colors[i % len(element_colors)], size=25, marker=False)
                #
                free = free.difference(customers)
                #
                # g = Graph()
                # g = graph.copy()
                # print "PART 1: SDs started"
                # time1 = time.clock()
                # g.compute_dist_paths(origins=customers, destinations=customers, compute_paths=False)
                # g.compute_dist_paths(origins=customers, destinations=stores, compute_paths=False)
                # g.compute_dist_paths(origins=stores, destinations=stores, compute_paths=False)
                # time2 = time.clock() - time1
                # print "PART 1: SDs finished", time2
                #
                for ratio in ratios:
                    num_drivers = int(round(num_customers / ratio))
                    z = osm.zipf_sample_bbox(bbox, free, num_drivers, hotspots=False, pois=False, seed=seed)
                    if z is None:
                        continue
                    u = rnd.choice(a=list(free.difference(z)), size=num_drivers, replace=False)
                    for d_l in driver_locations:
                        if d_l == 'U-U':
                            d_starts_ends = rnd.choice(a=list(free), size=num_drivers * 2, replace=False)
                            ds = [((d_starts_ends[i], 1, 300), (d_starts_ends[i + num_drivers], 1, 300))
                                  for i in range(num_drivers)]
                        else:
                            if d_l == "Z-U":
                                ds = [((z[i], 1, 300), (u[i], 1, 300)) for i in range(num_drivers)]
                            else:
                                ds = [((u[i], 1, 300), (z[i], 1, 300)) for i in range(num_drivers)]
                        #
                        s_lats = list()
                        s_lons = list()
                        e_lats = list()
                        e_lons = list()
                        starts = list()
                        ends = list()
                        paths = list()
                        for ((s, _, _), (e, _, _)) in ds:
                            s_lats.append(graph[s][2]['lat'])
                            s_lons.append(graph[s][2]['lon'])
                            e_lats.append(graph[e][2]['lat'])
                            e_lons.append(graph[e][2]['lon'])
                            #
                            starts.append(s)
                            ends.append(e)
                            graph.compute_dist_paths(origins=[s], destinations=[e])
                            paths.append(graph.paths[tuple(sorted([s, e]))])

                        gmap.scatter(s_lats, s_lons, '#000000', size=60, marker=False)
                        gmap.scatter(e_lats, e_lons, '#000000', size=40, marker=False)

                        gmap.draw("maps/setup.html")

                        # print "PART 1: SDs started"
                        # time1 = time.clock()
                        # g.compute_dist_paths(origins=starts, destinations=stores, compute_paths=False)
                        # g.compute_dist_paths(origins=customers, destinations=ends, compute_paths=False)
                        # time2 = time.clock() - time1
                        # print "PART 2: SDs finished", time2
                        #
                        csdp_ap = CsdpAp(graph)
                        csdp_ap._requests = rs
                        csdp_ap._drivers = list(ds)
                        csdp_ap._pre_process_requests_drivers()
                        partitions = csdp_ap._compute_partitions(method='SP-fraction', fraction_sd=0.1)
                        v_lats = list()
                        v_lons = list()
                        if len(partitions) > 0:
                            gmap.shapes = []
                            s, e = partitions.keys()[0]
                            shops_customers = partitions[(s, e)]
                            for v in shops_customers['all']:
                                try:
                                    v_lats.append(graph[v][2]['lat'])
                                    v_lons.append(graph[v][2]['lon'])
                                except KeyError:
                                    pass
                            gmap.scatter([graph[s][2]['lat']], [graph[s][2]['lon']], '#0000FF', size=60, marker=False)
                            gmap.scatter([graph[e][2]['lat']], [graph[e][2]['lon']], '#0000FF', size=40, marker=False)
                            gmap.scatter(v_lats, v_lons, '#0000FF', size=15, marker=False)
                            gmap.draw("maps/partition_0.html")

                            cells, _ = graph.get_voronoi_paths_cells(paths, nodes=nodes, nodes_by_path=nodes_by_path)

                        # # ----------------------------------------------------------------------------------------------
                        # # SP-based -> Partition='SP-Voronoi'
                        # # ----------------------------------------------------------------------------------------------
                        # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
                        # print cost
                        # routes_map = get_routes_map(routes, graph)
                        # gmap.paths = []
                        # for i, (lats, lons) in enumerate(routes_map):
                        #     gmap.plot(lats, lons, element_colors[i % len(element_colors)])
                        # gmap.draw("maps/Voronoi_FCFA.html")
                        #
                        # # ----------------------------------------------------------------------------------------------
                        # # SP-based -> Partition='SP-fraction'
                        # # ----------------------------------------------------------------------------------------------
                        # for fraction in fractions:
                        #     routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=fraction,
                        #                                  tiebreaker='FCFA')
                        #     print cost
                        #     routes_map = get_routes_map(routes, graph)
                        #     gmap.paths = []
                        #     for i, (lats, lons) in enumerate(routes_map):
                        #         gmap.plot(lats, lons, element_colors[i % len(element_colors)])
                        #     gmap.draw("maps/Fraction_%s_FCFA.html" % str(fraction))
                        #
                        #     routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=fraction,
                        #                                  tiebreaker='B-MST')
                        #     print cost
                        #     routes_map = get_routes_map(routes, graph)
                        #     gmap.paths = []
                        #     for i, (lats, lons) in enumerate(routes_map):
                        #         gmap.plot(lats, lons, element_colors[i % len(element_colors)])
                        #     gmap.draw("maps/Fraction_%s_B-MST.html" % str(fraction))
                        #
                        # for threshold in thresholds:
                        #     # ------------------------------------------------------------------------------------------
                        #     # SP-based -> Partition='SP-threshold'
                        #     # ------------------------------------------------------------------------------------------
                        #     routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold',
                        #                                  threshold_sd=threshold, tiebreaker='FCFA')
                        #     print cost
                        #     routes_map = get_routes_map(routes, graph)
                        #     gmap.paths = []
                        #     for i, (lats, lons) in enumerate(routes_map):
                        #         gmap.plot(lats, lons, element_colors[i % len(element_colors)])
                        #     gmap.draw("maps/Threshold_%s_FCFA.html" % str(threshold))
                        #
                        #     routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold',
                        #                                  threshold_sd=threshold, tiebreaker='B-MST')
                        #     print cost
                        #     routes_map = get_routes_map(routes, graph)
                        #     gmap.paths = []
                        #     for i, (lats, lons) in enumerate(routes_map):
                        #         gmap.plot(lats, lons, element_colors[i % len(element_colors)])
                        #     gmap.draw("maps/Threshold_%s_B-MST.html" % str(threshold))
            #
            sample += 1

