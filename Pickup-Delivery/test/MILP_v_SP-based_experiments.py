import operator
import time
import csv

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState
from csdp_ap import CsdpAp
from digraph import Digraph


def compute_dedicated(routes_):
    dedicated_ = 0
    for route in routes_:
        s = route[0]
        e = route[-1]
        if s == e:
            dedicated_ += 1
    return dedicated_


def compute_route_cost(route, graph_):
    route_graph = Digraph(undirected=False)
    route_graph.append_from_path(route, graph_)
    return route_graph.compute_total_weights()[0]


def compute_avg_cost_routes(routes_, graph_):
    total_cost = 0
    for route in routes_:
        route_cost = compute_route_cost(route, graph_)
        total_cost += route_cost
    return total_cost / len(routes)


def compute_avg_cost_routes_per_driver_type(routes_, graph_):
    avgs_ = {'ad hoc': 0, 'dedicated': 0}
    routes_ad_hoc = list()
    routes_dedicated = list()
    for route in routes_:
        s = route[0]
        e = route[-1]
        if s == e:
            routes_dedicated.append(route)
        else:
            routes_ad_hoc.append(route)
    avgs_['ad hoc'] = compute_avg_cost_routes(routes_ad_hoc, graph_)
    avgs_['dedicated'] = compute_avg_cost_routes(routes_dedicated, graph_)
    return avgs_


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
    num_samples = 10
    num_req_per_retailer = 5
    num_drv_per_retailer = 2
    #
    results = []
    sample = 0
    initial_seed = 0
    for region, info in regions.iteritems():
        while sample < num_samples:
            #
            rnd = RandomState(initial_seed)
            initial_seed += 1
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

            # ----------------------------------------------------------------------------------------------------------
            # MILP
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['MILP', 0, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)

            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-Voronoi'
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-Voronoi')
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-Voronoi', 0, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-fraction' -> fraction_sd=0.5
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based')
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-fraction', 0.5, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-fraction' -> fraction_sd=0.4
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.4)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-fraction', 0.4, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-fraction' -> fraction_sd=0.3
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.3)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-fraction', 0.3, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-fraction' -> fraction_sd=0.2
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.2)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-fraction', 0.2, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-fraction' -> fraction_sd=0.1
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', fraction_sd=.1)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-fraction', 0.1, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.5
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 1.5, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.6
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.6)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 1.6, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.7
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.7)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 1.7, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.8
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.8)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 1.8, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=1.9
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=1.9)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 1.9, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            # ----------------------------------------------------------------------------------------------------------
            # SP-based -> Partition='SP-threshold' -> threshold_sd=2.0
            # ----------------------------------------------------------------------------------------------------------
            st = time.clock()
            routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold', threshold_sd=2.0)
            dedicated = compute_dedicated(routes)
            avgs = compute_avg_cost_routes_per_driver_type(routes, graph)
            et = time.clock() - st

            line = ['SP-threshold', 2.0, region, N, delta_meters, num_pois, num_retailers, num_req_per_retailer,
                    num_drv_per_retailer, sample, et, cost, dedicated, avgs['ad hoc'], avgs['dedicated']]
            print line
            results.append(line)
            #
            sample += 1

    result_file = open("files/csdp_ap_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
