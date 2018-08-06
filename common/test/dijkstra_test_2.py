from suitability import SuitabilityDigraph, SuitableNodeWeightGenerator
from grid_digraph_generator import GridDigraphGenerator
from networkx_graph_helper import NetworkXGraphHelper

if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 1
    m = n = 10

    gh = GridDigraphGenerator()
    graph = gh.generate(m, n,
                        edge_weighted=False,
                        node_weighted=True,
                        node_weight_generator=generator,
                        seed=seed)

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(graph)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    suitability_graph.contract_suitable_regions(generator)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(print_node_labels=True)

    suitability_graph.compute_dist_paths(origins=[53], destinations=[65, 86])
    print suitability_graph.dist[(53, 65)], suitability_graph.paths[(53, 65)]
    print suitability_graph.dist[(53, 86)], suitability_graph.paths[(53, 86)]

    suitability_graph.compute_dist_paths(origins=[28], destinations=[72])
    print suitability_graph.dist[(28, 72)], suitability_graph.paths[(28, 72)]
