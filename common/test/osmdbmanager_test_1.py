from osmdbmanager import OsmDBManager


if __name__ == "__main__":
    osmdbmngr = OsmDBManager("postgres", "anabelle1803!", "osm", "localhost")
    # print osmdbmngr.get_knn(144.960339, -37.798569, 5, 200)
    # print osmdbmngr.get_coordinates(30239532)
    # osmdbmngr.copy_hotspots_by_type("service", "parking_aisle")
    # osmdbmngr.copy_hotspots_by_type("amenity", "parking")
    osmdbmngr.copy_highway_nodes()
    # osmdbmngr.copy_pois_by_type("shop", "mall")
