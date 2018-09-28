from grid_digraph_generator import GridDigraphGenerator
from suitability import SuitableNodeWeightGenerator, SuitabilityDigraph
from networkx_graph_helper import NetworkXGraphHelper


if __name__ == '__main__':

    generator = SuitableNodeWeightGenerator()

    seed = 0
    m = n = 40

    gh = GridDigraphGenerator()

    node_weighted = gh.generate(m, n,
                                edge_weighted=False,
                                node_weighted=True,
                                node_weight_generator=generator,
                                seed=seed)

    terminals = [470, 388, 750, 1185, 1222, 739, 487, 850, 1299, 333]
    poi = 899

    suitability_graph = SuitabilityDigraph()
    suitability_graph.append_from_graph(node_weighted)

    suitability_graph.extend_suitable_regions(seed, generator)
    suitability_graph.extend_suitable_regions(seed, generator)

    regions = suitability_graph.get_suitable_regions(generator)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(special_nodes=[([poi], None, None), (terminals, None, None)],
                   special_subgraphs=[(r, "#00FF00") for _, (r, _, _, _, _, _) in regions.iteritems()],
                   print_node_labels=True)

    suitability_graph.contract_suitable_regions(generator)

    ngh = NetworkXGraphHelper(suitability_graph)
    ngh.draw_graph(print_node_labels=True)
