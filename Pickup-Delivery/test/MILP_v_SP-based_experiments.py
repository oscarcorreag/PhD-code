import operator
import time
import csv
import cProfile

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
    #
    osm = OsmManager()
    generator = SuitableNodeWeightGenerator()
    #
    regions = {
        'MEL': (
            [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727],
            ['COLES', 'WOOLWORTHS', 'ALDI']
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
    num_samples = 100
    num_req_per_retailer = 100
    num_drv_per_retailer = 50
    #
    results = []
    sample = 0
    seed = 10001
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
            # Generate network sample.
            graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                               hotspots=False, poi_names=info[1])
            #
            components = graph.get_components()
            if len(components) > 1:
                sizes = {component: len(nodes) for component, nodes in components.iteritems()}
                nodes = components[max(sizes.iteritems(), key=operator.itemgetter(1))[0]]
                graph = graph.extract_node_induced_subgraph(nodes)
                pois = set(graph.keys()).intersection(pois)
            #
            csdp_ap = CsdpAp(graph)
            #
            N = len(graph.keys())
            num_pois = len(pois)
            #
            if num_pois == 0:
                continue
            #
            stores_per_ret = dict()
            for poi in pois:
                retailer = graph[poi][2]['name']
                try:
                    stores_per_ret[retailer].append(poi)
                except KeyError:
                    stores_per_ret[retailer] = [poi]
            #
            num_retailers = len(stores_per_ret.keys())
            num_customers = num_req_per_retailer * num_retailers
            free = set(graph.keys()).difference(pois)
            customers = rnd.choice(a=list(free), size=num_customers, replace=False)
            rs = list()
            for i, retailer in enumerate(stores_per_ret):
                first_cust_ret = i * num_req_per_retailer
                cust_ret = customers[first_cust_ret:first_cust_ret + num_req_per_retailer]
                for customer in cust_ret:
                    rs.append(([(store, 1, 300) for store in stores_per_ret[retailer]], (customer, 1, 300)))
            #
            free = set(graph.keys()).difference(customers)
            num_drivers = num_drv_per_retailer * num_retailers
            d_starts_ends = rnd.choice(a=list(free), size=num_drivers * 2, replace=False)
            ds = [((d_starts_ends[i], 1, 300), (d_starts_ends[i + num_drivers], 1, 300)) for i in range(num_drivers)]

            # # ----------------------------------------------------------------------------------------------------------
            # # MILP
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # try:
            #     routes, cost = csdp_ap.solve(rs, ds)
            # except RuntimeError:
            #     continue
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP', 0, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-Voronoi'
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-Voronoi', 0, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based')
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-fraction', 0.5, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-fraction' -> fraction_sd=0.4
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.4)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-fraction', 0.4, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-fraction' -> fraction_sd=0.3
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.3)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-fraction', 0.3, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-fraction' -> fraction_sd=0.2
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.2)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-fraction', 0.2, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # SP-based -> Partition='SP-fraction' -> fraction_sd=0.1
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.1)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['SP-fraction', 0.1, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=1.5
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=1.5)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 1.5, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.5
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 1.5, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=1.6
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=1.6)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 1.6, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.6
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.6)
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 1.6, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=1.7
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=1.7)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 1.7, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.7
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.7)
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 1.7, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=1.8
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=1.8)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 1.8, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.8
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.8)
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 1.8, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=1.9
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=1.9)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 1.9, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.9
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.9)
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 1.9, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            # # ----------------------------------------------------------------------------------------------------------
            # # MILP-threshold -> threshold_sd=2.0
            # # ----------------------------------------------------------------------------------------------------------
            # st = time.clock()
            # routes, cost = csdp_ap.solve(rs, ds, method='MILP-threshold', threshold_sd=2.0)
            # et = time.clock() - st
            # stats = compute_stats_per_driver_type(routes, graph)
            #
            # line = ['MILP-threshold', 2.0, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
            #         num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
            #         stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
            #         stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            # print line
            # results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=2.0
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=2.0)
            et = time.clock() - st
            stats = compute_stats_per_driver_type(routes, graph)

            line = ['SP-threshold', 2.0, seed, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['no'], stats['dedicated']['no'], stats['ad hoc']['avg'], stats['dedicated']['avg'],
                    stats['ad hoc']['avg detour'], stats['ad hoc']['w avg detour']]
            print line
            results.append(line)
            #
            sample += 1

    result_file = open("files/csdp_ap_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
