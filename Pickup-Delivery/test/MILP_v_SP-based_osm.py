import numpy as np
import gmplot

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from csdp_ap import CsdpAp

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
    #
    bounds = [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727]  # Melbourne
    delta_meters = 10000.0
    delta = delta_meters / 111111
    found = False
    #
    iter = 0
    while not found and iter < 1000:

        iter += 1

        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        #
        osm = OsmManager()
        generator = SuitableNodeWeightGenerator()
        graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                           hotspots=False, poi_names=['COLES', 'WOOLWORTHS', 'ALDI'])
        if len(pois) < 10:
            continue

        print min_lon, min_lat, max_lon, max_lat
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        gmap = gmplot.GoogleMapPlotter(center_lat, center_lon, 13, apikey='')
        #
        stores_customers = dict()
        # STORES
        for poi in pois:
            lat = graph[poi][2]['lat']
            lon = graph[poi][2]['lon']
            name = graph[poi][2]['name']
            try:
                stores_customers[(name, 's')]['ids'].append(poi)
                stores_customers[(name, 's')]['lats'].append(lat)
                stores_customers[(name, 's')]['lons'].append(lon)
            except KeyError:
                stores_customers[(name, 's')] = {'ids': [poi], 'lats': [lat], 'lons': [lon]}
        # CUSTOMERS
        customers = np.random.choice(a=list(graph.keys()), size=30, replace=False)
        for customer in customers:
            lat = graph[customer][2]['lat']
            lon = graph[customer][2]['lon']
            rnd = np.random.uniform()
            if rnd < 1.0 / 3.0:
                name = 'COLES'
            elif rnd < 2.0 / 3.0:
                name = 'WOOLWORTHS'
            else:
                name = 'ALDI'
            try:
                stores_customers[(name, 'c')]['ids'].append(customer)
                stores_customers[(name, 'c')]['lats'].append(lat)
                stores_customers[(name, 'c')]['lons'].append(lon)
            except KeyError:
                stores_customers[(name, 'c')] = {'ids': [customer], 'lats': [lat], 'lons': [lon]}
        # Scatter stores and customers.
        customers_dict = dict()
        for (name, type_), info in stores_customers.iteritems():
            lats = info['lats']
            lons = info['lons']
            if name == 'COLES':
                gmap.scatter(lats, lons, '#FF0000', size=75 if type_ == 's' else 25, marker=False)
            elif name == 'WOOLWORTHS':
                gmap.scatter(lats, lons, '#00FF00', size=75 if type_ == 's' else 25, marker=False)
            else:
                gmap.scatter(lats, lons, '#0000FF', size=75 if type_ == 's' else 25, marker=False)
            if type_ == 'c':
                customers_dict.update({customer: name for customer in info['ids']})
        # DRIVERS
        free = set(graph.keys()).difference(pois).difference(customers)
        d_starts_ends = np.random.choice(a=list(free), size=20, replace=False)
        s_lats = list()
        s_lons = list()
        e_lats = list()
        e_lons = list()
        for i, start_end in enumerate(d_starts_ends):
            if i < 10:
                s_lats.append(graph[start_end][2]['lat'])
                s_lons.append(graph[start_end][2]['lon'])
            else:
                e_lats.append(graph[start_end][2]['lat'])
                e_lons.append(graph[start_end][2]['lon'])
        gmap.scatter(s_lats, s_lons, '#000000', size=60, marker=False)
        gmap.scatter(e_lats, e_lons, '#000000', size=40, marker=False)
        ds = [((d_starts_ends[i], 1, 300), (d_starts_ends[i + 10], 1, 300)) for i in range(10)]
        # REQUESTS
        rs = list()
        for customer, retailer in customers_dict.iteritems():
            rs.append(([(store, 1, 300) for store in stores_customers[(retailer, 's')]['ids']], (customer, 1, 300)))
        # CSDP-AP
        csdp_ap = CsdpAp(graph)
        routes, cost = csdp_ap.solve(rs, ds, method='SP-based', partition_method='SP-threshold')
        for i, route in enumerate(routes):
            lats = list()
            lons = list()
            for v in route:
                lats.append(graph[v][2]['lat'])
                lons.append(graph[v][2]['lon'])
            gmap.plot(lats, lons, element_colors[i % len(element_colors)])

        gmap.draw("my_map.html")
        found = True
