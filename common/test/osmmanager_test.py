from osmmanager import OsmManager
from suitability import SuitableNodeWeightGenerator

if __name__ == "__main__":
    osm = OsmManager()
    # osm.generate_samples(21303, "maribyrnong")
    generator = SuitableNodeWeightGenerator()
    _, _, _, _, nodes_by_sa2_code = osm.generate_graph_for_file("maribyrnong", 602, generator, with_hotspots=False)
    osm.choose_hotspots_according_to_population(21303, 127, nodes_by_sa2_code)
