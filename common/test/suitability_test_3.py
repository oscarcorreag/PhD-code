from suitability import SuitableNodeWeightGenerator
from osmdbmanager import OsmDBManager


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    gh = OsmDBManager("postgres", "naya0105", "osm", "localhost")
    suitability_graph = gh.generate_based_on_coords(-37.779007, 144.927753, -37.835427, 144.983372, generator)

    regions = suitability_graph.get_suitable_regions(generator, get_border_internal_nodes=False,
                                                     get_centroid_medoid=True)
