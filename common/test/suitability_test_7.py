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

    weights = {i: generator.weights["VERY_SUITABLE"][0] for i in range(m * n)}
    suitability_graph.update_node_weights(weights)
