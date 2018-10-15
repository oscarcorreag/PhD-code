from osmdbmanager import OsmDBManager


if __name__ == "__main__":
    osmdbmngr = OsmDBManager("postgres", "naya0105", "osm", "localhost")
    print osmdbmngr.get_knn(144.960339, -37.798569, 5)
