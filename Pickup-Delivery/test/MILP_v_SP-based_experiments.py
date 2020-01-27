import sys
import operator
import time
import csv
import cProfile

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState
from csdp_ap import CsdpAp


class Experiment:

    def __init__(self, city, bbox, meters, market_share, rnd, seed, graph, shops):
        self._city = city
        self._bbox = bbox
        self._meters = meters
        self._seed = seed
        self._rnd = rnd
        self._graph = graph.copy()
        self._shops = set(shops)
        self._free = set(graph.keys()).difference(shops)
        self._net_size = len(graph.keys())
        self._num_shops = len(shops)
        self._shops_per_ret = dict()
        for shop in shops:
            retailer = graph[shop][2]['name']
            try:
                self._shops_per_ret[retailer].append(shop)
            except KeyError:
                self._shops_per_ret[retailer] = [shop]
        self._num_retailers = len(self._shops_per_ret.keys())
        total_share = 0
        for retailer in self._shops_per_ret:
            total_share += market_share[retailer]
        self._market_share = {retailer: market_share[retailer] / total_share for retailer in self._shops_per_ret}
        #
        self._params = dict()
        self._rs = None
        self._rs_bck = None
        self._ds = None
        self._z = None
        self._u = None

    def set_customers(self, num_customers):
        self._params['num_customers'] = num_customers
        customers = self._rnd.choice(a=list(self._free), size=num_customers, replace=False)
        self._rs = list()
        idx = 0
        for i, (retailer, shops_ret) in enumerate(self._shops_per_ret.iteritems()):
            num_customers_retailer = int(round(num_customers * self._market_share[retailer]))
            if i < self._num_retailers - 1:
                cust_ret = customers[idx:idx + num_customers_retailer]
            else:
                cust_ret = customers[idx:num_customers]
            for customer in cust_ret:
                self._rs.append(([(shop, 1, 300) for shop in shops_ret], (customer, 1, 300)))
            idx += num_customers_retailer
        self._rs_bck = list(self._rs)
        self._free = self._free.difference(customers)
        self._z = None
        self._u = None
        return customers

    def set_drivers(self, ratio, distr):
        # Drivers
        self._params['ratio'] = ratio
        self._params['distr'] = distr
        num_drivers = int(round(self._params['num_customers'] / ratio))
        if self._z is None:
            osm = OsmManager()
            self._z = osm.zipf_sample_bbox(self._bbox, self._free, num_drivers, hotspots=False, pois=False,
                                           seed=self._seed)
            if self._z is None:
                return None
            self._u = self._rnd.choice(a=list(self._free.difference(self._z)), size=num_drivers, replace=False)
        if distr == 'U-U':
            d_starts_ends = self._rnd.choice(a=list(self._free), size=num_drivers * 2, replace=False)
            self._ds = [((d_starts_ends[i], 1, 300), (d_starts_ends[i + num_drivers], 1, 300))
                        for i in range(num_drivers)]
        else:
            if distr == "Z-U":
                self._ds = [((self._z[i], 1, 300), (self._u[i], 1, 300)) for i in range(num_drivers)]
            else:
                self._ds = [((self._u[i], 1, 300), (self._z[i], 1, 300)) for i in range(num_drivers)]
        return self._ds

    def run(self, graph, approach, sample, solve='BB', limit=0, partition=None, fraction=.5, threshold=1.5,
            classical=False):
        csdp_ap = CsdpAp(graph)
        param = 0
        #
        if classical:
            new_rs = list()
            for shops_tws, (customer, _, _) in self._rs:
                shops = tuple(sorted([shop for shop, _, _ in shops_tws]))
                nearest = None
                sd = sys.maxint
                for shop in shops:
                    d = graph.dist[tuple(sorted([customer, shop]))]
                    if d < sd:
                        sd = d
                        nearest = shop
                new_rs.append(([(nearest, 1, 300)], (customer, 1, 300)))
            self._rs = list(new_rs)
        else:
            self._rs = list(self._rs_bck)
        #
        st = time.clock()
        if approach == 'MILP':
            routes, cost, _ = csdp_ap.solve(self._rs, self._ds)
        else:
            if partition is None:
                routes, cost, sc = csdp_ap.solve(self._rs, self._ds, method='SP-based', assignment_method=approach,
                                                 solve_partition_method=solve, max_load=limit)
            elif partition == 'SP-fraction':
                routes, cost, sc = csdp_ap.solve(self._rs, self._ds, method='SP-based', assignment_method=approach,
                                                 partition_method=partition, fraction_sd=fraction,
                                                 solve_partition_method=solve, max_load=limit, strict=True)
                param = fraction
            else:
                routes, cost, sc = csdp_ap.solve(self._rs, self._ds, method='SP-based', assignment_method=approach,
                                                 partition_method=partition, threshold_sd=threshold,
                                                 solve_partition_method=solve, max_load=limit, strict=True)
                param = threshold
        et = time.clock() - st

        # TODO: Simple control to avoid prohibitive computation
        if cost == -1:
            line = [approach, partition, solve, param, self._seed, self._city, self._net_size, self._meters,
                    self._num_shops, self._num_retailers, len(self._rs), self._params['ratio'], len(self._ds),
                    self._params['distr'], sample, et, cost, 0, 0, 0, 0, 0, 0, 0, 0]
        else:
            stats = Experiment.compute_stats_per_driver_type(graph, routes)

            line = [approach, partition, solve, param, self._seed, self._city, self._net_size, self._meters,
                    self._num_shops, self._num_retailers, len(self._rs), self._params['ratio'], len(self._ds),
                    self._params['distr'], sample, et, cost, stats['ad hoc']['total'], stats['dedicated']['total'],
                    stats['ad hoc']['service'], stats['ad hoc']['no'], stats['dedicated']['no'],
                    stats['ad hoc']['avg detour'], limit, len(sc)]
        print line
        return line

    @staticmethod
    def compute_stats_per_driver_type(graph, routes):
        #
        pairs = list()
        for route in routes:
            pairs.append(tuple(sorted([route[0], route[-1]])))
        graph.compute_dist_paths(pairs=pairs, compute_paths=False)
        #
        no_ad_hoc = 0
        no_dedicated = 0
        total_ad_hoc = 0
        total_dedicated = 0
        total_sd = 0
        costs_ad_hoc = list()
        total_detour = 0
        service = 0
        for route in routes:
            start_v = route[0]
            end_v = route[-1]
            if start_v == end_v:
                no_dedicated += 1
                total_dedicated += Experiment.compute_route_cost(graph, route)
            else:
                no_ad_hoc += 1
                cost_ = Experiment.compute_route_cost(graph, route)
                total_ad_hoc += cost_
                sd = graph.dist[tuple(sorted([start_v, end_v]))]
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

    @staticmethod
    def compute_route_cost(graph, route):
        cost = 0
        for i_ in range(len(route) - 1):
            v = route[i_]
            w = route[i_ + 1]
            if v != w:
                cost += graph.get_edges()[tuple(sorted([v, w]))]
        return cost


if __name__ == '__main__':
    #
    o = OsmManager()
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
    num_samples = 20
    #
    models = [True, False]  # True: classical CD, False: CD-CRSS
    #
    num_customers_r = [1024, 2048]
    # num_customers_r = [4096]
    # ratios = [1.0, 2.0, 4.0, 8.0]
    ratios = [4.0]
    # fractions = [0.05, 0.1, 0.15, 0.2]
    fractions = []
    # thresholds = [1.05, 1.1, 1.15, 1.2]
    thresholds = []
    without_partitioning = True
    # driver_locations = ['Z-U', 'U-Z', 'U-U']
    driver_locations = ['Z-U']
    # max_loads = [4, 6, 8, 10, 12]
    max_loads = [8]
    # bounds = ['both', 'lb', 'ub']
    bounds = ['both']
    #
    # approaches = ['MILP', 'V-NN', 'V-BB', 'IRB-NN', 'IRB-BB']
    approaches = ['IRB-NN', 'IRB-BB']
    # approaches = ['IRB-NN', 'IRB-BB']
    results = []
    smpl = 0
    s = 1077
    for region, info in regions.iteritems():
        while smpl < num_samples:
            #
            s += 1
            rnds = RandomState(s)
            # Compute bbox coordinates.
            min_lon = rnds.uniform(info[0][0], info[0][2] - delta)
            min_lat = rnds.uniform(info[0][1], info[0][3] - delta)
            max_lon = min_lon + delta
            max_lat = min_lat + delta
            bounding_box = (min_lon, min_lat, max_lon, max_lat)
            # Generate network sample.
            g, _, stores, _, _ = o.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                           hotspots=False, poi_names=info[1].keys())
            #
            components = g.get_components()
            if len(components) > 1:
                sizes = {component: len(nodes) for component, nodes in components.iteritems()}
                nodes = components[max(sizes.iteritems(), key=operator.itemgetter(1))[0]]
                g = g.extract_node_induced_subgraph(nodes)
                stores = set(g.keys()).intersection(stores)

            if len(stores) == 0:
                continue

            experiment = Experiment(region, bounding_box, delta_meters, info[1], rnds, s, g, stores)

            for nc in num_customers_r:
                if 2 * nc + len(stores) > len(g.keys()):  # Assuming max. no. drivers = no. customers / 2.0
                    print "Not enough vertices!"
                    break
                custs = experiment.set_customers(nc)

                print "PART 1: SDs started"
                time1 = time.clock()
                g.compute_dist_paths(origins=custs, destinations=custs, compute_paths=False)
                g.compute_dist_paths(origins=custs, destinations=stores, compute_paths=False)
                g.compute_dist_paths(origins=stores, destinations=stores, compute_paths=False)
                time2 = time.clock() - time1
                print "PART 1: SDs finished", time2

                for r in ratios:
                    for d_l in driver_locations:
                        ds = experiment.set_drivers(r, d_l)
                        if ds is None:
                            break
                        starts = list()
                        ends = list()
                        for (start, _, _), (end, _, _) in ds:
                            g.compute_dist_paths(origins=[start], destinations=[end])
                            starts.append(start)
                            ends.append(end)

                        print "PART 2: SDs started"
                        time1 = time.clock()
                        g.compute_dist_paths(origins=starts, destinations=stores, compute_paths=False)
                        g.compute_dist_paths(origins=custs, destinations=ends, compute_paths=False)
                        time2 = time.clock() - time1
                        print "PART 2: SDs finished", time2

                        for model in models:
                            for appr in approaches:
                                if appr == 'MILP':
                                    res = experiment.run(g, 'MILP', smpl, classical=model)
                                    results.append(res)
                                else:
                                    if without_partitioning:
                                        if appr == 'V-NN':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'NN', classical=model)
                                            results.append(res)
                                        elif appr == 'V-BB':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'BB', classical=model)
                                            results.append(res)
                                        elif appr == 'IRB-NN' or appr == 'IRB-BB':
                                            for max_load in max_loads:
                                                if appr == 'IRB-NN':
                                                    res = experiment.run(g, 'LL-EP', smpl, 'NN', max_load,
                                                                         classical=model)
                                                else:
                                                    res = experiment.run(g, 'LL-EP', smpl, 'BB', max_load,
                                                                         classical=model)
                                                results.append(res)
                                    for f in fractions:
                                        if appr == 'V-NN':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'NN', partition='SP-fraction',
                                                                 fraction=f, classical=model)
                                            results.append(res)
                                        elif appr == 'V-BB':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'BB', partition='SP-fraction',
                                                                 fraction=f, classical=model)
                                            results.append(res)
                                        elif appr == 'IRB-NN' or appr == 'IRB-BB':
                                            for max_load in max_loads:
                                                if appr == 'IRB-NN':
                                                    res = experiment.run(g, 'LL-EP', smpl, 'NN', max_load,
                                                                         partition='SP-fraction', fraction=f,
                                                                         classical=model)
                                                else:
                                                    res = experiment.run(g, 'LL-EP', smpl, 'BB', max_load,
                                                                         partition='SP-fraction', fraction=f,
                                                                         classical=model)
                                                results.append(res)

                                    for t in thresholds:
                                        if appr == 'V-NN':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'NN', partition='SP-threshold',
                                                                 threshold=t, classical=model)
                                            results.append(res)
                                        elif appr == 'V-BB':
                                            res = experiment.run(g, 'SP-Voronoi', smpl, 'BB', partition='SP-threshold',
                                                                 threshold=t, classical=model)
                                            results.append(res)
                                        elif appr == 'IRB-NN' or appr == 'IRB-BB':
                                            for max_load in max_loads:
                                                if appr == 'IRB-NN':
                                                    res = experiment.run(g, 'LL-EP', smpl, 'NN', max_load,
                                                                         partition='SP-threshold', threshold=t,
                                                                         classical=model)
                                                else:
                                                    res = experiment.run(g, 'LL-EP', smpl, 'BB', max_load,
                                                                         partition='SP-threshold', threshold=t,
                                                                         classical=model)
                                                results.append(res)

            #
            smpl += 1

    result_file = open("files/csdp_ap_" + time.strftime("%d%b%Y_%H%M%S") + ".csv", 'wb')
    wr = csv.writer(result_file)
    wr.writerows(results)
