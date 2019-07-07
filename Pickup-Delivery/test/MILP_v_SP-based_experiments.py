import numpy as np

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from numpy.random import RandomState
from csdp_ap import CsdpAp


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
    num_req_per_retailer = 5
    num_drv_per_retailer = 2
    #
    results = []
    sample = 0
    initial_seed = 500
    for region, info in regions.iteritems():
        while sample < num_samples:
            #
            rnd = RandomState(initial_seed)
            initial_seed += 1
            # Compute bbox coordinates.
            min_lon = np.random.uniform(info[0][0], info[0][2] - delta)
            min_lat = np.random.uniform(info[0][1], info[0][3] - delta)
            max_lon = min_lon + delta
            max_lat = min_lat + delta
            # Generate network sample.
            graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                               hotspots=False, poi_names=info[1])
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
            customers = np.random.choice(a=list(free), size=num_customers, replace=False)
            rs = list()
            for i, retailer in enumerate(stores_per_ret):
                first_cust_ret = i * num_req_per_retailer
                cust_ret = customers[first_cust_ret:first_cust_ret + num_req_per_retailer]
                for customer in cust_ret:
                    rs.append(([(store, 1, 300) for store in stores_per_ret[retailer]], (customer, 1, 300)))
            #
            free = set(graph.keys()).difference(customers)
            num_drivers = num_drv_per_retailer * num_retailers
            d_starts_ends = np.random.choice(a=list(free), size=num_drivers * 2, replace=False)
            ds = [((d_starts_ends[i], 1, 300), (d_starts_ends[i + num_drivers], 1, 300)) for i in range(num_drivers)]
            _, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
            print cost