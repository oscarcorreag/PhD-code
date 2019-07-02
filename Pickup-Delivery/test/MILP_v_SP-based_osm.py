from osmmanager import OsmManager

if __name__ == '__main__':
    #
    bounds = [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727]  # Melbourne
    delta_meters = 3000.0
    delta = delta_meters / 111111
    #
    osm = OsmManager()
