import numpy as np

from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator
from gmplot import gmplot


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
        #
        stores_by_cust = dict()
        for (name, type), info in stores_customers.iteritems():
            lats = info['lats']
            lons = info['lons']
            if name == 'COLES':
                gmap.scatter(lats, lons, '#FF0000', size=75 if type == 's' else 25, marker=False)
            elif name == 'WOOLWORTHS':
                gmap.scatter(lats, lons, '#00FF00', size=75 if type == 's' else 25, marker=False)
            else:
                gmap.scatter(lats, lons, '#0000FF', size=75 if type == 's' else 25, marker=False)


        gmap.draw("my_map.html")
        found = True
