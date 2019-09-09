import operator
import time
import csv

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState
from csdp_ap import CsdpAp


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
    service = 0
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
            service += cost_ - sd
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
            'service': service,
        },
        'dedicated': {
            'no': no_dedicated,
            'total': total_dedicated,
            'avg': (total_dedicated / no_dedicated) if no_dedicated > 0 else 0,
        }
    }
    return stats_


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
    num_samples = 50
    # num_customers_r = [16, 64, 256, 1024]
    num_customers_r = [32]
    ratios = [4.0]
    # ratios = [2.0]
    # fractions = [0.1, 0.3, 0.5]
    fractions = []
    # thresholds = [1.1, 1.3, 1.5]
    thresholds = []
    # driver_locations = ['Z-U', 'U-Z', 'U-U']
    driver_locations = ['Z-U']
    max_loads = [0, 2, 4, 8, 10]
    # max_loads = [0]
    #
    results = []
    sample = 0
    seed = 1000
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
            # Generate network sample.
            graph, _, shops, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                                hotspots=False, poi_names=info[1].keys())
            #
            components = graph.get_components()
            if len(components) > 1:
                sizes = {component: len(nodes) for component, nodes in components.iteritems()}
                nodes = components[max(sizes.iteritems(), key=operator.itemgetter(1))[0]]
                graph = graph.extract_node_induced_subgraph(nodes)
                shops = set(graph.keys()).intersection(shops)
            #
            csdp_ap = CsdpAp(graph)
            #
            N = len(graph.keys())
            num_shops = len(shops)
            #
            if num_shops == 0:
                continue
            #
            shops_per_ret = dict()
            for shop in shops:
                retailer = graph[shop][2]['name']
                try:
                    shops_per_ret[retailer].append(shop)
                except KeyError:
                    shops_per_ret[retailer] = [shop]
            #
            num_retailers = len(shops_per_ret.keys())
            total_share = 0
            for retailer in shops_per_ret:
                total_share += info[1][retailer]
            adj_share = {retailer: info[1][retailer] / total_share for retailer in shops_per_ret}
            # if num_retailers < len(info[1]):
            #     continue
            #
            free = set(graph.keys()).difference(shops)
            for num_customers in num_customers_r:
                customers = rnd.choice(a=list(free), size=num_customers, replace=False)
                rs = list()
                idx = 0
                for i, (retailer, shops_ret) in enumerate(shops_per_ret.iteritems()):
                    # num_customers_retailer = int(round(num_customers * info[1][retailer]))
                    num_customers_retailer = int(round(num_customers * adj_share[retailer]))
                    if i < num_retailers - 1:
                        cust_ret = customers[idx:idx + num_customers_retailer]
                    else:
                        cust_ret = customers[idx:num_customers]
                    for customer in cust_ret:
                        rs.append(([(shop, 1, 300) for shop in shops_ret], (customer, 1, 300)))
                    idx += num_customers_retailer
                #
                free = set(graph.keys()).difference(customers)
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

                        # starts = [ds[i][0][0] for i in range(num_drivers)]
                        # ends = [ds[i][1][0] for i in range(num_drivers)]
                        # graph.compute_dist_paths(origins=starts, destinations=shops, compute_paths=False)
                        # graph.compute_dist_paths(origins=shops, destinations=customers, compute_paths=False)
                        # graph.compute_dist_paths(origins=customers, destinations=ends, compute_paths=False)

                        # # ----------------------------------------------------------------------------------------------
                        # # MILP
                        # # ----------------------------------------------------------------------------------------------
                        # st = time.clock()
                        # try:
                        #     routes, cost = csdp_ap.solve(rs, ds)
                        # except RuntimeError:
                        #     continue
                        # et = time.clock() - st
                        # stats = compute_stats_per_driver_type(routes, graph)
                        #
                        # line = ['MILP', 0, seed, region, N, delta_meters, num_pois, num_retailers, len(rs), ratio,
                        #         len(ds), d_l, sample, et, cost, stats['ad hoc']['total'],
                        #         stats['dedicated']['total'], stats['ad hoc']['service'], stats['ad hoc']['no'],
                        #         stats['dedicated']['no'], stats['ad hoc']['avg detour'], 0]
                        # print line
                        # results.append(line)

                        # ----------------------------------------------------------------------------------------------
                        # SP-based -> Partition='SP-Voronoi'
                        # ----------------------------------------------------------------------------------------------
                        st = time.clock()
                        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', assignment_method='SP-Voronoi')
                        et = time.clock() - st

                        # TODO: Simple control to avoid prohibitive computation
                        if (routes, cost) == (None, -1):
                            line = ['SP-Voronoi-DT', 0, seed, region, N, delta_meters, num_shops, num_retailers,
                                    len(rs),
                                    ratio, len(ds), d_l, sample, et, cost, 0, 0, 0, 0, 0, 0]
                        else:
                            stats = compute_stats_per_driver_type(routes, graph)

                            line = ['SP-Voronoi', 0, seed, region, N, delta_meters, num_shops, num_retailers,
                                    len(rs), ratio, len(ds), d_l, sample, et, cost, stats['ad hoc']['total'],
                                    stats['dedicated']['total'], stats['ad hoc']['service'],
                                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg detour']]
                        print line
                        results.append(line)

                        for max_load in max_loads:
                            st = time.clock()
                            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', max_load=max_load)
                            et = time.clock() - st

                            # TODO: Simple control to avoid prohibitive computation
                            if (routes, cost) == (None, -1):
                                line = ['LL-EP', 0, seed, region, N, delta_meters, num_shops, num_retailers, len(rs),
                                        ratio, len(ds), d_l, sample, et, cost, 0, 0, 0, 0, 0, 0, max_load]
                            else:
                                stats = compute_stats_per_driver_type(routes, graph)

                                line = ['LL-EP', 0, seed, region, N, delta_meters, num_shops, num_retailers, len(rs),
                                        ratio, len(ds), d_l, sample, et, cost, stats['ad hoc']['total'],
                                        stats['dedicated']['total'], stats['ad hoc']['service'], stats['ad hoc']['no'],
                                        stats['dedicated']['no'], stats['ad hoc']['avg detour'], max_load]
                            print line
                            results.append(line)

                            # ----------------------------------------------------------------------------------------------
                            # SP-based -> Partition='SP-fraction'
                            # ----------------------------------------------------------------------------------------------
                            for fraction in fractions:
                                st = time.clock()
                                routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-fraction',
                                                             fraction_sd=fraction, max_load=max_load)
                                et = time.clock() - st

                                # TODO: Simple control to avoid prohibitive computation
                                if (routes, cost) == (None, -1):
                                    line = ['SP-fraction_LL-EP', fraction, seed, region, N, delta_meters, num_shops,
                                            num_retailers, len(rs), ratio, len(ds), d_l, sample, et, cost, 0, 0, 0, 0, 0, 0, max_load]
                                else:
                                    stats = compute_stats_per_driver_type(routes, graph)

                                    line = ['SP-fraction_LL-EP', fraction, seed, region, N, delta_meters, num_shops,
                                            num_retailers, len(rs), ratio, len(ds), d_l, sample, et, cost,
                                            stats['ad hoc']['total'], stats['dedicated']['total'],
                                            stats['ad hoc']['service'], stats['ad hoc']['no'], stats['dedicated']['no'],
                                            stats['ad hoc']['avg detour'], max_load]
                                print line
                                results.append(line)

                            for threshold in thresholds:
                                # # ------------------------------------------------------------------------------------------
                                # # MILP-threshold
                                # # ------------------------------------------------------------------------------------------
                                # st = time.clock()
                                # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=threshold)
                                # et = time.clock() - st
                                # stats = compute_stats_per_driver_type(routes, graph)
                                #
                                # line = ['MILP-threshold', threshold, seed, region, N, delta_meters, num_pois, num_retailers,
                                #         len(rs), ratio, len(ds), d_l, sample, et, cost, stats['ad hoc']['total'],
                                #         stats['dedicated']['total'], stats['ad hoc']['no'], stats['dedicated']['no'],
                                #         stats['ad hoc']['avg'], stats['dedicated']['avg'], stats['ad hoc']['avg detour'],
                                #         stats['ad hoc']['w avg detour']]
                                # print line
                                # results.append(line)

                                # ------------------------------------------------------------------------------------------
                                # SP-based -> Partition='SP-threshold'
                                # ------------------------------------------------------------------------------------------
                                st = time.clock()
                                routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold',
                                                             threshold_sd=threshold, max_load=max_load)
                                et = time.clock() - st

                                # TODO: Simple control to avoid prohibitive computation
                                if (routes, cost) == (None, -1):
                                    line = ['SP-threshold_LL_EP', threshold, seed, region, N, delta_meters, num_shops,
                                            num_retailers, len(rs), ratio, len(ds), d_l, sample, et, cost, 0, 0, 0, 0, 0, 0, max_load]
                                else:
                                    stats = compute_stats_per_driver_type(routes, graph)

                                    line = ['SP-threshold_LL_EP', threshold, seed, region, N, delta_meters, num_shops,
                                            num_retailers, len(rs), ratio, len(ds), d_l, sample, et, cost,
                                            stats['ad hoc']['total'], stats['dedicated']['total'],
                                            stats['ad hoc']['service'], stats['ad hoc']['no'], stats['dedicated']['no'],
                                            stats['ad hoc']['avg detour'], max_load]
                                print line
                                results.append(line)
            #
            sample += 1

    result_file = open("files/csdp_ap_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
