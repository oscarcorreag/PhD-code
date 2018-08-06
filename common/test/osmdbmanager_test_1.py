from osmdbmanager import OsmDBManager


if __name__ == "__main__":
    osmdbmngr = OsmDBManager("postgres", "anabelle1803!", "osm")
    # osmdbmngr.copy_hotspots_by_type("service", "parking_aisle")
    # osmdbmngr.copy_hotspots_by_type("amenity", "parking")
    osmdbmngr.copy_highway_nodes()
    # osmdbmngr.copy_pois_by_type("shop", "mall")
