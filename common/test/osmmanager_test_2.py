from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator

if __name__ == "__main__":
    osm = OsmManager()
    res = osm.get_session_users(65)
    print res