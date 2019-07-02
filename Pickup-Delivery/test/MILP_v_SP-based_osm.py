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
        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        #
        osm = OsmManager()
        generator = SuitableNodeWeightGenerator()
        graph, _, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator,
                                                           hotspots=False, poi_names=['COLES', 'WOOLWORTHS', 'ALDI'])
        if len(pois) >= 10:
            print min_lon, min_lat, max_lon, max_lat
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            gmap = gmplot.GoogleMapPlotter(center_lat, center_lon, 13, apikey='AIzaSyApAatZz85dsgZSWQD_L59EmeBt5enPPDE')
            lats = list()
            lons = list()
            for poi in pois:
                lats.append(graph[poi][2]['lat'])
                lons.append(graph[poi][2]['lon'])
            gmap.scatter(lats, lons, '#3B0B39', size=40, marker=False)
            gmap.draw("my_map.html")
            found = True
        iter += 1

