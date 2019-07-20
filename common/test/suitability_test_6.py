from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityGraph


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 30

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=True,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    suitability_graph = SuitabilityGraph()
    suitability_graph.append_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    suitability_graph.get_dist_paths_between_regions(generator, exc_wcr=[10, 500, 854], inc_wcp=[10, 500, 854])
